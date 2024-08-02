import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
from pdf2image import convert_from_path

from utils import add_homebrew_path, ICON_STARTING, ICON_ERROR, ICON_COMPLETED

# Constants
PDF_DPI = 300
PNG_EXTENSION = '.png'
PDF_EXTENSION = '.pdf'
JPEG_EXTENSION = '.jpeg'
JPG_EXTENSION = '.jpg'
DEFAULT_OUTPUT_FILE = 'output.png'
IMAGE_EXTENSIONS = (PNG_EXTENSION, JPG_EXTENSION, JPEG_EXTENSION)
COLOR_RECTANGLE = (0, 255, 0)
COLOR_LINE = (255, 0, 0)
DEFAULT_NUM_FILES = 3


def load_images(folder_path='assets', num_files=DEFAULT_NUM_FILES):
    """Load a limited number of images from the assets folder."""
    add_homebrew_path()
    images_with_names = []
    file_count = 0
    for filename in os.listdir(folder_path):
        print(f"{ICON_STARTING} [Import] Loading image file {filename}")
        if file_count >= num_files:
            break
        if filename.lower().endswith(PDF_EXTENSION):
            try:
                pages = convert_from_path(os.path.join(folder_path, filename), dpi=PDF_DPI)
                image = np.array(pages[0])
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                images_with_names.append((image, filename))
                file_count += 1
                print(f"{ICON_COMPLETED} [Import] Loaded image file {filename}")
            except Exception as e:
                raise RuntimeError(f"{ICON_ERROR} [Import] Failed to load PDF file. Error: {e}")
        elif filename.lower().endswith(IMAGE_EXTENSIONS):
            image = cv2.imread(os.path.join(folder_path, filename))
            if image is None:
                raise FileNotFoundError(f"{ICON_ERROR} [Import] Image not found: {filename}")
            images_with_names.append((image, filename))
            file_count += 1
            print(f"{ICON_COMPLETED} [Import] Loaded image file {filename}")
    return images_with_names


def save_results(results, max_images=9, target_file_name=DEFAULT_OUTPUT_FILE):
    """Save a plot of the processed images as a PNG file."""
    filtered_results = results[:max_images]
    if target_file_name.lower().endswith(PDF_EXTENSION):
        output_filename = target_file_name.replace(PDF_EXTENSION, PNG_EXTENSION)
    else:
        output_filename = target_file_name
    print(f"{ICON_STARTING} [Save] Saving {len(filtered_results)} results to {output_filename}")
    num_images = len(results)
    if num_images == 0:
        print(f"{ICON_ERROR} [Save] No results to save. Skipping...")
        return
    num_cols = int(np.ceil(np.sqrt(max_images)))
    num_rows = int(np.ceil(num_images / num_cols))
    plt.figure(figsize=(num_cols * 5, num_rows * 5), dpi=300)
    font_size = np.ceil(48 / (num_cols + 1))

    for i, result in enumerate(filtered_results):
        overlay = cv2.cvtColor(result.edge_img, cv2.COLOR_BGR2RGB)
        overlay = _draw_objects(overlay, result.rects, result.lines)
        plt.subplot(num_rows, num_cols, i + 1)
        plt.imshow(overlay)
        plt.title(result.label, fontsize=font_size)
        plt.axis('off')

    output_path = os.path.join('outputs', output_filename)
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.3, wspace=0.3)  # Adjust the horizontal and vertical padding
    plt.savefig(output_path)
    plt.close()
    print(f"{ICON_COMPLETED} [Save] Saved {len(filtered_results)} results to {output_filename}")


def _draw_objects(overlay, rects, lines):
    """Draw rectangles and lines on the image."""
    for rect in rects:
        cv2.rectangle(overlay, (rect.x, rect.y), (rect.x + rect.w, rect.y + rect.h), COLOR_RECTANGLE, 5)
    for line in lines:
        cv2.line(overlay, line.start, line.end, COLOR_LINE, 5)
    return overlay
