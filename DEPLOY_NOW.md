# Deploy Your Platform NOW (10 minutes)

Your code is already pushed to GitHub: https://github.com/joycezhou66/trading-backtest-platform

## Step 1: Deploy Backend to Render (5 minutes)

1. **Go to Render**: https://render.com
2. **Sign in with GitHub** (or create account)
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub account (if not already)
5. Select repository: **trading-backtest-platform**
6. Configure:
   - **Name**: `trading-backtest-api`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free

7. Click **"Create Web Service"**
8. Wait 5-10 minutes for deployment
9. **Copy the URL**: Something like `https://trading-backtest-api.onrender.com`

### Test Backend

```bash
# Replace with your actual URL
curl https://trading-backtest-api.onrender.com/api/health
# Should return: {"status":"healthy"}
```

---

## Step 2: Deploy Frontend to Vercel (3 minutes)

1. **Go to Vercel**: https://vercel.com
2. **Sign in with GitHub**
3. Click **"Add New..."** → **"Project"**
4. Import **trading-backtest-platform** repository
5. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Environment Variables** → Add:
     - Name: `VITE_API_URL`
     - Value: `https://trading-backtest-api.onrender.com` (your backend URL)

6. Click **"Deploy"**
7. Wait 2-3 minutes
8. **Copy the URL**: Something like `https://trading-backtest-platform.vercel.app`

### Test Frontend

Open your Vercel URL in browser and run a backtest!

---

## Step 3: Pre-Cache Data (2 minutes)

Run this command with your actual backend URL:

```bash
curl -X POST https://trading-backtest-api.onrender.com/api/cache-data \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "SPY", "MSFT", "GOOGL", "AMZN", "TSLA"]}'
```

This ensures instant backtests during your demo!

---

## Step 4: Test Everything (1 minute)

1. Open your Vercel URL
2. Run backtest: AAPL, Moving Average, 2020-2023
3. Verify results load in <10 seconds
4. Check all three strategies work

---

## Your Demo URLs

**Frontend (share this with interviewers)**:
```
https://trading-backtest-platform.vercel.app
```

**Backend API**:
```
https://trading-backtest-api.onrender.com
```

**GitHub Repo**:
```
https://github.com/joycezhou66/trading-backtest-platform
```

---

## Backup Plan

If deployment has issues:

### Option A: Use Render for Both

1. Deploy backend (same as above)
2. Build frontend locally:
   ```bash
   cd frontend
   npm run build
   ```
3. Deploy `frontend/dist` folder as static site on Render

### Option B: Local Demo with ngrok

If production fails during demo:

```bash
# Terminal 1: Backend
cd backend && python3 app.py

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Expose with ngrok
brew install ngrok  # if not installed
ngrok http 5173
```

Share the ngrok URL with interviewers.

---

## Quick Troubleshooting

**Backend won't deploy**:
- Check Render build logs
- Verify `Procfile` exists in backend/
- Ensure `requirements.txt` is correct

**Frontend can't connect to backend**:
- Verify `VITE_API_URL` environment variable
- Check CORS is enabled (it is in app.py)
- Open browser console (F12) for errors

**Slow backtests**:
- Run pre-cache command again
- Render free tier spins down after 15 min (first request is slow)
- Consider upgrading to paid tier ($7/mo for instant response)

---

## For Your Interview

**What to share**:
```
"I've deployed the platform to production. You can try it at:
https://trading-backtest-platform.vercel.app

The backend API is at:
https://trading-backtest-api.onrender.com

And the code is on GitHub:
https://github.com/joycezhou66/trading-backtest-platform"
```

**Demo flow**:
1. Open the live URL
2. Run AAPL backtest (data is pre-cached, loads in <5 sec)
3. Show results: equity curve, metrics, trades
4. Open GitHub to show code
5. Discuss architecture and decisions

---

## Important Notes

**Render Free Tier**:
- Spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- Solution: Open the URL 5 minutes before interview to warm it up

**Vercel Free Tier**:
- Always on, instant response
- 100 GB bandwidth/month (more than enough)

**Total Cost**: $0/month (free tier)
**Upgrade Cost** (if needed): $7/month for Render starter

---

## After Your Interview

If you want to keep it running:
- Free tier is fine for portfolio
- Upgrade backend if you get traffic
- Add your own domain (optional)

If you want to take it down:
- Render: Dashboard → Service → Settings → Delete Service
- Vercel: Dashboard → Project → Settings → Delete Project
- GitHub: Repo → Settings → Delete Repository

---

You're all set! 🚀

Once deployed, bookmark your URLs and test them before your interview.
