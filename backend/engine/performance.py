"""
Performance Metrics and Risk Analytics

WHY THESE METRICS: Hedge funds use these to evaluate strategy quality:
- Return metrics: How much money did we make?
- Risk metrics: How much risk did we take?
- Risk-adjusted metrics: Are returns worth the risk?

INTERVIEW TIP: Always discuss metrics in context of risk-adjusted returns.
A 50% return with 60% volatility is worse than 20% return with 5% volatility.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


def calculate_total_return(equity_curve: pd.Series) -> float:
    """
    Calculate total return over the period.

    Formula: (Final Value - Initial Value) / Initial Value

    WHY: Most basic performance metric. But can be misleading without
    considering time period and risk taken.

    Returns:
        Total return as percentage
    """
    if len(equity_curve) < 2:
        return 0.0

    initial = equity_curve.iloc[0]
    final = equity_curve.iloc[-1]

    if initial == 0:
        return 0.0

    return ((final - initial) / initial) * 100.0


def calculate_annualized_return(equity_curve: pd.Series, periods_per_year: int = 252) -> float:
    """
    Calculate annualized return.

    Formula: (1 + Total Return)^(periods_per_year / num_periods) - 1

    WHY ANNUALIZE: Allows comparing strategies over different time periods.
    50% over 2 years is different from 50% over 6 months.

    Args:
        equity_curve: Series of portfolio values
        periods_per_year: Trading days per year (252 for daily data)

    WHY 252: NYSE is open ~252 days/year (365 - weekends - holidays)

    Returns:
        Annualized return as percentage
    """
    if len(equity_curve) < 2:
        return 0.0

    initial = equity_curve.iloc[0]
    final = equity_curve.iloc[-1]
    num_periods = len(equity_curve)

    if initial == 0 or num_periods == 0:
        return 0.0

    total_return = final / initial
    annualized = (total_return ** (periods_per_year / num_periods)) - 1

    return annualized * 100.0


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> float:
    """
    Calculate Sharpe Ratio - most important risk-adjusted return metric.

    Formula: (Mean Return - Risk Free Rate) / Std Dev of Returns

    WHY: Measures excess return per unit of risk.
    Higher Sharpe = better risk-adjusted performance.

    INTERPRETATION:
    - Sharpe > 1.0: Good (returns exceed risk)
    - Sharpe > 2.0: Very good (what most hedge funds target)
    - Sharpe > 3.0: Excellent (rare, might indicate overfitting)

    Args:
        returns: Series of period returns
        risk_free_rate: Annual risk-free rate (default 2% = 0.02)
        periods_per_year: For annualization (252 for daily)

    WHY RISK-FREE RATE: We only care about returns ABOVE what we could
    earn risk-free (e.g., Treasury bills). This is the "excess return".

    EDGE CASE: If std dev = 0 (no volatility), return infinity.
    This would mean consistent returns with no risk (unrealistic).
    """
    if len(returns) < 2:
        return 0.0

    # Calculate mean return
    mean_return = returns.mean()

    # Calculate volatility (standard deviation)
    volatility = returns.std()

    # Avoid division by zero
    if volatility == 0:
        return np.inf if mean_return > 0 else 0.0

    # Annualize the metrics
    # WHY: Sharpe ratio is typically quoted annualized
    mean_return_annual = mean_return * periods_per_year
    volatility_annual = volatility * np.sqrt(periods_per_year)

    # Calculate Sharpe
    sharpe = (mean_return_annual - risk_free_rate) / volatility_annual

    return sharpe


def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> float:
    """
    Calculate Sortino Ratio - like Sharpe but only penalizes downside volatility.

    Formula: (Mean Return - Risk Free Rate) / Downside Deviation

    WHY BETTER THAN SHARPE: Sharpe penalizes ALL volatility, including upside.
    Sortino only penalizes downside volatility (the risk investors actually care about).

    HEDGE FUND PERSPECTIVE: "I don't mind when my returns are volatile to the upside!"
    Sortino recognizes that upside volatility is good.

    Returns:
        Sortino ratio (higher is better)
    """
    if len(returns) < 2:
        return 0.0

    mean_return = returns.mean()

    # Downside deviation: std dev of negative returns only
    # WHY: We only care about volatility of losses, not gains
    downside_returns = returns[returns < 0]

    if len(downside_returns) == 0:
        # No negative returns = no downside risk = infinite Sortino
        return np.inf if mean_return > 0 else 0.0

    downside_deviation = downside_returns.std()

    if downside_deviation == 0:
        return np.inf if mean_return > 0 else 0.0

    # Annualize
    mean_return_annual = mean_return * periods_per_year
    downside_deviation_annual = downside_deviation * np.sqrt(periods_per_year)

    sortino = (mean_return_annual - risk_free_rate) / downside_deviation_annual

    return sortino


def calculate_max_drawdown(equity_curve: pd.Series) -> float:
    """
    Calculate maximum drawdown - largest peak-to-trough decline.

    Formula: (Trough Value - Peak Value) / Peak Value

    WHY CRITICAL: Shows worst-case loss an investor would have experienced.
    More intuitive than volatility for understanding risk.

    EXAMPLE: If max drawdown is -30%, investor would have seen their
    $100K portfolio drop to $70K at some point. Can they stomach that?

    HEDGE FUND PERSPECTIVE: Max drawdown is often a hard constraint.
    "We can't have drawdowns exceeding 20%" = risk limit.

    Returns:
        Maximum drawdown as percentage (negative value)
    """
    if len(equity_curve) < 2:
        return 0.0

    # Calculate running maximum (peak so far)
    # WHY: At each point, what's the highest value we've seen?
    running_max = equity_curve.expanding().max()

    # Calculate drawdown at each point
    # Drawdown = (Current - Peak) / Peak
    drawdown = (equity_curve - running_max) / running_max

    # Maximum drawdown is the worst (most negative) drawdown
    max_dd = drawdown.min()

    return max_dd * 100.0  # Convert to percentage


def calculate_calmar_ratio(
    equity_curve: pd.Series,
    periods_per_year: int = 252
) -> float:
    """
    Calculate Calmar Ratio = Annualized Return / |Max Drawdown|

    WHY: Another risk-adjusted metric. Compares returns to worst drawdown.
    Higher Calmar = better returns relative to worst loss.

    INTERPRETATION:
    - Calmar > 1.0: Returns exceed worst drawdown
    - Calmar > 3.0: Very good (high returns, controlled drawdowns)

    HEDGE FUND PERSPECTIVE: Calmar is popular because drawdown is
    easy to explain to investors. "We made 30% with max 10% drawdown."

    Returns:
        Calmar ratio (higher is better)
    """
    ann_return = calculate_annualized_return(equity_curve, periods_per_year)
    max_dd = calculate_max_drawdown(equity_curve)

    # Avoid division by zero
    if max_dd == 0:
        return np.inf if ann_return > 0 else 0.0

    # Calmar uses absolute value of drawdown
    calmar = ann_return / abs(max_dd)

    return calmar


def calculate_win_rate(trades: List[Dict[str, Any]]) -> float:
    """
    Calculate win rate - percentage of profitable trades.

    Formula: Number of Winning Trades / Total Trades

    WHY: Simple metric investors understand. But can be misleading!
    You can have 90% win rate and still lose money if losses are huge.

    Returns:
        Win rate as percentage
    """
    if not trades:
        return 0.0

    winning_trades = sum(1 for trade in trades if trade.get('pnl_percent', 0) > 0)

    return (winning_trades / len(trades)) * 100.0


def calculate_profit_factor(trades: List[Dict[str, Any]]) -> float:
    """
    Calculate profit factor = Gross Profit / Gross Loss

    WHY: Shows relationship between winning and losing trades.
    - PF > 1.0: Profitable strategy
    - PF > 2.0: Very good (wins are 2x larger than losses)
    - PF < 1.0: Losing strategy

    BETTER THAN WIN RATE: Accounts for trade sizes.
    You can have 40% win rate but PF=2.0 if winners are much larger.

    Returns:
        Profit factor (>1 is profitable)
    """
    if not trades:
        return 0.0

    gross_profit = sum(
        trade.get('pnl_dollars', 0)
        for trade in trades
        if trade.get('pnl_dollars', 0) > 0
    )

    gross_loss = abs(sum(
        trade.get('pnl_dollars', 0)
        for trade in trades
        if trade.get('pnl_dollars', 0) < 0
    ))

    # Avoid division by zero
    if gross_loss == 0:
        return np.inf if gross_profit > 0 else 0.0

    return gross_profit / gross_loss


def calculate_average_win_loss(trades: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate average winning and losing trade sizes.

    WHY: Understanding trade distribution helps improve strategy.
    Ideal: Large average wins, small average losses.

    Returns:
        Dictionary with avg_win, avg_loss, win_loss_ratio
    """
    if not trades:
        return {'avg_win': 0.0, 'avg_loss': 0.0, 'win_loss_ratio': 0.0}

    wins = [t['pnl_percent'] for t in trades if t.get('pnl_percent', 0) > 0]
    losses = [abs(t['pnl_percent']) for t in trades if t.get('pnl_percent', 0) < 0]

    avg_win = np.mean(wins) if wins else 0.0
    avg_loss = np.mean(losses) if losses else 0.0

    win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0.0

    return {
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'win_loss_ratio': win_loss_ratio
    }


