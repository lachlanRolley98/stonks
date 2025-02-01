import ccxt
import pandas as pd
import backtrader as bt
import time

# 1 - COLLECT HISTORICAL DATA

def fetch_data(symbol, timeframe, limit=1000):
    exchange = ccxt.binance()
    all_bars = []
    since = None

    while True:
        # Fetch data from the exchange
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
        if len(bars) == 0:
            break
        all_bars.extend(bars)

        # Update the timestamp to fetch the next batch of data
        since = bars[-1][0] + 1  # Add 1 to ensure you get the next batch
        time.sleep(1)  # Avoid hitting rate limits

    return all_bars

# Fetch the historical data for BTC/USDT (use 1-hour timeframe or adjust as needed)
bars = fetch_data('ETH/USDT', '1d', limit=1000)  # For longer testing use '1d' or other timeframe
df = pd.DataFrame(bars, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')

# Check the first few rows of the dataframe and the total length of data
print(df.head())
print(f"Data length: {len(df)}")  # Ensure sufficient data

# Ensure the DataFrame has enough data points for SMA200
if len(df) < 200:
    raise ValueError("Not enough data to compute SMA200. Please fetch more data points.")

# 2 - IMPLEMENT YOUR STRATEGY

class SmaCross(bt.SignalStrategy):
    def __init__(self):
        self.sma1 = bt.indicators.SimpleMovingAverage(self.data.close, period=50)
        self.sma2 = bt.indicators.SimpleMovingAverage(self.data.close, period=200)
        self.crossover = bt.indicators.CrossOver(self.sma1, self.sma2)

    def next(self):
        if len(self.data) < 200:
            return

        # Print out the current SMA values for debugging
        print(f"Date: {self.data.datetime.date(0)} | SMA50: {self.sma1[0]} | SMA200: {self.sma2[0]}")

        # Buy signal (SMA50 crosses above SMA200)
        if self.crossover > 0 and not self.position:
            self.buy()
            print(f"Buy Signal at {self.data.datetime.date(0)}")

        # Sell signal (SMA50 crosses below SMA200)
        elif self.crossover < 0 and self.position:
            self.sell()
            print(f"Sell Signal at {self.data.datetime.date(0)}")

        if self.position:
            print(f"Position: {self.position.size} at {self.position.price}")

# 3 - USE BACKTRADER TO TEST THE STRATEGY

cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)

# Convert DataFrame to Backtrader data feed
data = bt.feeds.PandasData(
    dataname=df,
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=5,
    openinterest=-1
)

cerebro.adddata(data)

# Run the backtest
cerebro.run()

# Plot the results
cerebro.plot()
