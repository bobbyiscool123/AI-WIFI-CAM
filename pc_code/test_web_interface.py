#!/usr/bin/env python3
"""
Test script for the AI WiFi CAM web interface.

This script simulates the ESP32-CAM by sending test video frames to the server.
It's useful for testing the web interface without an actual ESP32-CAM connected.
"""

import asyncio
import websockets
import cv2
import numpy as np
import argparse
import time
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Parse command line arguments
parser = argparse.ArgumentParser(description='AI WiFi CAM Web Interface Test')
parser.add_argument('--host', type=str, default='localhost', help='Server host')
parser.add_argument('--port', type=int, default=8888, help='Server port')
parser.add_argument('--video', type=str, default='0', help='Video source (0 for webcam, or path to video file)')
parser.add_argument('--fps', type=int, default=15, help='Target FPS for sending frames')
args = parser.parse_args()

async def send_frames():
    """Send video frames to the server."""
    # Connect to the server
    uri = f"ws://{args.host}:{args.port}"
    logging.info(f"Connecting to {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            logging.info("Connected to server")
            
            # Open video source
            if args.video.isdigit():
                cap = cv2.VideoCapture(int(args.video))
                logging.info(f"Using webcam {args.video}")
            else:
                cap = cv2.VideoCapture(args.video)
                logging.info(f"Using video file: {args.video}")
            
            if not cap.isOpened():
                logging.error("Failed to open video source")
                return
            
            # Calculate frame delay based on target FPS
            frame_delay = 1.0 / args.fps
            
            try:
                while True:
                    start_time = time.time()
                    
                    # Read a frame
                    ret, frame = cap.read()
                    if not ret:
                        if args.video.isdigit():
                            # For webcam, continue even if a frame is missed
                            continue
                        else:
                            # For video file, loop back to the beginning
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            continue
                    
                    # Encode frame as JPEG
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    
                    # Send frame to server
                    await websocket.send(buffer.tobytes())
                    
                    # Display the frame locally
                    cv2.imshow('Test Video Source', frame)
                    
                    # Check for key press
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    
                    # Calculate time to wait to maintain target FPS
                    elapsed = time.time() - start_time
                    wait_time = max(0, frame_delay - elapsed)
                    await asyncio.sleep(wait_time)
            
            finally:
                # Clean up
                cap.release()
                cv2.destroyAllWindows()
    
    except websockets.exceptions.ConnectionClosed:
        logging.error("Connection closed")
    except Exception as e:
        logging.error(f"Error: {e}")

async def main():
    """Main function."""
    logging.info("AI WiFi CAM Web Interface Test")
    logging.info(f"Target FPS: {args.fps}")
    
    await send_frames()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Test stopped by user")
    except Exception as e:
        logging.error(f"Error: {e}")
