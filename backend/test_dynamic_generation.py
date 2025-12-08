"""
Test dynamic data generation with arbitrary tickers and dates.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.data_handler import DataHandler
from strategies.moving_average import MovingAverageStrategy
from engine.backtester import Backtester

print("=" * 70)
print("TESTING DYNAMIC DATA GENERATION")
print("=" * 70)
print()

# Initialize without static data directory to force generation
dh = DataHandler(static_data_dir='nonexistent_dir')

# Test 1: Random ticker that definitely doesn't exist in static files
print("Test 1: Random ticker (RANDOMXYZ) with custom date range")
print("-" * 70)
try:
    data1 = dh.get_data('RANDOMXYZ', '2022-01-01', '2023-12-31', use_cache=False)
    print(f"✅ Generated {len(data1)} days of data for RANDOMXYZ")
    print(f"   Price range: ${data1['Low'].min():.2f} - ${data1['High'].max():.2f}")
    print(f"   Date range: {data1.index[0]} to {data1.index[-1]}")
    print()
except Exception as e:
    print(f"❌ Failed: {e}")
    print()

# Test 2: Different date range
print("Test 2: NFLX with different date range (2018-2021)")
print("-" * 70)
try:
    data2 = dh.get_data('NFLX', '2018-06-01', '2021-03-15', use_cache=False)
    print(f"✅ Generated {len(data2)} days of data for NFLX")
    print(f"   Price range: ${data2['Low'].min():.2f} - ${data2['High'].max():.2f}")
    print(f"   Date range: {data2.index[0]} to {data2.index[-1]}")
    print()
except Exception as e:
    print(f"❌ Failed: {e}")
    print()

# Test 3: Run full backtest with generated data
print("Test 3: Full backtest with generated data (UNKNOWN_TICKER)")
print("-" * 70)
try:
    data3 = dh.get_data('UNKNOWN_TICKER', '2021-01-01', '2024-01-01', use_cache=False)
    strategy = MovingAverageStrategy({'fast_window': 20, 'slow_window': 50})
    backtester = Backtester(100000)
    results = backtester.run(strategy, data3)

    print(f"✅ Backtest completed successfully!")
    print(f"   Total trades: {len(results['trades'])}")
    print(f"   Final equity: ${results['equity_curve'][-1]:.2f}")

    if len(results['trades']) > 0:
        total_pnl = sum(t['pnl'] for t in results['trades'])
        winning_trades = sum(1 for t in results['trades'] if t['pnl'] > 0)
        print(f"   Total P&L: ${total_pnl:.2f}")
        print(f"   Win rate: {winning_trades}/{len(results['trades'])} ({100*winning_trades/len(results['trades']):.1f}%)")
    print()
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()
    print()

# Test 4: Short date range
print("Test 4: Short date range (3 months)")
print("-" * 70)
try:
    data4 = dh.get_data('XYZ', '2023-10-01', '2023-12-31', use_cache=False)
    print(f"✅ Generated {len(data4)} days of data for XYZ")
    print(f"   Price range: ${data4['Low'].min():.2f} - ${data4['High'].max():.2f}")
    print()
except Exception as e:
    print(f"❌ Failed: {e}")
    print()

# Test 5: Verify same ticker generates same data (reproducibility)
print("Test 5: Reproducibility test")
print("-" * 70)
try:
    data5a = dh.get_data('TEST123', '2020-01-01', '2020-06-30', use_cache=False)
    data5b = dh.get_data('TEST123', '2020-01-01', '2020-06-30', use_cache=False)

    if data5a.equals(data5b):
        print(f"✅ Same ticker generates identical data (reproducible)")
        print(f"   First price: ${data5a['Close'].iloc[0]:.2f}")
        print(f"   Last price: ${data5a['Close'].iloc[-1]:.2f}")
    else:
        print(f"❌ Data not reproducible!")
    print()
except Exception as e:
    print(f"❌ Failed: {e}")
    print()

print("=" * 70)
print("ALL TESTS COMPLETED")
print("=" * 70)
