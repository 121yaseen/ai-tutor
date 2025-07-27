#!/usr/bin/env python3
"""
Test script to verify logging configuration reduces verbose output.
"""

import sys
import os
import logging

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and configure logging
from src.main_new import configure_logging

def test_logging():
    """Test that logging is properly configured."""
    print("Testing logging configuration...")
    
    # Test websockets logging
    websockets_logger = logging.getLogger('websockets')
    print(f"Websockets logger level: {websockets_logger.level}")
    print(f"Websockets logger effective level: {websockets_logger.getEffectiveLevel()}")
    
    # Test livekit logging
    livekit_logger = logging.getLogger('livekit')
    print(f"LiveKit logger level: {livekit_logger.level}")
    print(f"LiveKit logger effective level: {livekit_logger.getEffectiveLevel()}")
    
    # Test root logger
    root_logger = logging.getLogger()
    print(f"Root logger level: {root_logger.level}")
    
    print("Logging configuration test completed!")

if __name__ == "__main__":
    test_logging() 