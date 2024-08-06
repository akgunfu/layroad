import argparse
import concurrent.futures
from typing import Tuple, List

import cv2.typing

from src.config_generator import generate_configs
from src.file_utils import load_images, save_result_images, save_result_shapes
from src.image_pipeline import process_image
from src.utils import create_clean_output_directory, TextColor


def process_images(images_with_names: List[Tuple[cv2.typing.MatLike, str]], output_dir: str, max_images: int):
    """Process a list of images, generate configurations, and save results."""
    configs = generate_configs()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_image, img_with_name, configs) for img_with_name in images_with_names]

    create_clean_output_directory(f'{output_dir}/images')
    create_clean_output_directory(f'{output_dir}/shapes')

    best_responses = []
    for future in concurrent.futures.as_completed(futures):
        filename, results = future.result()
        save_result_shapes(results[0].rects + results[0].lines, target_file_name=f'{output_dir}/shapes/{filename}')
        save_result_images(results, max_images=max_images, target_file_name=f'{output_dir}/images/{filename}')
        best_responses.append(results[0])
    if len(best_responses) <= 1:
        return
        # Sort overall best results based on the number of rectangles detected
    best_responses.sort(key=lambda x: x.num_rects, reverse=True)
    save_result_images(best_responses, max_images=len(best_responses),
                       target_file_name=f'{output_dir}/images/output.png')

    print(f"\n{TextColor.GREEN}All tasks are completed!{TextColor.RESET} "
          f"({len(images_with_names)}/{len(images_with_names)})")


def process_from_directory(input_dir: str, output_dir: str, max_images: int):
    """Process images from a directory."""
    images_with_names = load_images(input_dir)
    process_images(images_with_names, output_dir, max_images)


def process_from_file(file_path: str, output_dir: str):
    """Process a single image file."""
    images_with_names = []  ## todo implement file path
    process_images(images_with_names, output_dir, max_images=len(images_with_names))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process images and save results.')
    parser.add_argument('-i', '--input_dir', type=str, default='assets',
                        help='Directory containing input images')
    parser.add_argument('-o', '--output_dir', type=str, default='outputs',
                        help='Directory to save output images and shapes')
    parser.add_argument('-m', '--max_images', type=int, default=3,
                        help='Maximum number of images to process')
    parser.add_argument('-f', '--file_path', type=str, default=None,
                        help='Path to the input image file')

    args = parser.parse_args()

    if args.input_dir and args.file_path:
        parser.error("Please provide either --input_dir or --file_path, not both.")

    if args.file_path:
        process_from_file(args.file_path, args.output_dir)
    elif args.input_dir:
        process_from_directory(args.input_dir, args.output_dir, args.max_images)
    else:
        # Default behavior if no arguments are provided
        print("No input provided. Running with default parameters.")
        # Set default values for processing from a default directory with default parameters
        default_input_dir = 'default_inputs'
        default_output_dir = 'default_outputs'
        default_max_images = 4

        process_from_directory(default_input_dir, default_output_dir, default_max_images)
