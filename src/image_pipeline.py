import concurrent.futures
from typing import List, Tuple

import cv2

from .geometry import Line, Node, Rectangle
from .line_generator import LineGenerator
from .node_generator import NodeGenerator
from .rectangle_detection import RectangleDetector
from .utils import Icon, TextColor


class ProcessedImage:
    def __init__(self, original_img: cv2.typing.MatLike, edge_img: cv2.typing.MatLike, label: str,
                 rects: List[Rectangle], lines: List[Line], nodes: List[Node], upscale_factor: int):
        """Initialize the processed image with results."""
        self.original_img = original_img
        self.edge_img = edge_img
        self.label = label
        self.rects = rects
        self.lines = lines
        self.nodes = nodes
        self.upscale_factor = upscale_factor
        # self.upscaled_rects = self._scale_rectangles(rects, upscale_factor)

        self.num_rects = len(rects)

    @staticmethod
    def _scale_rectangles(rects: List[Rectangle], upscale_factor: int) -> List[Rectangle]:
        """Update rectangles for scaling."""
        updated = []
        for rect in rects:
            new_rect = Rectangle(rect.id, rect.x, rect.y, rect.w, rect.h)
            if upscale_factor != 1:
                new_rect.x = int(rect.x / upscale_factor)
                new_rect.y = int(rect.y / upscale_factor)
                new_rect.w = int(rect.w / upscale_factor)
                new_rect.h = int(rect.h / upscale_factor)
            new_rect.cluster = rect.cluster
            updated.append(new_rect)
        return updated


def _process_single_config(filename: str, original_img: cv2.typing.MatLike, gray_img: cv2.typing.MatLike,
                           config) -> ProcessedImage:
    """Process a single image configuration."""
    print(f"{Icon.START} [Process] Started processing image {TextColor.YELLOW}{filename}{TextColor.RESET} "
          f"with config {config} ...")
    detector = RectangleDetector(gray_img, original_img, config)
    edge_img, rects, upscale_factor = detector.detect()
    print(f"{Icon.DETECT} [Detection] {TextColor.GREEN}Detected {len(rects)} rectangles{TextColor.RESET} "
          f"for image {TextColor.YELLOW}{filename}{TextColor.RESET} with config {config}")
    lines = LineGenerator(edge_img, rects, upscale_factor).generate()
    print(f"{Icon.DETECT} [Detection] {TextColor.GREEN}Detected {len(lines)} lines{TextColor.RESET} "
          f"for image {TextColor.YELLOW}{filename}{TextColor.RESET} with config {config}")
    nodes = NodeGenerator(rects, lines).generate()
    print(f"{Icon.DETECT} [Detection] {TextColor.GREEN}Detected {len(nodes)} nodes{TextColor.RESET} "
          f"for image {TextColor.YELLOW}{filename}{TextColor.RESET} with config {config}")

    if lines:
        smallest_line_length = min(line.length() for line in lines)
        smallest_line_count = sum(1 for line in lines if line.length() <= 1.1 * smallest_line_length)
    else:
        smallest_line_length = 0
        smallest_line_count = 0
    if rects:
        smallest_rect_area = min(rect.size() for rect in rects)
        smallest_rect_count = sum(1 for rect in rects if rect.w * rect.h <= 1.1 * smallest_rect_area)
    else:
        smallest_rect_area = 0
        smallest_rect_count = 0

    min_line_label = f"Min Line: {smallest_line_length:.2f} px (~{smallest_line_count})"
    min_rect_label = f"Min Rect: {smallest_rect_area} px² (~{smallest_rect_count})"
    #
    steps_label = f"{'->'.join(config['steps'])}"
    clusters_label = f"Clusters: {len(set([rect.cluster for rect in rects]))}"
    rects_label = f"Rects: {len(rects)}"
    lines_label = f"Lines: {len(lines)}"
    label = f"{steps_label}\n{clusters_label}\n{rects_label} - {lines_label}\n{min_rect_label}\n{min_line_label}"

    print(f"{Icon.DONE} [Process] Finished processing image {TextColor.YELLOW}{filename}{TextColor.RESET} "
          f"with config {config}")
    return ProcessedImage(original_img, edge_img, label, rects, lines, nodes, upscale_factor)


def process_image(image_file: Tuple[cv2.typing.MatLike, str], configs) -> Tuple[str, List[ProcessedImage]]:
    """Process a single image with all configurations in parallel."""
    original_img, filename = image_file
    gray_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(_process_single_config, filename, original_img, gray_img, config) for config in
                   configs]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # Sort results based on the number of rectangles detected
    results.sort(key=lambda x: x.num_rects, reverse=True)

    return filename, results
