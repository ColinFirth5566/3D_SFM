#!/bin/bash

# Development startup script for 3D Reconstruction App
# This script starts both frontend and backend in separate terminals

echo "Starting 3D Reconstruction Development Environment..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
if ! command_exists python3; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "Error: npm is not installed"
    exit 1
fi

# Start backend
echo "Starting backend on http://localhost:8000..."
gnome-terminal -- bash -c "cd backend && source venv/bin/activate && python main.py; exec bash" 2>/dev/null || \
xterm -e "cd backend && source venv/bin/activate && python main.py" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '"$PWD"'/backend && source venv/bin/activate && python main.py"' 2>/dev/null || \
echo "Could not open terminal. Please manually run: cd backend && source venv/bin/activate && python main.py"

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "Starting frontend on http://localhost:3000..."
gnome-terminal -- bash -c "cd frontend && npm run dev; exec bash" 2>/dev/null || \
xterm -e "cd frontend && npm run dev" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '"$PWD"'/frontend && npm run dev"' 2>/dev/null || \
echo "Could not open terminal. Please manually run: cd frontend && npm run dev"

echo ""
echo "Development environment started!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C in each terminal to stop the servers"
