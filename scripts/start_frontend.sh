#!/bin/bash

# Script to run the new React frontend with FastAPI backend

echo "🚀 Starting A2A Strategy Agent - New Frontend"
echo "============================================"

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if Python dependencies are installed
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "⚠️  FastAPI not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if Node.js is available
if ! command -v npm &> /dev/null; then
    echo "❌ Error: Node.js is required but not found. Please install Node.js first."
    exit 1
fi

# Install frontend dependencies
cd frontend
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Build the frontend
echo "🔨 Building frontend..."
npm run build

# Go back to root and start the backend in the background
echo "🌐 Starting FastAPI backend on port 8002..."
cd ..
python3 api_real.py &
BACKEND_PID=$!

# Give the backend a moment to start
sleep 3

# Check if backend is running
echo "🔍 Checking backend status..."
if curl -s http://localhost:8002/api/health &> /dev/null; then
    echo "✅ Backend is running successfully!"
else
    echo "❌ Error: Backend failed to start. Killing process..."
    kill $BACKEND_PID
    exit 1
fi

# Start the frontend
echo "🎨 Starting React frontend..."
cd frontend
npm run preview &
FRONTEND_PID=$!

# Give the frontend a moment to start
sleep 2

echo ""
echo "🎉 A2A Strategy Agent is now running!"
echo "===================================="
echo "📍 Frontend URL: http://localhost:4173"
echo "📍 Backend URL:  http://localhost:8002"
echo ""
echo "💡 Press Ctrl+C to stop both services"
echo ""

# Wait for user to stop
wait $FRONTEND_PID $BACKEND_PID

echo "👋 Shutting down..."
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null