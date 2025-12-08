# Algorithmic Trading Backtesting Platform

A comprehensive backtesting engine for evaluating systematic trading strategies on historical market data. Built with Python, Flask, and React to provide professional-grade performance analytics and risk metrics.

## Features

### Trading Strategies
- **Moving Average Crossover**: Trend-following strategy based on MA crossovers
- **Mean Reversion**: Bollinger Bands-based mean reversion strategy
- **Momentum**: RSI-based momentum trading strategy

### Performance Analytics
- **Return Metrics**: Total return, annualized return, CAGR
- **Risk-Adjusted Metrics**: Sharpe ratio, Sortino ratio, Calmar ratio
- **Risk Metrics**: Maximum drawdown, annualized volatility, Value at Risk (VaR 95%), Conditional VaR
- **Trade Analytics**: Win rate, profit factor, average win/loss, trade count

### Technical Features
- Real-time market data integration via Yahoo Finance API
- Intelligent data caching for fast backtests
- RESTful API architecture
- Interactive web dashboard with Chart.js visualizations
- Comprehensive error handling and input validation

## Architecture

### Backend (Python/Flask)
```
backend/
├── strategies/          # Trading strategy implementations
│   ├── base_strategy.py       # Abstract base class using Strategy pattern
│   ├── moving_average.py      # MA crossover strategy
│   ├── mean_reversion.py      # Bollinger Bands strategy
│   └── momentum.py            # RSI strategy
├── engine/             # Backtesting engine
│   ├── backtester.py          # Strategy execution engine
│   └── performance.py         # Performance metrics calculator
├── data/              # Data management
│   └── data_handler.py        # Market data fetching & caching
└── app.py             # Flask REST API
```

### Frontend (React/Vite)
```
frontend/
├── src/
│   ├── components/
│   │   ├── StrategySelector.jsx    # Strategy configuration UI
│   │   └── ResultsDashboard.jsx    # Results visualization
│   └── App.jsx                     # Main application
```

## Tech Stack

**Backend**
- Python 3.10+
- Flask (REST API)
- pandas (time series analysis)
- NumPy (numerical computations)
- yfinance (market data)

**Frontend**
- React 18
- Vite (build tool)
- Chart.js (visualizations)
- Axios (HTTP client)

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

The API will be available at `http://localhost:5000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The application will be available at `http://localhost:5173`

## Usage

### Web Interface

1. Start both backend and frontend servers
2. Navigate to `http://localhost:5173` in your browser
3. Configure your backtest:
   - Select a trading strategy
   - Enter ticker symbol (e.g., AAPL, SPY, MSFT)
   - Set date range
   - Adjust strategy parameters
4. Click "Run Backtest" to execute
5. View results including equity curve, performance metrics, and trade history

### API Endpoints

#### Run Backtest
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

#### List Available Strategies
```bash
GET /api/strategies
```

#### Pre-cache Market Data
```bash
POST /api/cache-data
Content-Type: application/json

{
  "tickers": ["AAPL", "SPY", "MSFT"],
  "start_date": "2018-01-01",
  "end_date": "2024-12-01"
}
```

#### Health Check
```bash
GET /api/health
```

## Strategy Details

### Moving Average Crossover

A trend-following strategy that generates signals based on moving average crossovers.

**Parameters:**
- `fast_window` (default: 20): Fast moving average period
- `slow_window` (default: 50): Slow moving average period

**Logic:**
- Buy signal when fast MA crosses above slow MA
- Sell signal when fast MA crosses below slow MA

**Best suited for:** Trending markets

### Mean Reversion (Bollinger Bands)

A mean reversion strategy based on Bollinger Bands statistical analysis.

**Parameters:**
- `window` (default: 20): Moving average period
- `num_std` (default: 2.0): Number of standard deviations for bands

**Logic:**
- Buy signal when price crosses below lower band (oversold)
- Sell signal when price crosses above upper band (overbought)

**Best suited for:** Range-bound markets

### Momentum (RSI)

A momentum strategy using the Relative Strength Index.

