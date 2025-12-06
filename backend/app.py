"""
Flask API for Algorithmic Trading Backtesting Platform

ARCHITECTURE:
- RESTful API design
- Stateless (each request is independent)
- JSON responses
- CORS enabled for React frontend

WHY FLASK: Lightweight, perfect for MVP/demo. In production, might use FastAPI
for async support or Django for full framework features.

ENDPOINTS:
1. POST /api/backtest - Run strategy backtest
2. GET /api/strategies - List available strategies
3. POST /api/cache-data - Pre-download data
4. GET /api/health - Health check
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import os

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.data_handler import DataHandler
from engine.backtester import Backtester
from engine.performance import generate_performance_report
from strategies.moving_average import MovingAverageStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for React frontend
# WHY: Browser security prevents frontend (localhost:3000) from calling
# backend (localhost:5000) without CORS headers
CORS(app)

# Initialize data handler and backtester
# WHY GLOBAL: These are stateless, safe to share across requests
# Use absolute path for static_data_dir to ensure it works in deployed environment
import os
static_data_path = os.path.join(os.path.dirname(__file__), 'static_data')
logger.info(f"Static data path: {static_data_path}")
logger.info(f"Static data exists: {os.path.exists(static_data_path)}")
if os.path.exists(static_data_path):
    logger.info(f"Static data files: {os.listdir(static_data_path)}")

data_handler = DataHandler(cache_dir='cache', static_data_dir=static_data_path)
backtester = Backtester(initial_capital=100000.0)

# Strategy registry
# WHY REGISTRY PATTERN: Easy to add new strategies without changing API code
STRATEGY_REGISTRY = {
    'moving_average': MovingAverageStrategy,
    'mean_reversion': MeanReversionStrategy,
    'momentum': MomentumStrategy
}


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    WHY: Essential for monitoring, load balancers, deployment checks.
    Quick way to verify service is running.

    Returns:
        200 OK with status message
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Trading Backtest API',
        'version': '1.0.1',
        'has_session': hasattr(data_handler, 'session')
    }), 200

@app.route('/api/test-yfinance', methods=['GET'])
def test_yfinance():
    """Debug endpoint to test yfinance directly"""
    import yfinance as yf
    try:
        # Try multiple methods
        ticker = yf.Ticker("AAPL", session=data_handler.session)

        # Method 1: period parameter
        data1 = ticker.history(period="1mo")

        # Method 2: start/end dates
        data2 = ticker.history(start="2024-01-01", end="2024-01-10")

        # Method 3: yf.download
        data3 = yf.download("AAPL", start="2024-01-01", end="2024-01-10", progress=False)

        return jsonify({
            'success': True,
            'method1_period_rows': len(data1),
            'method2_dates_rows': len(data2),
            'method3_download_rows': len(data3),
            'columns': list(data1.columns) if len(data1) > 0 else list(data2.columns) if len(data2) > 0 else list(data3.columns) if len(data3) > 0 else []
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'type': type(e).__name__
        }), 500


@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """
    List available strategies and their parameters.

    WHY: Self-documenting API. Frontend can dynamically generate
    parameter forms without hardcoding strategy details.

    Returns:
        200 OK with list of strategies and metadata
    """
    try:
        strategies = []

        for name, strategy_class in STRATEGY_REGISTRY.items():
            # Create instance with defaults to get parameter info
            instance = strategy_class()
            info = instance.get_parameter_info()
            info['id'] = name  # Add ID for frontend reference
            strategies.append(info)

        return jsonify({
            'strategies': strategies,
            'count': len(strategies)
        }), 200

    except Exception as e:
        logger.error(f"Error listing strategies: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to list strategies',
            'message': str(e)
        }), 500


@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """
    Execute strategy backtest.

    Request body:
        {
            "strategy": "moving_average",
            "ticker": "AAPL",
            "start_date": "2020-01-01",
            "end_date": "2023-12-31",
            "parameters": {"fast_window": 20, "slow_window": 50}
        }

    Returns:
        200 OK with backtest results (equity curve, trades, metrics)
        400 Bad Request if validation fails
        500 Internal Server Error if backtest fails

    WHY POST: Backtests have parameters and trigger computation.
    POST is semantically correct (not idempotent, creates result).
    """
    try:
        # Parse request body
        data = request.get_json()

        # Validate required fields
        # WHY EXPLICIT VALIDATION: Better error messages than exceptions
        required_fields = ['strategy', 'ticker', 'start_date', 'end_date']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing
            }), 400

        strategy_name = data['strategy']
        ticker = data['ticker'].upper()  # Normalize to uppercase
        start_date = data['start_date']
        end_date = data['end_date']
        parameters = data.get('parameters', {})

        logger.info(f"Running backtest: {strategy_name} on {ticker} from {start_date} to {end_date}")

        # Validate strategy exists
        if strategy_name not in STRATEGY_REGISTRY:
            return jsonify({
                'error': 'Invalid strategy',
                'message': f"Strategy '{strategy_name}' not found",
                'available_strategies': list(STRATEGY_REGISTRY.keys())
            }), 400

        # Validate date range
        # WHY SEPARATE VALIDATION: Fail fast with clear error messages
        try:
            data_handler.validate_date_range(start_date, end_date)
        except ValueError as e:
            return jsonify({
                'error': 'Invalid date range',
                'message': str(e)
            }), 400

        # Fetch market data (uses cache if available)
        try:
            market_data = data_handler.get_data(ticker, start_date, end_date)
        except ValueError as e:
            return jsonify({
                'error': 'Data fetch failed',
                'message': str(e),
                'ticker': ticker
            }), 400

        # Initialize strategy with parameters
        try:
            strategy_class = STRATEGY_REGISTRY[strategy_name]
            strategy = strategy_class(parameters)
        except ValueError as e:
            return jsonify({
                'error': 'Invalid strategy parameters',
                'message': str(e),
                'parameters': parameters
            }), 400

        # Run backtest
        # WHY TRY-EXCEPT: Backtests can fail for many reasons (bad data, strategy errors)
        # Catch all and return meaningful errors
        try:
            results = backtester.run(strategy, market_data)
        except Exception as e:
            logger.error(f"Backtest execution failed: {e}", exc_info=True)
            return jsonify({
                'error': 'Backtest execution failed',
                'message': str(e)
            }), 500

        # Calculate performance metrics
        try:
            performance = generate_performance_report(
                equity_curve=results['equity_curve'],
                returns=results['returns'],
                trades=results['trades'],
                initial_capital=results['initial_capital']
            )
        except Exception as e:
            logger.error(f"Performance calculation failed: {e}", exc_info=True)
            # Return results without performance metrics if calculation fails
            performance = {'error': f'Failed to calculate metrics: {str(e)}'}

        # Compile response
        response = {
            'success': True,
            'strategy': strategy_name,
            'ticker': ticker,
            'period': {
                'start': start_date,
                'end': end_date
            },
            'equity_curve': results['equity_curve'],
            'equity_dates': results['equity_dates'],
            'positions': results['positions'],
            'position_dates': results['position_dates'],
            'trades': results['trades'],
            'performance': performance
        }

        logger.info(f"Backtest completed successfully: {len(results['trades'])} trades")

        return jsonify(response), 200

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error in backtest endpoint: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/cache-data', methods=['POST'])
def cache_data():
    """
    Pre-download and cache data for common tickers.

    Request body:
        {
            "tickers": ["AAPL", "SPY", "MSFT"],
            "start_date": "2018-01-01",  # optional
            "end_date": "2024-12-01"      # optional
        }

    WHY: Run this before demos to ensure instant backtests.
    No waiting for API calls during presentation.

    Returns:
        200 OK with caching results
    """
    try:
        data = request.get_json()

        # Validate tickers
        tickers = data.get('tickers', [])
        if not tickers:
            return jsonify({
                'error': 'No tickers provided',
                'message': 'Please provide list of tickers to cache'
            }), 400

        # Optional date range (use defaults if not provided)
        start_date = data.get('start_date', '2018-01-01')
        end_date = data.get('end_date', '2024-12-01')

        logger.info(f"Caching data for {len(tickers)} tickers")

        # Pre-cache data
        results = data_handler.pre_cache_data(tickers, start_date, end_date)

        # Count successes and failures
        successes = sum(1 for r in results.values() if r == 'success')
        failures = len(results) - successes

        return jsonify({
            'success': True,
            'message': f'Cached {successes} tickers, {failures} failed',
            'results': results,
            'stats': {
                'total': len(tickers),
                'succeeded': successes,
                'failed': failures
            }
        }), 200

    except Exception as e:
        logger.error(f"Cache data error: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to cache data',
            'message': str(e)
        }), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with JSON response."""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors (wrong HTTP method)."""
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The HTTP method is not supported for this endpoint'
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    # Development server
    # WHY: For local testing. In production, use gunicorn (see requirements.txt)
    logger.info("Starting Flask development server...")
    logger.info("API available at: http://localhost:5000")
    logger.info("Health check: http://localhost:5000/api/health")

    app.run(
        host='0.0.0.0',  # WHY: Listen on all interfaces (allows Docker, remote access)
        port=5000,
        debug=True  # WHY: Auto-reload on code changes, detailed errors
    )
