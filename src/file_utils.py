import os

import cv2
import matplotlib.pyplot as plt
import numpy as np

from utils import create_output_directory


def load_images_from_assets_folder(folder_path='assets'):
    """
    Load images from the assets folder. If the file is a PDF, convert the first page to an image.
    """
    images_with_filenames = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            _add_homebrew_path_to_env()
            try:
                from pdf2image import convert_from_path
                pages = convert_from_path(os.path.join(folder_path, filename), dpi=300)
                image = np.array(pages[0])
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                images_with_filenames.append((image, filename))
            except Exception as e:
                raise RuntimeError(f"Failed to load PDF file. Original error: {e}")
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image = cv2.imread(os.path.join(folder_path, filename))
            if image is None:
                raise FileNotFoundError(f"Image not found at path: {os.path.join(folder_path, filename)}")
            images_with_filenames.append((image, filename))
    return images_with_filenames


def save_plot_as_png(results, max_images=9, target_file_name=None):
    create_output_directory()

    num_images = len(results)
    if num_images == 0:
        print("No images with rectangles to display.")
        return

    ncols = int(np.ceil(np.sqrt(max_images)))
    nrows = int(np.ceil(num_images / ncols))

    plt.figure(figsize=(ncols * 5, nrows * 5), dpi=300)
    font_size = np.ceil(48 / (ncols + 1))
    for i, result in enumerate(results[:max_images]):
        overlay = cv2.cvtColor(result.edge_image, cv2.COLOR_BGR2RGB)
        for (x, y, w, h, cluster_id) in result.rectangles:
            cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 255), -1)

        for line in result.lines:
            cv2.line(overlay, line.start, line.end, (255, 255, 0), 3)  # Cyan lines, thickness 3

        plt.subplot(nrows, ncols, i + 1)
        plt.imshow(overlay)
        plt.title(result.label, fontweight='bold', fontsize=font_size)
        plt.axis('off')
        plt.gca().add_patch(
            plt.Rectangle((0, 0), overlay.shape[1], overlay.shape[0], linewidth=3,
                          edgecolor='black', facecolor='none'))

    output_filename = target_file_name.replace('.pdf', '.png') if target_file_name else "output.png"
    output_path = os.path.join('outputs', output_filename)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def _add_homebrew_path_to_env():
    """
    Add Homebrew path to the environment if it's not already included.
    """
    homebrew_path = '/opt/homebrew/bin'
    if homebrew_path not in os.environ['PATH']:
        os.environ['PATH'] += os.pathsep + homebrew_path
