"""
Generate static data files for deployment to avoid Yahoo Finance rate limiting.

This creates pre-downloaded CSV files for common tickers that will be bundled
with the deployment, ensuring demos always work regardless of API availability.
"""

import yfinance as yf
import pandas as pd
from pathlib import Path

# Demo tickers to pre-cache
DEMO_TICKERS = ['AAPL', 'SPY', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

# Date range for demo data
START_DATE = '2020-01-01'
END_DATE = '2024-12-01'

# Output directory
OUTPUT_DIR = Path(__file__).parent / 'static_data'
OUTPUT_DIR.mkdir(exist_ok=True)

def download_and_save(ticker: str):
    """Download ticker data and save as CSV."""
    print(f"Downloading {ticker}...")
    try:
        # Try using period='max' first (more reliable)
        ticker_obj = yf.Ticker(ticker)
        data = ticker_obj.history(period="5y")  # Get 5 years of data

        if data.empty:
            print(f"  ❌ No data for {ticker}")
            return False

        # Filter to our date range
        data = data[START_DATE:END_DATE]

        # Save as CSV
        filename = f"{ticker}_{START_DATE}_{END_DATE}.csv"
        filepath = OUTPUT_DIR / filename
        data.to_csv(filepath)

        print(f"  ✅ Saved {len(data)} rows to {filename}")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("Generating static data files for deployment...")
    print("=" * 60)

    success_count = 0
    for ticker in DEMO_TICKERS:
        if download_and_save(ticker):
            success_count += 1

    print("=" * 60)
    print(f"Successfully generated {success_count}/{len(DEMO_TICKERS)} files")
    print(f"Files saved to: {OUTPUT_DIR}")
