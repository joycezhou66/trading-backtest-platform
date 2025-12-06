"""
Create realistic sample market data for demo purposes.

Uses realistic price movements based on typical stock behavior.
This ensures the demo always works regardless of API availability.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# Output directory
OUTPUT_DIR = Path(__file__).parent / 'static_data'
OUTPUT_DIR.mkdir(exist_ok=True)

# Date range
START_DATE = '2020-01-01'
END_DATE = '2024-12-01'

def generate_realistic_stock_data(ticker: str, start_price: float, volatility: float, trend: float):
    """
    Generate realistic stock price data using geometric Brownian motion.

    Args:
        ticker: Stock symbol
        start_price: Initial price
        volatility: Daily volatility (e.g., 0.02 = 2%)
        trend: Annual drift/trend (e.g., 0.10 = 10% annual growth)
    """
    # Generate date range
    dates = pd.date_range(start=START_DATE, end=END_DATE, freq='B')  # Business days only
    n_days = len(dates)

    # Generate random returns using geometric Brownian motion
    # WHY: This is how actual stock prices behave (random walk with drift)
    daily_returns = np.random.normal(trend/252, volatility, n_days)
    price_series = start_price * np.exp(np.cumsum(daily_returns))

    # Generate OHLCV data
    # WHY: Realistic intraday movements for backtesting
    data = pd.DataFrame(index=dates)
    data['Close'] = price_series
    data['Open'] = data['Close'] * (1 + np.random.normal(0, volatility/4, n_days))
    data['High'] = np.maximum(data['Open'], data['Close']) * (1 + np.abs(np.random.normal(0, volatility/2, n_days)))
    data['Low'] = np.minimum(data['Open'], data['Close']) * (1 - np.abs(np.random.normal(0, volatility/2, n_days)))
    data['Adj Close'] = data['Close']  # Same as close for our purposes
    data['Volume'] = np.random.randint(50_000_000, 150_000_000, n_days)

    # Round to realistic precision
    data[['Open', 'High', 'Low', 'Close', 'Adj Close']] = data[['Open', 'High', 'Low', 'Close', 'Adj Close']].round(2)

    # Save to CSV
    filename = f"{ticker}_{START_DATE}_{END_DATE}.csv"
    filepath = OUTPUT_DIR / filename
    data.to_csv(filepath)

    print(f"✅ {ticker}: Generated {len(data)} days, price range ${data['Low'].min():.2f}-${data['High'].max():.2f}")

    return data

# Generate data for demo tickers with realistic parameters
DEMO_STOCKS = {
    'AAPL': {'start_price': 75, 'volatility': 0.020, 'trend': 0.25},   # High growth tech
    'SPY': {'start_price': 320, 'volatility': 0.012, 'trend': 0.12},   # Market index, lower vol
    'MSFT': {'start_price': 160, 'volatility': 0.018, 'trend': 0.22},  # Steady tech giant
    'GOOGL': {'start_price': 1400, 'volatility': 0.019, 'trend': 0.18}, # Large cap tech
    'AMZN': {'start_price': 1850, 'volatility': 0.025, 'trend': 0.15},  # High vol ecommerce
    'TSLA': {'start_price': 85, 'volatility': 0.040, 'trend': 0.50},   # Very volatile growth
}

if __name__ == '__main__':
    print("Generating realistic sample data for demo...")
    print("=" * 60)

    for ticker, params in DEMO_STOCKS.items():
        generate_realistic_stock_data(ticker, **params)

    print("=" * 60)
    print(f"Successfully generated {len(DEMO_STOCKS)} data files")
    print(f"Files saved to: {OUTPUT_DIR}")
    print("\nThese files will be bundled with deployment for reliable demos.")
