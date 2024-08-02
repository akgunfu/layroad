import cv2
import numpy as np

from clustering import cluster_rectangles
from image_processing import ENHANCE_CONTRAST, BLUR, THRESHOLD, UPSCALE, enhance_contrast, blur, adaptive_threshold, \
    upscale

# Constants
AREA_FACTOR = 9600
CONTOUR_APPROX_EPSILON = 0.01


class Rectangle:
    def __init__(self, id, x, y, w, h):
        """Initialize a Rectangle with given attributes."""
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cluster = None

    def __iter__(self):
        """Allow unpacking rectangle attributes."""
        return iter((self.x, self.y, self.w, self.h))

    def size(self):
        """Calculate the size of the rectangle."""
        return self.w * self.h

    def set_cluster(self, cluster):
        """Set the cluster ID for the rectangle."""
        self.cluster = cluster

    def is_identical(self, other):
        """Check if two rectangles have the same dimensions and position."""
        return (self.x == other.x and self.y == other.y and
                self.w == other.w and self.h == other.h)

    def is_nested_within(self, other):
        """Check if this rectangle is nested within another rectangle."""
        return (self.x >= other.x and self.y >= other.y and
                self.x + self.w <= other.x + other.w and
                self.y + self.h <= other.y + other.h)

    def intersects(self, other, axis):
        """Check if ranges of two rectangles intersect based on the specified axis."""
        if axis == 'x':
            return max(self.x, other.x) < min(self.x + self.w, other.x + other.w)
        else:
            return max(self.y, other.y) < min(self.y + self.h, other.y + other.h)

    def get_intersection_range(self, other, axis):
        """Get the overlapping range on the specified axis."""
        if axis == 'x':
            start = max(self.x, other.x)
            end = min(self.x + self.w, other.x + other.w)
        else:
            start = max(self.y, other.y)
            end = min(self.y + self.h, other.y + other.h)
        return start, end

    def get_bounding_range(self, other, axis, discontinuity):
        """Get the bounding range between two rectangles on the specified axis."""
        if axis == 'x':
            bound_start = min(self.y + self.h, other.y + other.h) + discontinuity
            bound_end = max(self.y, other.y) - discontinuity
        else:
            bound_start = min(self.x + self.w, other.x + other.w) + discontinuity
            bound_end = max(self.x, other.x) - discontinuity
        return bound_start, bound_end


class RectangleDetector:
    def __init__(self, gray_img, original_img, config):
        """Initialize the RectangleDetector class."""
        self.gray_img = gray_img
        self.original_img = original_img
        self.edge_img = None
        self.config = config
        self.upscale_factor = 1
        height, width = self.original_img.shape[:2]
        self.min_area = round(width * height / AREA_FACTOR)
        self.cluster_mode = 'distance'

    def detect(self):
        """Process the image to detect and cluster rectangles."""
        processed_img = self._apply_steps()
        self.edge_img = self._detect_edges(processed_img)
        rects = self._find_rects(self.edge_img)
        rects = self._remove_outliers(rects)
        rects = self._filter_nested_rectangles(rects)
        if len(rects) > 1:
            rects = cluster_rectangles(rects, self.cluster_mode)
        else:
            for rect in rects:
                rect.set_cluster(0)
        return self.edge_img, rects, self.upscale_factor

    def _apply_steps(self):
        """Apply configured processing steps to the grayscale image."""
        img = self.gray_img
        for step in self.config['steps']:
            if step == ENHANCE_CONTRAST:
                img = enhance_contrast(img)
            elif step == BLUR:
                img = blur(img, self.config.get('blur_kernel_size', (5, 5)))
            elif step == THRESHOLD:
                img = adaptive_threshold(img)
            elif step == UPSCALE:
                img = upscale(img, 2)
                self.upscale_factor *= 2
        return img

    @staticmethod
    def _detect_edges(img):
        """Detect edges using the Canny edge detection algorithm."""
        median_val = np.median(img)
        lower = int(max(0, 0.24 * median_val))
        upper = int(min(255, 0.96 * median_val))
        return cv2.Canny(img, lower, upper)

    def _find_rects(self, img):
        """Find rectangles in the edge-detected image."""
        area_threshold = self.min_area * (self.upscale_factor ** 2)
        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rects = []
        for idx, contour in enumerate(contours):
            contour_area = cv2.contourArea(contour)
            if area_threshold < contour_area < 4 * area_threshold:
                eps = CONTOUR_APPROX_EPSILON * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, eps, True)
                if len(approx) == 4:
                    (x, y, w, h) = cv2.boundingRect(approx)
                    ratio = max(w, h) / min(w, h)
                    if ratio >= 3:
                        continue
                    rects.append(Rectangle(id=idx, x=x, y=y, w=w, h=h))
        return rects

    @staticmethod
    def _remove_outliers(rects):
        """Remove outlier rectangles based on size."""
        sizes = np.array([rect.w * rect.h for rect in rects])
        mean_size = np.mean(sizes)
        std_size = np.std(sizes)
        return [rect for rect in rects if (mean_size - 2 * std_size) <= (rect.w * rect.h) <= (mean_size + 2 * std_size)]

    @staticmethod
    def _filter_nested_rectangles(rects):
        """Filter out rectangles that are nested within other rectangles"""
        filtered_rects = []
        for i, rect in enumerate(rects):
            is_nested = False
            for j, other in enumerate(rects):
                if i == j:  # Skip self-comparison by comparing indices
                    continue
                if rect.is_identical(other):
                    if i < j:  # Skip the second occurrence
                        continue
                    else:
                        is_nested = True
                        break
                if rect.is_nested_within(other):
                    is_nested = True
                    break
            if not is_nested:
                filtered_rects.append(rect)
        return filtered_rects
