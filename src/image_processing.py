import cv2
import numpy as np

# Constants for processing steps
ENHANCE_CONTRAST = 'EC'
BLUR = 'BL'
EDGE_DETECTION = 'ED'
THRESHOLD = 'TH'
UPSCALE = 'US'


def combined_contrast_enhancement(gray_image):
    """
    Enhance contrast using multiple techniques for better results.
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(5, 5))
    enhanced_image = clahe.apply(gray_image)
    enhanced_image = cv2.equalizeHist(enhanced_image)
    inv_gamma = 1.0 / 1.2
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in np.arange(0, 256)]).astype("uint8")
    enhanced_image = cv2.LUT(enhanced_image, table)
    return cv2.normalize(enhanced_image, None, 0, 255, cv2.NORM_MINMAX)


def apply_adaptive_threshold(image):
    """
    Enhance edges using adaptive thresholding.
    """
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)


def upscale_image(image, scale=2):
    """
    Upscale the image.
    """
    return cv2.resize(image, (0, 0), fx=scale, fy=scale)


def apply_blur(image, kernel_size=(5, 5)):
    """
    Reduce noise and improve edge detection with Gaussian blur.
    """
    return cv2.GaussianBlur(image, kernel_size, 0)
