# Troubleshooting Guide for AI WiFi CAM

This guide addresses common issues you might encounter when setting up and running the AI WiFi CAM system, along with their solutions.

## ESP32-CAM Issues

### ESP32-CAM Fails to Connect to WiFi

**Symptoms:**
- Serial monitor shows "Connecting to WiFi..." but never connects
- ESP32-CAM keeps restarting while trying to connect

**Solutions:**
1. **Check WiFi Credentials**
   - Verify SSID and password in the Arduino sketch are correct (case-sensitive)
   - Ensure there are no special characters in the WiFi password that might need escaping

2. **WiFi Signal and Compatibility**
   - Ensure the ESP32-CAM is within good range of your WiFi router
   - Confirm your router is broadcasting on 2.4GHz band (ESP32 doesn't support 5GHz)
   - Try moving the ESP32-CAM closer to the router temporarily to test

3. **Router Issues**
   - Check if other devices can connect to the WiFi network
   - Try rebooting your router
   - Check if MAC address filtering is enabled on your router

4. **Code Verification**
   - Add more debug prints in your code to see where it's failing
   ```cpp
   Serial.print("Connecting to WiFi...");
   WiFi.begin(ssid, password);
   int attempts = 0;
   while (WiFi.status() != WL_CONNECTED && attempts < 20) {
     delay(500);
     Serial.print(".");
     attempts++;
   }
   if (WiFi.status() == WL_CONNECTED) {
     Serial.println("\nWiFi connected");
     Serial.println("IP address: ");
     Serial.println(WiFi.localIP());
   } else {
     Serial.println("\nWiFi connection failed. Status code: ");
     Serial.println(WiFi.status());
   }
   ```

### ESP32-CAM Connects to WiFi but Not to PC Server

**Symptoms:**
- Serial monitor shows "WiFi connected" but "Connection to server failed"
- ESP32-CAM keeps trying to connect to the server

**Solutions:**
1. **IP Address and Port Verification**
   - Verify the PC's IP address in the ESP32-CAM sketch matches the actual IP address
   - Confirm the port number in the ESP32-CAM sketch matches the port in the PC script
   - Check if the IP address of your PC has changed (use `ipconfig` on Windows or `ifconfig`/`ip addr` on Linux/macOS)

2. **Server Status**
   - Ensure the Python server script is running on the PC before the ESP32-CAM tries to connect
   - Check the terminal output of the server script for any error messages

3. **Firewall and Network Issues**
   - Check if your PC's firewall is blocking the connection on the specified port
   - Try temporarily disabling the firewall for testing
   - Ensure both devices are on the same network/subnet

4. **Test with Simple Tools**
   - Use a tool like Netcat to test if the port is open and accessible:
     ```
     # On Windows (with PowerShell)
     Test-NetConnection -ComputerName YOUR_PC_IP -Port YOUR_PORT
     
     # On Linux/macOS
     nc -zv YOUR_PC_IP YOUR_PORT
     ```

### Camera Initialization Failed / Brownout Detected

**Symptoms:**
- Serial monitor shows "Camera initialization failed" or "Brownout detected"
- ESP32-CAM keeps restarting

**Solutions:**
1. **Power Supply Issues**
   - Use a stable 5V power supply capable of delivering at least 1A
   - Try a different USB cable (some cables have high resistance)
   - If powering via FTDI, use an external 5V power supply instead
   - Add a large capacitor (470-1000μF) between VCC and GND

2. **Camera Hardware Issues**
   - Check if the camera ribbon cable is properly seated in the connector
   - Try carefully re-seating the ribbon cable
   - Inspect the ribbon cable for any damage
   - Try a different ESP32-CAM module if available

3. **Camera Configuration**
   - Try a lower resolution or JPEG quality setting in your code
   ```cpp
   camera_config_t config;
   config.frame_size = FRAMESIZE_VGA; // Try a lower resolution like FRAMESIZE_QVGA
   config.jpeg_quality = 12; // Higher number = lower quality (try 15-20)
   ```

### Sketch Upload Fails

**Symptoms:**
- Arduino IDE shows "Failed to connect to ESP32" or similar error
- Upload process times out

**Solutions:**
1. **Board and Port Selection**
   - Verify the correct board is selected in Arduino IDE (Tools > Board > ESP32 Arduino > AI Thinker ESP32-CAM)
   - Ensure the correct COM port is selected

2. **Flashing Mode**
   - Confirm ESP32-CAM is in flashing mode by connecting GPIO0 to GND
   - Press and release the RESET button while GPIO0 is connected to GND
   - Some boards may require holding the RESET button while uploading

3. **FTDI Connection**
   - Double-check the wiring between FTDI and ESP32-CAM:
     - FTDI TX → ESP32-CAM RX
     - FTDI RX → ESP32-CAM TX
     - FTDI GND → ESP32-CAM GND
     - FTDI VCC → ESP32-CAM 5V (if powering from FTDI)

4. **Driver Issues**
   - Ensure FTDI drivers are properly installed
   - Try a different USB port
   - On Windows, check Device Manager for any devices with warning symbols

## PC Script Issues

### Python Script Crashes on Startup

**Symptoms:**
- ImportError or ModuleNotFoundError when running the script
- "No module named 'opencv-python'" or similar errors

**Solutions:**
1. **Virtual Environment**
   - Ensure the virtual environment is activated:
     ```
     # Windows
     .\venv\Scripts\activate
     
     # Linux/macOS
     source venv/bin/activate
     ```
   - Verify you see `(venv)` at the beginning of your command prompt

2. **Dependencies Installation**
   - Reinstall dependencies:
     ```
     pip install -r requirements.txt
     ```
   - Check for any error messages during installation
   - Try installing problematic packages individually:
     ```
     pip install opencv-python
     pip install websockets
     pip install tensorflow  # or pytorch, depending on your AI model
     ```

3. **Python Version Compatibility**
   - Verify you're using a compatible Python version (3.7-3.10 recommended)
   - Check if any packages have specific Python version requirements

### Connection Errors in Python Script

**Symptoms:**
- "Could not open video stream" or "Connection refused" errors
- Script runs but doesn't receive any data

**Solutions:**
1. **Network Configuration**
   - Verify the server is listening on the correct IP address and port
   - Try using `0.0.0.0` as the listening address to accept connections from any network interface:
     ```python
     server = websockets.serve(handler, "0.0.0.0", 8888)
     ```

2. **Connection Sequence**
   - Ensure the Python script is running before the ESP32-CAM tries to connect
   - Add more debug prints to identify where the connection is failing

3. **Protocol Implementation**
   - Verify the WebSocket implementation is correct on both ends
   - Check for any version mismatches in the WebSocket libraries

### AI Model Loading Error

**Symptoms:**
- "Could not find model file" or similar errors
- "Failed to load model" errors

**Solutions:**
1. **File Path Issues**
   - Verify the model file path is correct
   - Use absolute paths instead of relative paths
   - Check file permissions

2. **Model File Integrity**
   - Re-download the model file if it might be corrupted
   - Verify the file size matches the expected size
   - Check if the model format is compatible with your AI library

3. **Library Compatibility**
   - Ensure you're using the correct version of TensorFlow/PyTorch/OpenCV for your model
   - Check if the model requires specific versions of libraries

## Performance Issues

### Video Stream is Laggy or Freezes

**Symptoms:**
- High latency between camera and display
- Frequent frame drops or freezes
- System becomes unresponsive

**Solutions:**
1. **Camera Settings**
   - Reduce the camera resolution in the ESP32-CAM code:
     ```cpp
     config.frame_size = FRAMESIZE_VGA;  // Try FRAMESIZE_QVGA or FRAMESIZE_CIF for lower resolution
     ```
   - Reduce JPEG quality to decrease data size:
     ```cpp
     config.jpeg_quality = 15;  // Higher number = lower quality (try 15-20)
     ```

2. **Network Optimization**
   - Ensure strong WiFi signal between ESP32-CAM and router
   - Reduce network congestion by disconnecting unnecessary devices
   - Consider using a dedicated WiFi network for the project

3. **PC Resource Usage**
   - Close unnecessary applications on the PC
   - Monitor CPU/GPU usage during operation
   - For AI processing, consider:
     - Using a lighter model
     - Processing fewer frames (e.g., every other frame)
     - Reducing the inference resolution

4. **Code Optimization**
   - Implement frame skipping if necessary:
     ```python
     # Process only every Nth frame
     if frame_count % 3 == 0:  # Process every 3rd frame
         # Run AI processing
     ```
   - Use threading to separate video receiving from AI processing

### Memory Leaks or Crashes During Extended Use

**Symptoms:**
- System becomes slower over time
- Eventually crashes after running for a while

**Solutions:**
1. **Memory Management**
   - Ensure proper cleanup of resources in your Python code
   - Explicitly release OpenCV frames when done:
     ```python
     # Properly release resources
     cv2.destroyAllWindows()
     ```

2. **ESP32 Stability**
   - Implement a watchdog timer on the ESP32-CAM:
     ```cpp
     #include <esp_task_wdt.h>
     
     void setup() {
       // ...
       esp_task_wdt_init(30, true); // 30 second timeout, panic on timeout
       esp_task_wdt_add(NULL);
       // ...
     }
     
     void loop() {
       // ...
       esp_task_wdt_reset();
       // ...
     }
     ```

3. **Monitoring and Debugging**
   - Add logging to track memory usage and performance
   - Implement periodic reconnection logic to recover from failures

## Still Having Issues?

If you've tried the solutions above and are still experiencing problems:

1. Check the project's GitHub Issues page for similar problems and solutions
2. Create a detailed issue report including:
   - Exact error messages
   - Hardware configuration
   - Software versions
   - Steps to reproduce the problem
   - What you've already tried

For urgent issues, you can also try the project's discussion forum or contact the maintainers directly.
