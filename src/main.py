import concurrent.futures

from config_generator import generate_configs
from file_utils import load_images, save_result_images, save_result_shapes
from image_pipeline import process_image
from utils import create_clean_output_directory, TextColor


def main():
    """Process images, generate configurations, and save results."""
    images_with_names = load_images()
    configs = generate_configs()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_image, img_with_name, configs) for img_with_name in images_with_names]

    create_clean_output_directory('outputs/images')
    create_clean_output_directory('outputs/shapes')
    #
    best_responses = []
    for future in concurrent.futures.as_completed(futures):
        filename, results = future.result()
        save_result_shapes(results[0].rects + results[0].lines, target_file_name=filename)
        save_result_images(results, max_images=4, target_file_name=filename)
        best_responses.append(results[0])
    # Sort overall best results based on the number of rectangles detected
    best_responses.sort(key=lambda x: x.num_rects, reverse=True)
    save_result_images(best_responses, max_images=len(best_responses))

    print(f"\n{TextColor.GREEN}All tasks are completed!{TextColor.RESET} "
          f"({len(images_with_names)}/{len(images_with_names)})")


if __name__ == '__main__':
    main()
