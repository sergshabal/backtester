import queue
import time
from datetime import datetime
from event import MarketEvent, SignalEvent, OrderEvent, FillEvent
from data import HistoricCSVDataHandler
from strategies.hold import BuyAndHoldStrategy, SellAndHoldStrategy
from strategies.macd import MovingAveragesLongStrategy, MovingAveragesLongShortStrategy
from strategies.stop_loss import StopLossStrategy
from portfolio import NaivePortfolio
from execution import SimulateExecutionHandler

events = queue.Queue()
data = HistoricCSVDataHandler(events, 'csv/', ['OMXS30'])
portfolio = NaivePortfolio(data, events, '', initial_capital=1500)
# strategy = BuyAndHoldStrategy(data, events, portfolio)
# strategy = SellAndHoldStrategy(data, events, portfolio)
strategy = MovingAveragesLongStrategy(data, events, portfolio, 100, 200)
# strategy = MovingAveragesLongShortStrategy(data, events, portfolio, 100, 200)
# strategy = StopLossStrategy(data, events, portfolio, 0.9)
portfolio.strategy_name = strategy.name
broker = SimulateExecutionHandler(events)

while True:
    data.update_latest_data()
    if data.continue_backtest == False:
        break

    while True:
        try:
            event = events.get(block=False)
        except queue.Empty:
            break

        if event is not None:
            if event.type == 'MARKET':
                strategy.calculate_signals(event)
                portfolio.update_timeindex(event)
            elif event.type == 'SIGNAL':
                portfolio.update_signal(event)
            elif event.type == 'ORDER':
                broker.execute_order(event)
            elif event.type == 'FILL':
                portfolio.update_fill(event)

    # time.sleep(10*60)

stats = portfolio.output_summary_stats()
for stat in stats:
    print(stat[0] + ": " + stat[1])
portfolio.plot_performance()
