import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
from pdf2image import convert_from_path

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


def save_plot_as_png(images_with_filenames, titles, max_images=9, target_file_name=None):
    """
    Save a list of images with their corresponding titles as a PNG file.
    """
    create_output_directory()
    images_with_filenames_and_titles = [
        (image, filename, title)
        for (image, filename), title in zip(images_with_filenames, titles)
    ]
    images_with_filenames_and_titles.sort(key=lambda x: int(x[2].split("\n")[1].split(": ")[-1]), reverse=True)
    top_images_with_filenames_and_titles = images_with_filenames_and_titles[:max_images]

    sorted_images_with_filenames = [item[:2] for item in top_images_with_filenames_and_titles]
    sorted_titles = [item[2] for item in top_images_with_filenames_and_titles]

    num_images = len(sorted_images_with_filenames)
    if num_images == 0:
        print("No images with rectangles to display.")
        return

    ncols = int(np.ceil(np.sqrt(max_images)))
    nrows = int(np.ceil(num_images / ncols))

    plt.figure(figsize=(ncols * 5, nrows * 5), dpi=100)
    font_size = np.ceil(48 / (ncols + 1))
    for i, ((image, filename), title) in enumerate(zip(sorted_images_with_filenames, sorted_titles)):
        plt.subplot(nrows, ncols, i + 1)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.title(title, fontweight='bold', fontsize=font_size)
        plt.axis('off')
        plt.gca().add_patch(
            plt.Rectangle((0, 0), image.shape[1], image.shape[0], linewidth=3, edgecolor='black', facecolor='none'))

    output_filename = target_file_name if target_file_name else os.path.basename(
        sorted_images_with_filenames[0][1]).replace('P.png', '_output').replace('.pdf', '_output')
    output_path = os.path.join('outputs', f"{output_filename}.png")

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
