# Algorithmic Trading Backtest Platform

A production-quality backtesting engine for systematic trading strategies, built for hedge fund interview presentation.

## Overview

This platform allows quantitative analysis of trading strategies on historical market data with comprehensive performance metrics and risk analytics. Built with professional-grade architecture suitable for hedge fund environments.

### Features

- **Three Systematic Strategies**
  - Moving Average Crossover (trend following)
  - Mean Reversion (Bollinger Bands)
  - Momentum (RSI-based)

- **Comprehensive Performance Metrics**
  - Total Return & Annualized Return
  - Sharpe Ratio & Sortino Ratio
  - Calmar Ratio
  - Maximum Drawdown
  - Win Rate & Profit Factor

- **Risk Analytics**
  - Value at Risk (VaR) - 95% confidence
  - Conditional VaR (Expected Shortfall)
  - Annualized Volatility
  - Drawdown Analysis

- **Production Features**
  - Data caching for instant backtests
  - RESTful API with comprehensive error handling
  - Interactive React dashboard with charts
  - Type-hinted Python codebase
  - Well-documented code for interviews

## Technology Stack

### Backend
- **Python 3.10+** - Core language
- **Flask** - REST API framework
- **pandas** - Time series analysis
- **NumPy** - Numerical computations
- **yfinance** - Market data (Yahoo Finance)

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Chart.js** - Equity curve & drawdown charts
- **Axios** - API communication

## Project Structure

```
trading-backtest-platform/
├── backend/
│   ├── strategies/
│   │   ├── base_strategy.py       # Abstract base class
│   │   ├── moving_average.py      # MA crossover strategy
│   │   ├── mean_reversion.py      # Bollinger Bands strategy
│   │   └── momentum.py            # RSI-based strategy
│   ├── engine/
│   │   ├── backtester.py          # Backtesting engine
│   │   └── performance.py         # Performance metrics
│   ├── data/
│   │   └── data_handler.py        # Data fetching & caching
│   ├── cache/                     # Cached market data
│   ├── app.py                     # Flask API
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── StrategySelector.jsx
    │   │   └── ResultsDashboard.jsx
    │   └── App.jsx
    └── package.json
```

## Installation & Setup

### Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Flask server
python app.py
```

Server will start at `http://localhost:5000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will start at `http://localhost:5173`

## Usage

### Quick Start

1. **Start Backend**: `cd backend && python app.py`
2. **Start Frontend**: `cd frontend && npm run dev`
3. **Open Browser**: Navigate to `http://localhost:5173`
4. **Run Backtest**:
   - Select strategy (e.g., Moving Average)
   - Choose ticker (e.g., AAPL)
   - Set date range (e.g., 2020-01-01 to 2023-12-31)
   - Adjust parameters
   - Click "Run Backtest"

### Pre-Cache Data for Demo

For instant backtests during presentations:

```bash
curl -X POST http://localhost:5000/api/cache-data \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "SPY", "MSFT", "GOOGL", "AMZN"]}'
```

This downloads and caches data for common tickers (2018-2024).

## API Endpoints

### `POST /api/backtest`

Execute strategy backtest.

