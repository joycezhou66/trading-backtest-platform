#!/bin/bash
# Quick test to verify dynamic generation is working

echo "Testing arbitrary ticker (FAKECOMPANY)..."
result=$(curl -s -X POST https://trading-backtest-platform.onrender.com/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "moving_average",
    "ticker": "FAKECOMPANY",
    "start_date": "2021-01-01",
    "end_date": "2023-12-31",
    "parameters": {"fast_window": 20, "slow_window": 50}
  }')

if echo "$result" | grep -q '"success": true'; then
    echo "✅ SUCCESS! Dynamic generation is working!"
    echo "$result" | python3 -m json.tool | head -40
else
    echo "❌ FAILED - Old deployment still running"
    echo "$result" | python3 -m json.tool
fi
