"""
Base Strategy Class - Abstract base class for all trading strategies.

This implements the Template Method design pattern, where the base class
defines the skeleton of the algorithm (generate_signals -> calculate_positions)
and subclasses implement specific strategy logic.

WHY: This architecture ensures all strategies follow the same interface,
making it easy to swap strategies and maintain consistency across the platform.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd
import numpy as np


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.

    All strategies must implement:
    - generate_signals(): Produces buy/sell signals based on market data
    - validate_parameters(): Ensures strategy parameters are valid

    The base class provides:
    - Common interface for all strategies
    - Parameter validation framework
    - Position calculation from signals
    """

    def __init__(self, parameters: Dict[str, Any] = None):
        """
        Initialize strategy with parameters.

        Args:
            parameters: Strategy-specific parameters (e.g., window sizes, thresholds)

        WHY: Parameterized strategies allow for optimization and sensitivity analysis,
        which is critical for hedge funds to tune strategies to market conditions.
        """
        self.parameters = parameters or {}
        self.validate_parameters()

    @abstractmethod
    def validate_parameters(self) -> None:
        """
        Validate strategy parameters.

        WHY: Fail-fast validation prevents runtime errors during backtests.
        Better to catch invalid parameters (negative window sizes, etc.)
        before running expensive backtests.

        Raises:
            ValueError: If parameters are invalid
        """
        pass

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on market data.

        Args:
            data: DataFrame with OHLCV data (Open, High, Low, Close, Volume)
                  Index must be DatetimeIndex

        Returns:
            DataFrame with same index as input, containing 'signal' column:
            - 1.0: Buy signal (go long)
            - 0.0: Neutral (flat/no position)
            - -1.0: Sell signal (go short or exit long)

        WHY: Separating signal generation from position management allows for
        easier testing and strategy composition. Signals represent trade ideas,
        positions represent actual capital allocation.
        """
        pass

    def calculate_positions(self, signals: pd.DataFrame) -> pd.DataFrame:
        """
        Convert signals to positions using forward-fill.

        Args:
            signals: DataFrame with 'signal' column

        Returns:
            DataFrame with 'position' column representing current holdings

        WHY: In real trading, positions persist until a new signal arrives.
        Forward-fill simulates this behavior - if you bought yesterday and
        there's no signal today, you still hold the position.

        EDGE CASE HANDLING:
        - First position starts at 0 (no position before first signal)
        - Positions are shifted by 1 to avoid look-ahead bias (trade on next bar)
        """
        positions = pd.DataFrame(index=signals.index)

        # Replace NaN signals with 0 (no signal = no change)
        signals_filled = signals['signal'].fillna(0)

        # Forward-fill to maintain positions until next signal
        # WHY: This simulates holding a position until explicitly closing it
        positions['position'] = signals_filled.replace(0, np.nan).ffill().fillna(0)

        # Shift by 1 to avoid look-ahead bias
        # WHY: In real trading, you can't act on today's close until tomorrow's open.
        # This shift ensures we trade on the NEXT bar after a signal, preventing
        # unrealistic returns from impossible same-bar execution.
        positions['position'] = positions['position'].shift(1).fillna(0)

        return positions

    def get_parameter_info(self) -> Dict[str, Any]:
        """
        Get information about strategy parameters for API documentation.

        Returns:
            Dictionary with parameter names, types, defaults, and descriptions

        WHY: Self-documenting code is essential for team environments.
        This allows the frontend to dynamically generate parameter inputs
        without hardcoding strategy details.
        """
        return {
            'name': self.__class__.__name__,
            'parameters': self.parameters
        }
