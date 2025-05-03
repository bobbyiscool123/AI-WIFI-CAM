#!/usr/bin/env python3
"""
Download script for AI models used in the AI WiFi CAM project.

This script downloads the necessary model files for YOLOv4 object detection.
MediaPipe models are downloaded automatically when installing the mediapipe package.
"""

import os
import sys
import urllib.request
import shutil
from pathlib import Path

# Define model URLs and file paths
MODELS_DIR = Path(__file__).parent.parent / "models"
YOLO_FILES = {
    "yolov4.weights": "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights",
    "yolov4.cfg": "https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg",
    "coco.names": "https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names"
}

def download_file(url, destination):
    """Download a file from a URL to a destination path."""
    print(f"Downloading {url} to {destination}...")
    
    # Create a progress bar for large files
    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(int(downloaded * 100 / total_size), 100)
        sys.stdout.write(f"\rProgress: {percent}% [{downloaded} / {total_size} bytes]")
        sys.stdout.flush()
    
    try:
        urllib.request.urlretrieve(url, destination, reporthook=report_progress)
        print(f"\nDownloaded {destination}")
        return True
    except Exception as e:
        print(f"\nError downloading {url}: {e}")
        return False

def main():
    """Main function to download model files."""
    print("AI WiFi CAM - Model Downloader")
    print("==============================")
    
    # Create models directory if it doesn't exist
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Download YOLOv4 files
    print("\nDownloading YOLOv4 model files...")
    success = True
    for filename, url in YOLO_FILES.items():
        destination = MODELS_DIR / filename
        if destination.exists():
            print(f"{filename} already exists. Skipping download.")
        else:
            if not download_file(url, destination):
                success = False
    
    if success:
        print("\nAll model files downloaded successfully!")
        print(f"Files saved to: {MODELS_DIR}")
    else:
        print("\nSome files could not be downloaded. Please check the errors above.")

if __name__ == "__main__":
    main()
