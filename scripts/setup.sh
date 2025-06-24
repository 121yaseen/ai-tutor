#!/bin/bash

# Setup script for AI IELTS Examiner project

echo "Setting up AI IELTS Examiner project..."

cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
if command -v pnpm &> /dev/null; then
    pnpm install
elif command -v npm &> /dev/null; then
    npm install
else
    echo "Error: Neither pnpm nor npm found. Please install Node.js and pnpm."
    exit 1
fi
cd ..

# Make scripts executable
chmod +x scripts/*.sh

echo "Setup complete!"
echo "To run the backend: ./scripts/run_backend.sh"
echo "To run the frontend: ./scripts/run_frontend.sh" 