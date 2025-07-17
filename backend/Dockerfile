# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies for AV and build
RUN apt-get update && apt-get install -y --no-install-recommends \
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

# Install Python dependencies in a separate layer for caching
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy only the backend source code
COPY src ./src
COPY data ./data
COPY LLM_PROMPT_EXAMPLE.md ./LLM_PROMPT_EXAMPLE.md
COPY README.md ./README.md
COPY sample_ielts_test_result_structure.json ./sample_ielts_test_result_structure.json

# Copy any other files needed at runtime
COPY run_integration_tests.py ./run_integration_tests.py
COPY run_tests.py ./run_tests.py
COPY pytest.ini ./pytest.ini

# Expose the port the agent will use (if needed)
EXPOSE 8080

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Entrypoint for the agent
CMD ["python", "-m", "src.main", "start"] 
