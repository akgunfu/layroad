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
        """Check if x ranges of two rectangles intersect"""
        return max(rect1.x, rect2.x) < min(rect1.x + rect1.w, rect2.x + rect2.w)

    @staticmethod
    def _y_intersects(rect1, rect2):
        """Check if y ranges of two rectangles intersect"""
        return max(rect1.y, rect2.y) < min(rect1.y + rect1.h, rect2.y + rect2.h)

    def _vertical_line(self, rect1, rect2):
        """Get adjusted points to draw a vertical line just outside the target rectangles."""
        # Calculate the midpoint of the intersecting range
        intersect_x_start, intersect_x_end = max(rect1.x, rect2.x), min(rect1.x + rect1.w, rect2.x + rect2.w)
        midpoint_x = (intersect_x_start + intersect_x_end) // 2

        # Calculate the distance between the closest vertical edges of the rectangles
        distance_y = max(rect1.y, rect2.y) - min(rect1.y + rect1.h, rect2.y + rect2.h)
        if distance_y < self.min_line_length:
            return None
        point1 = (midpoint_x, rect1.y + rect1.h + self.discontinuity) if rect1.y < rect2.y else (
            midpoint_x, rect1.y - self.discontinuity)
        point2 = (midpoint_x, rect2.y + rect2.h + self.discontinuity) if rect2.y < rect1.y else (
            midpoint_x, rect2.y - self.discontinuity)

        return Line(point1, point2)

    def _horizontal_line(self, rect1, rect2):
        """Get adjusted points to draw a horizontal line just outside the target rectangles."""
        # Calculate the midpoint of the intersecting range
        intersect_y_start, intersect_y_end = max(rect1.y, rect2.y), min(rect1.y + rect1.h, rect2.y + rect2.h)
        midpoint_y = (intersect_y_start + intersect_y_end) // 2

        # Calculate the distance between the closest horizontal edges of the rectangles
        distance_x = max(rect1.x, rect2.x) - min(rect1.x + rect1.w, rect2.x + rect2.w)
        if distance_x < self.min_line_length:
            return None
        point1 = (rect1.x + rect1.w + self.discontinuity, midpoint_y) if rect1.x < rect2.x else (
            rect1.x - self.discontinuity, midpoint_y)
        point2 = (rect2.x + rect2.w + self.discontinuity, midpoint_y) if rect2.x < rect1.x else (
            rect2.x - self.discontinuity, midpoint_y)

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
            if not ((x1 > rect.x + rect.w or x2 < rect.x) or (y1 > rect.y + rect.h or y2 < rect.y)):
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
