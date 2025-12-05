# Quick Start Guide

## Installation (5 minutes)

### Step 1: Install Backend Dependencies

```bash
cd backend
pip3 install -r requirements.txt
```

### Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install
```

## Running the Platform (2 terminals needed)

### Terminal 1: Start Backend

```bash
cd backend
python3 app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

### Terminal 2: Start Frontend

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE ready in 500ms
  ➜  Local:   http://localhost:5173/
```

## Using the Platform

1. **Open your browser**: Go to `http://localhost:5173`

2. **Run your first backtest**:
   - Strategy: Moving Average Crossover (default)
   - Ticker: AAPL
   - Start Date: 2020-01-01
   - End Date: 2023-12-31
   - Click "Run Backtest"

3. **Explore results**:
   - Equity curve shows portfolio value over time
   - Performance metrics (Sharpe ratio, returns, etc.)
   - Trade history table

4. **Try other strategies**:
   - Mean Reversion (Bollinger Bands)
   - Momentum (RSI)

## Pre-Cache Data for Demo (Optional)

For instant backtests during presentations, pre-download common tickers:

```bash
curl -X POST http://localhost:5000/api/cache-data \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "SPY", "MSFT", "GOOGL", "AMZN"]}'
```

## Troubleshooting

**Backend won't start**:
- Make sure Python 3.10+ is installed: `python3 --version`
- Install dependencies: `pip3 install -r backend/requirements.txt`

**Frontend won't start**:
- Make sure Node.js is installed: `node --version`
- Install dependencies: `npm install` in frontend/

**Backtest fails**:
- Check backend is running: `http://localhost:5000/api/health`
- Try a common ticker (AAPL, SPY, MSFT)
- Use recent dates (2020-2024)

**Blank screen**:
- Open browser console (F12) and check for errors
- Verify backend URL in frontend/src/App.jsx

## Next Steps

- Read [DEMO.md](DEMO.md) for interview presentation guide
- Read [README.md](README.md) for full documentation
- Read [DEPLOYMENT.md](DEPLOYMENT.md) to deploy to production

Happy backtesting! 📈
