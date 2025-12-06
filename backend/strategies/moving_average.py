"""
Moving Average Crossover Strategy

CONCEPT: One of the most popular technical trading strategies.
Based on the idea that moving averages smooth out price noise and
reveal underlying trends.

LOGIC:
- Fast MA (short window) reacts quickly to price changes
- Slow MA (long window) shows long-term trend
- When fast MA crosses above slow MA = bullish signal (buy)
- When fast MA crosses below slow MA = bearish signal (sell)

WHY IT WORKS (in theory):
- Captures momentum when trends begin
- Filters out noise from random price fluctuations
- Follows the "trend is your friend" principle

LIMITATIONS:
- Whipsaw in sideways markets (many false signals)
- Lagging indicator (enters trades after trend starts)
- Not profitable in all market conditions

HEDGE FUND PERSPECTIVE:
While simple, this strategy teaches important concepts:
- Trend following
- Parameter sensitivity (window sizes)
- Risk/reward trade-offs
More sophisticated versions (exponential MA, adaptive windows) are used
in production.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class MovingAverageStrategy(BaseStrategy):
    """
    Moving Average Crossover strategy.

    Parameters:
        fast_window: Fast MA period (default 20 days ~ 1 month)
        slow_window: Slow MA period (default 50 days ~ 2.5 months)

    WHY THESE DEFAULTS: 20/50 is industry standard for daily data.
    Long enough to filter noise, short enough to catch trends early.
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
        """
        Validate strategy parameters.

        CHECKS:
        - Windows must be positive integers
        - Fast window must be less than slow window (otherwise not a "crossover")
        - Windows should be reasonable (not too small = noisy, not too large = laggy)
        """
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
        """
        Generate buy/sell signals based on MA crossover.

        ALGORITHM:
        1. Calculate fast and slow moving averages
        2. Identify crossover points
        3. Generate signals: 1 (buy), -1 (sell), 0 (no signal)

        WHY SIMPLE MA: More sophisticated MAs exist (EMA, WMA) but
        simple MA is easier to explain and still effective.

        EDGE CASES:
        - Insufficient data: Need at least slow_window bars to calculate
        - First slow_window bars have no signal (MA not ready yet)
        """
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        # Check we have enough data
        # WHY: Can't calculate 50-day MA with only 30 days of data
        if len(data) < self.parameters['slow_window']:
            raise ValueError(
                f"Insufficient data: need at least {self.parameters['slow_window']} bars, "
                f"got {len(data)}"
            )

        # Calculate moving averages
        # WHY .rolling(): Pandas built-in for efficient moving window calculations
        signals['fast_ma'] = data['Close'].rolling(
            window=self.parameters['fast_window'],
            min_periods=self.parameters['fast_window']
        ).mean()

        signals['slow_ma'] = data['Close'].rolling(
            window=self.parameters['slow_window'],
            min_periods=self.parameters['slow_window']
        ).mean()

        # Generate signals at crossover points
        # WHY: We only signal when MAs cross, not every bar where fast > slow
        # This reduces overtrading

        # Create position indicator: 1 when fast > slow, 0 otherwise
        signals['position_raw'] = np.where(
            signals['fast_ma'] > signals['slow_ma'],
            1.0,  # Fast above slow = bullish = long position
            0.0   # Fast below slow = bearish = no position (or short)
        )

        # Convert position changes to signals
        # Diff gives us: +1 when crossing up, -1 when crossing down, 0 otherwise
        # WHY diff(): Signal = change in position, not position itself
        # This way we only trade at crossovers, not every day
        signals['signal'] = signals['position_raw'].diff()

        # Clean up: first signal is NaN (no previous day to compare)
        signals['signal'].iloc[0] = 0.0

        return signals[['signal', 'position_raw']]

    def calculate_positions(self, signals: pd.DataFrame) -> pd.DataFrame:
        """
        Convert MA crossover signals to long-only positions.

        WHY OVERRIDE: Base class forward-fills signals which can create shorts.
        MA strategy is long-only: fast>slow = long (1), fast<slow = flat (0).
        """
        positions = pd.DataFrame(index=signals.index)

        # Use position_raw (already calculated in generate_signals)
        # position_raw = 1 when fast_ma > slow_ma, 0 otherwise
        positions['position'] = signals['position_raw']

        # Shift by 1 to avoid look-ahead bias
        # WHY: Can't act on today's MA calculation until tomorrow
        positions['position'] = positions['position'].shift(1).fillna(0)

        return positions

    def get_parameter_info(self) -> Dict[str, Any]:
        """
        Return strategy metadata for API documentation.

        WHY: Frontend can use this to generate parameter input forms
        without hardcoding strategy details.
        """
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
