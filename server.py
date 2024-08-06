import os
import shutil
import uuid

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify, send_from_directory, url_for
from werkzeug.utils import secure_filename

from src.config_generator import generate_configs
from src.file_utils import load_images, save_result_images, save_result_shapes
from src.image_pipeline import process_image
from src.utils import create_clean_output_directory

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Ensure upload and processed folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

scheduler = BackgroundScheduler()


def allowed_file(filename: str):
    """Check if the file is an allowed type."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_directory(directory: str):
    """Remove all files in the specified directory."""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


def start_cleanup_task():
    """Start the background scheduler to periodically clean up directories."""
    scheduler.add_job(func=lambda: cleanup_directory(UPLOAD_FOLDER), trigger="interval", hours=24)
    scheduler.add_job(func=lambda: cleanup_directory(PROCESSED_FOLDER), trigger="interval", hours=24)
    scheduler.start()


@app.route('/process', methods=['POST'])
def process():
    """Endpoint to handle file upload and processing."""
    if 'file' not in request.files:
        return jsonify(error="No file part"), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify(error="No selected file"), 400

    create_clean_output_directory(UPLOAD_FOLDER)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Generate a unique identifier for this request
        unique_id = str(uuid.uuid4())
        processed_folder = os.path.join(app.config['PROCESSED_FOLDER'], unique_id)
        os.makedirs(processed_folder, exist_ok=True)

        # Process the file
        try:
            create_clean_output_directory(processed_folder)
            image_url, shapes_url = _do_process(processed_folder, unique_id)
            return jsonify(
                message="File processed successfully",
                image_url=image_url,
                shapes_url=shapes_url
            ), 200
        except Exception as e:
            shutil.rmtree(processed_folder)
            return jsonify(error=str(e)), 500

    return jsonify(error="File type not allowed"), 400


@app.route('/processed/<unique_id>/<filename>', methods=['GET'])
def download(unique_id: str, filename: str):
    """Endpoint to download a processed file."""
    folder_path = os.path.join(app.config['PROCESSED_FOLDER'], unique_id)
    return send_from_directory(directory=folder_path, path=filename)


def _do_process(processed_folder: str, unique_id: str):
    images_with_names = load_images(app.config['UPLOAD_FOLDER'], num_files=1)
    configs = generate_configs()

    if len(images_with_names) != 1:
        raise Exception("Image not loaded")

    filename, results = process_image(images_with_names[0], configs)
    json_filename = f"{filename}.json"
    png_filename = f"{filename}.png"
    save_result_shapes(results[0].rects + results[0].lines + results[0].nodes,
                       target_file_name=os.path.join(processed_folder, json_filename))
    save_result_images(results, max_images=len(results),
                       target_file_name=os.path.join(processed_folder, png_filename))
    # Construct the download URL
    image_url = url_for('download', unique_id=unique_id, filename=png_filename, _external=True)
    shapes_url = url_for('download', unique_id=unique_id, filename=json_filename, _external=True)
    return image_url, shapes_url


@app.teardown_appcontext
def shutdown(exception=None):
    """Shutdown the scheduler."""
    if scheduler.running:
        scheduler.shutdown()


if __name__ == '__main__':
    start_cleanup_task()
    try:
        app.run(debug=True)
    finally:
        shutdown()
