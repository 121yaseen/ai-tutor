# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# build-essential is included in case any Python packages need to compile C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# Ensure .dockerignore is properly set up to exclude .venv, .git, .env, etc.
COPY . .

# Expose port (good practice, though PORT env var determines actual listening port)
EXPOSE 8080

# Entrypoint for Gunicorn with Uvicorn worker
# Uses PORT environment variable provided by Cloud Run, defaults to 8080 locally
# Uses 2 workers, suitable for a default 1 vCPU Cloud Run instance
CMD ["sh", "-c", "gunicorn api_server.main:app -k uvicorn.workers.UvicornWorker -b :${PORT:-8080} --workers 2"]
 