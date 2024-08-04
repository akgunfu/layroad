from typing import List, Tuple

import cv2.typing

from .geometry import Line, Point, Rectangle, Shape

LINE_DISCONTINUITY = 10  # must be > 0 , or else all lines could be filtered out
SPAN_DISCONTINUITY = 10
MIN_SPAN_LENGTH = 15
MIN_LINE_LENGTH = 60


class EdgeConnect:
    def __init__(self, edge_img: cv2.typing.MatLike, rectangles: List[Rectangle], upscale_factor: int):
        """Initialize with edge image, rectangles, specified discontinuity, and minimum line length."""
        self.edge_img = edge_img
        self.rectangles = rectangles
        self.line_discontinuity = LINE_DISCONTINUITY * upscale_factor
        self.span_discontinuity = SPAN_DISCONTINUITY * upscale_factor
        self.min_span_length = MIN_SPAN_LENGTH * upscale_factor
        self.min_line_length = MIN_LINE_LENGTH * upscale_factor
        self.subranges_dict = {'x': [], 'y': []}

    def connect(self) -> List[Line]:
        rtr_lines = self._create_lines_between_shapes(self.rectangles, self.rectangles)
        ltl_lines = self._create_lines_between_shapes(rtr_lines, rtr_lines)
        # todo create line->line connection lines
        # todo create rect->line connection lines
        # todo create line intersection nodes
        # todo prune very close near identical lines
        lines = rtr_lines + ltl_lines
        lines = self._filter_nested_lines(lines)
        return lines

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
        lines = []
        global_subranges_dict = {'x': [], 'y': []}
        for _from in _from_list:
            local_ranges_dict = {'x': [], 'y': []}
            for _to in _to_list:
                if _from == _to:
                    continue
                has_shared_axis, shared_axis = _from.has_spanning_axis(_to)
                if has_shared_axis:
                    uninterrupted_subranges = self._find_uninterrupted_subranges(_to, _from, shared_axis)
                    if len(uninterrupted_subranges) == 0:
                        continue
                    if isinstance(_from, Rectangle) or isinstance(_to, Rectangle):
                        uninterrupted_subranges = [uninterrupted_subranges[len(uninterrupted_subranges) // 2]]
                    for subrange in uninterrupted_subranges:
                        start, end = subrange
                        midpoint = (start + end) // 2
                        line = self._get_line(midpoint, _to, _from, shared_axis)
                        if line and line.length() >= self.min_line_length:
                            local_ranges_dict[shared_axis].append(subrange)
            #
            global_subranges_dict['x'] += self.condense_subranges(local_ranges_dict['x'])
            global_subranges_dict['y'] += self.condense_subranges(local_ranges_dict['y'])

        self.subranges_dict['x'] += self.condense_subranges(global_subranges_dict['x'])
        self.subranges_dict['y'] += self.condense_subranges(global_subranges_dict['y'])
        #
        self.subranges_dict['x'] = self.condense_subranges(self.subranges_dict['x'])
        _new_x = [((start + end) // 2, (start + end) // 2) for start, end in self.subranges_dict['x']]
        self.subranges_dict['x'] = _new_x
        #
        self.subranges_dict['y'] = self.condense_subranges(self.subranges_dict['y'])
        _new_y = [((start + end) // 2, (start + end) // 2) for start, end in self.subranges_dict['y']]
        self.subranges_dict['y'] = self.condense_subranges(self.subranges_dict['y'])

        for _from in _to_list:
            for _to in _to_list:
                if _from == _to:
                    continue

                has_shared_axis, shared_axis = _from.has_spanning_axis(_to)
                if has_shared_axis:
                    subranges = self._find_uninterrupted_subranges(_to, _from, shared_axis)
                    if len(subranges) == 0:
                        continue
                    if isinstance(_from, Rectangle) or isinstance(_to, Rectangle):
                        subranges = [subranges[len(subranges) // 2]]
                    for subrange in subranges:
                        start, end = self.find_inner_subrange(subrange, self.subranges_dict[shared_axis])
                        if start and end:
                            midpoint = (start + end) // 2
                            line = self._get_line(midpoint, _to, _from, shared_axis)
                            if line and line.length() >= self.min_line_length:
                                lines.append(line)

        return self._filter_nested_lines(list(set(lines)))

    @staticmethod
    def condense_subranges(subranges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Condense subranges by intersecting overlapping subranges and keeping non-overlapping subranges."""
        # Sort subranges by their start position and then by their end position
        subranges.sort(key=lambda x: (x[0], x[1]))

        condensed = []
        for current_start, current_end in subranges:
            # If the condensed list is empty, add the current subrange
            if not condensed:
                condensed.append((current_start, current_end))
                continue

            last_start, last_end = condensed[-1]

            # If the current subrange is completely inside the last added subrange, replace the last one
            if current_start >= last_start and current_end <= last_end:
                condensed[-1] = (current_start, current_end)
            # If the current subrange does not overlap with the last added subrange, add it to the list
            elif current_start >= last_end:
                condensed.append((current_start, current_end))
            # For overlapping ranges, add their intersection
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

    def _find_uninterrupted_subranges(self, shape1: Shape, shape2: Shape, axis) -> List[Tuple[int, int]]:
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
