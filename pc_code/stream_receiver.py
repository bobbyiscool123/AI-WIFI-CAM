#!/usr/bin/env python3
"""
ESP32-CAM WebSocket Video Stream Receiver with AI Processing and Web Interface

This script receives video frames from an ESP32-CAM over WebSockets,
processes them with AI for object detection, and displays the results.
It also provides a web interface for viewing the stream and controlling the system.

Requirements:
- Python 3.7+
- OpenCV
- NumPy
- websockets
- asyncio
- aiohttp (for web server)
- tensorflow/pytorch (depending on AI model used)
"""

import asyncio
import websockets
import cv2
import numpy as np
import argparse
import time
import os
import json
import base64
import logging
from datetime import datetime
from pathlib import Path
from ai_processor import AIProcessor

# For web server
import aiohttp
from aiohttp import web
from aiohttp.web_runner import GracefulExit

# Parse command line arguments
parser = argparse.ArgumentParser(description='ESP32-CAM WebSocket Video Stream Receiver with AI Processing and Web Interface')
parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to listen on')
parser.add_argument('--port', type=int, default=8888, help='Port to listen on')
parser.add_argument('--web-port', type=int, default=8080, help='Web server port')
parser.add_argument('--model', type=str, default='yolov4', choices=['yolov4', 'mediapipe_pose', 'mediapipe_face'],
                    help='AI model to use for processing')
parser.add_argument('--confidence', type=float, default=0.5, help='Confidence threshold for detections')
parser.add_argument('--display', action='store_true', default=True, help='Display video stream')
parser.add_argument('--no-display', dest='display', action='store_false', help='Do not display video stream')
parser.add_argument('--save', action='store_true', help='Save processed video to file')
parser.add_argument('--output-path', type=str, default='output', help='Path to save output video')
parser.add_argument('--web', action='store_true', default=True, help='Enable web interface')
parser.add_argument('--no-web', dest='web', action='store_false', help='Disable web interface')
parser.add_argument('--web-path', type=str, default='web', help='Path to web interface files')
args = parser.parse_args()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create output directory if saving video
if args.save:
    os.makedirs(args.output_path, exist_ok=True)
    output_filename = os.path.join(args.output_path,
                                  f'ai_cam_{datetime.now().strftime("%Y%m%d_%H%M%S")}.avi')
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = None  # Will be initialized after receiving first frame

# Create snapshots directory
os.makedirs('snapshots', exist_ok=True)

# Initialize AI processor
ai_processor = AIProcessor(model_name=args.model, confidence_threshold=args.confidence)

# Global variables
frame_count = 0
fps = 0
fps_time = time.time()
paused = False
last_frame = None
processed_frame = None
clients = set()
web_clients = set()
detection_count = 0
settings = {
    'ai_model': args.model,
    'confidence_threshold': args.confidence,
    'display_fps': True
}

# Create a lock for thread safety
frame_lock = asyncio.Lock()

