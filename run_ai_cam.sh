#!/bin/bash

echo "AI WiFi CAM - Startup Script"
echo "=========================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python not found! Please install Python 3.7 or newer."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Check if requirements are installed
if [ ! -d "venv/lib/python*/site-packages/cv2" ]; then
    echo "Installing required packages..."
    pip install -r pc_code/requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install required packages."
        exit 1
    fi
fi

# Check if model files exist
if [ ! -f "models/yolov4.weights" ]; then
    echo "Downloading model files..."
    python pc_code/download_models.py
    if [ $? -ne 0 ]; then
        echo "Failed to download model files."
        exit 1
    fi
fi

# Run the system check
echo "Running system compatibility check..."
python pc_code/check_system.py
if [ $? -ne 0 ]; then
    echo "System check failed. Please check the output above."
    exit 1
fi

echo
echo "Starting AI WiFi CAM..."
echo "Press Ctrl+C to stop the server."
echo

# Run the main script
python pc_code/stream_receiver.py "$@"

echo
echo "AI WiFi CAM has stopped."