def calculate_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR) - maximum expected loss at given confidence.

    WHY: Answers "How much can I lose on a bad day?"
    95% VaR = -2.5% means: 95% of days, you'll lose less than 2.5%.
    But 5% of days (1 in 20), you could lose more.

    METHOD: Historical simulation (uses actual return distribution)

    HEDGE FUND PERSPECTIVE: VaR is required risk metric for:
    - Risk management
    - Regulatory reporting (Basel accords)
    - Position sizing

    Args:
        returns: Series of returns
        confidence: Confidence level (0.95 = 95%)

    Returns:
        VaR as percentage (negative value = loss)
    """
    if len(returns) < 2:
        return 0.0

    # Calculate percentile
    # WHY percentile: If confidence=0.95, we want the 5th percentile
    # (the cutoff where 5% of returns are worse)
    var = np.percentile(returns, (1 - confidence) * 100)

    return var * 100.0  # Convert to percentage


def calculate_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    """
    Calculate Conditional VaR (CVaR / Expected Shortfall).

    CVaR = Average of all returns worse than VaR threshold

    WHY BETTER THAN VAR: VaR just tells you the threshold.
    CVaR tells you how bad it is WHEN you exceed VaR.

    EXAMPLE:
    - VaR(95%) = -2.5% (5% of days are worse than -2.5%)
    - CVaR(95%) = -4.0% (when it's bad, average loss is -4.0%)

    HEDGE FUND PERSPECTIVE: CVaR is preferred by risk managers because
    it captures "tail risk" - how bad are the really bad days?

    Returns:
        CVaR as percentage (negative value = average loss in tail)
    """
    if len(returns) < 2:
        return 0.0

    # Get VaR threshold
    var_threshold = np.percentile(returns, (1 - confidence) * 100)

    # Calculate average of returns worse than VaR
    # WHY: This is the "expected shortfall" - expected loss given we exceeded VaR
    tail_returns = returns[returns <= var_threshold]

    if len(tail_returns) == 0:
        return 0.0

    cvar = tail_returns.mean()

    return cvar * 100.0


def calculate_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """
    Calculate annualized volatility (standard deviation of returns).

    WHY: Most common risk metric. Higher volatility = higher risk.

    INTERPRETATION:
    - Stock market: ~15-20% annual volatility
    - Individual stocks: 20-40% annual volatility
    - Low-vol strategy: <10% annual volatility

    Returns:
        Annualized volatility as percentage
    """
    if len(returns) < 2:
        return 0.0

    # Calculate std dev
    vol = returns.std()

    # Annualize: multiply by sqrt(periods_per_year)
    # WHY sqrt: Variance scales linearly with time, std dev scales with sqrt(time)
    vol_annual = vol * np.sqrt(periods_per_year)

    return vol_annual * 100.0


def generate_performance_report(
    equity_curve: List[float],
    returns: List[float],
    trades: List[Dict[str, Any]],
    initial_capital: float
) -> Dict[str, Any]:
    """
    Generate comprehensive performance report.

    WHY COMPREHENSIVE: Give decision-makers all metrics they need.
    Different people care about different metrics:
    - PM cares about Sharpe ratio
    - Risk manager cares about drawdown and VaR
    - Investor cares about total return

    Returns:
        Dictionary with all performance and risk metrics
    """
    # Convert to pandas Series for calculations
    equity_series = pd.Series(equity_curve)
    returns_series = pd.Series(returns)

    # Calculate all metrics
    total_return = calculate_total_return(equity_series)
    ann_return = calculate_annualized_return(equity_series)
    sharpe = calculate_sharpe_ratio(returns_series)
    sortino = calculate_sortino_ratio(returns_series)
    max_dd = calculate_max_drawdown(equity_series)
    calmar = calculate_calmar_ratio(equity_series)
    win_rate = calculate_win_rate(trades)
    profit_factor = calculate_profit_factor(trades)
    avg_metrics = calculate_average_win_loss(trades)
    var_95 = calculate_var(returns_series, 0.95)
    cvar_95 = calculate_cvar(returns_series, 0.95)
    volatility = calculate_volatility(returns_series)

    report = {
        'performance_metrics': {
            'total_return': round(total_return, 2),
            'annualized_return': round(ann_return, 2),
            'sharpe_ratio': round(sharpe, 2),
            'sortino_ratio': round(sortino, 2),
            'calmar_ratio': round(calmar, 2)
        },
        'risk_metrics': {
            'max_drawdown': round(max_dd, 2),
            'annualized_volatility': round(volatility, 2),
            'var_95': round(var_95, 2),
            'cvar_95': round(cvar_95, 2)
        },
        'trade_metrics': {
            'total_trades': len(trades),
            'win_rate': round(win_rate, 2),
            'profit_factor': round(profit_factor, 2) if profit_factor != np.inf else 'Inf',
            'avg_win': round(avg_metrics['avg_win'], 2),
            'avg_loss': round(avg_metrics['avg_loss'], 2),
            'win_loss_ratio': round(avg_metrics['win_loss_ratio'], 2)
        },
        'summary': {
            'initial_capital': initial_capital,
            'final_capital': round(equity_curve[-1], 2) if equity_curve else initial_capital,
            'total_pnl': round(equity_curve[-1] - initial_capital, 2) if equity_curve else 0.0
        }
    }

    return report
