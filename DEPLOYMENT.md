# Deployment

## Live URLs

**Frontend:** https://frontend-gwj5g4pm4-joyce-zhous-projects.vercel.app
**Backend API:** https://trading-backtest-platform.onrender.com

## Deploy Updates

Both services auto-deploy from the main branch:

```bash
git push  # Triggers deployment on both platforms
```

**Frontend** (Vercel):
- Redeploy manually: `vercel --prod`
- Dashboard: https://vercel.com/dashboard

**Backend** (Render):
- Redeploy manually: Use Render dashboard
- Dashboard: https://dashboard.render.com

## Environment Variables

Frontend requires `VITE_API_URL` set to backend URL. Already configured in Vercel project settings.

## Testing Deployed API

```bash
# Health check
curl https://trading-backtest-platform.onrender.com/api/health

# List strategies
curl https://trading-backtest-platform.onrender.com/api/strategies

# Run backtest
curl -X POST https://trading-backtest-platform.onrender.com/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "moving_average",
    "ticker": "AAPL",
    "start_date": "2023-06-01",
    "end_date": "2023-09-01",
    "initial_capital": 100000,
    "parameters": {"fast_window": 20, "slow_window": 50}
  }'
```

## Stack

- Backend: Python 3.11, Flask, Render free tier
- Frontend: React 18, Vite, Vercel
- Data: Yahoo Finance via yfinance
