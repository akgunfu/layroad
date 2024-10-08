import os
from typing import List, Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np
from pdf2image import convert_from_path

from .geometry import Rectangle, Line, Shape, Node
from .image_pipeline import ProcessedImage
from .utils import add_homebrew_path, Icon, TextColor

INPUT_DPI = 500
OUTPUT_DPI = 1000
DEFAULT_NUM_FILES = 3
DEFAULT_OUTPUT_FILE = 'output.png'
#
PNG_EXTENSION = '.png'
PDF_EXTENSION = '.pdf'
JPEG_EXTENSION = '.jpeg'
JPG_EXTENSION = '.jpg'
JSON_EXTENSION = '.json'
IMAGE_EXTENSIONS = (PNG_EXTENSION, JPG_EXTENSION, JPEG_EXTENSION)
#
COLOR_RECTANGLE = (255, 49, 49)
COLOR_LINE = (170, 255, 0)
COLOR_TEXT = (0, 0, 0)
FILL_THICKNESS = -1
LINE_THICKNESS = 3
TRAVEL_NODE_COLOR = (255, 255, 255)
TRAVEL_NODE_RADIUS = 15
TERMINAL_NODE_COLOR = (0, 150, 255)
TERMINAL_NODE_RADIUS = 45


def load_images(folder_path='assets', num_files=DEFAULT_NUM_FILES) -> List[Tuple[cv2.typing.MatLike, str]]:
    """Load a limited number of images from the assets folder."""
    add_homebrew_path()
    images_with_names = []
    file_count = 0
    for filename in os.listdir(folder_path):
        print(f"{Icon.START} [Import] Loading image file {TextColor.YELLOW}{filename}{TextColor.RESET} ...")
        if file_count >= num_files:
            break
        if filename.lower().endswith(PDF_EXTENSION):
            try:
                pages = convert_from_path(os.path.join(folder_path, filename), dpi=INPUT_DPI)
                image = np.array(pages[0])
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                images_with_names.append((image, filename))
                file_count += 1
                print(f"{Icon.DONE} [Import] Loaded image file {TextColor.YELLOW}{filename}{TextColor.RESET}")
            except Exception as e:
                raise RuntimeError(f"{Icon.ERROR} [Import] Failed to load PDF file. Error: {e}")
        elif filename.lower().endswith(IMAGE_EXTENSIONS):
            image = cv2.imread(os.path.join(folder_path, filename))
            if image is None:
                raise FileNotFoundError(f"{Icon.ERROR} [Import] Image not found: {filename}")
            images_with_names.append((image, filename))
            file_count += 1
            print(f"{Icon.DONE} [Import] Loaded image file {TextColor.YELLOW}{filename}{TextColor.RESET}")
        else:
            print(f"{Icon.ERROR} [Import] Not a valid file {TextColor.YELLOW}{filename}{TextColor.RESET}")
    return images_with_names


def save_result_images(results: List[ProcessedImage], max_images: int, target_file_name: str):
    """Save a plot of the processed images as a PNG file."""
    filtered_results = results[:max_images]
    if target_file_name.lower().endswith(PDF_EXTENSION):
        output_filename = target_file_name.replace(PDF_EXTENSION, PNG_EXTENSION)
    else:
        output_filename = target_file_name
    print(f"{Icon.START} [Save] Saving {len(filtered_results)} results -> "
          f"{TextColor.YELLOW}{output_filename}{TextColor.RESET} ...")
    num_images = len(results)
    if num_images == 0:
        print(f"{Icon.ERROR} [Save] No results to save. Skipping...")
        return
    num_cols = int(np.ceil(np.sqrt(max_images)))
    num_rows = int(np.ceil(num_images / num_cols))
    plt.figure(figsize=(num_cols * 5, num_rows * 5), dpi=OUTPUT_DPI)
    font_size = 48 // (num_cols + 3)

    for i, result in enumerate(filtered_results):
        overlay = cv2.cvtColor(result.edge_img, cv2.COLOR_BGR2RGB)
        overlay = _draw_objects(overlay, result.rects, result.lines, result.nodes)
        plt.subplot(num_rows, num_cols, i + 1)
        plt.imshow(overlay)
        plt.title(result.label, fontsize=font_size)
        plt.axis('off')

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.3, wspace=0.3)  # Adjust the horizontal and vertical padding
    plt.savefig(output_filename)
    plt.close()
    print(f"{Icon.DONE} [Save] Saved {len(filtered_results)} results ->"
          f" {TextColor.CYAN}{output_filename}{TextColor.RESET}")


def _draw_objects(overlay: cv2.typing.MatLike, rects: List[Rectangle], lines: List[Line], nodes: List[Node]):
    """Draw rectangles and lines on the image."""
    for rect in rects:
        # draw rectangle
        cv2.rectangle(overlay, (rect.x, rect.y), (rect.x + rect.w, rect.y + rect.h), COLOR_RECTANGLE, LINE_THICKNESS)
        # draw text in the center of rectangle
        text = str(rect.id)
        # Calculate font scale based on rectangle dimensions
        font_scale = min(rect.w, rect.h) / 75  # sweet spot
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, font_scale, LINE_THICKNESS)[0]
        center_x = rect.x + rect.w // 2
        center_y = rect.y + rect.h // 2
        text_x = center_x - text_size[0] // 2
        text_y = center_y + text_size[1] // 2
        # Write index number at the center of the rectangle
        cv2.putText(overlay, text, (text_x, text_y), font, font_scale, COLOR_TEXT, LINE_THICKNESS,
                    lineType=cv2.LINE_AA)
    #
    for line in lines:
        cv2.line(overlay, (line.start.x, line.start.y), (line.end.x, line.end.y), COLOR_LINE, LINE_THICKNESS)
    #
    for node in nodes:
        color = TRAVEL_NODE_COLOR if not node.connection else TERMINAL_NODE_COLOR
        radius = TRAVEL_NODE_RADIUS if not node.connection else TERMINAL_NODE_RADIUS
        cv2.circle(overlay, (node.pos.x, node.pos.y), radius, color, FILL_THICKNESS)
    return overlay


def save_result_shapes(shapes: List[Shape], target_file_name: str):
    if target_file_name.lower().endswith(PDF_EXTENSION):
        output_filename = target_file_name.replace(PDF_EXTENSION, JSON_EXTENSION)
    else:
        output_filename = target_file_name
    print(f"{Icon.START} [Save] Saving {len(shapes)} shapes -> "
          f"{TextColor.YELLOW}{output_filename}{TextColor.RESET} ...")
    with open(output_filename, 'w') as file:
        for shape in shapes:
            json_str = shape.to_json()
            file.write(json_str + '\n')
    print(f"{Icon.DONE} [Save] Saved {len(shapes)} shapes ->"
          f" {TextColor.CYAN}{output_filename}{TextColor.RESET}")
