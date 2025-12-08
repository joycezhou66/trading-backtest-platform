/**
 * Strategy Selector Component
 * Allows users to configure and run backtests
 */

import { useState, useEffect } from 'react';
import './StrategySelector.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Common tickers for suggestions
const POPULAR_TICKERS = ['AAPL', 'SPY', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META'];

// Strategy parameter configurations
const STRATEGY_PARAMS = {
  moving_average: {
    fast_window: { label: 'Fast Window', type: 'number', default: 20, min: 5, max: 100 },
    slow_window: { label: 'Slow Window', type: 'number', default: 50, min: 20, max: 200 }
  },
  mean_reversion: {
    window: { label: 'Window', type: 'number', default: 20, min: 10, max: 50 },
    num_std: { label: 'Std Deviations', type: 'number', default: 2.0, min: 1.0, max: 3.0, step: 0.5 }
  },
  momentum: {
    window: { label: 'RSI Window', type: 'number', default: 14, min: 7, max: 28 },
    oversold: { label: 'Oversold Threshold', type: 'number', default: 30, min: 10, max: 40 },
    overbought: { label: 'Overbought Threshold', type: 'number', default: 70, min: 60, max: 90 }
  }
};

function StrategySelector({ onRunBacktest, loading }) {
  const [strategy, setStrategy] = useState('moving_average');
  const [ticker, setTicker] = useState('AAPL');
  const [startDate, setStartDate] = useState('2020-01-01');
  const [endDate, setEndDate] = useState('2023-12-31');
  const [parameters, setParameters] = useState({});

  // Initialize parameters when strategy changes
  useEffect(() => {
    const defaults = {};
    const config = STRATEGY_PARAMS[strategy];
    for (const [key, param] of Object.entries(config)) {
      defaults[key] = param.default;
    }
    setParameters(defaults);
  }, [strategy]);

  const handleSubmit = (e) => {
    e.preventDefault();

    onRunBacktest({
      strategy,
      ticker,
      start_date: startDate,
      end_date: endDate,
      parameters
    });
  };

  const handleParameterChange = (paramName, value) => {
    setParameters(prev => ({
      ...prev,
      [paramName]: parseFloat(value)
    }));
  };

  return (
    <div className="strategy-selector">
      <h2>Configure Backtest</h2>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          {/* Strategy Selection */}
          <div className="form-group">
            <label>Strategy</label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              disabled={loading}
            >
              <option value="moving_average">Moving Average Crossover</option>
              <option value="mean_reversion">Mean Reversion (Bollinger Bands)</option>
              <option value="momentum">Momentum (RSI)</option>
            </select>
          </div>

          {/* Ticker Input */}
          <div className="form-group">
            <label>Ticker Symbol</label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="AAPL"
              disabled={loading}
              required
            />
            <div className="ticker-suggestions">
              {POPULAR_TICKERS.map(t => (
                <button
                  key={t}
                  type="button"
                  className="ticker-chip"
                  onClick={() => setTicker(t)}
                  disabled={loading}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Date Range */}
          <div className="form-group">
            <label>Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <label>End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              disabled={loading}
              required
            />
          </div>
        </div>

        {/* Dynamic Parameters */}
        <div className="parameters-section">
          <h3>Strategy Parameters</h3>
          <div className="form-grid">
            {Object.entries(STRATEGY_PARAMS[strategy]).map(([paramName, config]) => (
              <div key={paramName} className="form-group">
                <label>{config.label}</label>
                <input
                  type="number"
                  value={parameters[paramName] || config.default}
                  onChange={(e) => handleParameterChange(paramName, e.target.value)}
                  min={config.min}
                  max={config.max}
                  step={config.step || 1}
                  disabled={loading}
                  required
                />
                <small>Range: {config.min} - {config.max}</small>
              </div>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="run-button"
          disabled={loading}
        >
          {loading ? 'Running Backtest...' : 'Run Backtest'}
        </button>
      </form>
    </div>
  );
}

export default StrategySelector;
