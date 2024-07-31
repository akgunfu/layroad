import concurrent.futures

import cv2

from rectangle_detection import RectangleDetection


def process_single_config(original_image, gray_image, config):
    """
    Process a single image configuration and return the result.
    """
    edge_detection = RectangleDetection(gray_image, original_image, config)
    intermediate_images, _, num_rectangles, num_clusters = edge_detection.process()
    final_image = intermediate_images[-1]

    steps_label = f"{'->'.join(config['steps'])}"
    cluster_count_label = f"Clusters: {num_clusters}"
    rect_count_label = f"Detected: {num_rectangles}"
    height, width = original_image.shape[:2]
    dimension_label = f"Dimensions: {width}x{height} px"
    image_dimension = width * height
    area_factor = 10000
    min_area_label = f"Threshold: {image_dimension / area_factor} px^2"
    label = f"{steps_label}\n{cluster_count_label} - {rect_count_label}\n{min_area_label}\n{dimension_label}"

    return final_image, label, num_rectangles


def process_image(image_with_filename, configs):
    """
    Process a single image with all configurations in parallel and return the results.
    """
    original_image, filename = image_with_filename
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_single_config, original_image, gray_image, config) for config in configs]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    final_images, labels, num_rectangles_list = zip(*results)
    return final_images, labels, num_rectangles_list, filename
