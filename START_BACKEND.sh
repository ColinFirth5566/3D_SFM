#!/bin/bash

echo "🚀 Starting 3D Reconstruction Backend..."
echo ""

cd "$(dirname "$0")/backend"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please run:"
    echo "   cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
fi

echo ""
echo "🔧 Configuration:"
echo "   - Backend: http://localhost:8000"
echo "   - Frontend: https://colinfirth5566.github.io/3D_SFM/"
echo "   - Implementation: $(grep GS_IMPLEMENTATION .env | cut -d'=' -f2)"
echo ""
echo "📊 Starting FastAPI server..."
echo "   Press Ctrl+C to stop"
echo ""

# Start the server
python main.py
