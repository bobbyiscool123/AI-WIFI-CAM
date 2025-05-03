# Installation Guide for AI WiFi CAM

This guide provides detailed instructions for setting up the AI WiFi CAM project, which streams video from an ESP32-CAM to a PC over WiFi for AI-based processing.

## Prerequisites

### Hardware Requirements
- [ ] ESP32-CAM module (AI Thinker or similar)
- [ ] FTDI programmer or USB-to-TTL converter
- [ ] Jumper wires
- [ ] Micro USB cable
- [ ] PC with WiFi capability
- [ ] Stable WiFi network
- [ ] 5V power supply for ESP32-CAM (can be USB)

### Software Requirements
- [ ] Git (for cloning the repository)
- [ ] Python 3.7 or newer
- [ ] Arduino IDE (1.8.x or newer)
- [ ] Web browser (for viewing results if web interface is used)

## PC Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-wifi-cam.git
cd ai-wifi-cam
```

### 2. Set Up Python Environment

#### Create and Activate Virtual Environment
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Install Dependencies
```bash
cd pc_code
pip install -r requirements.txt
```

### 3. Download AI Model (if not included in repository)

The project uses a pre-trained AI model for video analysis. If not included in the repository, download it using the following steps:

#### For YOLOv4 (Object Detection):
```bash
# Create a models directory if it doesn't exist
mkdir -p models
cd models

# Download YOLOv4 weights and configuration
wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights
wget https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg
wget https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names

cd ..
```

#### For MediaPipe (Pose Estimation):
MediaPipe models are downloaded automatically when you install the mediapipe package through pip.

## ESP32-CAM Setup

### 1. Configure Arduino IDE

#### Install ESP32 Board Support
1. Open Arduino IDE
2. Go to **File > Preferences**
3. Add the following URL to the "Additional Boards Manager URLs" field:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Click "OK"
5. Go to **Tools > Board > Boards Manager**
6. Search for "ESP32" and install "ESP32 by Espressif Systems"

#### Install Required Libraries
Go to **Tools > Manage Libraries** and install the following libraries:
- WiFi (included with ESP32 board package)
- esp32cam
- WebSocketsServer (by Markus Sattler)

### 2. Configure the ESP32-CAM Sketch

1. Open the Arduino sketch:
   ```
   File > Open > [navigate to]/ai-wifi-cam/esp32cam_code/esp32cam_stream.ino
   ```

2. Modify the WiFi and server settings in the sketch:
   ```cpp
   // WiFi credentials
   const char* ssid = "YOUR_WIFI_SSID";      // Replace with your WiFi network name
   const char* password = "YOUR_WIFI_PASSWORD";  // Replace with your WiFi password
   ```

### 3. Connect and Flash the ESP32-CAM

#### Wiring Diagram for FTDI Programmer
Connect the ESP32-CAM to the FTDI programmer as follows:

| ESP32-CAM | FTDI Programmer |
|-----------|-----------------|
| 5V        | VCC (5V)        |
| GND       | GND             |
| U0R (TX)  | RX              |
| U0T (RX)  | TX              |
| GPIO0     | GND (for flashing mode) |

**Important:** Connect GPIO0 to GND only during flashing. This puts the ESP32-CAM in download mode.

#### Upload the Sketch
1. Select the correct board in Arduino IDE:
   - Go to **Tools > Board > ESP32 Arduino > AI Thinker ESP32-CAM**
   
2. Select the correct port:
   - Go to **Tools > Port** and select the COM port connected to your FTDI programmer

3. Put the ESP32-CAM in flashing mode:
   - Connect GPIO0 to GND using a jumper wire
   - Press the reset button on the ESP32-CAM

4. Click the Upload button in Arduino IDE

5. After successful upload:
   - Disconnect GPIO0 from GND
   - Press the reset button again to start the program

### 4. Verify ESP32-CAM Operation

After uploading, the ESP32-CAM will:
1. Connect to the specified WiFi network
2. Establish a WebSocket connection to the PC
3. Begin streaming video

You can monitor the ESP32-CAM's status through the Arduino IDE Serial Monitor (115200 baud rate). Successful operation will show messages like:
- "WiFi connected"
- "Camera initialized"
- "WebSocket server started"

## Troubleshooting

If you encounter issues during installation, please refer to the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) file.

## Next Steps

Once installation is complete, refer to [USAGE.md](USAGE.md) for instructions on how to use the system.
