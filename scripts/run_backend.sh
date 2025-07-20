#!/bin/bash

# Script to run the AI IELTS Examiner backend

cd "$(dirname "$0")/.."

# Activate virtual environment
source venv/bin/activate

# Change to backend directory and run the main_new application in dev mode
cd backend
python -m src.main_new start 