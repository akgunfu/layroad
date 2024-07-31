# Image Processing Pipeline

## Overview

This project processes images and detects rectangles based on various configurations. It includes functionalities for
enhancing contrast, applying blurs, edge detection, adaptive thresholding, and upscaling images. The detected rectangles
are clustered by size or distance, and the results are visualized and saved as PNG files.

## Requirements

- Python 3.9+
- OpenCV
- NumPy
- Matplotlib
- pdf2image
- scikit-learn
- kneed

## Installation

1. **Install Homebrew (macOS only)**:
    ```sh
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

2. **Install required packages**:
    ```sh
    brew install poppler
    ```

3. **Set up a Python virtual environment**:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

4. **Install Python dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. **Prepare the `assets` folder**:
   Place your input images (PNG, JPG, JPEG) and PDF files in the `assets` folder.

2. **Run the pipeline**:
    ```sh
    python main.py
    ```

3. **View results**:
   The processed images and plots will be saved in the `outputs` folder.

## Troubleshooting

### Common Installation Errors

1. **Poppler not found**:
   Ensure Poppler is installed and added to your PATH.
    ```sh
    brew install poppler
    ```

2. **PDF to Image Conversion Error**:
   If you encounter errors related to `pdf2image`, make sure `poppler` is correctly installed and accessible in your
   PATH.
    ```sh
    export PATH=$PATH:/opt/homebrew/bin
    ```

## Project Structure

- **main.py**: Entry point of the application. Loads images, generates configurations, processes images, and saves the
  results.
- **image_pipeline.py**: Contains the core functions for processing images using different configurations.
- **utils.py**: Utility functions for creating directories and ranking images.
- **file_utils.py**: Functions for loading images from the `assets` folder and saving the plot as a PNG file.
- **edge_detection.py**: Contains the `EdgeDetection` class that handles the edge detection and rectangle drawing logic.
- **clustering.py**: Functions for clustering rectangles by size or distance.
- **image_processing.py**: Functions for various image processing techniques such as enhancing contrast, blurring,
  thresholding, and upscaling.

## Flow and Process

1. **Loading Images**:
    - Images and PDFs are loaded from the `assets` folder.
    - PDF files are converted to images.

2. **Generating Configurations**:
    - Various image processing steps (e.g., enhancing contrast, blurring, etc.) are combined into configurations.
    - Configurations determine the sequence of processing steps.

3. **Processing Images**:
    - Each image is processed using the generated configurations.
    - Edge detection and rectangle detection are performed.
    - Rectangles are clustered by size or distance.

4. **Visualization and Saving**:
    - Processed images with detected rectangles are plotted.
    - The results are saved as PNG files in the `outputs` folder.

5. **Ranking and Displaying**:
    - Images are ranked based on the number of detected rectangles.
    - The top-ranked images are displayed and saved.
