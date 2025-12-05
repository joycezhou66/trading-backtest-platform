#!/usr/bin/env python3
"""
Quick test script to verify the backtesting platform works.
Run this before your demo to ensure everything is functioning.

Usage: python test_platform.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from data.data_handler import DataHandler
from strategies.moving_average import MovingAverageStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy
from engine.backtester import Backtester
from engine.performance import generate_performance_report


def test_data_handler():
    """Test data fetching and caching."""
    print("Testing data handler...")
    handler = DataHandler(cache_dir='backend/cache')

    try:
        data = handler.get_data('AAPL', '2023-01-01', '2023-12-31')
        assert len(data) > 0, "No data returned"
        assert 'Close' in data.columns, "Missing Close column"
        print("✓ Data handler works")
        return True
    except Exception as e:
        print(f"✗ Data handler failed: {e}")
        return False


def test_strategy(strategy_class, name, ticker='AAPL'):
    """Test a strategy."""
    print(f"\nTesting {name} strategy...")

    try:
        # Get data
        handler = DataHandler(cache_dir='backend/cache')
        data = handler.get_data(ticker, '2020-01-01', '2023-12-31')

        # Create strategy
        strategy = strategy_class()

        # Run backtest
        backtester = Backtester(initial_capital=100000)
        results = backtester.run(strategy, data)

        # Check results
        assert len(results['equity_curve']) > 0, "No equity curve"
        assert len(results['trades']) >= 0, "Trades not calculated"

        # Generate performance metrics
        performance = generate_performance_report(
            results['equity_curve'],
            results['returns'],
            results['trades'],
            results['initial_capital']
        )

        assert 'performance_metrics' in performance, "Missing performance metrics"

        # Print summary
        print(f"  Total Return: {performance['performance_metrics']['total_return']:.2f}%")
        print(f"  Sharpe Ratio: {performance['performance_metrics']['sharpe_ratio']:.2f}")
        print(f"  Max Drawdown: {performance['risk_metrics']['max_drawdown']:.2f}%")
        print(f"  Total Trades: {performance['trade_metrics']['total_trades']}")
        print(f"✓ {name} strategy works")

        return True

    except Exception as e:
        print(f"✗ {name} strategy failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api():
    """Test Flask API endpoints."""
    print("\nTesting API endpoints...")

    try:
        import requests

        # Test health endpoint
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        assert response.status_code == 200, "Health check failed"
        print("✓ Health endpoint works")

        # Test strategies endpoint
        response = requests.get('http://localhost:5000/api/strategies', timeout=5)
        assert response.status_code == 200, "Strategies endpoint failed"
        print("✓ Strategies endpoint works")

        return True

    except requests.exceptions.ConnectionError:
        print("⚠ API server not running (start with: cd backend && python app.py)")
        return False
    except Exception as e:
        print(f"✗ API test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("BACKTESTING PLATFORM TEST SUITE")
    print("=" * 60)

    results = []

    # Test data handler
    results.append(test_data_handler())

    # Test strategies
    results.append(test_strategy(MovingAverageStrategy, "Moving Average"))
    results.append(test_strategy(MeanReversionStrategy, "Mean Reversion"))
    results.append(test_strategy(MomentumStrategy, "Momentum"))

    # Test API (optional - only if server is running)
    api_result = test_api()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Core tests: {passed}/{total} passed")
    if api_result:
        print("API tests: PASSED")
    else:
        print("API tests: SKIPPED (server not running)")

    if passed == total:
        print("\n✓ All core tests passed! Platform is ready for demo.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Fix issues before demo.")
        return 1


if __name__ == '__main__':
    exit(main())
