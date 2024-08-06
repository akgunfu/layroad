from typing import List, Tuple

import cv2.typing

from .geometry import Line, Point, Rectangle, Shape

LINE_DISCONTINUITY = 5  # must be > 0 , or else all lines could be filtered out
SPAN_DISCONTINUITY = 10
MIN_SPAN_LENGTH = 10
MIN_LINE_LENGTH = 75


class EdgeConnect:
    def __init__(self, edge_img: cv2.typing.MatLike, rectangles: List[Rectangle], upscale_factor: int):
        """Initialize with edge image, rectangles, specified discontinuity, and minimum line length."""
        self.edge_img = edge_img
        self.rectangles = rectangles
        self.line_discontinuity = LINE_DISCONTINUITY * upscale_factor
        self.span_discontinuity = SPAN_DISCONTINUITY * upscale_factor
        self.min_span_length = MIN_SPAN_LENGTH * upscale_factor
        self.min_line_length = MIN_LINE_LENGTH * upscale_factor
        self.converged_spans = {'x': [], 'y': []}

    def connect(self) -> List[Line]:
        r1 = self._create_lines_between_shapes(self.rectangles, self.rectangles)
        r2 = self._create_lines_between_shapes(self.rectangles, r1)
        r3 = self._create_lines_between_shapes(self.rectangles, r2)
        rr = self._filter_nested_lines(r1 + r2 + r3)
        r4 = self._create_lines_between_shapes(rr, rr)
        # todo create line->line connection lines
        # todo create rect->line connection lines
        # todo create line intersection nodes
        # todo prune very close near identical lines
        return self._filter_nested_lines(r1 + r2 + r3 + r4)

    @staticmethod
    def _filter_nested_lines(lines):
        filtered = []
        for line1 in lines:
            contained = False
            for line2 in lines:
                if line1 == line2:
                    continue
                if line1.is_nested_within(line2):
                    contained = True
                    break
            if not contained:
                filtered.append(line1)
        return filtered

    def _create_lines_between_shapes(self, _from_list: List[Shape], _to_list: List[Shape]) -> List[Line]:
        """Create direct lines between shapes."""
        # todo refactor
        self._preview_and_update_converged_spans(_from_list, _to_list)
        lines = []
        for _from in _to_list:
            for _to in _to_list:
                if _from == _to:
                    continue

                has_shared_axis, shared_axis = _from.has_spanning_axis(_to)
                if not has_shared_axis:
                    continue

                spans = self._get_spans(_from, _to, shared_axis)
                for span in spans:
                    start, end = self.find_inner_subrange(span, self.converged_spans[shared_axis])
                    if start and end:
                        midpoint = (start + end) // 2
                        line = self._get_line(midpoint, _to, _from, shared_axis)
                        if line and line.length() >= self.min_line_length:
                            lines.append(line)

        return self._filter_nested_lines(list(set(lines)))

    def _preview_and_update_converged_spans(self, _from_list, _to_list):
        iteration_spans_dict = {'x': [], 'y': []}
        for _from in _from_list:
            shape_spans_dict = {'x': [], 'y': []}
            for _to in _to_list:
                if _from == _to:
                    continue

                has_shared_axis, shared_axis = _from.has_spanning_axis(_to)
                if not has_shared_axis:
                    continue
                shape_spans_dict[shared_axis] += self._get_spans(_from, _to, shared_axis)
            iteration_spans_dict['x'] += self.converge_spans(shape_spans_dict['x'])
            iteration_spans_dict['y'] += self.converge_spans(shape_spans_dict['y'])
        self.converged_spans['x'] += self.converge_spans(iteration_spans_dict['x'])
        self.converged_spans['y'] += self.converge_spans(iteration_spans_dict['y'])
        #
        self.converged_spans['x'] = self.converge_spans(self.converged_spans['x'])
        _new_x = [((start + end) // 2, (start + end) // 2) for start, end in self.converged_spans['x']]
        self.converged_spans['x'] = _new_x
        #
        self.converged_spans['y'] = self.converge_spans(self.converged_spans['y'])
        _new_y = [((start + end) // 2, (start + end) // 2) for start, end in self.converged_spans['y']]
        self.converged_spans['y'] = self.converge_spans(self.converged_spans['y'])

    def _get_spans(self, _from, _to, shared_axis):
        spans = self._find_uninterrupted_spans(_to, _from, shared_axis)
        if not spans:
            return spans
        if isinstance(_from, Rectangle) or isinstance(_to, Rectangle):
            length = len(spans)
            if length % 2 != 0:
                middle_index = (length - 1) // 2
            else:
                middle_index = length // 2
            return [spans[middle_index]]
        return spans

    @staticmethod
    def converge_spans(spans: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Condense spans by intersecting overlapping spans and keeping non-overlapping spans."""
        # Sort spans by their start position and then by their end position
        spans.sort(key=lambda x: (x[0], x[1]))
        condensed = []
        for current_start, current_end in spans:
            # If the condensed list is empty, add the current span
            if not condensed:
                condensed.append((current_start, current_end))
                continue
            last_start, last_end = condensed[-1]
            # If the current span is completely inside the last added span, replace the last one
            if current_start >= last_start and current_end <= last_end:
                condensed[-1] = (current_start, current_end)
            # If the current span does not overlap with the last added span, add it to the list
            elif current_start >= last_end:
                condensed.append((current_start, current_end))
            # For overlapping spans, add their intersection
            else:
                intersect_start = max(current_start, last_start)
                intersect_end = min(current_end, last_end)
                condensed.append((intersect_start, intersect_end))
        return list(set(condensed))

    @staticmethod
    def find_inner_subrange(checked_subrange: Tuple[int, int],
                            condensed_subranges: List[Tuple[int, int]]) -> Tuple[int, int]:
        """
        Given a larger subrange and a list of condensed subranges,
        return the first subrange that is completely within the larger subrange.
        """
        for subrange in condensed_subranges:
            if checked_subrange[0] <= subrange[0] and checked_subrange[1] >= subrange[1]:
                return subrange
        return None, None

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

    def _find_uninterrupted_spans(self, shape1: Shape, shape2: Shape, axis) -> List[Tuple[int, int]]:
        """Find uninterrupted subranges between two rectangles, considering obstacles."""
        subranges = []
        in_uninterrupted_range = True

        start, end = shape1.get_spanning_axis_range(shape2)
        if (end - start) < self.min_span_length:
            return subranges

        bound_start, bound_end = shape1.get_bounding_range(shape2, self.line_discontinuity)
        if (bound_end - bound_start) < self.min_line_length:
            return subranges

        current_start = start

        for i in range(start, end + 1):
            if self._has_obstacle(self.edge_img, i, bound_start, bound_end, axis):
                if in_uninterrupted_range and i - current_start >= self.min_span_length:
                    subranges.append((current_start, i - 1))
                in_uninterrupted_range = False
            else:
                if not in_uninterrupted_range:
                    current_start = i + self.span_discontinuity
                    if current_start >= end:
                        break
                    in_uninterrupted_range = True

        if in_uninterrupted_range and end - current_start >= self.min_span_length:
            subranges.append((current_start, end))

        return subranges

    @staticmethod
    def _has_obstacle(edge_img: cv2.typing.MatLike, pos: int, bound_start: int, bound_end: int, axis) -> bool:
        """Check for obstacles in the specified range."""
        if axis == 'x':
            return (edge_img[bound_start:bound_end, pos] == 255).any()
        else:
            return (edge_img[pos, bound_start:bound_end] == 255).any()
