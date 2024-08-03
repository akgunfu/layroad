import os
import shutil

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
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


def allowed_file(filename):
    """Check if the file is an allowed type."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_directory(directory):
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

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the file
        try:
            create_clean_output_directory(app.config['PROCESSED_FOLDER'])
            images_with_names = load_images(app.config['UPLOAD_FOLDER'], num_files=1)
            configs = generate_configs()
            for image_with_name in images_with_names:
                filename, results = process_image(image_with_name, configs)
                save_result_shapes(results[0].rects + results[0].lines,
                                   target_file_name=f"{app.config['PROCESSED_FOLDER']}/{filename}.json")
                save_result_images(results, max_images=len(results),
                                   target_file_name=f"{app.config['PROCESSED_FOLDER']}/{filename}.png")
            return jsonify(message="File processed successfully", processed_file=f"{filename}.png",
                           shapes_file=f"{filename}.json"), 200
        except Exception as e:
            return jsonify(error=str(e)), 500

    return jsonify(error="File type not allowed"), 400


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
