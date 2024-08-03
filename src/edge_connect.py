from typing import List, Tuple

import cv2.typing

from .geometry import Line, Point, Rectangle, Shape

DISCONTINUITY = 5  # must be > 0 , or else all lines could be filtered out
MIN_LINE_LENGTH = 50


class EdgeConnect:
    def __init__(self, edge_img: cv2.typing.MatLike, rectangles: List[Rectangle], upscale_factor: int):
        """Initialize with edge image, rectangles, specified discontinuity, and minimum line length."""
        self.edge_img = edge_img
        self.rectangles = rectangles
        self.discontinuity = DISCONTINUITY * upscale_factor
        self.min_line_length = MIN_LINE_LENGTH * upscale_factor

    def connect(self) -> List[Line]:
        lines = self._create_direct_lines_between_rectangles()  # rect->rect connection lines
        # todo create line->line connection lines
        # todo create rect->line connection lines
        # todo create line intersection nodes
        # todo prune very close near identical lines
        lines.extend(self._filter_out_intersecting_lines(lines))  # edge-case filter rect overlapping lines
        return lines

    def _create_direct_lines_between_rectangles(self) -> List[Line]:
        """Create direct lines between rectangles."""
        lines = []
        for i in range(len(self.rectangles)):
            for j in range(i + 1, len(self.rectangles)):
                rect1 = self.rectangles[i]
                rect2 = self.rectangles[j]

                if rect1.intersects(rect2, axis='x'):
                    lines.extend(self._generate_lines(rect1, rect2, axis='x'))
                elif rect1.intersects(rect2, axis='y'):
                    lines.extend(self._generate_lines(rect1, rect2, axis='y'))
        return lines

    def _generate_lines(self, shape1: Shape, shape2: Shape, axis) -> List[Line]:
        """Generate lines between two rectangles based on the specified axis."""
        lines = []
        subranges = self._find_uninterrupted_subranges(shape1, shape2, axis)
        for start, end in subranges:
            midpoint = (start + end) // 2
            line = self._get_line(midpoint, shape1, shape2, axis)
            if line and line.length() >= self.min_line_length:
                lines.append(line)
        return lines

    @staticmethod
    def _get_line(midpoint: int, shape1: Shape, shape2: Shape, axis) -> Line:
        """Get adjusted points for a line just outside the target shapes."""
        start_x_1, end_x_1, start_y_1, end_y_1 = shape1.bounds()
        start_x_2, end_x_2, start_y_2, end_y_2 = shape2.bounds()
        if axis == 'x':
            point1 = Point(midpoint, end_y_1) if start_y_1 < start_y_2 else Point(midpoint, start_y_1)
            point2 = Point(midpoint, end_y_2) if start_y_2 < start_y_1 else Point(midpoint, start_y_2)
        else:
            point1 = Point(end_x_1, midpoint) if start_x_1 < start_x_2 else Point(start_x_1, midpoint)
            point2 = Point(end_x_2, midpoint) if start_x_2 < start_x_1 else Point(start_x_2, midpoint)
        return Line(point1, point2)

    def _find_uninterrupted_subranges(self, shape1: Shape, shape2: Shape, axis) -> List[Tuple[int, int]]:
        """Find uninterrupted subranges between two rectangles, considering obstacles."""
        subranges = []
        in_uninterrupted_range = True

        start, end = shape1.get_intersection_range(shape2, axis)
        bound_start, bound_end = shape1.get_bounding_range(shape2, axis, self.discontinuity)

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
    def _has_obstacle(edge_img: cv2.typing.MatLike, pos: int, bound_start: int, bound_end: int, axis) -> bool:
        """Check for obstacles in the specified range."""
        if axis == 'x':
            return (edge_img[bound_start:bound_end, pos] == 255).any()
        else:
            return (edge_img[pos, bound_start:bound_end] == 255).any()

    def _filter_out_intersecting_lines(self, candidate_lines: List[Line]) -> List[Line]:
        """Filter out lines that intersect with any other rectangle."""
        return [line for line in candidate_lines if not self._line_intersects_any_rectangle(line)]

    def _line_intersects_any_rectangle(self, line: Line) -> bool:
        """Check if a line intersects with any rectangle other than rect1 and rect2."""
        for rect in self.rectangles:
            if line.intersects_rectangle(rect):
                return True
        return False
