#!/bin/bash
# Smart Stadium - Unix/Linux Startup Script
# Launches both API backend and React frontend

echo "=========================================="
echo "🏟️ Smart Stadium System Launcher"
echo "=========================================="

echo ""
echo "🔧 Setting up Python environment..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🚀 Starting Smart Stadium API Server..."
cd api
python start_server.py &
API_PID=$!
cd ..

echo "Waiting for API to start..."
sleep 5

echo ""
echo "🎨 Starting React Frontend Dashboard..."
cd frontend/smart-stadium-dashboard
npm install
npm run dev &
FRONTEND_PID=$!
cd ../..

echo ""
echo "=========================================="
echo "✅ Smart Stadium is running!"
echo ""
echo "📱 API Server: http://localhost:8000"
echo "🎮 Dashboard: http://localhost:3000"
echo "📋 API Docs: http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop all services..."
echo "=========================================="

# Wait for interrupt
trap "echo ''; echo '🛑 Shutting down Smart Stadium...'; kill $API_PID $FRONTEND_PID; exit 0" INT
wait