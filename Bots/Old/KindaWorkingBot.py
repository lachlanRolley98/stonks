import ccxt
import pandas as pd
import time
import backtrader as bt

# 1 - CONNECT TO EXCHANGE (Binance in this case)

exchange = ccxt.binance({
    'apiKey': 'your_api_key_here',
    'secret': 'your_secret_key_here',
})

# 2 - COLLECT HISTORICAL DATA (for initial backtest and ongoing updates)
def get_data():
    bars = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=200)  # Fetch last 200 hours of data
    df = pd.DataFrame(bars, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    return df

# 3 - STRATEGY DEFINITION (SMA Crossover)
class SmaCross(bt.SignalStrategy):
    def __init__(self):
        self.sma1 = bt.ind.SMA(period=50)
        self.sma2 = bt.ind.SMA(period=200)
        self.crossover = bt.ind.CrossOver(self.sma1, self.sma2)
        self.signal_add(bt.SIGNAL_LONG, self.crossover)
        self.signal_add(bt.SIGNAL_SHORT, -self.crossover)

    def next(self):
        # Logic for placing buy/sell orders on live market
        if self.position:  # Check if we have an open position
            if self.position.size > 0 and self.crossover < 0:  # If we are long and crossover turns negative
                self.close()  # Sell
            elif self.position.size < 0 and self.crossover > 0:  # If we are short and crossover turns positive
                self.close()  # Buy

        # Add buy signal condition
        elif self.crossover > 0:  # If crossover happens (SMA50 crosses above SMA200)
            self.buy()

        # Add sell signal condition
        elif self.crossover < 0:  # If crossover happens (SMA50 crosses below SMA200)
            self.sell()

# 4 - ORDER EXECUTION FUNCTION (place live orders with exchange)
def place_live_order(action, symbol='BTC/USDT', amount=0.001):
    try:
        if action == 'buy':
            order = exchange.create_market_buy_order(symbol, amount)
            print(f"Buy Order Executed: {order}")
        elif action == 'sell':
            order = exchange.create_market_sell_order(symbol, amount)
            print(f"Sell Order Executed: {order}")
    except ccxt.BaseError as e:
        print(f"Error executing order: {e}")

# 5 - BACKTEST STRATEGY ON INITIAL DATA (First test using historical data)
def run_backtest():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCross)

    # Initial historical data for backtest
    df = get_data()

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
    cerebro.run()

# 6 - LIVE TRADING LOOP (Run this every 5 minutes or whatever interval you prefer)
def live_trading_loop():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCross)

    while True:
        df = get_data()  # Get latest data

        # Convert new DataFrame to Backtrader data feed
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
        cerebro.run()  # Run strategy logic

        # Here, we check for buy or sell signals
        if cerebro.strats[0][0].position:  # Check if there's a position open
            if cerebro.strats[0][0].position.size > 0:  # Long position
                if cerebro.strats[0][0].crossover < 0:  # Crossover turns negative
                    place_live_order('sell')  # Sell the position
            elif cerebro.strats[0][0].position.size < 0:  # Short position
                if cerebro.strats[0][0].crossover > 0:  # Crossover turns positive
                    place_live_order('buy')  # Buy the position back

        # Wait before checking again (set to your preferred interval)
        time.sleep(300)  # 5-minute interval (change as needed)

# 7 - RUN THE BOT
if __name__ == "__main__":
    run_backtest()  # Optionally run the backtest first
    live_trading_loop()  # Start live trading


"""
Live Data Fetching: The get_data() function fetches real-time data every time the loop runs.
Trading Strategy: The SmaCross class now checks for buy and sell signals based on the SMA crossover, and it triggers live orders using place_live_order().
Live Trading Loop: The live_trading_loop() runs indefinitely, checks for new data every 5 minutes (or your chosen interval), and places orders in real time.
Order Execution: The place_live_order() function sends market buy and sell orders to Binance using the ccxt API.
What You Need to Change:
API Keys: Replace 'your_api_key_here' and 'your_secret_key_here' with your actual Binance API keys.
Interval: The loop runs every 5 minutes (time.sleep(300)). You can adjust the sleep time to a different value (in seconds) if you want a different frequency for checking the market.
Amount: The place_live_order() function uses 0.001 BTC as a sample order amount. You can change that to any value you wish.
How It Works:
Backtesting: The run_backtest() function allows you to test your strategy with historical data first.
Live Trading: The live_trading_loop() fetches new data at intervals, evaluates the strategy, and places live buy/sell orders based on the signals generated.
Continuous Trading:
The bot continuously runs in the background, making decisions every interval, and placing orders based on your strategy's signals.
"""

