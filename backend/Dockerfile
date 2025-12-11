
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

# Create and set working directory
WORKDIR $APP_HOME

# Install system dependencies (build-essential needed for some python packages like chromadb/hnswlib)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies (use cache to speed up rebuilds)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port (default 8000)
EXPOSE 8000

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Run the application
ENTRYPOINT ["./entrypoint.sh"]
