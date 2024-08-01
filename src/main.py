import concurrent.futures

from config_generator import generate_configs
from file_utils import load_images, save_results
from image_pipeline import process_image


def main():
    """Process images, generate configurations, and save results."""
    imgs_with_names = load_images()
    configs = generate_configs()

    best_responses = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_image, img_with_name, configs) for img_with_name in imgs_with_names]

        for future in concurrent.futures.as_completed(futures):
            filename, results = future.result()
            save_results(results, max_images=4, target_file_name=filename)
            best_responses.append(results[0])

    # Sort overall best results based on the number of rectangles detected
    best_responses.sort(key=lambda x: x.num_rects, reverse=True)
    save_results(best_responses, max_images=len(best_responses), target_file_name="all-output")


if __name__ == '__main__':
    main()
