#!/usr/bin/env python3
"""
Run all tests for the AI WiFi CAM project.

This script discovers and runs all tests in the tests directory.
"""

import unittest
import sys
from pathlib import Path

def run_tests():
    """Discover and run all tests."""
    # Add the parent directory to the path
    sys.path.insert(0, str(Path(__file__).parent))
    
    # Discover tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent / "tests"
    suite = loader.discover(start_dir)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return the number of failures and errors
    return len(result.failures) + len(result.errors)

if __name__ == "__main__":
    print("Running AI WiFi CAM tests...")
    sys.exit(run_tests())
