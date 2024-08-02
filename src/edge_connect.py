DISCONTINUITY = 5
MIN_LINE_LENGTH = 20


class Line:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class EdgeConnect:
    def __init__(self, edge_img, rectangles, discontinuity=DISCONTINUITY, min_line_length=MIN_LINE_LENGTH,
                 upscale_factor=1):
        """Initialize with edge image, rectangles, specified discontinuity and minimum line length."""
        self.edge_img = edge_img
        self.rectangles = rectangles
        self.discontinuity = discontinuity * upscale_factor
        self.min_line_length = min_line_length * upscale_factor

    def create_lines(self):
        """Create direct connect lines between rectangles."""
        lines = []
        for i in range(len(self.rectangles)):
            for j in range(i + 1, len(self.rectangles)):
                rect1 = self.rectangles[i]
                rect2 = self.rectangles[j]

                if self._x_intersects(rect1, rect2):  # Check for x-range intersection
                    subranges = self._find_uninterrupted_subranges(rect1, rect2, vertical=True)
                    for start, end in subranges:
                        midpoint_x = (start + end) // 2
                        line = self._vertical_line(midpoint_x, rect1, rect2)
                        if line:
                            lines.append(line)

                if self._y_intersects(rect1, rect2):  # Check for y-range intersection
                    subranges = self._find_uninterrupted_subranges(rect1, rect2, vertical=False)
                    for start, end in subranges:
                        midpoint_y = (start + end) // 2
                        line = self._horizontal_line(midpoint_y, rect1, rect2)
                        if line:
                            lines.append(line)

        return lines

    @staticmethod
    def _x_intersects(rect1, rect2):
        """Check if x ranges of two rectangles intersect"""
        return max(rect1.x, rect2.x) < min(rect1.x + rect1.w, rect2.x + rect2.w)

    @staticmethod
    def _y_intersects(rect1, rect2):
        """Check if y ranges of two rectangles intersect"""
        return max(rect1.y, rect2.y) < min(rect1.y + rect1.h, rect2.y + rect2.h)

    def _vertical_line(self, midpoint_x, rect1, rect2):
        """Get adjusted points to draw a vertical line just outside the target rectangles."""
        # Calculate the distance between the closest vertical edges of the rectangles
        distance_y = max(rect1.y, rect2.y) - min(rect1.y + rect1.h, rect2.y + rect2.h)
        if distance_y < self.min_line_length:
            return None
        point1 = (midpoint_x, rect1.y + rect1.h) if rect1.y < rect2.y else (midpoint_x, rect1.y)
        point2 = (midpoint_x, rect2.y + rect2.h) if rect2.y < rect1.y else (midpoint_x, rect2.y)

        return Line(point1, point2)

    def _horizontal_line(self, midpoint_y, rect1, rect2):
        """Get adjusted points to draw a horizontal line just outside the target rectangles."""
        # Calculate the distance between the closest horizontal edges of the rectangles
        distance_x = max(rect1.x, rect2.x) - min(rect1.x + rect1.w, rect2.x + rect2.w)
        if distance_x < self.min_line_length:
            return None
        point1 = (rect1.x + rect1.w, midpoint_y) if rect1.x < rect2.x else (rect1.x, midpoint_y)
        point2 = (rect2.x + rect2.w, midpoint_y) if rect2.x < rect1.x else (rect2.x, midpoint_y)

        return Line(point1, point2)

    def _find_uninterrupted_subranges(self, rect1, rect2, vertical=True):
        subranges = []
        in_uninterrupted_range = True

        if vertical:
            start = max(rect1.x, rect2.x)
            end = min(rect1.x + rect1.w, rect2.x + rect2.w)
            bound_start = min(rect1.y + rect1.h, rect2.y + rect2.h) + self.discontinuity
            bound_end = max(rect1.y, rect2.y) - self.discontinuity
        else:
            start = max(rect1.y, rect2.y)
            end = min(rect1.y + rect1.h, rect2.y + rect2.h)
            bound_start = min(rect1.x + rect1.w, rect2.x + rect2.w) + self.discontinuity
            bound_end = max(rect1.x, rect2.x) - self.discontinuity

        if end <= start or bound_end <= bound_start:
            return subranges

        current_start = start

        for i in range(start, end + 1):
            if vertical:
                column_has_obstacle = (self.edge_img[bound_start:bound_end, i] == 255).any()
            else:
                row_has_obstacle = (self.edge_img[i, bound_start:bound_end] == 255).any()

            if (vertical and column_has_obstacle) or (not vertical and row_has_obstacle):
                if in_uninterrupted_range:
                    if i - current_start >= self.discontinuity:
                        subranges.append((current_start, i - 1))
                    in_uninterrupted_range = False
            else:
                if not in_uninterrupted_range:
                    current_start = i
                    in_uninterrupted_range = True

        if in_uninterrupted_range and end - current_start >= self.discontinuity:
            subranges.append((current_start, end))

        return subranges
