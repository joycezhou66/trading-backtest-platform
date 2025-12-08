#!/bin/bash

echo "========================================================================="
echo "COMPREHENSIVE DEPLOYMENT TEST - Trading Backtest Platform"
echo "========================================================================="
echo ""

API_URL="https://trading-backtest-platform.onrender.com"

# Test 1: Health Check
echo "Test 1: Health Check"
echo "---------------------------------------------------------------------"
health=$(curl -s "${API_URL}/api/health")
echo "$health" | python3 -m json.tool
echo ""

# Test 2: Arbitrary ticker (never existed before)
echo "Test 2: Random Ticker (XYZABC) - Custom Date Range"
echo "---------------------------------------------------------------------"
curl -s -X POST "${API_URL}/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "moving_average",
    "ticker": "XYZABC",
    "start_date": "2019-01-01",
    "end_date": "2022-12-31",
    "parameters": {"fast_window": 20, "slow_window": 50}
  }' | python3 -m json.tool | head -60
echo ""
echo "========================================================================="
echo ""

# Test 3: Known ticker (should use static file)
echo "Test 3: Known Ticker (AAPL) - Pre-loaded Data"
echo "---------------------------------------------------------------------"
curl -s -X POST "${API_URL}/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "moving_average",
    "ticker": "AAPL",
    "start_date": "2020-01-01",
    "end_date": "2024-12-01",
    "parameters": {"fast_window": 20, "slow_window": 50}
  }' | python3 -m json.tool | head -60
echo ""
echo "========================================================================="
echo ""

# Test 4: Different strategy
echo "Test 4: Mean Reversion Strategy - Random Ticker (TESTXYZ)"
echo "---------------------------------------------------------------------"
curl -s -X POST "${API_URL}/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "mean_reversion",
    "ticker": "TESTXYZ",
    "start_date": "2021-01-01",
    "end_date": "2023-12-31",
    "parameters": {"window": 20, "num_std": 2.0}
  }' | python3 -m json.tool | head -60
echo ""
echo "========================================================================="
echo ""

# Test 5: Short date range
echo "Test 5: Short Date Range (6 months) - Ticker: ABC123"
echo "---------------------------------------------------------------------"
curl -s -X POST "${API_URL}/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "momentum",
    "ticker": "ABC123",
    "start_date": "2023-01-01",
    "end_date": "2023-06-30",
    "parameters": {"window": 14, "oversold": 30, "overbought": 70}
  }' | python3 -m json.tool | head -60
echo ""
echo "========================================================================="
echo ""

# Test 6: Different date range than pre-loaded
echo "Test 6: Different Date Range - AAPL (2015-2018)"
echo "---------------------------------------------------------------------"
curl -s -X POST "${API_URL}/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "moving_average",
    "ticker": "AAPL",
    "start_date": "2015-01-01",
    "end_date": "2018-12-31",
    "parameters": {"fast_window": 20, "slow_window": 50}
  }' | python3 -m json.tool | head -60
echo ""
echo "========================================================================="
echo ""

# Summary
echo "✅ DEPLOYMENT TEST COMPLETE"
echo ""
echo "If all tests show 'success: true' with trades and metrics, deployment"
echo "is working perfectly with dynamic data generation!"
echo ""
echo "========================================================================="
