#!/bin/bash

# Script to run the AI IELTS Examiner frontend

cd "$(dirname "$0")/../frontend"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    pnpm install
fi

# Start the development server
echo "Starting frontend development server..."
pnpm dev 