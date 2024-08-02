import concurrent.futures

import cv2

from edge_connect import EdgeConnect
from rectangle_detection import RectangleDetector, Rectangle
from utils import ICON_STARTING, ICON_COMPLETED, ICON_DETECTED


class ProcessedImage:
    def __init__(self, original_img, edge_img, label, rects, lines, upscale_factor):
        """Initialize the processed image with results."""
        self.original_img = original_img
        self.edge_img = edge_img
        self.label = label
        self.rects = rects
        self.upscale_factor = upscale_factor
        self.upscaled_rects = self._scale_rectangles(rects, upscale_factor)
        self.lines = lines
        self.num_rects = len(rects)

    @staticmethod
    def _scale_rectangles(rects, factor):
        """Update rectangles for scaling."""
        updated = []
        for rect in rects:
            new_rect = Rectangle(rect.id, rect.x, rect.y, rect.w, rect.h)
            if factor != 1:
                new_rect.x = int(rect.x / factor)
                new_rect.y = int(rect.y / factor)
                new_rect.w = int(rect.w / factor)
                new_rect.h = int(rect.h / factor)
            new_rect.cluster = rect.cluster
            updated.append(new_rect)
        return updated


def _process_single_config(filename, original_img, gray_img, config):
    """Process a single image configuration."""
    print(f"{ICON_STARTING} [Process] Started processing image {filename} with config {config}")
    detector = RectangleDetector(gray_img, original_img, config)
    edge_img, rects, upscale_factor = detector.detect()
    print(f"{ICON_DETECTED} [Detection] Detected {len(rects)} rectangles for image {filename} with config {config}")
    lines = EdgeConnect().create_lines(rects, edge_img)
    print(f"{ICON_DETECTED} [Detection] Detected {len(lines)} rectangles for image {filename} with config {config}")

    steps_label = f"{'->'.join(config['steps'])}"
    clusters_label = f"Clusters: {len(set([rect.cluster for rect in rects]))}"
    rects_label = f"Rects: {len(rects)}"
    lines_label = f"Lines: {len(lines)}"
    height, width = original_img.shape[:2]
    dims_label = f"Dimensions: {width}x{height} px"
    label = f"{steps_label}\n{clusters_label}\n{rects_label} - {lines_label}\n{dims_label}"

    print(f"{ICON_COMPLETED} [Process] Finished processing image {filename} with config {config}")
    return ProcessedImage(original_img, edge_img, label, rects, lines, upscale_factor)


def process_image(image_file, configs):
    """Process a single image with all configurations in parallel."""
    original_img, filename = image_file
    gray_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(_process_single_config, filename, original_img, gray_img, config) for config in
                   configs]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # Sort results based on the number of rectangles detected
    results.sort(key=lambda x: x.num_rects, reverse=True)

    return filename, results
