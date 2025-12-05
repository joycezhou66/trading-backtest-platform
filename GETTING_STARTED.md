# Getting Started

Quick guide to get the trading backtest platform running locally.

## Prerequisites

- Python 3.10+ installed
- Node.js 18+ installed
- Terminal/command line access

## Installation

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Or if using a virtual environment (recommended):

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

## Running the Application

You'll need two terminal windows:

### Terminal 1: Backend

```bash
cd backend
python app.py
```

Backend will start on http://localhost:5000

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

Frontend will start on http://localhost:5173

## Quick Test

1. Open http://localhost:5173 in your browser
2. Select "Moving Average Crossover" strategy
3. Enter ticker: AAPL
4. Set dates: 2020-01-01 to 2023-12-31
5. Click "Run Backtest"

First run will download data (~10-15 seconds), subsequent runs will be cached (<5 seconds).

## Pre-caching Data (Optional)

For faster backtests, pre-download common tickers:

```bash
curl -X POST http://localhost:5000/api/cache-data \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "SPY", "MSFT", "GOOGL", "AMZN"]}'
```

## Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (need 3.10+)
- Reinstall dependencies: `pip install -r backend/requirements.txt`

**Frontend won't start:**
- Check Node version: `node --version` (need 18+)
- Delete node_modules and reinstall: `rm -rf frontend/node_modules && cd frontend && npm install`

**Backtest fails:**
- Make sure backend is running (check http://localhost:5000/api/health)
- Try a common ticker (AAPL, SPY, MSFT)
- Check date range is valid (not in future, not before 1990)

**Browser shows blank page:**
- Check browser console (F12) for errors
- Verify backend URL in frontend/src/App.jsx is correct
- Clear browser cache and reload

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore different strategies (Mean Reversion, Momentum)
- Try different tickers and date ranges
- Review API endpoints in README.md for programmatic access

Happy backtesting!
