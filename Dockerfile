# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
# tesseract-ocr: for OCR functionality
# libgl1-mesa-glx: for OpenCV
# python3-opencv: sometimes needed
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend requirements first to leverage cache
COPY backend/requirements.txt backend/requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the rest of the application
# We copy both backend and frontend to preserve the directory structure
# required by Flask's template_folder="../../frontend/templates"
COPY backend backend/
COPY frontend frontend/

# Expose the API port
EXPOSE 8000

# Set working directory to backend so flask commands work naturally
WORKDIR /app/backend

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Environment variables for Flask
ENV FLASK_APP=app.main
ENV FLASK_DEBUG=0

# Run the application
CMD ["/bin/bash", "./entrypoint.sh"]
