# Algorithmic Trading Backtesting Platform

A quantitative trading backtesting engine for evaluating systematic strategies on market data. Test moving average, mean reversion, and momentum strategies with professional performance analytics.

**🚀 Live Demo:** https://frontend-httxb0fzw-joyce-zhous-projects.vercel.app

## Features

- **Three Trading Strategies:** Moving Average Crossover, Mean Reversion (Bollinger Bands), RSI Momentum
- **Professional Metrics:** Sharpe Ratio, Sortino Ratio, Calmar Ratio, Maximum Drawdown, VaR/CVaR
- **Interactive Dashboard:** Real-time results with equity curves and trade history
- **RESTful API:** Flask backend with comprehensive endpoints

## Tech Stack

**Backend:** Python 3.10, Flask, pandas, NumPy
**Frontend:** React 18, Vite, Chart.js
**Deployment:** Render (API), Vercel (Frontend)

## Quick Start

### Backend
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install && npm run dev
```

## API Usage

```bash
POST /api/backtest
Content-Type: application/json

{
  "strategy": "moving_average",
  "ticker": "AAPL",
  "start_date": "2020-01-01",
  "end_date": "2023-12-31",
  "parameters": {
    "fast_window": 20,
    "slow_window": 50
  }
}
```

## Architecture

```
backend/
├── strategies/          # Strategy implementations
│   ├── base_strategy.py
│   ├── moving_average.py
│   ├── mean_reversion.py
│   └── momentum.py
├── engine/              # Backtesting engine
│   ├── backtest_engine.py
│   └── performance.py
├── data/                # Data management
└── app.py               # Flask API

frontend/
├── src/
│   ├── components/
│   │   ├── StrategySelector.jsx
│   │   └── ResultsDashboard.jsx
│   └── App.jsx
```

## Strategies

### Moving Average Crossover
Trend-following strategy using fast/slow MA crossovers.

**Parameters:** `fast_window` (default: 20), `slow_window` (default: 50)

### Mean Reversion
Bollinger Bands-based strategy for range-bound markets.

**Parameters:** `window` (default: 20), `num_std` (default: 2.0)

### Momentum (RSI)
Relative Strength Index strategy for identifying reversals.

**Parameters:** `window` (default: 14), `oversold` (default: 30), `overbought` (default: 70)

## Performance Metrics

- **Sharpe Ratio:** Risk-adjusted return metric
- **Sortino Ratio:** Downside-focused risk metric
- **Maximum Drawdown:** Largest peak-to-trough decline
- **VaR/CVaR:** Value at Risk and Conditional VaR at 95% confidence

## License

MIT
