from typing import List

import cv2
import numpy as np

from .clustering import cluster_rectangles
from .geometry import Rectangle
from .image_processing import ENHANCE_CONTRAST, BLUR, THRESHOLD, UPSCALE, enhance_contrast, blur, adaptive_threshold, \
    upscale

# Constants
AREA_FACTOR = 9600
CONTOUR_APPROX_EPSILON = 0.01


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
        rects = self._remove_nested_rectangles(rects)
        if len(rects) > 1:
            rects = cluster_rectangles(rects, self.cluster_mode)
        else:
            for rect in rects:
                rect.set_cluster(0)
        rects = self.renumber_rectangles(rects)
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

    def _find_rects(self, img) -> List[Rectangle]:
        """Find rectangles in the edge-detected image."""
        area_threshold = self.min_area * (self.upscale_factor ** 2)
        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rects = []
        counter = 1
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
                    rects.append(Rectangle(idx=counter, x=x, y=y, w=w, h=h))
                    counter += 1
        return rects

    @staticmethod
    def _remove_outliers(rects: List[Rectangle]) -> List[Rectangle]:
        """Remove outlier rectangles based on size."""
        sizes = np.array([rect.w * rect.h for rect in rects])
        mean_size = np.mean(sizes)
        std_size = np.std(sizes)
        return [rect for rect in rects if (mean_size - 2 * std_size) <= (rect.w * rect.h) <= (mean_size + 2 * std_size)]

    @staticmethod
    def _remove_nested_rectangles(rects: List[Rectangle]) -> List[Rectangle]:
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

    @staticmethod
    def renumber_rectangles(rects: List[Rectangle]) -> List[Rectangle]:
        # Sort rectangles by x coordinate, then by y coordinate to easily number them
        sorted_rectangles = sorted(rects, key=lambda rect: (rect.center().x, rect.center().y))
        # Assign new consecutive IDs based on sorted order
        for new_id, rect in enumerate(sorted_rectangles):
            rect.id = new_id
        return sorted_rectangles
