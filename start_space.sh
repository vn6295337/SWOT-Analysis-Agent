#!/bin/bash

echo "🚀 Starting A2A Strategy Agent Space"
echo "==================================="

# Start the FastAPI backend in the background
echo "🌐 Starting FastAPI backend on port 8002..."
python api_real.py &
BACKEND_PID=$!

# Give the backend a moment to start
sleep 5

# Check if backend is running
echo "🔍 Checking backend status..."
if curl -s http://localhost:8002/api/health &> /dev/null; then
    echo "✅ Backend is running successfully!"
else
    echo "❌ Error: Backend failed to start"
    exit 1
fi

# Start the React frontend
echo "🎨 Starting React frontend on port 3000..."
serve -s frontend/dist -l 3000

echo "👋 Space is shutting down..."