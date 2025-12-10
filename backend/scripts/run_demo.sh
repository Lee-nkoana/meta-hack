#!/bin/bash
# Run the demo API script

# Ensure we are in the backend directory
cd "$(dirname "$0")/.."

echo "Running Demo API..."
venv/bin/python demo_api.py
