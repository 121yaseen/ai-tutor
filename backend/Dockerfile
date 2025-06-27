# Use the official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by AV
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libopus-dev \
    libvpx-dev \
    libavdevice-dev \
    libavfilter-dev \
    libavformat-dev \
    libavcodec-dev \
    libswresample-dev \
    libswscale-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY . .

# Expose the port the livekit-agent runs on
EXPOSE 8080

# The command to run the agent. Note: Cloud Run sets the PORT env var.
CMD ["python", "-m", "livekit.agents.cli", "src.main"] 
