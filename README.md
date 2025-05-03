# AI WiFi CAM

<div align="center">
  <img src="docs/images/logo.svg" alt="AI WiFi CAM Logo" width="200"/>
  <h3>Real-time AI Video Processing with ESP32-CAM</h3>
</div>

## Overview

AI WiFi CAM is an advanced real-time video processing system that integrates an ESP32-CAM module with powerful AI algorithms running on a PC. The system establishes a wireless connection over a local WiFi network, enabling seamless streaming of video from the ESP32-CAM to a computer where sophisticated computer vision algorithms analyze the content in real-time.

## Key Features

- **High-Performance Video Streaming**: Transmits high-quality video from ESP32-CAM to PC over WiFi
- **Efficient Wireless Communication**: Implements WebSockets protocol for reliable, low-overhead data transfer
- **Advanced AI Processing**: Leverages state-of-the-art computer vision algorithms for real-time analysis
- **Intelligent Visual Annotations**: Renders processed video with precise AI-generated annotations
- **Optimized Performance**: Engineered for minimal latency between capture and display
- **Versatile AI Model Support**: Compatible with multiple AI frameworks including object detection, pose estimation, and facial recognition

## System Architecture

<div align="center">
  <img src="docs/images/system_architecture.svg" alt="System Architecture" width="700"/>
</div>

The ESP32-CAM module captures high-resolution video frames and transmits them wirelessly to a PC using the WebSockets protocol. The PC-side application processes these frames through specialized AI algorithms for various computer vision tasks and displays the enhanced video stream with real-time annotations through an intuitive web interface.

## Hardware Requirements

- **ESP32-CAM Module**: AI Thinker ESP32-CAM or compatible module with OV2640 camera
- **Programming Interface**: FTDI programmer or USB-to-TTL converter (3.3V logic level)
- **Computing Platform**: PC or laptop with WiFi connectivity
- **Network Infrastructure**: Stable WiFi network with sufficient bandwidth
- **Power Source**: Regulated 5V power supply (minimum 500mA capacity)

## Software Requirements

### ESP32-CAM Firmware
- **Development Environment**: Arduino IDE (1.8.x or newer)
- **Board Support**: ESP32 Board support package (2.0.0 or newer)
- **Required Libraries**:
  - WiFi.h (Core ESP32 library)
  - WebSocketsServer (Links2004 WebSockets library)
  - esp32cam (ESP32 Camera Driver)

### PC Application
- **Runtime Environment**: Python 3.7+ with pip package manager
- **Core Dependencies** (automatically installed via requirements.txt):
  - opencv-python: Computer vision operations
  - numpy: Numerical processing
  - websockets: WebSocket client implementation
  - mediapipe: Google's ML solutions for pose/face detection
  - tensorflow/pytorch: Deep learning frameworks for AI models

## Quick Start Guide

1. **Configure ESP32-CAM**:
   ```bash
   # Flash the ESP32-CAM with the provided firmware
   arduino-cli compile --fqbn esp32:esp32:esp32cam esp32cam_code/esp32cam_stream.ino
   arduino-cli upload -p [PORT] --fqbn esp32:esp32:esp32cam esp32cam_code/esp32cam_stream.ino
   ```

2. **Set Up PC Environment**:
   ```bash
   # Install required Python dependencies
   pip install -r pc_code/requirements.txt
   ```

3. **Launch the Application**:
   ```bash
   # Start the PC receiver application
   python pc_code/stream_receiver.py
   ```

4. **Connect Hardware**: Power on the ESP32-CAM and wait for the connection to establish

For comprehensive documentation, please refer to:
- [📚 Installation Guide](docs/INSTALL.md) - Detailed setup instructions
- [🔍 Usage Guide](docs/USAGE.md) - Operation and configuration options
- [⚠️ Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Solutions to common issues

## Project Structure

```
AI-WIFI-CAM/
├── esp32cam_code/                  # ESP32-CAM firmware
│   └── esp32cam_stream.ino         # Main Arduino sketch for video streaming
├── pc_code/                        # PC-side application
│   ├── stream_receiver.py          # WebSocket client and video processing
│   ├── ai_processor.py             # AI model integration and inference
│   └── requirements.txt            # Python dependency specifications
├── docs/                           # Documentation
│   ├── images/                     # Diagrams and screenshots
│   │   ├── system_architecture.svg # System architecture diagram
│   │   ├── esp32cam_wiring.svg     # Hardware connection diagram
│   │   └── web_interface.svg       # UI reference
│   ├── INSTALL.md                  # Comprehensive installation guide
│   ├── USAGE.md                    # Detailed usage instructions
│   └── TROUBLESHOOTING.md          # Problem-solving guide
├── models/                         # Pre-trained AI models (gitignored)
│   ├── yolov4/                     # YOLOv4 model files
│   └── mediapipe/                  # MediaPipe model files
├── web/                            # Web interface assets
│   ├── css/                        # Stylesheets
│   ├── js/                         # JavaScript files
│   └── index.html                  # Main web interface
├── LICENSE                         # MIT License
└── README.md                       # Project overview
```

## Supported AI Models

| Model | Type | Description | Performance |
|-------|------|-------------|------------|
| **YOLOv4** | Object Detection | Identifies and localizes 80+ object categories with bounding boxes | 30-45 FPS |
| **MediaPipe Pose** | Pose Estimation | Tracks 33 body landmarks for human pose analysis | 25-40 FPS |
| **MediaPipe Face** | Face Detection | Detects and analyzes facial features with 468 landmarks | 20-35 FPS |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions to enhance AI WiFi CAM! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgements

- [ESP32 Development Community](https://github.com/espressif/arduino-esp32)
- [OpenCV Team](https://opencv.org/) for their computer vision library
- [TensorFlow](https://www.tensorflow.org/) and [PyTorch](https://pytorch.org/) communities
- [MediaPipe Team](https://mediapipe.dev/) for their ML solutions
- All contributors who have helped shape this project
