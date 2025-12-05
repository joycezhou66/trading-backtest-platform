"""
Data Handler - Manages market data fetching and caching.

WHY CACHING: During interviews/demos, you can't afford to wait for API calls.
Pre-caching common tickers ensures instant backtests. Also respects API rate limits.

DESIGN DECISION: Use pickle for caching instead of CSV because:
- Preserves data types (dates, floats) without parsing overhead
- Faster serialization/deserialization
- Maintains pandas index structure
"""

import os
import pickle
import logging
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import yfinance as yf

# Configure logging to track cache hits/misses
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataHandler:
    """
    Handles downloading, caching, and retrieving market data.

    Architecture:
    1. Check cache first (fast path)
    2. Download if cache miss (slow path)
    3. Always cache downloads for future use

    WHY: This pattern (cache-aside) is standard in production systems.
    Reduces latency and external dependencies.
    """

    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize data handler.

        Args:
            cache_dir: Directory to store cached data files

        WHY: Configurable cache directory allows testing with temp directories
        and production use with persistent storage.
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_path(self, ticker: str, start_date: str, end_date: str) -> str:
        """
        Generate cache file path for given parameters.

        WHY: Deterministic naming scheme based on query parameters ensures
        we cache the exact data requested and retrieve it correctly.

        Format: {ticker}_{start_date}_{end_date}.pkl
        """
        return os.path.join(
            self.cache_dir,
            f"{ticker}_{start_date}_{end_date}.pkl"
        )

    def _load_from_cache(self, cache_path: str, max_age_days: int = 1) -> Optional[pd.DataFrame]:
        """
        Load data from cache if it exists and is recent.

        Args:
            cache_path: Path to cached pickle file
            max_age_days: Maximum age of cache in days (default 1)

        Returns:
            DataFrame if cache hit, None if cache miss

        WHY MAX_AGE: Market data becomes stale. For historical backtests,
        1-day old cache is fine. For live trading, you'd want fresher data.

        EDGE CASE: Corrupted cache files are caught and treated as cache miss.
        """
        if not os.path.exists(cache_path):
            return None

        # Check file age
        file_modified = datetime.fromtimestamp(os.path.getmtime(cache_path))
        age = datetime.now() - file_modified

        if age.days > max_age_days:
            logger.info(f"Cache expired (age: {age.days} days): {cache_path}")
            return None

        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            logger.info(f"Cache HIT: {cache_path}")
            return data
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None

    def _save_to_cache(self, data: pd.DataFrame, cache_path: str) -> None:
        """
        Save DataFrame to cache.

        WHY: Atomic write pattern (write to temp, then rename) prevents
        corrupted caches if write is interrupted.
        """
        try:
            temp_path = cache_path + '.tmp'
            with open(temp_path, 'wb') as f:
                pickle.dump(data, f)
            os.replace(temp_path, cache_path)  # Atomic operation
            logger.info(f"Cached data: {cache_path}")
        except Exception as e:
            logger.error(f"Cache write error: {e}")

    def _download_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Download data from yfinance.

        WHY YFINANCE: Free, reliable, and widely used. Provides adjusted close
        prices which account for splits/dividends (critical for accurate backtests).

        Returns:
            DataFrame with OHLCV data

        Raises:
            ValueError: If download fails or data is empty
        """
        logger.info(f"Downloading {ticker} from {start_date} to {end_date}")

        try:
            # Download data with auto_adjust=True to get split/dividend adjusted prices
            # WHY: Unadjusted prices give false signals at split events
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False,
                auto_adjust=True  # Critical for accurate backtests
            )

            if data.empty:
                raise ValueError(f"No data returned for {ticker}")

            # Ensure we have the required columns
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing = set(required_cols) - set(data.columns)
            if missing:
                raise ValueError(f"Missing columns: {missing}")

            return data

        except Exception as e:
            raise ValueError(f"Download failed for {ticker}: {str(e)}")

    def get_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Get market data, using cache when possible.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            use_cache: Whether to use cached data (default True)

        Returns:
            DataFrame with OHLCV data and DatetimeIndex

        WHY SEPARATE use_cache FLAG: Sometimes you want fresh data (e.g., live trading).
        This flag allows bypassing cache when needed.

        FLOW:
        1. Try cache (if enabled)
        2. Download if cache miss
        3. Save to cache for future use
        4. Return data
        """
        cache_path = self._get_cache_path(ticker, start_date, end_date)

        # Try cache first
        if use_cache:
            cached_data = self._load_from_cache(cache_path)
            if cached_data is not None:
                return cached_data

        # Cache miss - download data
        logger.info(f"Cache MISS: {ticker}")
        data = self._download_data(ticker, start_date, end_date)

        # Save to cache for next time
        if use_cache:
            self._save_to_cache(data, cache_path)

        return data

    def pre_cache_data(
        self,
        tickers: list[str],
        start_date: str = "2018-01-01",
        end_date: str = "2024-12-01"
    ) -> dict[str, str]:
        """
        Pre-download and cache data for multiple tickers.

        Args:
            tickers: List of ticker symbols
            start_date: Start date for all tickers
            end_date: End date for all tickers

        Returns:
            Dictionary mapping tickers to status ('success' or error message)

        WHY: Run this before demos to ensure all backtests are instant.
        No waiting for API calls during your presentation.

        DESIGN DECISION: Return status dict instead of raising errors so
        partial failures don't block caching other tickers.
        """
        results = {}

        for ticker in tickers:
            try:
                self.get_data(ticker, start_date, end_date, use_cache=True)
                results[ticker] = 'success'
                logger.info(f"Pre-cached {ticker}")
            except Exception as e:
                results[ticker] = f"error: {str(e)}"
                logger.error(f"Failed to cache {ticker}: {e}")

        return results

    def validate_date_range(self, start_date: str, end_date: str) -> None:
        """
        Validate date range parameters.

        WHY: Fail fast on invalid inputs. Better to catch errors here than
        after downloading data or during backtest.

        Raises:
            ValueError: If dates are invalid or in wrong order
        """
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Invalid date format. Use YYYY-MM-DD: {e}")

        if start >= end:
            raise ValueError("start_date must be before end_date")

        if end > datetime.now():
            raise ValueError("end_date cannot be in the future")

        if start < datetime(1990, 1, 1):
            raise ValueError("start_date too far in past (before 1990)")
