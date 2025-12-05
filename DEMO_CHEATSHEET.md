# Interview Demo Cheat Sheet 📋

**Print this out or keep it open during your demo!**

---

## 🔗 Your URLs

**LIVE DEMO**: https://trading-backtest-platform.vercel.app
**GITHUB**: https://github.com/joycezhou66/trading-backtest-platform
**API**: https://trading-backtest-api.onrender.com

---

## ⚡ Quick Demo (5 minutes)

### Opening Line
> "I built an algorithmic trading backtesting platform that implements three systematic strategies with institutional-grade performance metrics."

### Demo Steps

**1. Show Live Platform** (1 min)
- Open Vercel URL
- "Clean, professional interface designed for hedge fund analysts"

**2. Run Backtest** (2 min)
- **Ticker**: AAPL
- **Strategy**: Moving Average Crossover
- **Dates**: 2020-01-01 to 2023-12-31
- **Parameters**: Leave defaults (20/50)
- Click "Run Backtest"

**While loading**:
> "This strategy buys when the 20-day MA crosses above the 50-day MA - classic trend following used by CTAs. I pre-cached the data so this returns in under 5 seconds."

**3. Explain Results** (2 min)

Point to:
- **Equity Curve**: "Portfolio grew from $100K to $[X]"
- **Sharpe Ratio**: "Sharpe of [X] - hedge funds target >1, this is [excellent/good]"
- **Max Drawdown**: "Worst decline was [X]% - critical for risk management"
- **Trades**: "[X] trades executed, [Y]% win rate"

---

## 💬 Key Talking Points

### Architecture
✅ "Strategy pattern makes adding strategies trivial"
✅ "Data caching ensures <10 sec backtests - critical for demos and production"
✅ "RESTful API separates concerns, could serve mobile/web/internal tools"

### Metrics
✅ "Sharpe ratio = (return - risk-free rate) / volatility"
✅ "VaR tells you: 95% of days, you lose less than X%"
✅ "Sortino only penalizes downside - upside volatility is good!"

### Production Thinking
✅ "Comprehensive error handling with meaningful messages"
✅ "Type hints throughout for maintainability"
✅ "Comments explain WHY not just WHAT"

---

## 🤔 Expected Questions & Answers

**Q: How would you handle 10,000 users?**
> Horizontal scaling behind load balancer, Redis for distributed caching, PostgreSQL for persistence, Celery for background jobs, Docker/Kubernetes for orchestration. Estimated $500-1000/mo on AWS.

**Q: What about transaction costs?**
> Not modeled here for simplicity. Production would add commission model (e.g., $0.01/share) and slippage model (0.1% of trade value). Typically reduces returns 1-3% annually.

**Q: Why Sharpe ratio?**
> Most widely used risk-adjusted metric. But has limitations - assumes normal distribution (markets have fat tails) and penalizes upside volatility. That's why I also include Sortino and Calmar.

**Q: Can this handle high-frequency trading?**
> No, this is for daily timeframes. HFT needs tick data, microsecond execution, co-location - completely different architecture. This targets systematic strategies trading daily/weekly like most hedge funds.

**Q: How do you prevent overfitting?**
> Not implemented in MVP but would add: walk-forward optimization, out-of-sample testing, parameter sensitivity analysis, Monte Carlo simulation. Key is ensuring strategy works on unseen data.

---

## 🎯 Best Backtests to Show

**1. AAPL + Moving Average (2020-2023)**
- Strong uptrend, clear signals
- Good Sharpe ratio
- Easy to explain

**2. SPY + Mean Reversion (2020-2023)**
- Different strategy approach
- Shows versatility
- Range-bound performance

**3. MSFT + Momentum (2020-2023)**
- RSI catches reversals
- Good win rate
- Demonstrates all three strategies

---

## ⏰ 5 Minutes Before Interview

**Checklist**:
- [ ] Open Vercel URL - verify it loads
- [ ] Run test backtest (AAPL) - warm up Render server
- [ ] Open GitHub repo in tab
- [ ] Have this cheat sheet ready
- [ ] Water, deep breath, you've got this!

---

## 🛑 Emergency Backup

**If production fails**:

Run locally:
```bash
# Terminal 1
cd backend && python3 app.py

# Terminal 2
cd frontend && npm run dev

# Share screen showing http://localhost:5173
```

Say:
> "I have this deployed but let me show you the local version which includes all the latest features."

---

## 📊 Key Numbers to Remember

- **3** trading strategies implemented
- **15+** performance & risk metrics
- **<10 seconds** backtest time (with caching)
- **2 design patterns** (Strategy, Template Method)
- **252** trading days per year (for annualization)
- **95%** confidence level for VaR
- **>1.0** = good Sharpe ratio, **>2.0** = excellent

---

## 🎤 Closing Statement

> "This platform demonstrates my ability to build production systems for quantitative finance. I combined clean engineering, domain knowledge, and product thinking. I'm excited to bring these skills to [company name] and contribute to [specific thing you researched]."

---

## 🚀 Remember

- **Confidence**: You built something impressive
- **Clarity**: Explain simply, avoid jargon overload
- **Curiosity**: Ask questions about their systems
- **Calm**: It's okay to say "I don't know, but here's how I'd find out"

**You've got this!** 💪

---

**Last Check**:
- [ ] URLs work
- [ ] Test backtest runs
- [ ] Charts display
- [ ] No console errors

**NOW GO CRUSH THAT INTERVIEW!** 🎯
