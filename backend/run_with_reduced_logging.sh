#!/bin/bash

# Set environment variables to reduce verbose logging
export LOG_LEVEL=WARNING
export WEBSOCKETS_LOG_LEVEL=WARNING
export LIVEKIT_LOG_LEVEL=WARNING
export GOOGLE_LOG_LEVEL=WARNING
export AIOHTTP_LOG_LEVEL=WARNING
export PYTHONPATH=/Users/muhammedyaseen/Development/ai-voice-assistant-livekit/backend

# Activate virtual environment
source ../venv/bin/activate

echo "Starting application with reduced logging..."
echo "Log levels set to WARNING to suppress verbose websockets and LiveKit logs"

# Run your application (replace with your actual command)
python src/main_new.py "$@" 