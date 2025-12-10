"""
Performance Metrics and Risk Analytics

Comprehensive performance and risk metric calculations for backtesting results.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


def calculate_total_return(equity_curve: pd.Series) -> float:
    """Calculate total return over the period."""
    if len(equity_curve) < 2:
        return 0.0

    initial = equity_curve.iloc[0]
    final = equity_curve.iloc[-1]

    if initial == 0:
        return 0.0

    return ((final - initial) / initial) * 100.0


def calculate_annualized_return(equity_curve: pd.Series, periods_per_year: int = 252) -> float:
    """Calculate annualized return."""
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
    """Calculate Sharpe Ratio - risk-adjusted return metric."""
    if len(returns) < 2:
        return 0.0

    mean_return = returns.mean()
    volatility = returns.std()

    if volatility == 0:
        return np.inf if mean_return > 0 else 0.0

    # Annualize metrics
    mean_return_annual = mean_return * periods_per_year
    volatility_annual = volatility * np.sqrt(periods_per_year)

    sharpe = (mean_return_annual - risk_free_rate) / volatility_annual

    return sharpe


def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> float:
    """Calculate Sortino Ratio - penalizes only downside volatility."""
    if len(returns) < 2:
        return 0.0

    mean_return = returns.mean()
    downside_returns = returns[returns < 0]

    if len(downside_returns) == 0:
        return np.inf if mean_return > 0 else 0.0

    downside_deviation = downside_returns.std()

    if downside_deviation == 0:
        return np.inf if mean_return > 0 else 0.0

    # Annualize metrics
    mean_return_annual = mean_return * periods_per_year
    downside_deviation_annual = downside_deviation * np.sqrt(periods_per_year)

    sortino = (mean_return_annual - risk_free_rate) / downside_deviation_annual

    return sortino


def calculate_max_drawdown(equity_curve: pd.Series) -> float:
    """Calculate maximum drawdown - largest peak-to-trough decline."""
    if len(equity_curve) < 2:
        return 0.0

    running_max = equity_curve.expanding().max()
    drawdown = (equity_curve - running_max) / running_max
    max_dd = drawdown.min()

    return max_dd * 100.0


def calculate_calmar_ratio(
    equity_curve: pd.Series,
    periods_per_year: int = 252
) -> float:
    """Calculate Calmar Ratio = Annualized Return / |Max Drawdown|."""
    ann_return = calculate_annualized_return(equity_curve, periods_per_year)
    max_dd = calculate_max_drawdown(equity_curve)

    if max_dd == 0:
        return np.inf if ann_return > 0 else 0.0

    calmar = ann_return / abs(max_dd)

    return calmar


def calculate_win_rate(trades: List[Dict[str, Any]]) -> float:
    """Calculate win rate - percentage of profitable trades."""
    if not trades:
        return 0.0

    winning_trades = sum(1 for trade in trades if trade.get('pnl_percent', 0) > 0)

    return (winning_trades / len(trades)) * 100.0


def calculate_profit_factor(trades: List[Dict[str, Any]]) -> float:
    """Calculate profit factor = Gross Profit / Gross Loss."""
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

    if gross_loss == 0:
        return np.inf if gross_profit > 0 else 0.0

    return gross_profit / gross_loss


def calculate_average_win_loss(trades: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate average winning and losing trade sizes."""
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
    """Calculate Value at Risk (VaR) - maximum expected loss at given confidence."""
    if len(returns) < 2:
        return 0.0

    var = np.percentile(returns, (1 - confidence) * 100)

    return var * 100.0


def calculate_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    """Calculate Conditional VaR (CVaR / Expected Shortfall)."""
    if len(returns) < 2:
        return 0.0

    var_threshold = np.percentile(returns, (1 - confidence) * 100)
    tail_returns = returns[returns <= var_threshold]

    if len(tail_returns) == 0:
        return 0.0

    cvar = tail_returns.mean()

    return cvar * 100.0


def calculate_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """Calculate annualized volatility (standard deviation of returns)."""
    if len(returns) < 2:
        return 0.0

    vol = returns.std()
    vol_annual = vol * np.sqrt(periods_per_year)

    return vol_annual * 100.0


def generate_performance_report(
    equity_curve: List[float],
    returns: List[float],
    trades: List[Dict[str, Any]],
    initial_capital: float
) -> Dict[str, Any]:
    """Generate comprehensive performance report."""
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
