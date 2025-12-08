#!/bin/bash

# Simple script to run the trading backtest platform
# Starts both backend and frontend in the background

echo "Starting Trading Backtest Platform..."
echo "======================================="

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Error: Run this script from the trading-backtest-platform directory"
    exit 1
fi

# Start backend
echo "Starting backend on http://localhost:5000..."
cd backend
/Library/Frameworks/Python.framework/Versions/3.9/bin/python3 app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend on http://localhost:5173..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✓ Platform is running!"
echo "  Backend:  http://localhost:5000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"
echo ""
echo "Logs:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; echo 'Stopped.'; exit" INT
wait
