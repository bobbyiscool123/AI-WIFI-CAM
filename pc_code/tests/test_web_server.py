#!/usr/bin/env python3
"""
Unit tests for the web server functionality.

This module contains tests for the web server components of the stream_receiver.py script.
"""

import unittest
import os
import sys
import asyncio
import aiohttp
from aiohttp import web
import websockets
import json
from pathlib import Path

# Add parent directory to path to import stream_receiver
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestWebServer(unittest.TestCase):
    """Test cases for the web server functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for web files
        self.web_dir = Path(__file__).parent / "mock_web"
        os.makedirs(self.web_dir, exist_ok=True)
        
        # Create a simple index.html file
        with open(self.web_dir / "index.html", "w") as f:
            f.write("<html><body><h1>Test</h1></body></html>")
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove mock web files
        for file in self.web_dir.glob("*"):
            file.unlink()
        
        # Remove mock web directory
        self.web_dir.rmdir()
    
    async def test_web_server_setup(self):
        """Test that the web server can be set up."""
        # Import the setup_web_server function
        # We import it here to avoid loading the entire module at import time
        from stream_receiver import setup_web_server
        
        # Create a mock args object
        class MockArgs:
            host = "localhost"
            web_port = 8080
            web_path = str(self.web_dir)
        
        # Set up the web server
        runner = await setup_web_server(MockArgs())
        
        # Check that the runner is not None
        self.assertIsNotNone(runner)
        
        # Clean up
        await runner.cleanup()
    
    async def test_web_socket_control(self):
        """Test the WebSocket control endpoint."""
        # Import the handle_web_socket_control function
        # We import it here to avoid loading the entire module at import time
        from stream_receiver import handle_web_socket_control
        
        # Create a simple aiohttp application
        app = web.Application()
        app.router.add_get('/control', handle_web_socket_control)
        
        # Start the server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8081)
        await site.start()
        
        try:
            # Connect to the WebSocket
            async with websockets.connect('ws://localhost:8081/control') as ws:
                # Wait for the settings message
                response = await ws.recv()
                data = json.loads(response)
                
                # Check that the response is a settings message
                self.assertEqual(data['type'], 'settings')
                self.assertIn('ai_model', data)
                self.assertIn('confidence_threshold', data)
                self.assertIn('display_fps', data)
                
                # Send a command
                await ws.send(json.dumps({
                    'command': 'get_settings'
                }))
                
                # Wait for the response
                response = await ws.recv()
                data = json.loads(response)
                
                # Check that the response is a settings message
                self.assertEqual(data['type'], 'settings')
        finally:
            # Clean up
            await runner.cleanup()
    
    async def test_web_socket_video(self):
        """Test the WebSocket video endpoint."""
        # Import the handle_web_socket_video function
        # We import it here to avoid loading the entire module at import time
        from stream_receiver import handle_web_socket_video
        
        # Create a simple aiohttp application
        app = web.Application()
        app.router.add_get('/video', handle_web_socket_video)
        
        # Start the server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8082)
        await site.start()
        
        try:
            # Connect to the WebSocket
            async with websockets.connect('ws://localhost:8082/video') as ws:
                # Check that the connection is established
                self.assertTrue(ws.open)
        finally:
            # Clean up
            await runner.cleanup()

if __name__ == "__main__":
    # Run the tests
    unittest.main()
