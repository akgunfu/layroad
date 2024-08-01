import concurrent.futures

import cv2

from edge_connect import EdgeConnect
from rectangle_detection import RectangleDetector


class ProcessedImage:
    def __init__(self, original_image, edge_image, label, rects, lines, upscale_factor):
        """Initialize the processed image with results."""
        self.original_image = original_image
        self.edge_image = edge_image
        self.label = label
        self.rects = rects
        self.upscale_factor = upscale_factor
        self.upscaled_rects = self._scale_rectangles(rects, upscale_factor)
        self.lines = lines
        self.num_rects = len(rects)

    @staticmethod
    def _scale_rectangles(rectangles, factor):
        """Update rectangles for scaling."""
        updated = []
        for (x, y, w, h, cluster) in rectangles:
            if factor != 1:
                x = int(x / factor)
                y = int(y / factor)
                w = int(w / factor)
                h = int(h / factor)
            updated.append((x, y, w, h, cluster))
        return updated


def _process_single_config(original_image, gray_image, config):
    """Process a single image configuration."""
    detector = RectangleDetector(gray_image, original_image, config)
    edge_image, rects, upscale_factor = detector.detect()
    lines = EdgeConnect().create_lines(rects, edge_image)

    steps_label = f"{'->'.join(config['steps'])}"
    clusters_label = f"Clusters: {len(set([rect[-1] for rect in rects]))}"
    rects_label = f"Detected: {len(rects)}"
    height, width = original_image.shape[:2]
    dims_label = f"Dimensions: {width}x{height} px"
    area_factor = 10000
    min_area_label = f"Threshold: {width * height / area_factor} px^2"
    label = f"{steps_label}\n{clusters_label} - {rects_label}\n{min_area_label}\n{dims_label}"

    return ProcessedImage(original_image, edge_image, label, rects, lines, upscale_factor)


def process_image(image_file, configs):
    """Process a single image with all configurations in parallel."""
    original_image, filename = image_file
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(_process_single_config, original_image, gray_image, config) for config in configs]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # Sort results based on the number of rectangles detected
    results.sort(key=lambda x: x.num_rects, reverse=True)

    return filename, results