**Request:**
```json
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

**Response:**
```json
{
  "success": true,
  "equity_curve": [...],
  "trades": [...],
  "performance": {
    "performance_metrics": {...},
    "risk_metrics": {...},
    "trade_metrics": {...}
  }
}
```

### `GET /api/strategies`

List available strategies and their parameters.

### `POST /api/cache-data`

Pre-download market data.

### `GET /api/health`

Health check endpoint.

## Strategy Details

### 1. Moving Average Crossover

**Concept**: Trend-following strategy based on MA crossovers.

**Parameters**:
- `fast_window` (default 20): Fast moving average period
- `slow_window` (default 50): Slow moving average period

**Logic**:
- Buy when fast MA crosses above slow MA (bullish signal)
- Sell when fast MA crosses below slow MA (bearish signal)

**Best For**: Trending markets

### 2. Mean Reversion (Bollinger Bands)

**Concept**: Price reverts to mean after extreme deviations.

**Parameters**:
- `window` (default 20): Moving average period
- `num_std` (default 2.0): Standard deviations for bands

**Logic**:
- Buy when price crosses below lower band (oversold)
- Sell when price crosses above upper band (overbought)

**Best For**: Range-bound markets

### 3. Momentum (RSI)

**Concept**: RSI identifies overbought/oversold conditions.

**Parameters**:
- `window` (default 14): RSI calculation period
- `oversold` (default 30): Oversold threshold
- `overbought` (default 70): Overbought threshold

**Logic**:
- Buy when RSI exits oversold zone (crosses above 30)
- Sell when RSI exits overbought zone (crosses below 70)

**Best For**: Capturing reversals

## Architecture Decisions

### Why This Tech Stack?

**Python Backend**:
- Industry standard for quantitative finance
- Rich ecosystem (pandas, NumPy) for financial analysis
- Easy to explain algorithms in interviews

**Flask API**:
- Lightweight, perfect for MVP
- RESTful design scales to production
- Easy to add authentication, rate limiting later

**React Frontend**:
- Modern, component-based architecture
- Fast development with Vite
- Professional UI libraries (Chart.js)

**Data Caching**:
- Critical for demo reliability (no API failures during presentation)
- Respects API rate limits
- 10x faster backtests

### Design Patterns Used

1. **Strategy Pattern** (strategies inherit from BaseStrategy)
   - Easy to add new strategies
   - Consistent interface for backtester
   - Testable in isolation

2. **Template Method** (BaseStrategy defines algorithm skeleton)
   - Subclasses implement specifics
   - Common logic (position calculation) in base class

3. **Cache-Aside** (check cache, load on miss, populate)
   - Standard caching pattern
   - Balances freshness vs performance

## Performance Metrics Explained

### Sharpe Ratio
- **Formula**: (Return - Risk-Free Rate) / Volatility
- **Interpretation**: Risk-adjusted return
- **Good**: > 1.0, **Very Good**: > 2.0, **Excellent**: > 3.0

### Sortino Ratio
- Like Sharpe but only penalizes downside volatility
- Better metric as upside volatility is desirable

### Maximum Drawdown
- Largest peak-to-trough decline
- Critical for risk management
- "Can I survive this loss?"

### VaR (Value at Risk)
- Maximum expected loss at 95% confidence
- "5% of days, I'll lose more than this"

### CVaR (Conditional VaR)
- Average loss when VaR is exceeded
- "How bad is a bad day?"

## Testing for Interview

### Recommended Demo Tickers

**Best Results**:
- **AAPL** with Moving Average (2020-2023): Strong trends
- **SPY** with Mean Reversion (2018-2024): Range-bound periods
- **MSFT** with Momentum (2020-2023): Clear momentum cycles

**Period**: 2020-01-01 to 2023-12-31 (3 years, good sample size)

### Demo Flow

1. **Pre-cache data**: Run cache endpoint before demo
2. **Show Moving Average on AAPL**: Explain trend following
3. **Compare strategies**: Run all three on same ticker
4. **Discuss metrics**: Focus on Sharpe ratio, max drawdown
5. **Show trade history**: Explain individual trades

### Expected Questions & Answers

**Q: Why not use real-time data?**
A: Historical backtests require adjusted prices (splits/dividends). Real-time is for live trading, not backtesting.

**Q: How do you prevent overfitting?**
A: Out-of-sample testing, walk-forward analysis, parameter sensitivity analysis (not implemented in this MVP but would add for production).

**Q: What about transaction costs?**
A: Not modeled here for simplicity. Production would add slippage model and commission structure.

**Q: Can this handle high-frequency trading?**
A: No, this is for daily timeframes. HFT requires tick data and microsecond execution (different architecture).

**Q: How would you scale this?**
A: Async processing (Celery), distributed caching (Redis), database for results (PostgreSQL), containerization (Docker), orchestration (Kubernetes).

## Future Enhancements

### For Production

1. **More Strategies**
   - Pairs trading
   - Machine learning strategies
   - Multi-factor models

2. **Advanced Features**
   - Walk-forward optimization
   - Monte Carlo simulation
   - Multi-asset portfolios
   - Custom commission models

3. **Infrastructure**
   - Database for persistence
   - User authentication
   - Background job processing
   - WebSocket for real-time updates

4. **Testing**
   - Unit tests (pytest)
   - Integration tests
   - Performance benchmarks

5. **Deployment**
   - Docker containerization
   - CI/CD pipeline
   - Monitoring & logging
   - Auto-scaling

## Deployment

### Backend (Render/Railway)

```bash
# Add to backend/Procfile
web: gunicorn app:app

# Deploy
git push render main
```

### Frontend (Vercel)

```bash
# From frontend directory
npm run build
vercel --prod
```

### Environment Variables

**Frontend** (`.env`):
```
VITE_API_URL=https://your-backend-url.com
```

**Backend**:
- No env vars needed for MVP
- Production: Add API keys, database URLs

## License

MIT License - Free to use for educational/interview purposes.

## Author

Built for hedge fund interview presentation.
Demonstrates production-quality code, system design, and quantitative finance knowledge.

---

**Interview Notes**: This platform showcases:
- Clean code architecture (SOLID principles)
- Financial domain knowledge (strategies, metrics)
- Full-stack development (Python backend, React frontend)
- Production thinking (caching, error handling, scalability)
- Communication skills (comprehensive documentation)
