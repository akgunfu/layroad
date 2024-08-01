class Line:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class EdgeConnect:
    def __init__(self, discontinuity=10, min_line_length=50):
        """
        Initialize the EdgeConnect class with specified discontinuity and minimum line length.

        Parameters:
        discontinuity (int): Distance from the edge of rectangles to the start and end points of the connecting line.
        min_line_length (int): Minimum distance required between two rectangles to draw a connecting line.
        """
        self.discontinuity = discontinuity
        self.min_line_length = min_line_length

    def create_direct_connect_lines(self, clustered_rects, edge_img):
        """
        Create direct connect lines between rectangles that do not intersect with any other rectangle
        or obstacle in the edge image.
        """
        lines = []
        for i in range(len(clustered_rects)):
            for j in range(i + 1, len(clustered_rects)):
                rect1 = clustered_rects[i]
                rect2 = clustered_rects[j]

                # Check if x ranges intersect and create vertical lines
                if self._x_ranges_intersect(rect1, rect2):
                    line = self._get_vertical_line(rect1, rect2)
                    if line and self._is_line_clear(line, clustered_rects, rect1, rect2, edge_img):
                        lines.append(line)

                # Check if y ranges intersect and create horizontal lines
                if self._y_ranges_intersect(rect1, rect2):
                    line = self._get_horizontal_line(rect1, rect2)
                    if line and self._is_line_clear(line, clustered_rects, rect1, rect2, edge_img):
                        lines.append(line)

        return lines

    @staticmethod
    def _x_ranges_intersect(rect1, rect2):
        """Check if x ranges of two rectangles intersect"""
        x1, _, w1, _, _ = rect1
        x2, _, w2, _, _ = rect2
        return max(x1, x2) < min(x1 + w1, x2 + w2)

    @staticmethod
    def _y_ranges_intersect(rect1, rect2):
        """Check if y ranges of two rectangles intersect"""
        _, y1, _, h1, _ = rect1
        _, y2, _, h2, _ = rect2
        return max(y1, y2) < min(y1 + h1, y2 + h2)

    def _get_vertical_line(self, rect1, rect2):
        """
        Get adjusted points to draw a vertical line just outside the target rectangles.

        Parameters:
        rect1 (tuple): First rectangle parameters (x, y, w, h, cluster).
        rect2 (tuple): Second rectangle parameters (x, y, w, h, cluster).

        Returns:
        tuple: Start and end points of the vertical line, or None if the line cannot be drawn.
        """
        x1, y1, w1, h1, _ = rect1
        x2, y2, w2, h2, _ = rect2

        # Calculate the midpoint of the intersecting range
        intersect_x_start, intersect_x_end = max(x1, x2), min(x1 + w1, x2 + w2)
        midpoint_x = (intersect_x_start + intersect_x_end) // 2

        # Calculate the distance between the closest vertical edges of the rectangles
        distance_y = max(y1, y2) - min(y1 + h1, y2 + h2)
        if distance_y < self.min_line_length:
            # Ensure the vertical distance is greater than the minimum line length to avoid overlap
            return None
        point1 = (midpoint_x, y1 + h1 + self.discontinuity) if y1 < y2 else (midpoint_x, y1 - self.discontinuity)
        point2 = (midpoint_x, y2 + h2 + self.discontinuity) if y2 < y1 else (midpoint_x, y2 - self.discontinuity)

        return Line(point1, point2)

    def _get_horizontal_line(self, rect1, rect2):
        x1, y1, w1, h1, _ = rect1
        x2, y2, w2, h2, _ = rect2

        # Calculate the midpoint of the intersecting range
        intersect_y_start, intersect_y_end = max(y1, y2), min(y1 + h1, y2 + h2)
        midpoint_y = (intersect_y_start + intersect_y_end) // 2

        # Calculate the distance between the closest horizontal edges of the rectangles
        distance_x = max(x1, x2) - min(x1 + w1, x2 + w2)
        if distance_x < self.min_line_length:
            # Ensure the horizontal distance is greater than the minimum line length to avoid overlap
            return None
        point1 = (x1 + w1 + self.discontinuity, midpoint_y) if x1 < x2 else (x1 - self.discontinuity, midpoint_y)
        point2 = (x2 + w2 + self.discontinuity, midpoint_y) if x2 < x1 else (x2 - self.discontinuity, midpoint_y)

        return Line(point1, point2)

    def _is_line_clear(self, line, rects, rect1, rect2, edge_img):
        return self._no_rect_in_way(line, rects, rect1, rect2) and self._no_obs_in_way(line, edge_img)

    @staticmethod
    def _no_rect_in_way(line, rects, rect1, rect2):
        (x1, y1) = line.start
        (x2, y2) = line.end
        for rect in rects:
            if rect == rect1 or rect == rect2:
                # Skip checking the rectangles that are being connected
                continue
            rx, ry, rw, rh, _ = rect
            # Check if the line intersects with the rectangle
            if not ((x1 > rx + rw or x2 < rx) or (y1 > ry + rh or y2 < ry)):
                # If the line intersects the rectangle, return False
                return False
        return True

    @staticmethod
    def _no_obs_in_way(line, edge_img):
        (x1, y1) = line.start
        (x2, y2) = line.end
        # Define the bounding range of the line
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)

        # Ensure the bounding box is within the image bounds
        min_x, min_y = max(min_x, 0), max(min_y, 0)
        max_x, max_y = min(max_x, edge_img.shape[1] - 1), min(max_y, edge_img.shape[0] - 1)

        # Check for white pixels in the bounding range of the line in the edge image
        if min_x == max_x:  # Vertical line
            for y in range(min_y, max_y + 1):
                if edge_img[y, min_x] == 255:  # Check if the pixel is white
                    return False
        elif min_y == max_y:  # Horizontal line
            for x in range(min_x, max_x + 1):
                if edge_img[min_y, x] == 255:  # Check if the pixel is white
                    return False
        else:
            return False  # Diagonal lines are not handled

        return True
