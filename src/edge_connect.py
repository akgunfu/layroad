# Constants
DISCONTINUITY = 10
MIN_LINE_LENGTH = 50


class Line:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class EdgeConnect:
    def __init__(self, discontinuity=DISCONTINUITY, min_line_length=MIN_LINE_LENGTH):
        """Initialize with specified discontinuity and minimum line length."""
        self.discontinuity = discontinuity
        self.min_line_length = min_line_length

    def create_lines(self, clustered_rects, edge_img):
        """Create direct connect lines between rectangles."""
        lines = []
        for i in range(len(clustered_rects)):
            for j in range(i + 1, len(clustered_rects)):
                rect1 = clustered_rects[i]
                rect2 = clustered_rects[j]

                if self._x_intersects(rect1, rect2):  # Check for x-range intersection
                    line = self._vertical_line(rect1, rect2)
                    if line and self._line_clear(line, clustered_rects, rect1, rect2, edge_img):
                        lines.append(line)

                if self._y_intersects(rect1, rect2):  # Check for y-range intersection
                    line = self._horizontal_line(rect1, rect2)
                    if line and self._line_clear(line, clustered_rects, rect1, rect2, edge_img):
                        lines.append(line)
        return lines

    @staticmethod
    def _x_intersects(rect1, rect2):
        """Check if x ranges of two rectangles intersect."""
        x1, _, w1, _, _ = rect1
        x2, _, w2, _, _ = rect2
        return max(x1, x2) < min(x1 + w1, x2 + w2)

    @staticmethod
    def _y_intersects(rect1, rect2):
        """Check if y ranges of two rectangles intersect."""
        _, y1, _, h1, _ = rect1
        _, y2, _, h2, _ = rect2
        return max(y1, y2) < min(y1 + h1, y2 + h2)

    def _vertical_line(self, rect1, rect2):
        """Get vertical line between two rectangles."""
        x1, y1, w1, h1, _ = rect1
        x2, y2, w2, h2, _ = rect2

        intersect_x_start, intersect_x_end = max(x1, x2), min(x1 + w1, x2 + w2)
        midpoint_x = (intersect_x_start + intersect_x_end) // 2

        distance_y = max(y1, y2) - min(y1 + h1, y2 + h2)
        if distance_y < self.min_line_length:
            return None

        point1 = (midpoint_x, y1 + h1 + self.discontinuity) if y1 < y2 else (midpoint_x, y1 - self.discontinuity)
        point2 = (midpoint_x, y2 + h2 + self.discontinuity) if y2 < y1 else (midpoint_x, y2 - self.discontinuity)

        return Line(point1, point2)

    def _horizontal_line(self, rect1, rect2):
        """Get horizontal line between two rectangles."""
        x1, y1, w1, h1, _ = rect1
        x2, y2, w2, h2, _ = rect2

        intersect_y_start, intersect_y_end = max(y1, y2), min(y1 + h1, y2 + h2)
        midpoint_y = (intersect_y_start + intersect_y_end) // 2

        distance_x = max(x1, x2) - min(x1 + w1, x2 + w2)
        if distance_x < self.min_line_length:
            return None

        point1 = (x1 + w1 + self.discontinuity, midpoint_y) if x1 < x2 else (x1 - self.discontinuity, midpoint_y)
        point2 = (x2 + w2 + self.discontinuity, midpoint_y) if x2 < x1 else (x2 - self.discontinuity, midpoint_y)

        return Line(point1, point2)

    def _line_clear(self, line, rects, rect1, rect2, edge_img):
        """Check if a line is clear of rectangles and obstacles."""
        return self._no_rect_in_way(line, rects, rect1, rect2) and self._no_obstacle_in_way(line, edge_img)

    @staticmethod
    def _no_rect_in_way(line, rects, rect1, rect2):
        """Check if a line intersects with any rectangles."""
        (x1, y1) = line.start
        (x2, y2) = line.end
        for rect in rects:
            if rect == rect1 or rect == rect2:
                continue
            rx, ry, rw, rh, _ = rect
            if not ((x1 > rx + rw or x2 < rx) or (y1 > ry + rh or y2 < ry)):  # Check for intersection
                return False
        return True

    @staticmethod
    def _no_obstacle_in_way(line, edge_img):
        """Check if a line intersects with any obstacles in the edge image."""
        (x1, y1) = line.start
        (x2, y2) = line.end
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)

        min_x, min_y = max(min_x, 0), max(min_y, 0)
        max_x, max_y = min(max_x, edge_img.shape[1] - 1), min(max_y, edge_img.shape[0] - 1)

        if min_x == max_x:  # Vertical line
            for y in range(min_y, max_y + 1):
                if edge_img[y, min_x] == 255:  # Check for obstacle
                    return False
        elif min_y == max_y:  # Horizontal line
            for x in range(min_x, max_x + 1):
                if edge_img[min_y, x] == 255:  # Check for obstacle
                    return False
        else:
            return False

        return True
