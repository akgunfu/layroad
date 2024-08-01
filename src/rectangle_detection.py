import cv2
import numpy as np

from clustering import cluster_rectangles
from image_processing import ENHANCE_CONTRAST, BLUR, THRESHOLD, UPSCALE
from image_processing import combined_contrast_enhancement, apply_blur, apply_adaptive_threshold, upscale_image


class RectangleDetection:

    def __init__(self, gray_image, original_image, config):
        self.gray_image = gray_image
        self.original_image = original_image
        self.edge_image = None
        self.config = config
        self.upscale_factor = 1
        height, width = self.original_image.shape[:2]
        self.min_area = round(width * height / 10000)
        self.cluster_mode = 'distance'

    def process(self):
        image = self._apply_steps()
        self.edge_image = self._detect_edges(image)
        rectangles = self._find_rectangles(self.edge_image)
        if len(rectangles) > 1:
            clustered_rectangles = cluster_rectangles(rectangles, self.cluster_mode)
        else:
            clustered_rectangles = [(x, y, w, h, 0) for (x, y, w, h) in rectangles]
        return self.edge_image, clustered_rectangles, self.upscale_factor

    def _apply_steps(self):
        image = self.gray_image
        for step in self.config['steps']:
            if step == ENHANCE_CONTRAST:
                image = combined_contrast_enhancement(image)
            elif step == BLUR:
                image = apply_blur(image, self.config.get('blur_kernel_size', (5, 5)))
            elif step == THRESHOLD:
                image = apply_adaptive_threshold(image)
            elif step == UPSCALE:
                image = upscale_image(image, 2)
                self.upscale_factor *= 2
        return image

    @staticmethod
    def _detect_edges(image):
        median_val = np.median(image)
        lower = int(max(0, 0.24 * median_val))
        upper = int(min(255, 0.96 * median_val))
        return cv2.Canny(image, lower, upper)

    def _find_rectangles(self, image):
        adjusted_area_threshold = self.min_area * (self.upscale_factor ** 2)
        contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rectangles = []
        for contour in contours:
            if cv2.contourArea(contour) > adjusted_area_threshold:
                epsilon = 0.01 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                if len(approx) == 4:
                    (x, y, w, h) = cv2.boundingRect(approx)
                    ratio = max(w, h) / min(w, h)
                    if ratio >= 3:
                        continue
                    rectangles.append((x, y, w, h))
        return rectangles
