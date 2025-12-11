
#!/bin/bash
set -e

echo "Starting Backend Entrypoint..."

# Check if DB file exists (just for logging purposes, main.py handles creation)
if [ -f "medical_records.db" ]; then
    echo "Existing database found."
else
    echo "No database found. It will be initialized by the application."
fi

# Run the Flask Application
# Using flask run with host 0.0.0.0 to be accessible outside container
exec flask run --host=0.0.0.0 --port=8000
