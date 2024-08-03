import cv2
import numpy as np

# Constants for processing steps
ENHANCE_CONTRAST = 'EC'
BLUR = 'BL'
EDGE_DETECTION = 'ED'
THRESHOLD = 'TH'
UPSCALE = 'US'
GAMMA = 1.2
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID_SIZE = (5, 5)
BLUR_KERNEL_SIZE = (5, 5)
THRESHOLD_MAX_VALUE = 255


def enhance_contrast(image: cv2.typing.MatLike) -> cv2.typing.MatLike:
    """Enhance contrast using multiple techniques."""
    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE_GRID_SIZE)
    enhanced_image = clahe.apply(image)
    enhanced_image = cv2.equalizeHist(enhanced_image)
    inv_gamma = 1.0 / GAMMA
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(enhanced_image, table)


def adaptive_threshold(image: cv2.typing.MatLike) -> cv2.typing.MatLike:
    """Apply adaptive thresholding."""
    return cv2.adaptiveThreshold(image, THRESHOLD_MAX_VALUE, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)


def upscale(image: cv2.typing.MatLike, scale=2) -> cv2.typing.MatLike:
    """Upscale the image."""
    return cv2.resize(image, (0, 0), fx=scale, fy=scale)


def blur(image: cv2.typing.MatLike, kernel_size=BLUR_KERNEL_SIZE) -> cv2.typing.MatLike:
    """Apply Gaussian blur to reduce noise."""
    return cv2.GaussianBlur(image, kernel_size, 0)
