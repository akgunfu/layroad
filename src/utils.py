import os


def create_output_directory(path='outputs'):
    if not os.path.exists(path):
        os.makedirs(path)


def rank_images(images_with_filenames, titles, num_rectangles_list):
    images_with_filenames_and_titles = [
        (image, filename, title, count)
        for (image, filename), title, count in zip(images_with_filenames, titles, num_rectangles_list)
        if count > 0
    ]

    images_with_filenames_and_titles.sort(key=lambda x: x[3], reverse=True)

    sorted_images_with_filenames = [item[:2] for item in images_with_filenames_and_titles]
    sorted_titles = [item[2] for item in images_with_filenames_and_titles]

    return sorted_images_with_filenames, sorted_titles
