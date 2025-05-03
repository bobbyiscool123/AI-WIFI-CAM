#!/usr/bin/env python3
"""
System Compatibility Check for AI WiFi CAM

This script checks if your system meets the requirements for running the AI WiFi CAM
Python application, including Python version, required packages, and hardware capabilities.
"""

import sys
import platform
import subprocess
import importlib.util
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    print(f"Python version: {platform.python_version()}")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print("✅ Python version is compatible")
    return True

def check_package(package_name):
    """Check if a Python package is installed and get its version."""
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            print(f"❌ {package_name} is not installed")
            return False
        
        # Try to get the version
        try:
            module = importlib.import_module(package_name)
            version = getattr(module, "__version__", "unknown")
            print(f"✅ {package_name} is installed (version: {version})")
        except:
            print(f"✅ {package_name} is installed (version unknown)")
        
        return True
    except ImportError:
        print(f"❌ {package_name} is not installed")
        return False

def check_opencv_with_gpu():
    """Check if OpenCV is built with GPU support."""
    try:
        import cv2
        print(f"OpenCV version: {cv2.__version__}")
        
        # Check for GPU support
        if hasattr(cv2, 'cuda') and cv2.cuda.getCudaEnabledDeviceCount() > 0:
            print("✅ OpenCV has GPU support and GPU is available")
            return True
        else:
            print("ℹ️ OpenCV is using CPU only (GPU support not detected)")
            return False
    except:
        print("❌ Failed to check OpenCV GPU support")
        return False

def check_tensorflow_gpu():
    """Check if TensorFlow can access GPU."""
    try:
        import tensorflow as tf
        print(f"TensorFlow version: {tf.__version__}")
        
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            print(f"✅ TensorFlow can access {len(gpus)} GPU(s)")
            for gpu in gpus:
                print(f"   - {gpu.name}")
            return True
        else:
            print("ℹ️ TensorFlow is using CPU only (no GPUs detected)")
            return False
    except ImportError:
        print("ℹ️ TensorFlow is not installed")
        return False
    except Exception as e:
        print(f"ℹ️ Error checking TensorFlow GPU: {e}")
        return False

def check_mediapipe():
    """Check if MediaPipe is properly installed."""
    try:
        import mediapipe as mp
        print(f"MediaPipe version: {mp.__version__}")
        
        # Try to initialize a simple solution to verify it works
        try:
            hands = mp.solutions.hands.Hands()
            print("✅ MediaPipe initialized successfully")
            return True
        except Exception as e:
            print(f"❌ MediaPipe initialization failed: {e}")
            return False
    except ImportError:
        print("❌ MediaPipe is not installed")
        return False

def check_websockets():
    """Check if websockets package is properly installed."""
    try:
        import websockets
        print(f"websockets version: {websockets.__version__}")
        print("✅ websockets package is installed")
        return True
    except ImportError:
        print("❌ websockets package is not installed")
        return False

def check_model_files():
    """Check if required model files exist."""
    models_dir = Path(__file__).parent.parent / "models"
    
    print(f"Checking for model files in {models_dir}")
    
    if not models_dir.exists():
        print(f"❌ Models directory not found: {models_dir}")
        return False
    
    # Check for YOLOv4 files
    yolo_files = ["yolov4.weights", "yolov4.cfg", "coco.names"]
    missing_files = []
    
    for file in yolo_files:
        file_path = models_dir / file
        if not file_path.exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing YOLOv4 files: {', '.join(missing_files)}")
        print("   Run pc_code/download_models.py to download them")
        return False
    else:
        print("✅ All YOLOv4 model files found")
        return True

def main():
    """Run all compatibility checks."""
    print("AI WiFi CAM - System Compatibility Check")
    print("=======================================")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Machine: {platform.machine()}")
    print("")
    
    # Check Python version
    python_ok = check_python_version()
    print("")
    
    # Check required packages
    print("Checking required packages:")
    opencv_ok = check_package("cv2")  # OpenCV
    numpy_ok = check_package("numpy")
    websockets_ok = check_websockets()
    print("")
    
    # Check GPU support
    print("Checking GPU support:")
    opencv_gpu = check_opencv_with_gpu()
    tf_gpu = check_tensorflow_gpu()
    print("")
    
    # Check MediaPipe
    print("Checking MediaPipe:")
    mediapipe_ok = check_mediapipe()
    print("")
    
    # Check model files
    print("Checking model files:")
    models_ok = check_model_files()
    print("")
    
    # Summary
    print("Summary:")
    all_required_ok = python_ok and opencv_ok and numpy_ok and websockets_ok
    
    if all_required_ok:
        print("✅ Your system meets all the basic requirements for AI WiFi CAM")
    else:
        print("❌ Your system is missing some required components")
    
    if not opencv_gpu and not tf_gpu:
        print("ℹ️ No GPU acceleration detected - the application will run slower")
    
    if not models_ok:
        print("ℹ️ Model files are missing - run pc_code/download_models.py to download them")
    
    print("")
    print("For detailed setup instructions, see docs/INSTALL.md")

if __name__ == "__main__":
    main()
