# AI WiFi CAM

## Overview
AI WiFi CAM is a real-time video streaming and AI analysis system that connects an ESP32-CAM to a PC over a local WiFi network. The system captures video from the ESP32-CAM, streams it wirelessly to a PC, where it's processed using AI algorithms for real-time analysis and displayed with annotations.

## Features
- **Real-time Video Streaming**: Transmits live video from ESP32-CAM to PC over WiFi
- **Wireless Communication**: Uses WebSockets protocol for efficient and reliable data transfer
- **AI-Powered Analysis**: Processes video frames with computer vision algorithms
- **Real-time Annotations**: Displays processed video with AI-generated annotations
- **Low Latency**: Optimized for minimal delay between capture and display
- **Multiple AI Models**: Support for object detection, pose estimation, and face detection

## System Architecture
```
┌─────────────┐     WiFi      ┌─────────────────────────────────────┐
│ ESP32-CAM   │ ─────────────▶│ PC                                  │
│             │               │                                     │
│ - Camera    │ WebSockets    │ - Python Script                     │
│ - WiFi      │ Protocol      │ - AI Processing                     │
│ - Arduino   │               │ - Display with Annotations          │
└─────────────┘               └─────────────────────────────────────┘
```

The ESP32-CAM captures video frames and sends them over WiFi using the WebSockets protocol. The PC receives these frames, processes them with AI algorithms for tasks like object detection, and displays the annotated video stream in real-time.

## Hardware Requirements
- ESP32-CAM module (AI Thinker or similar)
- FTDI programmer or USB-to-TTL converter (for programming the ESP32-CAM)
- PC with WiFi capability
- Stable WiFi network
- Power supply for ESP32-CAM (5V)

## Software Requirements
### ESP32-CAM
- Arduino IDE (1.8.x or newer)
- ESP32 Board support package
- Required libraries:
  - WiFi.h
  - WebSocketsServer
  - esp32cam

### PC
- Python 3.7 or newer
- Required Python packages (see `pc_code/requirements.txt`):
  - opencv-python
  - numpy
  - websockets
  - mediapipe
  - tensorflow/pytorch (depending on AI model used)

## Quick Start
1. Set up the ESP32-CAM with the Arduino sketch in `esp32cam_code/esp32cam_stream.ino`
2. Install Python dependencies with `pip install -r pc_code/requirements.txt`
3. Run the PC receiver script with `python pc_code/stream_receiver.py`
4. Power on the ESP32-CAM and watch the AI-processed video stream on your PC

For detailed instructions, see:
- [Installation Guide](docs/INSTALL.md)
- [Usage Guide](docs/USAGE.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

## Project Structure
```
AI-WIFI-CAM/
├── esp32cam_code/
│   └── esp32cam_stream.ino     # Arduino sketch for ESP32-CAM
├── pc_code/
│   ├── stream_receiver.py      # Python script for receiving video stream
│   ├── ai_processor.py         # AI processing module
│   └── requirements.txt        # Python dependencies
├── docs/
│   ├── INSTALL.md              # Installation guide
│   ├── USAGE.md                # Usage instructions
│   └── TROUBLESHOOTING.md      # Troubleshooting guide
├── models/                     # Directory for AI model files
└── README.md                   # This file
```

## Supported AI Models
- **YOLOv4**: Object detection (default)
- **MediaPipe Pose**: Human pose estimation
- **MediaPipe Face**: Face detection

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements
- ESP32 Community
- OpenCV Team
- TensorFlow/PyTorch Community
- MediaPipe Team
