import concurrent.futures

from config_generator import generate_configs
from file_utils import load_images_from_assets_folder, save_plot_as_png
from image_pipeline import process_image
from utils import rank_images


def main():
    images_with_filenames = load_images_from_assets_folder()
    configs = generate_configs()

    best_image_process_response_list = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_image, image_with_filename, configs) for image_with_filename in
                   images_with_filenames]

        for future in concurrent.futures.as_completed(futures):
            filename, results = future.result()

            sorted_results = rank_images(results)
            save_plot_as_png(sorted_results, max_images=4, target_file_name=filename)

            best_image_process_response_list.append(sorted_results[0])

    overall_best_results = rank_images(best_image_process_response_list)
    save_plot_as_png(overall_best_results, max_images=len(overall_best_results), target_file_name="all-output")


if __name__ == '__main__':
    main()
