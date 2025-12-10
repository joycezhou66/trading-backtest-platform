"""
Momentum Strategy (RSI - Relative Strength Index)

Generates buy signals when RSI crosses above oversold threshold,
sell signals when RSI crosses below overbought threshold.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """
    Momentum strategy using RSI (Relative Strength Index).

    Parameters:
        window: RSI calculation period (default 14 days)
        oversold: Oversold threshold (default 30)
        overbought: Overbought threshold (default 70)
    """

    def __init__(self, parameters: Dict[str, Any] = None):
        """Initialize with default parameters if none provided."""
        default_params = {
            'window': 14,
            'oversold': 30,
            'overbought': 70
        }
        if parameters:
            default_params.update(parameters)

        super().__init__(default_params)

    def validate_parameters(self) -> None:
        """Validate strategy parameters."""
        window = self.parameters.get('window')
        oversold = self.parameters.get('oversold')
        overbought = self.parameters.get('overbought')

        if not isinstance(window, (int, float)) or window <= 0:
            raise ValueError(f"window must be positive number, got {window}")

        if not isinstance(oversold, (int, float)) or not (0 < oversold < 100):
            raise ValueError(f"oversold must be between 0 and 100, got {oversold}")

        if not isinstance(overbought, (int, float)) or not (0 < overbought < 100):
            raise ValueError(f"overbought must be between 0 and 100, got {overbought}")

        if oversold >= overbought:
            raise ValueError(
                f"oversold ({oversold}) must be less than overbought ({overbought})"
            )

        if window < 7:
            print(f"Warning: window={window} is small, RSI may be noisy")
        if window > 28:
            print(f"Warning: window={window} is large, RSI may be laggy")

    def _calculate_rsi(self, prices: pd.Series, window: int) -> pd.Series:
        """
        Calculate RSI (Relative Strength Index).

        Args:
            prices: Series of closing prices
            window: RSI period

        Returns:
            Series of RSI values (0-100)
        """
        delta = prices.diff()
        gains = delta.where(delta > 0, 0.0)
        losses = -delta.where(delta < 0, 0.0)

        avg_gains = gains.ewm(span=window, adjust=False).mean()
        avg_losses = losses.ewm(span=window, adjust=False).mean()

        rs = avg_gains / avg_losses
        rsi = 100.0 - (100.0 / (1.0 + rs))
        rsi = rsi.fillna(100.0)

        return rsi

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate signals based on RSI crossovers."""
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        if len(data) < self.parameters['window'] + 1:
            raise ValueError(
                f"Insufficient data: need at least {self.parameters['window'] + 1} bars, "
                f"got {len(data)}"
            )

        # Calculate RSI
        signals['rsi'] = self._calculate_rsi(
            data['Close'],
            self.parameters['window']
        )

        oversold = self.parameters['oversold']
        overbought = self.parameters['overbought']

        # Generate signals at threshold crossovers
        for i in range(1, len(signals)):
            current_rsi = signals['rsi'].iloc[i]
            prev_rsi = signals['rsi'].iloc[i-1]

            if pd.isna(current_rsi) or pd.isna(prev_rsi):
                continue

            # Buy when RSI crosses above oversold threshold
            if prev_rsi <= oversold and current_rsi > oversold:
                signals.iloc[i, signals.columns.get_loc('signal')] = 1.0

            # Sell when RSI crosses below overbought threshold
            elif prev_rsi >= overbought and current_rsi < overbought:
                signals.iloc[i, signals.columns.get_loc('signal')] = -1.0

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
            'name': 'Momentum (RSI)',
            'description': 'Buys when RSI exits oversold, sells when exits overbought',
            'parameters': {
                'window': {
                    'type': 'integer',
                    'default': 14,
                    'min': 7,
                    'max': 28,
                    'description': 'RSI calculation period (days)'
                },
                'oversold': {
                    'type': 'integer',
                    'default': 30,
                    'min': 10,
                    'max': 40,
                    'description': 'Oversold threshold (buy when RSI crosses above)'
                },
                'overbought': {
                    'type': 'integer',
                    'default': 70,
                    'min': 60,
                    'max': 90,
                    'description': 'Overbought threshold (sell when RSI crosses below)'
                }
            },
            'typical_use': 'Identifying oversold/overbought reversals',
            'strengths': 'Bounded indicator (0-100), widely used, catches reversals',
            'weaknesses': 'Can stay overbought/oversold in trends, lagging'
        }