async def process_frames(websocket, path):
    """Process incoming WebSocket frames from ESP32-CAM."""
    global frame_count, fps, fps_time, paused, last_frame, processed_frame, out, detection_count

    logging.info(f"ESP32-CAM connected from {websocket.remote_address}")

    try:
        async for message in websocket:
            if paused:
                continue

            # Convert binary message to numpy array
            frame_data = np.frombuffer(message, dtype=np.uint8)

            # Decode JPEG image
            frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
            if frame is None:
                logging.warning("Failed to decode image")
                continue

            # Store the current frame
            async with frame_lock:
                last_frame = frame.copy()

            # Process frame with AI
            processed = ai_processor.process_frame(frame)

            # Get detection count
            if hasattr(ai_processor, 'last_detection_count'):
                detection_count = ai_processor.last_detection_count

            # Calculate FPS
            frame_count += 1
            if time.time() - fps_time >= 1.0:
                fps = frame_count
                frame_count = 0
                fps_time = time.time()

            # Add FPS text to frame if enabled
            if settings['display_fps']:
                cv2.putText(processed, f"FPS: {fps}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Store the processed frame
            async with frame_lock:
                processed_frame = processed.copy()

            # Initialize video writer if saving and not yet initialized
            if args.save and out is None:
                height, width = processed_frame.shape[:2]
                out = cv2.VideoWriter(output_filename, fourcc, 20.0, (width, height))

            # Save frame to video if enabled
            if args.save:
                out.write(processed_frame)

            # Display the frame if enabled
            if args.display:
                cv2.imshow('AI WiFi CAM', processed_frame)
                key = cv2.waitKey(1) & 0xFF

                # Handle key presses
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Save snapshot
                    snapshot_path = os.path.join('snapshots',
                                               f'snapshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg')
                    cv2.imwrite(snapshot_path, processed_frame)
                    logging.info(f"Snapshot saved to {snapshot_path}")
                elif key == ord('p'):
                    # Toggle pause
                    paused = not paused
                elif key == ord('+') or key == ord('='):
                    # Increase confidence threshold
                    ai_processor.confidence_threshold = min(ai_processor.confidence_threshold + 0.05, 1.0)
                    settings['confidence_threshold'] = ai_processor.confidence_threshold
                    logging.info(f"Confidence threshold: {ai_processor.confidence_threshold:.2f}")
                elif key == ord('-'):
                    # Decrease confidence threshold
                    ai_processor.confidence_threshold = max(ai_processor.confidence_threshold - 0.05, 0.05)
                    settings['confidence_threshold'] = ai_processor.confidence_threshold
                    logging.info(f"Confidence threshold: {ai_processor.confidence_threshold:.2f}")

            # Send the frame to all connected web clients
            if web_clients and processed_frame is not None:
                await broadcast_frame()

    except websockets.exceptions.ConnectionClosed:
        logging.info("ESP32-CAM disconnected")
    except Exception as e:
        logging.error(f"Error processing frames: {e}")
    finally:
        if args.save and out is not None:
            out.release()
        if args.display:
            cv2.destroyAllWindows()

async def broadcast_frame():
    """Broadcast the current frame to all connected web clients."""
    if not web_clients or processed_frame is None:
        return

    try:
        # Convert the frame to JPEG
        _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])

        # Convert to bytes
        frame_bytes = buffer.tobytes()

        # Send to all connected clients
        disconnected_clients = set()
        for client in web_clients:
            try:
                await client.send(frame_bytes)
            except Exception:
                disconnected_clients.add(client)

        # Remove disconnected clients
        for client in disconnected_clients:
            web_clients.remove(client)

    except Exception as e:
        logging.error(f"Error broadcasting frame: {e}")

async def handle_web_socket_video(request):
    """Handle WebSocket connections for video streaming."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Add client to set
    web_clients.add(ws)
    logging.info(f"Web client connected for video stream: {request.remote}")

    try:
        async for msg in ws:
            # We don't expect any messages from the client
            pass
    except Exception as e:
        logging.error(f"Error in web socket video: {e}")
    finally:
        # Remove client from set
        if ws in web_clients:
            web_clients.remove(ws)
        logging.info(f"Web client disconnected from video stream: {request.remote}")

    return ws

async def handle_web_socket_control(request):
    """Handle WebSocket connections for control commands."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    logging.info(f"Web client connected for control: {request.remote}")

    # Send current settings to client
    await ws.send_json({
        'type': 'settings',
        'ai_model': settings['ai_model'],
        'confidence_threshold': settings['confidence_threshold'],
        'display_fps': settings['display_fps']
    })

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    await handle_control_message(ws, data)
                except json.JSONDecodeError:
                    logging.error(f"Invalid JSON received: {msg.data}")
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logging.error(f"WebSocket error: {ws.exception()}")
    except Exception as e:
        logging.error(f"Error in web socket control: {e}")
    finally:
        logging.info(f"Web client disconnected from control: {request.remote}")

    return ws

