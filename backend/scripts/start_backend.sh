#!/bin/bash
# Start the Flask backend

# Ensure we are in the backend directory
cd "$(dirname "$0")/.."

# Set environment variables if needed
export FLASK_APP=app.main:app
export FLASK_DEBUG=1

echo "Starting Flask backend..."
venv/bin/flask run --host=0.0.0.0 --port=8000
