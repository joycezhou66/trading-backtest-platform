#!/bin/bash

# Startup script for Trading Backtest Platform
# Makes it easy to start both backend and frontend

echo "================================================"
echo "  Algorithmic Trading Backtest Platform"
echo "================================================"
echo ""

# Check if backend dependencies are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Backend dependencies not installed"
    echo "   Run: cd backend && pip3 install -r requirements.txt"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Frontend dependencies not installed"
    echo "   Run: cd frontend && npm install"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""
echo "Starting servers..."
echo "   Backend:  http://localhost:5000"
echo "   Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start backend in background
cd backend
python3 app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
