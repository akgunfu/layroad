import cv2
import numpy as np

from clustering import cluster_rectangles
from image_processing import ENHANCE_CONTRAST, BLUR, THRESHOLD, UPSCALE, enhance_contrast, blur, adaptive_threshold, \
    upscale

# Constants
AREA_FACTOR = 10000
CONTOUR_APPROX_EPSILON = 0.01


class RectangleDetector:
    def __init__(self, gray_image, original_image, config):
        """Initialize the RectangleDetector class."""
        self.gray_image = gray_image
        self.original_image = original_image
        self.edge_image = None
        self.config = config
        self.upscale_factor = 1
        height, width = self.original_image.shape[:2]
        self.min_area = round(width * height / AREA_FACTOR)
        self.cluster_mode = 'distance'

    def detect(self):
        """Process the image to detect and cluster rectangles."""
        processed_image = self._apply_steps()
        self.edge_image = self._detect_edges(processed_image)
        rectangles = self._find_rectangles(self.edge_image)
        if len(rectangles) > 1:
            clustered_rectangles = cluster_rectangles(rectangles, self.cluster_mode)
        else:
            clustered_rectangles = [(x, y, w, h, 0) for (x, y, w, h) in rectangles]
        return self.edge_image, clustered_rectangles, self.upscale_factor

    def _apply_steps(self):
        """Apply configured processing steps to the grayscale image."""
        image = self.gray_image
        for step in self.config['steps']:
            if step == ENHANCE_CONTRAST:
                image = enhance_contrast(image)
            elif step == BLUR:
                image = blur(image, self.config.get('blur_kernel_size', (5, 5)))
            elif step == THRESHOLD:
                image = adaptive_threshold(image)
            elif step == UPSCALE:
                image = upscale(image, 2)
                self.upscale_factor *= 2
        return image

    @staticmethod
    def _detect_edges(image):
        """Detect edges using the Canny edge detection algorithm."""
        median_val = np.median(image)
        lower = int(max(0, 0.24 * median_val))
        upper = int(min(255, 0.96 * median_val))
        return cv2.Canny(image, lower, upper)

    def _find_rectangles(self, image):
        """Find rectangles in the edge-detected image."""
        adjusted_area_threshold = self.min_area * (self.upscale_factor ** 2)
        contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rectangles = []
        for contour in contours:
            if cv2.contourArea(contour) > adjusted_area_threshold:
                epsilon = CONTOUR_APPROX_EPSILON * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                if len(approx) == 4:
                    (x, y, w, h) = cv2.boundingRect(approx)
                    ratio = max(w, h) / min(w, h)
                    if ratio >= 3:
                        continue
                    rectangles.append((x, y, w, h))
        return rectangles
