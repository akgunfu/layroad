import cv2
import numpy as np

from clustering import cluster_rectangles
from image_processing import combined_contrast_enhancement, apply_blur, apply_adaptive_threshold, upscale_image


class EdgeDetection:
    EC = 'EC'  # Enhance Contrast
    BL = 'BL'  # Blur
    ED = 'ED'  # Edge Detection
    TH = 'TH'  # Threshold
    US = 'US'  # Upscale

    def __init__(self, gray_image, original_image, config):
        """
        Initialize with grayscale and original images, and configuration.
        """
        self.gray_image = gray_image
        self.original_image = original_image
        self.config = config
        self.upscale_factor = 1
        self.area_factor = 10000  # Updated area factor

    def process(self):
        """
        Detect edges and draw rectangles based on configuration.
        """
        intermediate_images, labels = self._apply_steps()

        # Calculate Min Area
        height, width = self.original_image.shape[:2]
        min_area = round(width * height / self.area_factor)

        # Find and filter rectangles
        rectangles = self._find_rectangles(intermediate_images[-1], min_area)

        # Apply clustering if applicable
        if len(rectangles) > 1:
            clustered_rectangles = cluster_rectangles(rectangles, mode='distance')
        else:
            clustered_rectangles = [(x, y, w, h, 0) for (x, y, w, h) in rectangles]

        final_image = self._draw_rectangles(clustered_rectangles)
        intermediate_images.append(final_image)
        labels.append(self._get_label(self.config['steps']))
        num_clusters = len(set([rect[-1] for rect in clustered_rectangles]))

        return intermediate_images, labels, len(clustered_rectangles), num_clusters

    def _apply_steps(self):
        """
        Apply image processing steps based on configuration.
        """
        image = self.gray_image
        intermediate_images = [self.original_image, self.gray_image]
        labels = ['Original Image', 'Grayscale Image']

        for step in self.config['steps']:
            if step == EdgeDetection.EC:
                image = combined_contrast_enhancement(image)
                intermediate_images.append(image)
                labels.append('Enhanced Contrast Image')
            elif step == EdgeDetection.BL:
                image = apply_blur(image, self.config.get('blur_kernel_size', (5, 5)))
                intermediate_images.append(image)
                labels.append('Blurred Image')
            elif step == EdgeDetection.ED:
                image = self._detect_edges(image)
                intermediate_images.append(image)
                labels.append('Edges Image')
            elif step == EdgeDetection.TH:
                image = apply_adaptive_threshold(image)
                intermediate_images.append(image)
                labels.append('Thresholded Image')
            elif step == EdgeDetection.US:
                image = upscale_image(image, 2)
                self.upscale_factor *= 2
                intermediate_images.append(image)
                labels.append('Upscaled Image')

        return intermediate_images, labels

    @staticmethod
    def _detect_edges(image):
        """
        Detect edges using the Canny edge detection algorithm.
        """
        median_val = np.median(image)
        lower = int(max(0, 0.24 * median_val))
        upper = int(min(255, 0.96 * median_val))
        return cv2.Canny(image, lower, upper)

    def _find_rectangles(self, image, area_threshold):
        """
        Find rectangles from contours.
        """
        adjusted_area_threshold = area_threshold * (self.upscale_factor ** 2)
        contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rectangles = []
        for contour in contours:
            if cv2.contourArea(contour) > adjusted_area_threshold:
                epsilon = 0.01 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                if len(approx) == 4:
                    (x, y, w, h) = cv2.boundingRect(approx)
                    ratio = max(w, h) / min(w, h)
                    if ratio < 3:
                        rectangles.append((x, y, w, h))
        return rectangles

    def _draw_rectangles(self, clustered_rectangles, thickness=2):
        """
        Draw rectangles on the image based on clusters.
        """
        image_with_rectangles = cv2.cvtColor(self.gray_image, cv2.COLOR_GRAY2BGR)
        if not clustered_rectangles:
            return image_with_rectangles

        cluster_sizes = {}
        cluster_counts = {}
        for x, y, w, h, cluster in clustered_rectangles:
            size = w * h
            if cluster in cluster_sizes:
                cluster_sizes[cluster] += size
                cluster_counts[cluster] += 1
            else:
                cluster_sizes[cluster] = size
                cluster_counts[cluster] = 1
        cluster_avg_sizes = {cluster: cluster_sizes[cluster] / cluster_counts[cluster] for cluster in cluster_sizes}

        avg_sizes = list(cluster_avg_sizes.values())
        min_avg_size, max_avg_size = min(avg_sizes), max(avg_sizes)

        def get_color(avg_size):
            ratio = (avg_size - min_avg_size) / (max_avg_size - min_avg_size) if max_avg_size > min_avg_size else 0
            green = int(255 * (1 - ratio))
            red = int(255 * ratio)
            return (0, green, red)

        cluster_colors = {cluster: get_color(avg_size) for cluster, avg_size in cluster_avg_sizes.items()}

        for idx, (x, y, w, h, cluster) in enumerate(clustered_rectangles):
            if self.upscale_factor != 1:
                x = int(x / self.upscale_factor)
                y = int(y / self.upscale_factor)
                w = int(w / self.upscale_factor)
                h = int(h / self.upscale_factor)
            color = cluster_colors[cluster]
            cv2.rectangle(image_with_rectangles, (x, y), (x + w, y + h), color, -1)
            cv2.rectangle(image_with_rectangles, (x, y), (x + w, y + h), (0, 0, 0), thickness)

        return image_with_rectangles

    @staticmethod
    def _get_label(steps):
        """
        Generate a label by joining the steps with '->'.
        """
        return '->'.join(steps)
