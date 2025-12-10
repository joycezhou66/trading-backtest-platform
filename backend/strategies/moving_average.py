"""
Moving Average Crossover Strategy

Generates buy signals when fast MA crosses above slow MA,
sell signals when fast MA crosses below slow MA.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class MovingAverageStrategy(BaseStrategy):
    """
    Moving Average Crossover strategy.

    Parameters:
        fast_window: Fast MA period (default 20 days)
        slow_window: Slow MA period (default 50 days)
    """

    def __init__(self, parameters: Dict[str, Any] = None):
        """Initialize with default parameters if none provided."""
        default_params = {
            'fast_window': 20,
            'slow_window': 50
        }
        if parameters:
            default_params.update(parameters)

        super().__init__(default_params)

    def validate_parameters(self) -> None:
        """Validate strategy parameters."""
        fast = self.parameters.get('fast_window')
        slow = self.parameters.get('slow_window')

        if not isinstance(fast, (int, float)) or fast <= 0:
            raise ValueError(f"fast_window must be positive number, got {fast}")

        if not isinstance(slow, (int, float)) or slow <= 0:
            raise ValueError(f"slow_window must be positive number, got {slow}")

        if fast >= slow:
            raise ValueError(
                f"fast_window ({fast}) must be less than slow_window ({slow})"
            )

        # Warn if parameters are unusual (not an error, but might indicate mistake)
        if fast < 5:
            print(f"Warning: fast_window={fast} is very small, may be noisy")
        if slow > 200:
            print(f"Warning: slow_window={slow} is very large, may be laggy")

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on MA crossover."""
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        if len(data) < self.parameters['slow_window']:
            raise ValueError(
                f"Insufficient data: need at least {self.parameters['slow_window']} bars, "
                f"got {len(data)}"
            )

        # Calculate moving averages
        signals['fast_ma'] = data['Close'].rolling(
            window=self.parameters['fast_window'],
            min_periods=self.parameters['fast_window']
        ).mean()

        signals['slow_ma'] = data['Close'].rolling(
            window=self.parameters['slow_window'],
            min_periods=self.parameters['slow_window']
        ).mean()

        # Use np.where for vectorized comparison (faster than iterating)
        signals['position_raw'] = np.where(
            signals['fast_ma'] > signals['slow_ma'],
            1.0,
            0.0
        )

        # Use diff() to generate signals only at crossover points
        signals['signal'] = signals['position_raw'].diff()
        signals['signal'].iloc[0] = 0.0

        return signals[['signal', 'position_raw']]

    def calculate_positions(self, signals: pd.DataFrame) -> pd.DataFrame:
        """Convert signals to positions, shifted to avoid look-ahead bias."""
        positions = pd.DataFrame(index=signals.index)
        positions['position'] = signals['position_raw']
        # Shift by 1 period: can't trade on today's close until tomorrow
        positions['position'] = positions['position'].shift(1).fillna(0)
        return positions

    def get_parameter_info(self) -> Dict[str, Any]:
        """Return strategy metadata for API documentation."""
        return {
            'name': 'Moving Average Crossover',
            'description': 'Buys when fast MA crosses above slow MA, sells on cross below',
            'parameters': {
                'fast_window': {
                    'type': 'integer',
                    'default': 20,
                    'min': 5,
                    'max': 100,
                    'description': 'Fast moving average period (days)'
                },
                'slow_window': {
                    'type': 'integer',
                    'default': 50,
                    'min': 20,
                    'max': 200,
                    'description': 'Slow moving average period (days)'
                }
            },
            'typical_use': 'Trend following in trending markets',
            'strengths': 'Simple, captures strong trends, well-understood',
            'weaknesses': 'Whipsaw in sideways markets, lagging signals'
        }