async def handle_control_message(ws, data):
    """Handle control messages from web clients."""
    global settings

    if 'command' not in data:
        return

    command = data['command']

    if command == 'get_settings':
        # Send current settings
        await ws.send_json({
            'type': 'settings',
            'ai_model': settings['ai_model'],
            'confidence_threshold': settings['confidence_threshold'],
            'display_fps': settings['display_fps']
        })

    elif command == 'update_settings':
        # Update settings
        if 'ai_model' in data and data['ai_model'] in ['yolov4', 'mediapipe_pose', 'mediapipe_face']:
            settings['ai_model'] = data['ai_model']
            ai_processor.model_name = data['ai_model']
            # Reinitialize the AI processor with the new model
            ai_processor.__init__(model_name=data['ai_model'], confidence_threshold=ai_processor.confidence_threshold)

        if 'confidence_threshold' in data:
            threshold = float(data['confidence_threshold'])
            if 0.0 <= threshold <= 1.0:
                settings['confidence_threshold'] = threshold
                ai_processor.confidence_threshold = threshold

        if 'display_fps' in data:
            settings['display_fps'] = bool(data['display_fps'])

        # Confirm settings update
        await ws.send_json({
            'type': 'settings',
            'ai_model': settings['ai_model'],
            'confidence_threshold': settings['confidence_threshold'],
            'display_fps': settings['display_fps']
        })

        logging.info(f"Settings updated: {settings}")

    # Send current stats
    await ws.send_json({
        'type': 'stats',
        'fps': fps
    })

    # Send detection count
    await ws.send_json({
        'type': 'detections',
        'count': detection_count
    })

# Set up the web server routes
async def setup_web_server():
    """Set up the web server with routes."""
    app = web.Application()

    # WebSocket routes
    app.router.add_get('/video', handle_web_socket_video)
    app.router.add_get('/control', handle_web_socket_control)

    # Static files
    app.router.add_static('/', Path(args.web_path), show_index=True)

    # Start the web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, args.host, args.web_port)
    await site.start()

    logging.info(f"Web server started at http://{args.host}:{args.web_port}")

    return runner

async def main():
    """Main function to start the WebSocket server and web server."""
    logging.info("AI WiFi CAM Server")
    logging.info("-----------------")
    logging.info(f"Model: {args.model}")
    logging.info(f"Confidence Threshold: {args.confidence}")

    # Start tasks
    tasks = []

    # Start WebSocket server for ESP32-CAM
    logging.info(f"Starting WebSocket server on {args.host}:{args.port}")
    cam_server = await websockets.serve(process_frames, args.host, args.port)
    logging.info(f"WebSocket server started on ws://{args.host}:{args.port}")
    logging.info("Waiting for ESP32-CAM connection...")

    # Start web server if enabled
    web_runner = None
    if args.web:
        logging.info(f"Starting web server on {args.host}:{args.web_port}")
        web_runner = await setup_web_server()
        logging.info(f"Web interface available at http://{args.host}:{args.web_port}")

    # Keep the servers running
    try:
        await asyncio.Future()  # Run forever
    finally:
        # Cleanup
        cam_server.close()
        await cam_server.wait_closed()

        if web_runner:
            await web_runner.cleanup()

if __name__ == "__main__":
    try:
        # Check if web directory exists
        if args.web and not os.path.isdir(args.web_path):
            logging.error(f"Web directory not found: {args.web_path}")
            logging.error("Web interface will not be available")
            args.web = False

        # Run the main function
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        if args.save and 'out' in locals() and out is not None:
            out.release()
        if args.display:
            cv2.destroyAllWindows()
    except Exception as e:
        logging.error(f"Error: {e}")
        if args.save and 'out' in locals() and out is not None:
            out.release()
        if args.display:
            cv2.destroyAllWindows()
