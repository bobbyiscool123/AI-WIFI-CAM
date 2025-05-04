# ESP32-CAM Stream Documentation

## Overview

The ESP32-CAM Stream component is a critical part of the AI WiFi CAM system that handles video capture and transmission from the ESP32-CAM hardware to the PC for AI processing. This document provides a detailed explanation of how the ESP32-CAM streaming functionality works, its configuration options, and implementation details.

## Hardware Requirements

- **ESP32-CAM Module**: AI Thinker ESP32-CAM or compatible module with OV2640 camera
- **Programming Interface**: FTDI programmer or USB-to-TTL converter (3.3V logic level)
- **Power Source**: Regulated 5V power supply (minimum 500mA capacity)

## Software Requirements

- **Arduino IDE**: Version 1.8.x or newer
- **ESP32 Board Support Package**: Version 2.0.0 or newer
- **Required Libraries**:
  - WiFi.h (Core ESP32 library)
  - WebSocketsServer (Links2004 WebSockets library)
  - esp_camera.h (ESP32 Camera Driver)
  - esp_timer.h (ESP32 Timer functions)
  - img_converters.h (Image conversion utilities)

## How It Works

The ESP32-CAM Stream component operates through the following process:

1. **Initialization**:
   - The ESP32-CAM initializes the camera hardware with specific pin configurations
   - Connects to the specified WiFi network
   - Starts a WebSocket server on port 8888

2. **Video Capture**:
   - Continuously captures frames from the camera
   - Compresses them as JPEG images
   - Sends them over WebSockets to connected clients

3. **Communication Protocol**:
   - Uses WebSockets for low-latency, bidirectional communication
   - Sends binary data (JPEG frames) to clients
   - Receives text commands from clients (if implemented)

## Code Structure

The ESP32-CAM Stream code (`esp32cam_stream.ino`) is organized into several key functions:

### Main Functions

- **`setup()`**: Initializes the camera, connects to WiFi, and starts the WebSocket server
- **`loop()`**: Main program loop that handles WebSocket connections and sends camera frames
- **`initCamera()`**: Configures the camera hardware with appropriate settings
- **`webSocketEvent()`**: Handles WebSocket events (connections, disconnections, messages)
- **`sendCameraFrame()`**: Captures a frame from the camera and sends it over WebSocket

### Camera Configuration

The camera is configured with the following pin assignments (for AI Thinker ESP32-CAM):

```cpp
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22
```

### Camera Settings

The camera is initialized with these settings:

- **Frame Size**: VGA (640x480) if PSRAM is available, QVGA (320x240) otherwise
- **JPEG Quality**: 10 (0-63 scale, lower is higher quality) with PSRAM, 12 without PSRAM
- **Frame Buffer Count**: 2 with PSRAM, 1 without PSRAM

Additional camera parameters that can be adjusted:

- Brightness (-2 to 2)
- Contrast (-2 to 2)
- Saturation (-2 to 2)
- Special effects (0 = none, 1 = negative, 2 = grayscale, etc.)
- White balance (enabled/disabled)
- AWB gain (enabled/disabled)
- WB mode (0-4: auto, sunny, cloudy, office, home)
- Exposure control (enabled/disabled)
- Gain control (enabled/disabled)
- Horizontal/vertical flip (enabled/disabled)

## Configuration

To use the ESP32-CAM Stream component, you need to modify the following parameters in the code:

```cpp
// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";      // Replace with your WiFi network name
const char* password = "YOUR_WIFI_PASSWORD";  // Replace with your WiFi password
```

You can also adjust the frame rate by modifying the delay in the main loop:

```cpp
// In the loop() function
delay(50);  // Adjust this value to change frame rate (higher value = lower frame rate)
```

## Performance Considerations

- **Frame Rate**: The achievable frame rate depends on several factors:
  - WiFi signal strength and network congestion
  - Camera resolution (lower resolutions achieve higher frame rates)
  - JPEG compression quality (lower quality achieves higher frame rates)
  - Processing load on the ESP32-CAM

- **Typical Performance**:
  - VGA (640x480): 15-25 FPS with good WiFi conditions
  - QVGA (320x240): 25-40 FPS with good WiFi conditions

- **Power Consumption**:
  - The ESP32-CAM consumes approximately 180-250mA during active streaming
  - Ensure your power supply can provide at least 500mA for stable operation

## Troubleshooting

### Common Issues

1. **Camera Initialization Failure**:
   - Check camera module connections
   - Ensure adequate power supply (5V, 500mA minimum)
   - Try resetting the ESP32-CAM

2. **WiFi Connection Issues**:
   - Verify WiFi credentials are correct
   - Ensure the ESP32-CAM is within range of the WiFi router
   - Check if the WiFi network is 2.4GHz (ESP32-CAM doesn't support 5GHz)

3. **Low Frame Rate or High Latency**:
   - Reduce camera resolution or JPEG quality
   - Improve WiFi signal strength
   - Reduce the delay in the main loop
   - Check for interference from other devices

4. **Brownout Resets**:
   - Use a stable, high-quality power supply
   - Add a large capacitor (470-1000μF) between VCC and GND
   - The code already disables brownout detection, but this is a temporary solution

## Integration with PC Application

The ESP32-CAM Stream component integrates with the PC application through WebSockets:

1. The ESP32-CAM creates a WebSocket server on port 8888
2. The PC application connects to this server as a client
3. The ESP32-CAM sends binary WebSocket messages containing JPEG frames
4. The PC application decodes these frames and processes them with AI algorithms

## Advanced Customization

### Implementing Bidirectional Communication

The current implementation primarily sends video frames from the ESP32-CAM to the PC. You can extend it to receive commands from the PC by enhancing the `webSocketEvent()` function:

```cpp
case WStype_TEXT:
  // Handle text messages from client
  String command = String((char*)payload);
  
  if (command == "resolution:high") {
    // Change to high resolution
    sensor_t * s = esp_camera_sensor_get();
    s->set_framesize(s, FRAMESIZE_VGA);
  } 
  else if (command == "resolution:low") {
    // Change to low resolution
    sensor_t * s = esp_camera_sensor_get();
    s->set_framesize(s, FRAMESIZE_QVGA);
  }
  // Add more commands as needed
  break;
```

### Adding Status Reporting

You can implement periodic status reporting to inform the PC application about the ESP32-CAM's state:

```cpp
unsigned long lastStatusTime = 0;
const unsigned long statusInterval = 5000; // 5 seconds

void loop() {
  webSocket.loop();
  
  // If client is connected, send camera frames
  if (clientConnected) {
    sendCameraFrame();
    delay(50);
  }
  
  // Send status update every 5 seconds
  unsigned long currentTime = millis();
  if (currentTime - lastStatusTime > statusInterval) {
    lastStatusTime = currentTime;
    sendStatusUpdate();
  }
}

void sendStatusUpdate() {
  if (clientConnected) {
    String status = "{\"type\":\"status\",\"uptime\":";
    status += millis() / 1000;
    status += ",\"heap\":";
    status += ESP.getFreeHeap();
    status += ",\"rssi\":";
    status += WiFi.RSSI();
    status += "}";
    webSocket.sendTXT(0, status);
  }
}
```

## Conclusion

The ESP32-CAM Stream component provides a reliable and efficient way to capture video from the ESP32-CAM and transmit it to a PC for AI processing. By understanding its operation and configuration options, you can optimize it for your specific use case and integrate it effectively with the rest of the AI WiFi CAM system.
