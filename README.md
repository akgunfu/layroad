
# Image-Based Layout Modeling and Pathfinding

## Overview

This project aims to convert real-life maps, layouts, or floor plans into computer-understandable models for various applications, such as shortest path finding. A key application is to use scaled maps of warehouse interiors to model warehouse shelves and optimize navigation for store personnel.

## Features

- **Image Processing**: Enhance contrast, apply Gaussian blur, adaptive thresholding, and upscaling.
- **Rectangle Detection**: Detect and filter rectangles representing shelves or obstacles.
- **Clustering**: Cluster detected rectangles by size or distance using KMeans.
- **Edge Connection**: Create connection lines between non-intersecting rectangles.

## Installation

### Prerequisites

- Python 3.7 or higher
- `pip` (Python package installer)

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/akgunfu/layroad.git
   cd layroad
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Additional Dependencies

Some dependencies may require additional system-level installations:
- `pdf2image` requires `poppler`:
  ```bash
  brew install poppler
  ```

## Usage

### Command-Line Interface

The main script, `main.py`, can be run from the command line to process images:

```bash
python main.py -i <input_directory> -o <output_directory> -m <max_images> -f <file_path>
```

#### Arguments

| Argument | Description | Default |
| --- | --- | --- |
| `-i, --input_dir` | Directory containing input images | `assets` |
| `-o, --output_dir` | Directory to save output images and shapes | `outputs` |
| `-m, --max_images` | Maximum number of images to process | `3` |
| `-f, --file_path` | Path to the input image file | `None` |

### Example

To process images from the `assets` directory and save the results to the `outputs` directory:

```bash
python main.py -i assets -o outputs -m 3
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**:
    - Ensure all required Python packages are installed. Run `pip install -r requirements.txt`.
    - For system-level dependencies like `poppler`, ensure they are installed on your system with `brew install poppler`.

2. **File Not Found**:
    - Ensure the input directory or file path specified exists and contains the correct images.

3. **Permission Errors**:
    - Ensure you have the necessary permissions to read from the input directory and write to the output directory.

4. **Invalid Image Formats**:
    - Ensure the images are in supported formats (PNG, JPG, JPEG, PDF).

### Sample Errors and Solutions

1. **Error: `ModuleNotFoundError: No module named 'cv2'`**
    - Solution: Open your terminal and run `pip install opencv-python`.

2. **Error: `OSError: poppler not found`**
    - Solution: Install `poppler` on your system:
      ```bash
      brew install poppler
      ```

3. **Error: `FileNotFoundError: Image not found`**
    - Solution: Ensure the image file paths are correct and the files exist in the specified directory.
