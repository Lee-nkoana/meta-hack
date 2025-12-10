#!/bin/bash
# Quick start script for Medical Records Bridge backend

echo "🏥 Medical Records Bridge - Backend Quick Start"
echo "================================================"
echo ""

# Quickstart script for the backend

echo "Starting Medical Records Bridge Backend..."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo " Please edit .env and add your configuration (especially META_AI_API_KEY)"
    echo "   The backend will work without AI features if no API key is provided"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Starting application..."
make run
