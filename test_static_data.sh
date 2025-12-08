#!/bin/bash

echo "Testing Deployed Platform with Static Data"
echo "==========================================="
echo ""

# Test 1: AAPL with Moving Average
echo "Test 1: AAPL - Moving Average Strategy (2020-2024)"
curl -s -X POST https://trading-backtest-platform.onrender.com/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "moving_average",
    "ticker": "AAPL",
    "start_date": "2020-01-01",
    "end_date": "2024-12-01",
    "initial_capital": 100000,
    "parameters": {"fast_window": 20, "slow_window": 50}
  }' | python3 -m json.tool | head -60

echo ""
echo "==========================================="
echo ""

# Test 2: SPY with Mean Reversion
echo "Test 2: SPY - Mean Reversion Strategy (2020-2024)"
curl -s -X POST https://trading-backtest-platform.onrender.com/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "mean_reversion",
    "ticker": "SPY",
    "start_date": "2020-01-01",
    "end_date": "2024-12-01",
    "initial_capital": 100000,
    "parameters": {"window": 20, "num_std": 2.0}
  }' | python3 -m json.tool | head -40

echo ""
echo "==========================================="
echo ""

# Test 3: TSLA with Momentum
echo "Test 3: TSLA - Momentum Strategy (2020-2024)"
curl -s -X POST https://trading-backtest-platform.onrender.com/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "momentum",
    "ticker": "TSLA",
    "start_date": "2020-01-01",
    "end_date": "2024-12-01",
    "initial_capital": 100000,
    "parameters": {"window": 14, "oversold": 30, "overbought": 70}
  }' | python3 -m json.tool | head -40

echo ""
echo "TEST COMPLETE!"