**Parameters:**
- `window` (default: 14): RSI calculation period
- `oversold` (default: 30): Oversold threshold
- `overbought` (default: 70): Overbought threshold

**Logic:**
- Buy signal when RSI crosses above oversold threshold
- Sell signal when RSI crosses below overbought threshold

**Best suited for:** Markets with clear overbought/oversold cycles

## Performance Metrics

### Sharpe Ratio
Risk-adjusted return metric calculated as:
```
Sharpe = (Portfolio Return - Risk-Free Rate) / Portfolio Volatility
```
Values > 1.0 indicate good risk-adjusted performance.

### Sortino Ratio
Similar to Sharpe but only penalizes downside volatility:
```
Sortino = (Portfolio Return - Risk-Free Rate) / Downside Deviation
```

### Maximum Drawdown
Largest peak-to-trough decline in portfolio value:
```
Max Drawdown = (Trough Value - Peak Value) / Peak Value
```

### Value at Risk (VaR)
Maximum expected loss at 95% confidence level using historical simulation.

### Conditional VaR (CVaR)
Average loss when VaR threshold is exceeded (tail risk metric).

## Design Patterns

### Strategy Pattern
All trading strategies inherit from `BaseStrategy` abstract class, making it easy to add new strategies without modifying the backtesting engine.

### Template Method
The base class defines the algorithm skeleton (signal generation → position calculation), while subclasses implement strategy-specific logic.

### Cache-Aside
Market data is cached locally to improve performance and reduce API calls.

## Configuration

### Data Caching
Market data is automatically cached in `backend/cache/` directory. Cache files are named:
```
{ticker}_{start_date}_{end_date}.pkl
```

### API Configuration
Default settings in `backend/app.py`:
- Host: `0.0.0.0`
- Port: `5000`
- Initial Capital: `$100,000`
- Risk-Free Rate: `2%` (0.02)

### Frontend Configuration
API URL can be configured via environment variable:
```bash
VITE_API_URL=http://localhost:5000
```

## Development

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Code Style
- Backend: Follows PEP 8 guidelines with type hints
- Frontend: ESLint with React recommended rules

### Adding a New Strategy

1. Create a new file in `backend/strategies/`
2. Inherit from `BaseStrategy`
3. Implement required methods:
   ```python
   class MyStrategy(BaseStrategy):
       def validate_parameters(self):
           # Validate strategy parameters
           pass

       def generate_signals(self, data):
           # Generate buy/sell signals
           pass
   ```
4. Register in `backend/app.py`

## Deployment

### Backend (Render/Railway)

Create `Procfile`:
```
web: gunicorn app:app
```

Deploy to Render or Railway with:
- Runtime: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Root Directory: `backend`

### Frontend (Vercel/Netlify)

Deploy with:
- Framework: Vite
- Build Command: `npm run build`
- Output Directory: `dist`
- Root Directory: `frontend`

Set environment variable:
- `VITE_API_URL`: Your backend API URL

## Performance Optimization

### Data Caching
Pre-cache frequently used tickers for instant backtests:
```bash
curl -X POST http://localhost:5000/api/cache-data \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "SPY", "MSFT", "GOOGL", "AMZN"]}'
```

### Backtest Performance
- Cached data: < 5 seconds
- Uncached data: 10-30 seconds (depends on date range)

## Limitations & Future Work

### Current Limitations
- No transaction costs or slippage modeling
- Daily timeframe only (no intraday data)
- Limited to long-only strategies
- No portfolio optimization

### Planned Features
- [ ] Transaction cost modeling
- [ ] Slippage simulation
- [ ] Short selling support
- [ ] Multi-asset portfolio backtesting
- [ ] Walk-forward optimization
- [ ] Monte Carlo simulation
- [ ] Parameter optimization (grid search)
- [ ] Custom strategy builder
- [ ] Export results to PDF/CSV
- [ ] Real-time strategy monitoring

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Market data provided by Yahoo Finance via yfinance library
- Inspired by quantitative trading platforms like QuantConnect and Zipline
- Chart visualizations powered by Chart.js

## Contact

For questions or feedback, please open an issue on GitHub.

---

Built with Python, Flask, and React
