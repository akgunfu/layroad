#!/bin/bash

# Create and activate virtual environment
if command -v python3 &>/dev/null; then
    python3 -m venv venv
    source venv/bin/activate
elif command -v python &>/dev/null; then
    python -m venv venv
    source venv/bin/activate
else
    echo "Python is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Install required dependencies
pip install -r requirements.txt

# Install poppler for pdf2image on macOS
brew install poppler

echo "Installation completed successfully."
echo ""
echo "To use the application from the command line interface (CLI):"
echo "  python main.py -i <input_directory> -o <output_directory> -m <max_images> -f <file_path>"
echo ""
echo "Example:"
echo "  python main.py -i assets -o outputs -m 3"
echo ""
echo "To start the server and use the application via the web interface:"
echo "  python server.py"
echo ""
echo "Then, upload a file to the server using curl or Postman:"
echo "  curl -F \"file=@/path/to/your/file.pdf\" http://127.0.0.1:5000/process"