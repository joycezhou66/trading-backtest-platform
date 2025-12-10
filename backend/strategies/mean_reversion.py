"""
Mean Reversion Strategy (Bollinger Bands)

Generates buy signals when price crosses below lower band,
sell signals when price crosses above upper band.
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
    """

    def __init__(self, parameters: Dict[str, Any] = None):
        """Initialize with default parameters if none provided."""
        default_params = {
            'window': 20,
            'num_std': 2.0
        }
        if parameters:
            default_params.update(parameters)

        super().__init__(default_params)

    def validate_parameters(self) -> None:
        """Validate strategy parameters."""
        window = self.parameters.get('window')
        num_std = self.parameters.get('num_std')

        if not isinstance(window, (int, float)) or window <= 0:
            raise ValueError(f"window must be positive number, got {window}")

        if not isinstance(num_std, (int, float)) or num_std <= 0:
            raise ValueError(f"num_std must be positive number, got {num_std}")

        if window < 10:
            print(f"Warning: window={window} is small, bands may be noisy")

        if num_std < 1.5 or num_std > 3.0:
            print(f"Warning: num_std={num_std} is unusual (typical: 1.5-3.0)")

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate signals based on Bollinger Band touches."""
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        if len(data) < self.parameters['window']:
            raise ValueError(
                f"Insufficient data: need at least {self.parameters['window']} bars, "
                f"got {len(data)}"
            )

        # Calculate Bollinger Bands
        signals['middle_band'] = data['Close'].rolling(
            window=self.parameters['window'],
            min_periods=self.parameters['window']
        ).mean()

        signals['std'] = data['Close'].rolling(
            window=self.parameters['window'],
            min_periods=self.parameters['window']
        ).std()

        signals['upper_band'] = signals['middle_band'] + (
            self.parameters['num_std'] * signals['std']
        )
        signals['lower_band'] = signals['middle_band'] - (
            self.parameters['num_std'] * signals['std']
        )

        signals['price'] = data['Close']

        # Generate signals at band crosses
        for i in range(1, len(signals)):
            current_price = signals['price'].iloc[i]
            prev_price = signals['price'].iloc[i-1]
            lower = signals['lower_band'].iloc[i]
            upper = signals['upper_band'].iloc[i]
            middle = signals['middle_band'].iloc[i]

            if pd.isna(lower) or pd.isna(upper):
                continue

            # Buy when price crosses below lower band
            if prev_price >= lower and current_price < lower:
                signals.iloc[i, signals.columns.get_loc('signal')] = 1.0

            # Sell when price crosses above upper band
            elif prev_price <= upper and current_price > upper:
                signals.iloc[i, signals.columns.get_loc('signal')] = -1.0

            elif abs(current_price - middle) < signals['std'].iloc[i] * 0.5:
                pass

        # Track positions
        signals['position_raw'] = 0.0
        position = 0.0
        for i in range(len(signals)):
            if signals['signal'].iloc[i] == 1.0:
                position = 1.0
            elif signals['signal'].iloc[i] == -1.0:
                position = 0.0
            signals.iloc[i, signals.columns.get_loc('position_raw')] = position

        return signals[['signal', 'position_raw']]

    def calculate_positions(self, signals: pd.DataFrame) -> pd.DataFrame:
        """Convert signals to positions, shifted to avoid look-ahead bias."""
        positions = pd.DataFrame(index=signals.index)
        positions['position'] = signals['position_raw']
        positions['position'] = positions['position'].shift(1).fillna(0)
        return positions

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
