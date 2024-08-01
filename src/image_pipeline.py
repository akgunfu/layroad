import concurrent.futures

import cv2

from rectangle_detection import RectangleDetection
from edge_connect import EdgeConnect


class ImageProcessResponse:
    def __init__(self, original_image, edge_image, label, rectangles, lines, upscale_factor):
        self.original_image = original_image
        self.edge_image = edge_image
        self.label = label
        self.upscale_factor = upscale_factor
        self.rectangles = rectangles
        self.upscaled_rectangles = self.update_rectangles_for_scaling(rectangles, upscale_factor)
        self.lines = lines
        self.num_rectangles = len(rectangles)

    @staticmethod
    def update_rectangles_for_scaling(rectangles, upscale_factor):
        updated = []
        for (x, y, w, h, cluster) in rectangles:
            if upscale_factor != 1:
                x = int(x / upscale_factor)
                y = int(y / upscale_factor)
                w = int(w / upscale_factor)
                h = int(h / upscale_factor)
            updated.append((x, y, w, h, cluster))
        return updated


def process_single_config(original_image, gray_image, config):
    """
    Process a single image configuration and return the result.
    """
    edge_detection = RectangleDetection(gray_image, original_image, config)
    edge_image, rectangles, upscale_factor = edge_detection.process()
    lines = EdgeConnect().create_direct_connect_lines(rectangles, edge_image)

    steps_label = f"{'->'.join(config['steps'])}"
    cluster_count_label = f"Clusters: {len(set([rect[-1] for rect in rectangles]))}"
    rect_count_label = f"Detected: {len(rectangles)}"
    height, width = original_image.shape[:2]
    dimension_label = f"Dimensions: {width}x{height} px"
    image_dimension = width * height
    area_factor = 10000
    min_area_label = f"Threshold: {image_dimension / area_factor} px^2"
    label = f"{steps_label}\n{cluster_count_label} - {rect_count_label}\n{min_area_label}\n{dimension_label}"

    return ImageProcessResponse(original_image, edge_image, label, rectangles, lines, upscale_factor)


def process_image(image_with_filename, configs):
    """
    Process a single image with all configurations in parallel and return the results.
    """
    original_image, filename = image_with_filename
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_single_config, original_image, gray_image, config) for config in configs]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    return filename, results
