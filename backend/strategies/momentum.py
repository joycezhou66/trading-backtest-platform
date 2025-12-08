"""
Momentum Strategy (RSI - Relative Strength Index)

CONCEPT: "The trend is your friend" - assets showing strength continue to strengthen.

MOMENTUM THEORY:
- Momentum = rate of price change
- Assets with positive momentum tend to continue rising (persistence)
- Assets with negative momentum tend to continue falling
- Behavioral finance: Investors underreact to news → momentum persists

RSI (Relative Strength Index):
- Oscillator ranging from 0 to 100
- Measures magnitude of recent price changes
- RSI > 70 = overbought (too much buying pressure)
- RSI < 30 = oversold (too much selling pressure)

CALCULATION:
1. Calculate average gains and losses over N periods
2. RS (Relative Strength) = Average Gain / Average Loss
3. RSI = 100 - (100 / (1 + RS))

WHY IT WORKS:
- Identifies when sentiment has gone too far in one direction
- Mean reversion at extremes (oversold → buy, overbought → sell)
- Widely watched = self-fulfilling prophecy

TRADING LOGIC (Contrarian approach):
- RSI crosses above 30 (leaving oversold) = Buy signal
- RSI crosses below 70 (leaving overbought) = Sell signal

WHY CONTRARIAN: We buy when oversold conditions END (not during).
This catches the reversal rather than trying to catch falling knives.

LIMITATIONS:
- Can stay overbought/oversold for extended periods in trends
- Whipsaw at threshold boundaries
- Lagging indicator (based on past prices)

HEDGE FUND PERSPECTIVE:
RSI is widely used in:
- Mean reversion strategies
- Market timing overlays
- Risk management (avoid buying overbought assets)
Production systems combine RSI with other indicators (MACD, volume, etc.)
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

    WHY 14/30/70: J. Welles Wilder's original RSI specification (1978).
    These values have become industry standard through decades of use.
    """

    def __init__(self, parameters: Dict[str, Any] = None):
        """Initialize with default parameters if none provided."""
        default_params = {
            'window': 14,      # WHY 14: Wilder's original setting, balances sensitivity/stability
            'oversold': 30,    # WHY 30: Standard oversold threshold
            'overbought': 70   # WHY 70: Standard overbought threshold
        }
        if parameters:
            default_params.update(parameters)

        super().__init__(default_params)

    def validate_parameters(self) -> None:
        """
        Validate strategy parameters.

        CHECKS:
        - Window must be positive
        - Thresholds must be between 0 and 100
        - Oversold < overbought (otherwise nonsensical)
        """
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

        # Sanity checks
        if window < 7:
            print(f"Warning: window={window} is small, RSI may be noisy")
        if window > 28:
            print(f"Warning: window={window} is large, RSI may be laggy")

    def _calculate_rsi(self, prices: pd.Series, window: int) -> pd.Series:
        """
        Calculate RSI (Relative Strength Index).

        WHY SEPARATE METHOD: RSI calculation is complex enough to deserve
        its own well-tested function. Easier to debug and unit test.

        ALGORITHM (Wilder's smoothing method):
        1. Calculate price changes (deltas)
        2. Separate gains and losses
        3. Calculate exponential moving average of gains and losses
        4. RS = EMA(gains) / EMA(losses)
        5. RSI = 100 - (100 / (1 + RS))

        Args:
            prices: Series of closing prices
            window: RSI period

        Returns:
            Series of RSI values (0-100)

        EDGE CASES:
        - Division by zero: If no losses, RSI = 100
        - First 'window' values are NaN (not enough data)
        """
        # Calculate price changes
        delta = prices.diff()

        # Separate gains and losses
        # WHY: RSI compares upward vs downward momentum
        gains = delta.where(delta > 0, 0.0)  # Positive changes only
        losses = -delta.where(delta < 0, 0.0)  # Negative changes (as positive values)

        # Calculate exponential moving averages
        # WHY EMA: Wilder's original method uses EMA for smoothing
        # This gives more weight to recent data while incorporating history
        avg_gains = gains.ewm(span=window, adjust=False).mean()
        avg_losses = losses.ewm(span=window, adjust=False).mean()

        # Calculate RS (Relative Strength)
        # EDGE CASE: If avg_losses is 0, RS is infinite → RSI = 100
        rs = avg_gains / avg_losses

        # Calculate RSI
        rsi = 100.0 - (100.0 / (1.0 + rs))

        # Handle edge case where avg_losses = 0
        rsi = rsi.fillna(100.0)

        return rsi

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate signals based on RSI crossovers.

        STRATEGY LOGIC:
        - Buy when RSI crosses above oversold threshold (30)
          WHY: Oversold condition is ending, reversal likely
        - Sell when RSI crosses below overbought threshold (70)
          WHY: Overbought condition is ending, pullback likely

        NOTE: This is CONTRARIAN approach (buy when leaving oversold,
        not when entering oversold). Alternative MOMENTUM approach would
        buy on strength (RSI > 50), sell on weakness (RSI < 50).

        Returns:
            DataFrame with 'signal' column
        """
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        # Validate data length
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

        # Generate signals based on threshold crossovers
        # WHY CROSSOVER not LEVEL: Signal when crossing threshold,
        # not continuously while above/below. Reduces overtrading.

        oversold = self.parameters['oversold']
        overbought = self.parameters['overbought']

        for i in range(1, len(signals)):
            current_rsi = signals['rsi'].iloc[i]
            prev_rsi = signals['rsi'].iloc[i-1]

            # Skip if RSI not ready yet
            if pd.isna(current_rsi) or pd.isna(prev_rsi):
                continue

            # BUY SIGNAL: RSI crosses above oversold threshold
            # WHY: This is the reversal point - oversold condition is ending
            # We're not catching falling knives, we're buying the bounce
            if prev_rsi <= oversold and current_rsi > oversold:
                signals.iloc[i, signals.columns.get_loc('signal')] = 1.0

            # SELL SIGNAL: RSI crosses below overbought threshold
            # WHY: Overbought condition is ending, take profits
            elif prev_rsi >= overbought and current_rsi < overbought:
                signals.iloc[i, signals.columns.get_loc('signal')] = -1.0

        # Create position indicator based on signals
        signals['position_raw'] = 0.0
        position = 0.0
        for i in range(len(signals)):
            if signals['signal'].iloc[i] == 1.0:
                position = 1.0  # Enter long
            elif signals['signal'].iloc[i] == -1.0:
                position = 0.0  # Exit (momentum is long-only or flat)
            signals.iloc[i, signals.columns.get_loc('position_raw')] = position

        return signals[['signal', 'position_raw']]

    def calculate_positions(self, signals: pd.DataFrame) -> pd.DataFrame:
        """
        Convert signals to positions for momentum strategy.

        Override base class to handle momentum logic correctly.
        """
        positions = pd.DataFrame(index=signals.index)
        positions['position'] = signals['position_raw']

        # Shift by 1 to avoid look-ahead bias
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
