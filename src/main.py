import concurrent.futures

from config_generator import generate_configs
from file_utils import load_images_from_assets_folder, save_plot_as_png
from image_pipeline import process_image
from utils import rank_images


def main():
    images_with_filenames = load_images_from_assets_folder()
    configs = generate_configs()

    best_images_with_filenames = []
    best_labels = []
    best_num_rectangles_list = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_image, image_with_filename, configs) for image_with_filename in
                   images_with_filenames]

        for future in concurrent.futures.as_completed(futures):
            final_images, labels, num_rectangles_list, filename = future.result()
            images_with_filenames_to_save = [(image, filename) for image in final_images]

            sorted_images, sorted_labels = rank_images(images_with_filenames_to_save, labels, num_rectangles_list)
            save_plot_as_png(sorted_images, sorted_labels, max_images=4)

            best_images_with_filenames.append(sorted_images[0])
            best_labels.append(sorted_labels[0])
            best_num_rectangles_list.append(num_rectangles_list[0])

    overall_best_images_with_filenames, overall_best_labels = rank_images(best_images_with_filenames, best_labels,
                                                                          best_num_rectangles_list)
    save_plot_as_png(overall_best_images_with_filenames, overall_best_labels,
                     max_images=len(overall_best_images_with_filenames), target_file_name="all-output")


if __name__ == '__main__':
    main()
