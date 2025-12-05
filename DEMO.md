# Demo Script for Interview Presentation

## Pre-Demo Checklist (Run 30 minutes before interview)

### 1. Start Backend
```bash
cd backend
source venv/bin/activate  # If using virtual environment
python app.py
```
**Verify**: Navigate to `http://localhost:5000/api/health` - should return `{"status": "healthy"}`

### 2. Pre-Cache Data
```bash
curl -X POST http://localhost:5000/api/cache-data \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "SPY", "MSFT", "GOOGL", "AMZN", "TSLA"], "start_date": "2018-01-01", "end_date": "2024-12-01"}'
```
**Expected**: All tickers return "success"

### 3. Start Frontend
```bash
cd frontend
npm run dev
```
**Verify**: Open `http://localhost:5173` - dashboard should load

### 4. Test Run
Run one quick backtest (AAPL, Moving Average, 2020-2023) to verify everything works.

---

## Demo Flow (10-15 minutes)

### Part 1: Introduction (2 minutes)

**Say**:
> "I built an algorithmic trading backtesting platform that hedge funds use to evaluate systematic trading strategies. It implements three classic strategies with comprehensive performance and risk analytics."

**Show**: Homepage with clean, professional design

**Highlight**:
- Production-quality architecture
- Real market data (Yahoo Finance)
- Institutional-grade metrics (Sharpe ratio, VaR, etc.)

---

### Part 2: Strategy Demo - Moving Average (4 minutes)

**Configure**:
- Strategy: Moving Average Crossover
- Ticker: AAPL
- Start: 2020-01-01
- End: 2023-12-31
- Parameters: Fast=20, Slow=50 (defaults)

**Click**: "Run Backtest"

**While loading (should be <5 seconds)**:
> "The strategy buys when the 20-day moving average crosses above the 50-day moving average, indicating an upward trend. This is a classic trend-following approach used by CTAs and hedge funds."

**When results load, walk through**:

1. **Equity Curve**
   > "Portfolio grew from $100,000 to $[final value], a [X]% return over 3 years. The upward slope shows the strategy captured AAPL's strong bull run."

2. **Sharpe Ratio**
   > "Sharpe ratio of [X] means we earned [X] units of return per unit of risk. Hedge funds typically target Sharpe > 1, so this is [good/excellent]."

3. **Maximum Drawdown**
   > "Max drawdown of [X]% shows the worst peak-to-trough decline. This is critical for risk management - investors need to know the worst-case scenario."

4. **Trade History**
   > "The strategy executed [X] trades. Win rate is [Y]%, but what matters more is the profit factor of [Z] - we make $[Z] for every $1 lost."

---

### Part 3: Strategy Comparison (4 minutes)

**Say**:
> "Let me show how different strategies perform on the same asset. This is how hedge funds evaluate strategy robustness."

**Run**: Mean Reversion strategy on SPY (2020-2023)

**Configure**:
- Strategy: Mean Reversion (Bollinger Bands)
- Ticker: SPY
- Same date range
- Parameters: window=20, num_std=2 (defaults)

**Explain while loading**:
> "This strategy assumes price reverts to its mean. When price touches the lower Bollinger Band (2 standard deviations below average), it's oversold - we buy expecting a bounce back."

**Compare results**:
- Point out differences in equity curve shape
- Highlight metrics (Sortino ratio shows downside risk focus)
- Discuss which market conditions suit each strategy

---

### Part 4: Technical Deep Dive (3 minutes)

**Show code** (backend/strategies/moving_average.py):

**Highlight**:
- Clean OOP design (Strategy pattern)
- Comprehensive docstrings explaining WHY not just WHAT
- Type hints for production code
- Edge case handling

**Say**:
> "I used the Strategy design pattern - all strategies inherit from BaseStrategy. This makes adding new strategies trivial and ensures consistent interfaces."

**Show** performance.py:

**Highlight**:
- Sharpe ratio calculation with comments explaining formula
- VaR calculation using historical simulation
- Vectorized pandas operations for performance

**Say**:
> "I calculated industry-standard metrics like Sharpe ratio, Sortino ratio, and Value-at-Risk. Each metric has detailed comments explaining what it measures and why it matters to investors."

---

### Part 5: Architecture & Scalability (2 minutes)

**Discuss**:

1. **Data Caching**
   > "I implemented a caching layer that stores downloaded data locally. This is critical for demos like this and for respecting API rate limits. In production, this would be Redis."

2. **API Design**
   > "RESTful API with proper error handling. Returns meaningful error messages with appropriate HTTP status codes. Easy to add authentication, rate limiting for production."

3. **Frontend**
   > "React with modern hooks, component-based architecture. Chart.js for visualizations. The design is inspired by Bloomberg Terminal - professional, data-dense but readable."

4. **Scalability** (if asked)
   > "For production scale:
   > - Add Celery for async backtests (long-running jobs)
   > - PostgreSQL for persistence
   > - Docker containers + Kubernetes for orchestration
   > - Redis for distributed caching
   > - Add monitoring (Prometheus/Grafana)"

---

## Expected Questions & Answers

### Technical Questions

**Q: How do you prevent overfitting?**

