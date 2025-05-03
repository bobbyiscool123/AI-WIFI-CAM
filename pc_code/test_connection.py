#!/usr/bin/env python3
"""
Test script for ESP32-CAM WebSocket connection.

This script sets up a simple WebSocket server that receives and displays
video frames from the ESP32-CAM without any AI processing. Use this to
verify that the basic connection and streaming are working correctly.
"""

import asyncio
import websockets
import cv2
import numpy as np
import argparse
import time
import os
from datetime import datetime

# Parse command line arguments
parser = argparse.ArgumentParser(description='ESP32-CAM WebSocket Connection Test')
parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to listen on')
parser.add_argument('--port', type=int, default=8888, help='Port to listen on')
parser.add_argument('--save', action='store_true', help='Save received video to file')
args = parser.parse_args()

# Create output directory if saving video
if args.save:
    os.makedirs('test_output', exist_ok=True)
    output_filename = os.path.join('test_output', 
                                  f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.avi')
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = None  # Will be initialized after receiving first frame

# Global variables
frame_count = 0
fps = 0
fps_time = time.time()
start_time = None

async def process_frames(websocket, path):
    """Process incoming WebSocket frames without AI processing."""
    global frame_count, fps, fps_time, start_time, out
    
    print(f"ESP32-CAM connected from {websocket.remote_address}")
    print("Receiving video stream...")
    start_time = time.time()
    
    try:
        async for message in websocket:
            # Convert binary message to numpy array
            frame_data = np.frombuffer(message, dtype=np.uint8)
            
            # Decode JPEG image
            frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
            if frame is None:
                print("Failed to decode image")
                continue
            
            # Calculate FPS
            frame_count += 1
            if time.time() - fps_time >= 1.0:
                fps = frame_count
                frame_count = 0
                fps_time = time.time()
            
            # Add FPS and duration text to frame
            duration = time.time() - start_time
            cv2.putText(frame, f"FPS: {fps}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Duration: {int(duration)}s", (10, 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Initialize video writer if saving and not yet initialized
            if args.save and out is None:
                height, width = frame.shape[:2]
                out = cv2.VideoWriter(output_filename, fourcc, 20.0, (width, height))
            
            # Save frame to video if enabled
            if args.save:
                out.write(frame)
            
            # Display the frame
            cv2.imshow('ESP32-CAM Test', frame)
            key = cv2.waitKey(1) & 0xFF
            
            # Press 'q' to quit
            if key == ord('q'):
                break
    
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")
    finally:
        duration = time.time() - start_time
        print(f"Connection duration: {duration:.2f} seconds")
        print(f"Average FPS: {frame_count / max(1, duration):.2f}")
        
        if args.save and out is not None:
            out.release()
        cv2.destroyAllWindows()

async def main():
    """Main function to start the WebSocket server."""
    print("ESP32-CAM Connection Test")
    print("========================")
    print(f"Server started on port {args.port}")
    print("Waiting for ESP32-CAM to connect...")
    
    server = await websockets.serve(process_frames, args.host, args.port)
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        if args.save and 'out' in locals() and out is not None:
            out.release()
        cv2.destroyAllWindows()
