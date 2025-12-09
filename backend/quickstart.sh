#!/bin/bash
# Quick start script for Medical Records Bridge backend

echo "🏥 Medical Records Bridge - Backend Quick Start"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv || {
        echo "⚠️  Note: python3-venv not available, installing dependencies globally"
        echo "   For Ubuntu/Debian: sudo apt install python3-venv"
    }
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate 2>/dev/null || {
        echo "⚠️  Could not activate venv, proceeding with global Python"
    }
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✏️  Please edit .env and add your configuration (especially META_AI_API_KEY)"
    echo "   The backend will work without AI features if no API key is provided"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the server, run:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "📚 Then visit:"
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo ""
