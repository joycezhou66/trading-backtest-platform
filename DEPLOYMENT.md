# Deployment Guide

## Quick Deployment Checklist

### Backend Deployment (Render.com)

1. **Push to GitHub**
```bash
cd trading-backtest-platform
git init
git add .
git commit -m "Initial commit - Trading backtest platform"
git remote add origin <your-repo-url>
git push -u origin main
```

2. **Create Render Web Service**
- Go to https://render.com
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Configure:
  - **Name**: trading-backtest-api
  - **Environment**: Python 3
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `gunicorn app:app`
  - **Root Directory**: `backend`

3. **Environment Variables** (if needed)
- None required for MVP
- For production: Add API keys, database URLs

4. **Deploy**
- Click "Create Web Service"
- Wait 5-10 minutes for deployment
- Note the URL: `https://trading-backtest-api.onrender.com`

5. **Test**
```bash
curl https://trading-backtest-api.onrender.com/api/health
# Should return: {"status": "healthy"}
```

---

### Frontend Deployment (Vercel)

1. **Update API URL**

Create `frontend/.env.production`:
```
VITE_API_URL=https://trading-backtest-api.onrender.com
```

2. **Install Vercel CLI**
```bash
npm install -g vercel
```

3. **Deploy**
```bash
cd frontend
vercel --prod
```

Follow prompts:
- Setup and deploy: Yes
- Which scope: Your account
- Link to existing project: No
- Project name: trading-backtest-platform
- Directory: `./`
- Override settings: No

4. **Note URL**
- Vercel will provide: `https://trading-backtest-platform.vercel.app`

5. **Test**
- Open URL in browser
- Run a backtest
- Verify results load correctly

---

## Alternative: Railway.app

### Backend on Railway

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Deploy**
```bash
cd backend
railway login
railway init
railway up
```

3. **Add Start Command**
- In Railway dashboard
- Settings → Deploy → Start Command: `gunicorn app:app`

---

## Docker Deployment

### Create Dockerfile

**backend/Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

**frontend/Dockerfile**:
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

**docker-compose.yml** (root directory):
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./backend/cache:/app/cache

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://localhost:5000
```

### Run with Docker
```bash
docker-compose up -d
```

---

## Pre-Deployment Testing

### 1. Test Backend Locally

```bash
cd backend
python app.py

# In another terminal
curl http://localhost:5000/api/health
curl http://localhost:5000/api/strategies
curl -X POST http://localhost:5000/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "moving_average",
    "ticker": "AAPL",
    "start_date": "2020-01-01",
    "end_date": "2023-12-31",
    "parameters": {"fast_window": 20, "slow_window": 50}
  }'
```

### 2. Test Frontend Locally

```bash
cd frontend
npm run dev
# Open http://localhost:5173
# Run a backtest and verify results
```

### 3. Test End-to-End

```bash
# Backend running on :5000
# Frontend running on :5173
# Run backtests for all three strategies
# Verify charts render correctly
# Check trade history displays
```

---

## Production Optimizations

### Backend

1. **Add Gunicorn Workers**
```python
# Procfile
web: gunicorn --workers 4 --timeout 120 app:app
```

2. **Enable Compression**
```python
# app.py
from flask_compress import Compress
Compress(app)
```

3. **Add Rate Limiting**
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/backtest')
@limiter.limit("10 per minute")
def backtest():
    # ...
```

4. **Redis Caching** (for production)
```python
import redis
cache = redis.Redis(host='localhost', port=6379)
```

### Frontend

1. **Optimize Build**
```json
// vite.config.js
export default {
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true
      }
    }
  }
}
```

2. **Enable Compression**
```bash
npm install vite-plugin-compression
```

---

## Monitoring & Logging

### Backend Logging

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
```

### Health Checks

Add to deployment platform:
- **Endpoint**: `/api/health`
- **Interval**: 60 seconds
- **Timeout**: 10 seconds

---

## Troubleshooting

### Backend Issues

**"Module not found"**
- Verify requirements.txt is in backend/
- Check build logs on Render/Railway

**"Port already in use"**
- Render assigns $PORT automatically
- Update app.py: `port=int(os.environ.get('PORT', 5000))`

**"Timeout errors"**
- Increase timeout in Procfile: `--timeout 120`
- Pre-cache data to reduce response time

### Frontend Issues

**"Cannot connect to API"**
- Verify VITE_API_URL is correct
- Check CORS is enabled on backend
- Inspect browser console for errors

**"Blank page after deploy"**
- Check build logs
- Verify dist/ folder was created
- Check nginx configuration

### Performance Issues

**Slow backtests**
- Pre-cache data: POST to /api/cache-data
- Reduce date ranges
- Add Redis caching layer

**High memory usage**
- Limit backtest date ranges
- Clear cache periodically
- Add pagination to trade history

---

## Security Considerations

### For Production

1. **API Authentication**
```python
from flask_httpauth import HTTPTokenAuth
auth = HTTPTokenAuth(scheme='Bearer')
```

2. **HTTPS Only**
```python
@app.before_request
def before_request():
    if not request.is_secure:
        return redirect(request.url.replace('http://', 'https://'))
```

3. **Input Validation**
```python
from marshmallow import Schema, fields, validate

class BacktestSchema(Schema):
    ticker = fields.Str(required=True, validate=validate.Length(min=1, max=10))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
```

4. **Rate Limiting**
```python
from flask_limiter import Limiter
limiter = Limiter(app, default_limits=["100 per hour"])
```

---

## Cost Estimates

### Free Tier (Good for demo/interview)
- **Render**: Free tier (spins down after 15 min inactivity)
- **Vercel**: Free tier (100GB bandwidth/month)
- **Total**: $0/month

### Production (Low traffic)
- **Render**: Starter ($7/month)
- **Vercel**: Free tier
- **Total**: $7/month

### Production (Moderate traffic)
- **Render**: Standard ($25/month) or Railway ($5/month)
- **Vercel**: Pro ($20/month)
- **Redis Cloud**: $5/month
- **PostgreSQL** (if needed): $5/month
- **Total**: ~$35-55/month

---

## Final Checklist

**Before Interview**:
- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] End-to-end test completed successfully
- [ ] Data pre-cached for demo tickers
- [ ] Health endpoint returns 200 OK
- [ ] All three strategies tested
- [ ] Charts render correctly
- [ ] Trade history displays
- [ ] No console errors in browser
- [ ] Mobile responsive (test on phone)

**Have Ready**:
- [ ] Deployment URLs saved
- [ ] GitHub repo URL
- [ ] Demo script printed/available
- [ ] Backup plan (local deployment if prod fails)

---

## Rollback Plan

If production deployment fails:

1. **Run locally during demo**
   - Start backend: `python app.py`
   - Start frontend: `npm run dev`
   - Share screen

2. **Use ngrok for public URL**
```bash
ngrok http 5000  # Backend
ngrok http 5173  # Frontend
```

3. **Record demo video**
   - Pre-record backtest runs
   - Play video if live demo fails
   - Walk through code instead

---

Good luck with your interview! 🚀