A: "Great question. This MVP doesn't implement it, but in production I'd add:
- Walk-forward optimization (train on period 1, test on period 2, roll forward)
- Out-of-sample testing (hold out recent data)
- Parameter sensitivity analysis (does strategy work with window=15 and 25, or only 20?)
- Monte Carlo simulation with randomized entry times

The key is ensuring the strategy works on data it hasn't seen."

---

**Q: What about transaction costs and slippage?**

A: "You're right - this is a significant oversight in basic backtests. Real trading has:
- Commission costs (though lower now than historically)
- Slippage (getting filled at worse prices than expected)
- Market impact (large orders move the market)

For production, I'd add a transaction cost model:
- Fixed commission per trade (e.g., $1)
- Percentage slippage based on bid-ask spread
- Market impact model for large orders

This typically reduces returns by 1-3% annually."

---

**Q: Why Sharpe ratio? What are its limitations?**

A: "Sharpe ratio is the most widely used risk-adjusted return metric because it's simple and intuitive. But it has limitations:
- Assumes normal distribution (markets have fat tails)
- Penalizes upside volatility (we like volatile gains!)
- Sensitive to observation frequency

That's why I also include Sortino ratio (only downside volatility) and Calmar ratio (return/max drawdown). Different investors care about different metrics."

---

**Q: Can this handle high-frequency trading?**

A: "No, this is designed for daily timeframe strategies. HFT requires:
- Tick-by-tick data (millisecond precision)
- Co-location (servers next to exchange)
- Different programming languages (C++, FPGA for ultra-low latency)
- Completely different infrastructure

This platform is for systematic strategies that trade daily/weekly, which is what most hedge funds do."

---

**Q: How would you validate these results?**

A: "Several approaches:
1. **Compare to buy-and-hold**: Does strategy beat simple buying SPY?
2. **Check trade count**: Too few trades = unreliable, too many = overtrading
3. **Analyze drawdowns**: Are they tolerable for investors?
4. **Walk-forward testing**: Does it work on new data?
5. **Multiple assets**: Does strategy work on MSFT, GOOGL, etc.?

I'd also check for data snooping bias - did I test 100 parameters and only show the best one?"

---

### Business/Product Questions

**Q: Who is the target user?**

A: "Quantitative analysts and portfolio managers at hedge funds/asset managers. They need to:
- Test new strategy ideas quickly
- Compare strategies on same data
- Generate reports for investment committees
- Do parameter sensitivity analysis

Future features: save backtests, compare multiple strategies side-by-side, export PDF reports."

---

**Q: What's your go-to-market strategy?**

A: "Start with:
1. **Free tier**: Limited backtests, basic strategies (get users hooked)
2. **Pro tier** ($99/mo): Unlimited backtests, all strategies, export reports
3. **Enterprise** ($999/mo): Custom strategies, API access, white-label

Target: 10,000 free users → 1% convert to Pro (100 × $99 = $9,900/mo) → 10 Enterprise ($9,990/mo) = ~$20K MRR in Year 1."

---

**Q: How is this different from QuantConnect/Zipline?**

A: "Great question - those are established platforms. Differences:
- **Simplicity**: This is focused on classic strategies, not complex ML models
- **Speed**: Pre-caching makes backtests instant (10x faster than competitors)
- **Education**: Comprehensive code comments teach strategies, not just implement them
- **UX**: Modern React UI vs their outdated interfaces

This is for practitioners who want quick validation, not researchers building complex multi-asset portfolios."

---

## Troubleshooting

### Backtest fails with "Insufficient data"
- Check date range (need at least 50 days)
- Verify ticker exists (use common stocks: AAPL, SPY, MSFT)

### Frontend can't connect to backend
- Verify backend is running: `http://localhost:5000/api/health`
- Check CORS is enabled in app.py
- Check API_URL in frontend code

### Slow backtests
- Run pre-cache script before demo
- Check cache/ folder has .pkl files
- Consider shorter date ranges

---

## Post-Demo

### If they're interested:

**Offer to send**:
- GitHub repo link
- Technical write-up on architecture decisions
- List of future enhancements

**Be ready to discuss**:
- Timeline to production (3-6 months with team)
- Team size needed (2 backend, 1 frontend, 1 QA)
- Infrastructure costs ($500-1000/mo for moderate scale)

---

## Closing Statement

> "This platform demonstrates my ability to build production-quality systems for quantitative finance. I combined:
> - Strong engineering (clean architecture, error handling, caching)
> - Domain knowledge (strategy implementation, risk metrics)
> - Product thinking (caching for demos, professional UI)
>
> I'm excited to bring these skills to [company name] and contribute to [specific thing you researched about their trading systems]."

---

## Success Metrics

**Nailed it if**:
- Backtests run in <10 seconds ✓
- You explained Sharpe ratio confidently ✓
- You handled technical questions without fumbling ✓
- They asked about your availability/salary ✓

**Could be better if**:
- Backtest took >15 seconds
- Couldn't explain a metric
- Didn't prepare for a question

**Red flags**:
- Backend crashes
- Cache doesn't work (slow backtests)
- UI breaks on their screen

Good luck! You've got this. 🚀
