"""
Mean Reversion Strategy (Bollinger Bands)

CONCEPT: "What goes up must come down" - prices tend to revert to their mean.

THEORY:
- Asset prices fluctuate around a long-term average (mean)
- Extreme deviations from mean are temporary
- When price is far above mean = overextended = likely to fall (sell)
- When price is far below mean = oversold = likely to rise (buy)

BOLLINGER BANDS:
- Middle band = 20-day moving average (the "mean")
- Upper band = Mean + 2 standard deviations
- Lower band = Mean - 2 standard deviations

STATISTICAL BASIS:
- Normal distribution: ~95% of data falls within 2 std devs
- Price touching outer bands = rare event = likely reversal

WHY IT WORKS (sometimes):
- Markets do exhibit mean reversion over certain timeframes
- Captures oversold/overbought conditions
- Works well in range-bound markets

LIMITATIONS:
- Fails in strong trends (price can stay "overextended")
- Assumes normal distribution (markets have fat tails)
- "The market can stay irrational longer than you can stay solvent"

HEDGE FUND PERSPECTIVE:
Mean reversion is basis of many quant strategies (pairs trading, statistical arbitrage).
This simple version teaches the concept. Production systems use more sophisticated
mean reversion models with dynamic thresholds.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """
    Mean reversion strategy using Bollinger Bands.

    Parameters:
        window: Period for MA and std dev calculation (default 20 days)
        num_std: Number of standard deviations for bands (default 2)

    LOGIC:
    - Buy when price touches/crosses below lower band (oversold)
    - Sell when price touches/crosses above upper band (overbought)
    - Exit when price returns to middle band (mean)
    """

    def __init__(self, parameters: Dict[str, Any] = None):
        """Initialize with default parameters if none provided."""
        default_params = {
            'window': 20,      # WHY 20: Standard Bollinger Band setting
            'num_std': 2.0     # WHY 2.0: Captures ~95% of normal distribution
        }
        if parameters:
            default_params.update(parameters)

        super().__init__(default_params)

    def validate_parameters(self) -> None:
        """
        Validate strategy parameters.

        CHECKS:
        - Window must be positive
        - Num_std must be positive and reasonable
        """
        window = self.parameters.get('window')
        num_std = self.parameters.get('num_std')

        if not isinstance(window, (int, float)) or window <= 0:
            raise ValueError(f"window must be positive number, got {window}")

        if not isinstance(num_std, (int, float)) or num_std <= 0:
            raise ValueError(f"num_std must be positive number, got {num_std}")

        # Sanity checks
        if window < 10:
            print(f"Warning: window={window} is small, bands may be noisy")

        if num_std < 1.5 or num_std > 3.0:
            print(f"Warning: num_std={num_std} is unusual (typical: 1.5-3.0)")

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate signals based on Bollinger Band touches.

        ALGORITHM:
        1. Calculate middle band (moving average)
        2. Calculate standard deviation
        3. Calculate upper/lower bands
        4. Generate signals when price crosses bands

        SIGNAL LOGIC:
        - Price crosses below lower band → Buy signal (1)
        - Price crosses above upper band → Sell signal (-1)
        - Price returns to middle band → Exit signal (opposite of current position)

        EDGE CASES:
        - Need at least 'window' bars for calculation
        - First 'window' bars have no signals
        """
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        # Validate data length
        if len(data) < self.parameters['window']:
            raise ValueError(
                f"Insufficient data: need at least {self.parameters['window']} bars, "
                f"got {len(data)}"
            )

        # Calculate middle band (simple moving average)
        # WHY: This is our "mean" that price should revert to
        signals['middle_band'] = data['Close'].rolling(
            window=self.parameters['window'],
            min_periods=self.parameters['window']
        ).mean()

        # Calculate standard deviation
        # WHY: Measures volatility - when volatility is high, bands widen
        signals['std'] = data['Close'].rolling(
            window=self.parameters['window'],
            min_periods=self.parameters['window']
        ).std()

        # Calculate upper and lower bands
        signals['upper_band'] = signals['middle_band'] + (
            self.parameters['num_std'] * signals['std']
        )
        signals['lower_band'] = signals['middle_band'] - (
            self.parameters['num_std'] * signals['std']
        )

        # Store price for convenience
        signals['price'] = data['Close']

        # Generate signals
        # WHY SEPARATE LOOPS: Clearer logic, easier to debug
        # Could be vectorized but this is more readable for interview

        for i in range(1, len(signals)):
            current_price = signals['price'].iloc[i]
            prev_price = signals['price'].iloc[i-1]
            lower = signals['lower_band'].iloc[i]
            upper = signals['upper_band'].iloc[i]
            middle = signals['middle_band'].iloc[i]

            # Skip if bands not ready yet (NaN)
            if pd.isna(lower) or pd.isna(upper):
                continue

            # BUY SIGNAL: Price crosses below lower band
            # WHY: Price is "too low", expect reversion upward
            if prev_price >= lower and current_price < lower:
                signals.iloc[i, signals.columns.get_loc('signal')] = 1.0

            # SELL SIGNAL: Price crosses above upper band
            # WHY: Price is "too high", expect reversion downward
            elif prev_price <= upper and current_price > upper:
                signals.iloc[i, signals.columns.get_loc('signal')] = -1.0

            # Optional: Exit when price returns to mean
            # This is a design choice - you could also hold until opposite band
            # WHY: Taking profit when reverted to mean locks in gains
            elif abs(current_price - middle) < signals['std'].iloc[i] * 0.5:
                # Price near middle = mean reversion complete
                # Signal 0 means "close position" (handled in position calculation)
                pass  # Keep as 0

        return signals[['signal']]

    def get_parameter_info(self) -> Dict[str, Any]:
        """Return strategy metadata for API documentation."""
        return {
            'name': 'Mean Reversion (Bollinger Bands)',
            'description': 'Buys when price is oversold (touches lower band), sells when overbought',
            'parameters': {
                'window': {
                    'type': 'integer',
                    'default': 20,
                    'min': 10,
                    'max': 50,
                    'description': 'Period for moving average and std dev calculation'
                },
                'num_std': {
                    'type': 'float',
                    'default': 2.0,
                    'min': 1.0,
                    'max': 3.0,
                    'step': 0.5,
                    'description': 'Number of standard deviations for band width'
                }
            },
            'typical_use': 'Range-bound markets, capturing short-term reversions',
            'strengths': 'Exploits volatility, statistical foundation, defined entry/exit',
            'weaknesses': 'Fails in strong trends, assumes normal distribution'
        }
