import logging
import os

def configure_logging():
    """
    Configure logging to reduce verbose output from websockets and LiveKit.
    """
    # Set environment variables for logging control
    os.environ.setdefault('LOG_LEVEL', 'WARNING')
    os.environ.setdefault('WEBSOCKETS_LOG_LEVEL', 'WARNING')
    os.environ.setdefault('LIVEKIT_LOG_LEVEL', 'WARNING')
    
    # Configure root logger
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Specifically reduce websockets logging
    websockets_logger = logging.getLogger('websockets')
    websockets_logger.setLevel(logging.WARNING)
    
    # Reduce LiveKit logging
    livekit_logger = logging.getLogger('livekit')
    livekit_logger.setLevel(logging.WARNING)
    
    # Reduce Google AI logging
    google_logger = logging.getLogger('google')
    google_logger.setLevel(logging.WARNING)
    
    # Reduce aiohttp logging
    aiohttp_logger = logging.getLogger('aiohttp')
    aiohttp_logger.setLevel(logging.WARNING)
    
    # Keep your application logs at INFO level
    app_logger = logging.getLogger('src')
    app_logger.setLevel(logging.INFO)
    
    print("Logging configured - verbose websockets and LiveKit logs disabled")

if __name__ == "__main__":
    configure_logging() 