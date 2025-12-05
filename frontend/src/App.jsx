/**
 * Main App Component - Trading Backtest Dashboard
 *
 * WHY THIS STRUCTURE: Clean, professional single-page application
 * State flows down, events flow up (React best practice)
 */

import { useState } from 'react';
import './App.css';
import StrategySelector from './components/StrategySelector';
import ResultsDashboard from './components/ResultsDashboard';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

function App() {
  // State management
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  /**
   * Handle backtest execution
   * WHY ASYNC: API calls must be asynchronous
   */
  const handleRunBacktest = async (backtestParams) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch(`${API_URL}/api/backtest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backtestParams)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Backtest failed');
      }

      setResults(data);
    } catch (err) {
      setError(err.message);
      console.error('Backtest error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Algorithmic Trading Backtest Platform</h1>
        <p className="subtitle">Systematic Strategy Analysis & Performance Evaluation</p>
      </header>

      <div className="app-container">
        {/* Strategy Configuration Section */}
        <StrategySelector
          onRunBacktest={handleRunBacktest}
          loading={loading}
        />

        {/* Error Display */}
        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="loading-banner">
            Running backtest... This may take a few seconds.
          </div>
        )}

        {/* Results Dashboard */}
        {results && !loading && (
          <ResultsDashboard results={results} />
        )}
      </div>

      <footer className="app-footer">
        <p>Production-quality backtesting engine for systematic trading strategies</p>
      </footer>
    </div>
  );
}

export default App;
