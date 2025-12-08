from data.data_handler import DataHandler
from strategies.moving_average import MovingAverageStrategy
from engine.backtester import Backtester

dh = DataHandler(static_data_dir='static_data')
data = dh.get_data('AAPL', '2020-01-01', '2024-12-01')

strategy = MovingAverageStrategy({'fast_window': 20, 'slow_window': 50})
backtester = Backtester(100000)
results = backtester.run(strategy, data)

print(f'Number of trades: {len(results["trades"])}')
if len(results['trades']) > 0:
    print('First 5 trades:')
    for trade in results['trades'][:5]:
        print(f"  Entry: {trade['entry_date']}, Exit: {trade['exit_date']}, P&L: ${trade['pnl']:.2f}")
