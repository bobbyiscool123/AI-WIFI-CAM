# Usage Guide for AI WiFi CAM

This guide explains how to use the AI WiFi CAM system after completing the installation steps in [INSTALL.md](INSTALL.md).

## Pre-run Checklist

Before starting the system, verify the following:

- [ ] **Network Configuration**: Ensure both the PC and ESP32-CAM are connected to the same WiFi network.

- [ ] **PC IP Address**: Verify that your PC's IP address hasn't changed since configuring the ESP32-CAM sketch.
  
  **To check your IP address:**
  
  **Windows:**
  ```
  ipconfig
  ```
  Look for the "IPv4 Address" under your WiFi adapter.
  
  **macOS/Linux:**
  ```
  ip addr
  ```
  or
  ```
  ifconfig
  ```
  Look for the "inet" address under your WiFi interface.
  
  **If your IP address has changed:**
  1. Update the `serverIP` variable in the ESP32-CAM sketch
  2. Re-flash the ESP32-CAM following the instructions in INSTALL.md

- [ ] **ESP32-CAM Power**: Ensure the ESP32-CAM is properly powered with a stable 5V supply.

## Running the System

### Step 1: Start the PC Server

1. Open a terminal/command prompt on your PC.

2. Navigate to the PC code directory:
   ```
   cd path/to/ai-wifi-cam/pc_code
   ```

3. Activate the Python virtual environment:
   
   **Windows:**
   ```
   .\venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```
   source venv/bin/activate
   ```
   You should see `(venv)` appear at the beginning of your command prompt.

4. Run the server script:
   ```
   python stream_receiver.py
   ```

   **Optional Command Line Arguments:**
   
   - `--port PORT`: Specify the WebSocket server port (default: 8888)
   - `--model MODEL`: Specify the AI model to use (default: "yolov4")
   - `--confidence CONF`: Set the detection confidence threshold (default: 0.5)
   - `--display`: Enable/disable display window (default: enabled)
   - `--save`: Save the processed video to a file (default: disabled)
   
   **Example with arguments:**
   ```
   python stream_receiver.py --port 8888 --model yolov4 --confidence 0.6 --save
   ```

5. You should see output similar to:
   ```
   AI WiFi CAM Server
   -----------------
   Model: YOLOv4
   Confidence Threshold: 0.6
   Server started on port 8888
   Waiting for connection...
   ```

### Step 2: Connect the ESP32-CAM

1. After the PC server is running, power on the ESP32-CAM or press its reset button if it's already powered.

2. The ESP32-CAM will:
   - Connect to the WiFi network
   - Establish a WebSocket connection with the PC server
   - Begin streaming video frames

3. On the PC terminal, you should see a message like:
   ```
   Client connected from 192.168.1.xxx
   Receiving video stream...
   ```

4. An OpenCV window titled "AI WiFi CAM" should appear, displaying the video stream with AI annotations.

### Step 3: Interact with the System

While the system is running, you can interact with it using the following keyboard controls:

- **q**: Quit the application
- **s**: Save a snapshot of the current frame
- **p**: Pause/resume the video stream
- **+**: Increase detection confidence threshold
- **-**: Decrease detection confidence threshold

## Stopping the System

To stop the system:

1. **Close the PC Application**:
   - Press the 'q' key while the OpenCV window is in focus
   - OR press Ctrl+C in the terminal where the Python script is running

2. **Power off the ESP32-CAM** (optional):
   - Disconnect the power supply
   - OR press the reset button to restart it

## Viewing Results

If you enabled the save option (`--save`), processed video will be saved to the `output` directory with a timestamp filename.

Snapshots taken during operation (by pressing 's') are saved to the `snapshots` directory.

## Troubleshooting

If you encounter issues while running the system, refer to [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common problems and solutions.

## Advanced Usage

### Changing AI Models

The system supports multiple AI models for different types of analysis:

1. **Object Detection (YOLOv4)** - Default
   ```
   python stream_receiver.py --model yolov4
   ```

2. **Pose Estimation (MediaPipe)**
   ```
   python stream_receiver.py --model mediapipe_pose
   ```

3. **Face Detection (MediaPipe)**
   ```
   python stream_receiver.py --model mediapipe_face
   ```

### Headless Operation

To run the system without displaying a video window (useful for servers or embedded systems):

```
python stream_receiver.py --no-display
```

### Recording Video

To save the processed video stream to a file:

```
python stream_receiver.py --save --output-path /path/to/save/video
```
