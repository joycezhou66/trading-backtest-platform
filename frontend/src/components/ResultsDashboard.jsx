/**
 * Results Dashboard Component
 * Displays backtest results with charts and metrics
 */

import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import './ResultsDashboard.css';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function ResultsDashboard({ results }) {
  const { equity_curve, equity_dates, trades, performance, ticker, strategy, period } = results;

  // Prepare equity curve data for chart
  const equityChartData = {
    labels: equity_dates,
    datasets: [
      {
        label: 'Portfolio Value',
        data: equity_curve,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.1
      }
    ]
  };

  const equityChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Equity Curve - Portfolio Value Over Time',
        font: {
          size: 16
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `Value: $${context.parsed.y.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      y: {
        ticks: {
          callback: function(value) {
            return '$' + value.toLocaleString();
          }
        }
      }
    }
  };

  // Calculate drawdown for chart
  const calculateDrawdown = (equity) => {
    const drawdowns = [];
    let peak = equity[0];

    for (let i = 0; i < equity.length; i++) {
      if (equity[i] > peak) {
        peak = equity[i];
      }
      const drawdown = ((equity[i] - peak) / peak) * 100;
      drawdowns.push(drawdown);
    }

    return drawdowns;
  };

  const drawdownData = calculateDrawdown(equity_curve);

  const drawdownChartData = {
    labels: equity_dates,
    datasets: [
      {
        label: 'Drawdown %',
        data: drawdownData,
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.1
      }
    ]
  };

  const drawdownChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Drawdown Over Time',
        font: {
          size: 16
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `Drawdown: ${context.parsed.y.toFixed(2)}%`;
          }
        }
      }
    },
    scales: {
      y: {
        ticks: {
          callback: function(value) {
            return value.toFixed(1) + '%';
          }
        }
      }
    }
  };

  return (
    <div className="results-dashboard">
      <div className="results-header">
        <h2>Backtest Results</h2>
        <div className="backtest-info">
          <span className="info-item"><strong>Strategy:</strong> {strategy.replace('_', ' ').toUpperCase()}</span>
          <span className="info-item"><strong>Ticker:</strong> {ticker}</span>
          <span className="info-item"><strong>Period:</strong> {period.start} to {period.end}</span>
        </div>
      </div>

      {/* Performance Metrics Grid */}
      <div className="metrics-grid">
        <div className="metric-card highlight">
          <div className="metric-label">Total Return</div>
          <div className={`metric-value ${performance.performance_metrics.total_return >= 0 ? 'positive' : 'negative'}`}>
            {performance.performance_metrics.total_return >= 0 ? '+' : ''}
            {performance.performance_metrics.total_return.toFixed(2)}%
          </div>
        </div>

        <div className="metric-card highlight">
          <div className="metric-label">Sharpe Ratio</div>
          <div className="metric-value">
            {performance.performance_metrics.sharpe_ratio.toFixed(2)}
          </div>
          <div className="metric-subtitle">
            {performance.performance_metrics.sharpe_ratio > 2 ? 'Excellent' :
             performance.performance_metrics.sharpe_ratio > 1 ? 'Good' : 'Fair'}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Max Drawdown</div>
          <div className="metric-value negative">
            {performance.risk_metrics.max_drawdown.toFixed(2)}%
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Win Rate</div>
          <div className="metric-value">
            {performance.trade_metrics.win_rate.toFixed(1)}%
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Sortino Ratio</div>
          <div className="metric-value">
            {performance.performance_metrics.sortino_ratio.toFixed(2)}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Calmar Ratio</div>
          <div className="metric-value">
            {performance.performance_metrics.calmar_ratio.toFixed(2)}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Volatility (Annual)</div>
          <div className="metric-value">
            {performance.risk_metrics.annualized_volatility.toFixed(2)}%
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Profit Factor</div>
          <div className="metric-value">
            {performance.trade_metrics.profit_factor}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Total Trades</div>
          <div className="metric-value">
            {performance.trade_metrics.total_trades}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">VaR (95%)</div>
          <div className="metric-value negative">
            {performance.risk_metrics.var_95.toFixed(2)}%
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">CVaR (95%)</div>
          <div className="metric-value negative">
            {performance.risk_metrics.cvar_95.toFixed(2)}%
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Final Capital</div>
          <div className="metric-value">
            ${performance.summary.final_capital.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-section">
        <div className="chart-container">
          <Line data={equityChartData} options={equityChartOptions} />
        </div>

        <div className="chart-container">
          <Line data={drawdownChartData} options={drawdownChartOptions} />
        </div>
      </div>

      {/* Trades Table */}
      <div className="trades-section">
        <h3>Trade History ({trades.length} trades)</h3>
        <div className="trades-table-container">
          <table className="trades-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Direction</th>
                <th>Entry Date</th>
                <th>Entry Price</th>
                <th>Exit Date</th>
                <th>Exit Price</th>
                <th>P&L %</th>
                <th>P&L $</th>
              </tr>
            </thead>
            <tbody>
              {trades.slice(0, 50).map((trade, idx) => (
                <tr key={idx} className={trade.pnl_percent >= 0 ? 'trade-win' : 'trade-loss'}>
                  <td>{idx + 1}</td>
                  <td className={`direction-${trade.direction}`}>{trade.direction.toUpperCase()}</td>
                  <td>{trade.entry_date}</td>
                  <td>${trade.entry_price.toFixed(2)}</td>
                  <td>{trade.exit_date}</td>
                  <td>${trade.exit_price.toFixed(2)}</td>
                  <td className={trade.pnl_percent >= 0 ? 'positive' : 'negative'}>
                    {trade.pnl_percent >= 0 ? '+' : ''}{trade.pnl_percent.toFixed(2)}%
                  </td>
                  <td className={trade.pnl_dollars >= 0 ? 'positive' : 'negative'}>
                    {trade.pnl_dollars >= 0 ? '+' : ''}${trade.pnl_dollars.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {trades.length > 50 && (
            <p className="table-note">Showing first 50 of {trades.length} trades</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default ResultsDashboard;
