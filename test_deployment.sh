#!/bin/bash

# Test Deployed Backend
echo "Testing Trading Backtest Platform Deployment"
echo "=============================================="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
curl -s https://trading-backtest-platform.onrender.com/api/health | python3 -m json.tool
echo ""
echo ""

# Test 2: Strategies List
echo "Test 2: Strategies List"
curl -s https://trading-backtest-platform.onrender.com/api/strategies | python3 -m json.tool | head -20
echo ""
echo ""

# Test 3: Run Backtest
echo "Test 3: Run Backtest (AAPL 2023)"
curl -s -X POST https://trading-backtest-platform.onrender.com/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "moving_average",
    "ticker": "AAPL",
    "start_date": "2023-06-01",
    "end_date": "2023-09-01",
    "initial_capital": 100000,
    "parameters": {
      "fast_window": 20,
      "slow_window": 50
    }
  }' | python3 -m json.tool | head -50

echo ""
echo ""
echo "Testing complete!"
