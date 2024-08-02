from geometry import Line, Point, Rectangle

DISCONTINUITY = 5
MIN_LINE_LENGTH = 50


class EdgeConnect:
    def __init__(self, edge_img, rectangles: list, upscale_factor: int):
        """Initialize with edge image, rectangles, specified discontinuity, and minimum line length."""
        self.edge_img = edge_img
        self.rectangles = rectangles
        self.discontinuity = DISCONTINUITY * upscale_factor
        self.min_line_length = MIN_LINE_LENGTH * upscale_factor

    def connect(self) -> list:
        """Create direct connect lines between rectangles."""
        lines = []
        for i in range(len(self.rectangles)):
            for j in range(i + 1, len(self.rectangles)):
                rect1 = self.rectangles[i]
                rect2 = self.rectangles[j]

                if rect1.intersects(rect2, axis='x'):
                    candidate_lines = self._generate_lines(rect1, rect2, axis='x')
                elif rect1.intersects(rect2, axis='y'):
                    candidate_lines = self._generate_lines(rect1, rect2, axis='y')
                else:
                    candidate_lines = []

                lines.extend(self._filter_out_intersecting_lines(candidate_lines, rect1, rect2))

        return lines

    def _generate_lines(self, rect1: Rectangle, rect2: Rectangle, axis) -> list:
        """Generate lines between two rectangles based on the specified axis."""
        lines = []
        subranges = self._find_uninterrupted_subranges(rect1, rect2, axis)
        for start, end in subranges:
            midpoint = (start + end) // 2
            line = self._get_line(midpoint, rect1, rect2, axis)
            if line and line.length() >= self.min_line_length:
                lines.append(line)
        return lines

    @staticmethod
    def _get_line(midpoint: int, rect1: Rectangle, rect2: Rectangle, axis) -> Line:
        """Get adjusted points for a line just outside the target rectangles."""
        if axis == 'x':
            point1 = Point(midpoint, rect1.y + rect1.h) if rect1.y < rect2.y else Point(midpoint, rect1.y)
            point2 = Point(midpoint, rect2.y + rect2.h) if rect2.y < rect1.y else Point(midpoint, rect2.y)
        else:
            point1 = Point(rect1.x + rect1.w, midpoint) if rect1.x < rect2.x else Point(rect1.x, midpoint)
            point2 = Point(rect2.x + rect2.w, midpoint) if rect2.x < rect1.x else Point(rect2.x, midpoint)
        return Line(point1, point2)

    def _find_uninterrupted_subranges(self, rect1: Rectangle, rect2: Rectangle, axis) -> list:
        """Find uninterrupted subranges between two rectangles, considering obstacles."""
        subranges = []
        in_uninterrupted_range = True

        start, end = rect1.get_intersection_range(rect2, axis)
        bound_start, bound_end = rect1.get_bounding_range(rect2, axis, self.discontinuity)

        if end <= start or bound_end <= bound_start:
            return subranges

        current_start = start

        for i in range(start, end + 1):
            if self._has_obstacle(self.edge_img, i, bound_start, bound_end, axis):
                if in_uninterrupted_range and i - current_start >= self.discontinuity:
                    subranges.append((current_start, i - 1))
                in_uninterrupted_range = False
            else:
                if not in_uninterrupted_range:
                    current_start = i
                    in_uninterrupted_range = True

        if in_uninterrupted_range and end - current_start >= self.discontinuity:
            subranges.append((current_start, end))

        return subranges

    @staticmethod
    def _has_obstacle(edge_img, pos: int, bound_start: int, bound_end: int, axis) -> bool:
        """Check for obstacles in the specified range."""
        if axis == 'x':
            return (edge_img[bound_start:bound_end, pos] == 255).any()
        else:
            return (edge_img[pos, bound_start:bound_end] == 255).any()

    def _filter_out_intersecting_lines(self, candidate_lines: list, rect1: Rectangle, rect2: Rectangle) -> list:
        """Filter out lines that intersect with any other rectangle."""
        return [line for line in candidate_lines if not self._line_intersects_any_rectangle(line, rect1, rect2)]

    def _line_intersects_any_rectangle(self, line: Line, rect1: Rectangle, rect2: Rectangle) -> bool:
        """Check if a line intersects with any rectangle other than rect1 and rect2."""
        for rect in self.rectangles:
            if rect is not rect1 and rect is not rect2:
                if line.intersects_rectangle(rect):
                    return True
        return False
