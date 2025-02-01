import ccxt
import pandas as pd
import backtrader as bt

# 1 - COLLECT HISTORICAL DATA

# Use ccxt library to fetch historical data from exchanges
exchange = ccxt.binance()

# Get the open, high, low, close, volume
bars = exchange.fetch_ohlcv('BTC/USDT', timeframe='1d', limit=250)  # Fetch more data points
# Put that into a dataframe with column names
df = pd.DataFrame(bars, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
# Convert timestamp to datetime
df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
# Check the data
print(df.head())
print(f"Data length: {len(df)}")  # Check data length

# Ensure the DataFrame has enough data points for SMA200
if len(df) < 200:
    raise ValueError("Not enough data to compute SMA200. Please fetch more data points.")

# 2 - IMPLEMENT YOUR STRATEGY WITH ORDER EXECUTION

class SmaCross(bt.SignalStrategy):
    def __init__(self):
        # Create the indicators: 50-day and 200-day SMAs
        self.sma1 = bt.ind.SMA(period=50)
        self.sma2 = bt.ind.SMA(period=200)
        self.crossover = bt.ind.CrossOver(self.sma1, self.sma2)

    def next(self):
        # Only start processing after enough data points
        if len(self.data) < 200:
            return

        # Check if there is a crossover
        if self.crossover > 0:  # Buy signal (50 SMA crosses above 200 SMA)
            self.buy()  # Execute a market buy order (for backtest)
            print(f"Buy Signal at {self.data.datetime.date(0)} | Price: {self.data.close[0]}")
            place_live_order('buy', amount=0.001)  # Execute live buy order (actual trade)
        elif self.crossover < 0:  # Sell signal (50 SMA crosses below 200 SMA)
            self.sell()  # Execute a market sell order (for backtest)
            print(f"Sell Signal at {self.data.datetime.date(0)} | Price: {self.data.close[0]}")
            place_live_order('sell', amount=0.001)  # Execute live sell order (actual trade)

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

# Add the broker for live trading
cerebro.broker.set_cash(1000)  # Set initial capital for trading
cerebro.broker.set_commission(commission=0.001)  # Set commission (optional)
cerebro.broker.set_slippage_perc(0.01)  # Set slippage (optional)

# Run the backtest
cerebro.run()

# For live trading, you'd continuously run the strategy on new data, not just once.
cerebro.plot()

# 4 - ORDER EXECUTION (LIVE TRADING) - PLACING REAL ORDERS

# Function to place live orders (make sure API keys are set up and your exchange supports trading)
def place_live_order(action, amount=0.001):
    try:
        if action == 'buy':
            order = exchange.create_market_buy_order('BTC/USDT', amount)
            print(f"Market Buy Order Executed: {order}")
        elif action == 'sell':
            order = exchange.create_market_sell_order('BTC/USDT', amount)
            print(f"Market Sell Order Executed: {order}")
    except Exception as e:
        print(f"Error placing order: {e}")

# Example usage with live orders (uncomment to test with live trading):
# place_live_order('buy', amount=0.001)  # For a buy order
# place_live_order('sell', amount=0.001)  # For a sell order
