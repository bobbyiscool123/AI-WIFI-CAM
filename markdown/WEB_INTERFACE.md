# Web Interface Documentation

## Overview

The `web` folder contains all the files necessary for the AI WiFi CAM's web interface. This interface allows users to view the video stream, control the AI processing settings, and interact with the system through a browser. The web interface is served by the Python application running on the PC and can be accessed from any device on the same network.

## Purpose of the Web Folder

The web folder serves several critical functions in the AI WiFi CAM project:

1. **User Interface**: Provides a graphical interface for users to interact with the system
2. **Video Display**: Shows the processed video stream with AI annotations
3. **Control Panel**: Allows users to adjust AI settings and camera parameters
4. **Snapshot Management**: Enables capturing and downloading still images
5. **Status Monitoring**: Displays system status, FPS, and detection counts

## Folder Structure

```
web/
├── css/                        # Stylesheets
│   └── styles.css              # Main CSS file for styling the interface
├── img/                        # Image assets
│   ├── favicon.svg             # Browser tab icon (16x16)
│   ├── favicon-32.svg          # Larger browser tab icon (32x32)
│   ├── favicon.ico             # Fallback favicon for older browsers
│   ├── logo.svg                # Main logo for footer
│   ├── logo_header.svg         # Horizontal logo for header
│   └── placeholder.svg         # Placeholder image when video is not streaming
├── js/                         # JavaScript files
│   └── main.js                 # Main JavaScript for interface functionality
└── index.html                  # Main HTML file that structures the interface
```

## Key Components

### HTML Structure (index.html)

The `index.html` file defines the structure of the web interface, including:

- **Header**: Contains the logo and connection status indicator
- **Main Content**: 
  - Video display area
  - Settings panel for AI model selection and configuration
  - Information panel showing system statistics
- **Snapshots Section**: Grid display of captured images
- **Footer**: Contains copyright information and links
- **Modal Dialogs**: For viewing and downloading snapshots

### CSS Styling (styles.css)

The `styles.css` file provides styling for all UI elements, including:

- Responsive layout that works on different screen sizes
- Color schemes for both light and dark modes
- Animations and transitions for interactive elements
- Styling for video container, controls, and overlays
- Grid layouts for snapshots and settings panels

### JavaScript Functionality (main.js)

The `main.js` file implements the interactive functionality of the interface:

- **WebSocket Connections**: 
  - Connects to the video stream WebSocket
  - Connects to the control WebSocket for sending commands
- **UI Updates**:
  - Updates connection status indicators
  - Refreshes statistics and detection counts
  - Manages the snapshots grid
- **User Interactions**:
  - Handles button clicks and form submissions
  - Processes settings changes
  - Manages fullscreen mode and snapshot capture
  - Controls modal dialogs

### Image Assets

The `img` folder contains various image assets:

- **Favicons**: Browser tab icons in different formats
- **Logos**: Vector graphics for the application branding
- **Placeholder**: Displayed when the video stream is not available

## How the Web Interface Works

1. **Initialization**:
   - When a user accesses the web interface, the browser loads `index.html`
   - The page loads CSS styles and JavaScript code
   - JavaScript initializes and attempts to connect to the WebSocket server

2. **WebSocket Connections**:
   - Two WebSocket connections are established:
     - `/video` WebSocket for receiving the video stream
     - `/control` WebSocket for sending commands and receiving status updates

3. **Video Streaming**:
   - The server sends Base64-encoded JPEG frames over the video WebSocket
   - JavaScript decodes these frames and displays them in the video container
   - The stream is updated in real-time as new frames arrive

4. **User Interactions**:
   - When users adjust settings (e.g., AI model, confidence threshold), JavaScript sends commands over the control WebSocket
   - The server processes these commands and updates the AI processing accordingly
   - Status updates and statistics are sent back to the client and displayed in the interface

5. **Snapshot Functionality**:
   - Users can capture snapshots of the current frame
   - These are stored in the browser and displayed in the snapshots grid
   - Users can view snapshots in a modal dialog and download them

## Integration with Python Backend

The web interface communicates with the Python backend through WebSockets:

```
┌─────────────┐      WebSocket      ┌─────────────┐
│             │  (Video Stream)     │             │
│  Browser    │◄─────────────────────┤  Python    │
│  (Web       │                     │  Backend    │
│  Interface) │      WebSocket      │  (stream_   │
│             │  (Control Channel)  │  receiver.py)│
│             │◄────────────────────►│             │
└─────────────┘                     └─────────────┘
```

The Python backend serves the web interface files and handles WebSocket connections:

```python
# Set up the web server routes
async def setup_web_server():
    app = web.Application()

    # WebSocket routes
    app.router.add_get('/video', handle_web_socket_video)
    app.router.add_get('/control', handle_web_socket_control)

    # Static files (serves the web folder)
    app.router.add_static('/', Path(args.web_path), show_index=True)

    # Start the web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, args.host, args.web_port)
    await site.start()
```

## Customizing the Web Interface

### Changing the Appearance

To modify the appearance of the web interface:

1. Edit `styles.css` to change colors, sizes, and layouts
2. Replace logo files in the `img` folder with your own designs
3. Adjust the HTML structure in `index.html` as needed

### Adding New Features

To add new features to the web interface:

1. Add new HTML elements to `index.html`
2. Implement the functionality in `main.js`
3. Add corresponding server-side handlers in `stream_receiver.py`

### Supporting Mobile Devices

The web interface is already responsive and works on mobile devices, but you can enhance it by:

1. Testing on various screen sizes and adjusting CSS as needed
2. Adding touch-specific interactions for mobile users
3. Optimizing image sizes for faster loading on mobile networks

## Browser Compatibility

The web interface is compatible with modern browsers:

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 16+

For older browsers, you may need to:
- Use polyfills for modern JavaScript features
- Provide alternative image formats (PNG instead of SVG)
- Adjust CSS for better compatibility

## Conclusion

The web folder is a crucial component of the AI WiFi CAM system, providing an intuitive and responsive interface for users to interact with the system. By understanding its structure and functionality, you can effectively use, maintain, and customize the web interface to suit your specific needs.
