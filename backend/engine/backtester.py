"""
Backtesting Engine - Executes strategies on historical data.

WHY SEPARATE ENGINE: Decoupling strategy logic from execution allows:
- Testing strategies independently
- Swapping execution models (e.g., add slippage, transaction costs)
- Running same strategy on different data

DESIGN PATTERN: This is the Strategy pattern - the engine executes
any object implementing the BaseStrategy interface.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)


class Backtester:
    """
    Backtesting engine that executes strategies on historical data.

    ASSUMPTIONS (standard in backtesting, but important to know for interviews):
    - Trade at close prices (could be improved with VWAP or next-bar open)
    - No slippage (real fills may be worse than close price)
    - No transaction costs (unrealistic but keeps demo simple)
    - Infinite liquidity (can buy/sell any amount)
    - No short-selling constraints (can short freely)

    WHY THESE ASSUMPTIONS: They're industry standard for initial strategy testing.
    In production, you'd add transaction cost models and slippage.
    """

    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize backtester.

        Args:
            initial_capital: Starting capital in dollars

        WHY $100K DEFAULT: Standard starting capital for backtests.
        Large enough to be realistic, small enough to avoid liquidity issues.
        """
        self.initial_capital = initial_capital

    def run(
        self,
        strategy: BaseStrategy,
        data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Execute strategy backtest on historical data.

        Args:
            strategy: Strategy instance implementing BaseStrategy
            data: DataFrame with OHLCV data

        Returns:
            Dictionary containing:
            - equity_curve: Time series of portfolio value
            - positions: Time series of positions held
            - trades: List of individual trades
            - returns: Period returns

        WHY RETURN DICT: Flexible format that's easy to serialize to JSON
        for API responses. Contains all data needed for analysis.

        FLOW:
        1. Generate signals using strategy
        2. Convert signals to positions
        3. Calculate returns from positions
        4. Track equity curve
        5. Extract individual trades
        """
        logger.info(f"Running backtest with {strategy.__class__.__name__}")

        # Validate input data
        self._validate_data(data)

        # Step 1: Generate trading signals
        signals = strategy.generate_signals(data)

        # Step 2: Convert signals to positions
        positions = strategy.calculate_positions(signals)

        # Step 3: Calculate returns
        # WHY pct_change(): Gives us period-to-period returns
        # WHY fillna(0): First return is NaN, treat as 0
        returns = data['Close'].pct_change().fillna(0)

        # Step 4: Calculate strategy returns
        # Position * return gives us the return we capture
        # WHY: If we're long (position=1) and market goes up (return=+0.02),
        # we earn +0.02. If we're flat (position=0), we earn 0 regardless of market.
        strategy_returns = positions['position'] * returns

        # Step 5: Calculate equity curve
        # WHY cumulative product: (1 + return) compounded over time
        # Example: +2% then +3% = 1.02 * 1.03 = 1.0506 (5.06% total)
        equity_curve = self.initial_capital * (1 + strategy_returns).cumprod()

        # Step 6: Extract individual trades
        trades = self._extract_trades(positions, data['Close'])

        # Step 7: Compile results
        results = {
            'equity_curve': equity_curve.tolist(),
            'equity_dates': equity_curve.index.strftime('%Y-%m-%d').tolist(),
            'positions': positions['position'].tolist(),
            'position_dates': positions.index.strftime('%Y-%m-%d').tolist(),
            'returns': strategy_returns.tolist(),
            'trades': trades,
            'initial_capital': self.initial_capital
        }

        logger.info(f"Backtest complete. {len(trades)} trades executed.")

        return results

    def _validate_data(self, data: pd.DataFrame) -> None:
        """
        Validate input data has required structure.

        WHY: Fail fast on invalid inputs. Better error messages help debugging.

        Raises:
            ValueError: If data is invalid
        """
        if data.empty:
            raise ValueError("Data is empty")

        required_cols = ['Close', 'Open', 'High', 'Low']
        missing = set(required_cols) - set(data.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data index must be DatetimeIndex")

        if len(data) < 50:
            raise ValueError("Insufficient data (minimum 50 bars required for meaningful backtest)")

    def _extract_trades(
        self,
        positions: pd.DataFrame,
        prices: pd.Series
    ) -> List[Dict[str, Any]]:
        """
        Extract individual trades from position time series.

        A trade occurs when position changes from 0 to non-zero (entry)
        and back to 0 (exit).

        Returns:
            List of trade dictionaries with entry/exit dates, prices, and P&L

        WHY TRACK TRADES: Individual trade analysis is critical for:
        - Calculating win rate
        - Understanding trade duration
        - Identifying best/worst trades
        - Detecting overfitting (too few trades = unreliable strategy)

        ALGORITHM:
        1. Find position changes (diff)
        2. Entry = position goes from 0 to non-zero
        3. Exit = position goes from non-zero to 0
        4. Calculate P&L for each completed trade
        """
        trades = []
        position_changes = positions['position'].diff()

        # Track current trade
        current_trade = None

        for date, pos in positions.iterrows():
            current_pos = pos['position']
            prev_pos = positions.loc[:date, 'position'].iloc[-2] if len(positions.loc[:date]) > 1 else 0

            # Entry: position changes from 0 to non-zero
            if prev_pos == 0 and current_pos != 0:
                current_trade = {
                    'entry_date': date.strftime('%Y-%m-%d'),
                    'entry_price': prices.loc[date],
                    'direction': 'long' if current_pos > 0 else 'short',
                    'size': abs(current_pos)
                }

            # Exit: position changes from non-zero to 0
            elif prev_pos != 0 and current_pos == 0 and current_trade is not None:
                exit_price = prices.loc[date]
                entry_price = current_trade['entry_price']

                # Calculate P&L
                # WHY: Long trade profits when price increases, short when decreases
                if current_trade['direction'] == 'long':
                    pnl_pct = (exit_price - entry_price) / entry_price
                else:  # short
                    pnl_pct = (entry_price - exit_price) / entry_price

                current_trade['exit_date'] = date.strftime('%Y-%m-%d')
                current_trade['exit_price'] = exit_price
                current_trade['pnl_percent'] = pnl_pct * 100  # Convert to percentage
                current_trade['pnl_dollars'] = self.initial_capital * pnl_pct

                trades.append(current_trade)
                current_trade = None

        return trades

    def run_multiple_strategies(
        self,
        strategies: List[Tuple[str, BaseStrategy]],
        data: pd.DataFrame
    ) -> Dict[str, Dict[str, Any]]:
        """
        Run multiple strategies for comparison.

        Args:
            strategies: List of (name, strategy) tuples
            data: Market data

        Returns:
            Dictionary mapping strategy names to results

        WHY: Comparing multiple strategies on same data is common workflow.
        This method makes it convenient and ensures same data is used.
        """
        results = {}

        for name, strategy in strategies:
            logger.info(f"Running strategy: {name}")
            results[name] = self.run(strategy, data)

        return results
