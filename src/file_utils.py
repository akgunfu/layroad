import os

import cv2
import matplotlib.pyplot as plt
import numpy as np

from utils import create_output_directory, add_homebrew_path

# Constants
PDF_DPI = 300
PNG_EXTENSION = '.png'
PDF_EXTENSION = '.pdf'
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg')
COLOR_RECTANGLE = (0, 0, 255)
COLOR_LINE = (255, 255, 0)


def load_images(folder_path='assets'):
    """Load images from the assets folder."""
    images_with_filenames = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(PDF_EXTENSION):
            add_homebrew_path()
            try:
                from pdf2image import convert_from_path
                pages = convert_from_path(os.path.join(folder_path, filename), dpi=PDF_DPI)
                image = np.array(pages[0])
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                images_with_filenames.append((image, filename))
            except Exception as e:
                raise RuntimeError(f"Failed to load PDF file. Error: {e}")
        elif filename.lower().endswith(IMAGE_EXTENSIONS):
            image = cv2.imread(os.path.join(folder_path, filename))
            if image is None:
                raise FileNotFoundError(f"Image not found: {os.path.join(folder_path, filename)}")
            images_with_filenames.append((image, filename))
    return images_with_filenames


def save_results(results, max_images=9, target_file_name=None):
    """Save a plot of the processed images as a PNG file."""
    create_output_directory()

    num_images = len(results)
    if num_images == 0:
        print("No images with rectangles to display.")
        return

    num_cols = int(np.ceil(np.sqrt(max_images)))
    num_rows = int(np.ceil(num_images / num_cols))

    plt.figure(figsize=(num_cols * 5, num_rows * 5), dpi=300)
    font_size = np.ceil(48 / (num_cols + 1))
    for i, result in enumerate(results[:max_images]):
        overlay = cv2.cvtColor(result.edge_image, cv2.COLOR_BGR2RGB)
        for (x, y, w, h, cluster_id) in result.rects:
            cv2.rectangle(overlay, (x, y), (x + w, y + h), COLOR_RECTANGLE, -1)

        for line in result.lines:
            cv2.line(overlay, line.start, line.end, COLOR_LINE, 3)  # Cyan lines, thickness 3

        plt.subplot(num_rows, num_cols, i + 1)
        plt.imshow(overlay)
        plt.title(result.label, fontweight='bold', fontsize=font_size)
        plt.axis('off')
        plt.gca().add_patch(
            plt.Rectangle((0, 0), overlay.shape[1], overlay.shape[0], linewidth=3,
                          edgecolor='black', facecolor='none'))

    output_filename = target_file_name.replace(PDF_EXTENSION, PNG_EXTENSION) if target_file_name else "output.png"
    output_path = os.path.join('outputs', output_filename)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
