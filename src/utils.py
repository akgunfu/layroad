import os


def create_output_directory(path='outputs'):
    if not os.path.exists(path):
        os.makedirs(path)


def rank_images(results):
    """
    Rank images based on the number of rectangles detected.
    """
    results.sort(key=lambda x: x.num_rectangles, reverse=True)
    return results
