import backtrader as bt
from datetime import datetime



# This was made buy asking copiolt for a trading strategy for ceribro. Then asking it over and over to make it more advanced


class AdvancedComplexStrategy(bt.Strategy):
    # Define the parameters for the strategy
    params = (
        ('bollinger_period', 20),  # Period for Bollinger Bands
        ('bollinger_devfactor', 2),  # Standard deviation factor for Bollinger Bands
        ('rsi_period', 14),  # Period for RSI
        ('rsi_overbought', 70),  # RSI value indicating overbought condition
        ('rsi_oversold', 30),  # RSI value indicating oversold condition
        ('macd1', 12),  # Fast period for MACD
        ('macd2', 26),  # Slow period for MACD
        ('macdsig', 9),  # Signal period for MACD
        ('ema_fast', 10),  # Period for fast EMA
        ('ema_slow', 50),  # Period for slow EMA
        ('trail_percent', 0.02),  # Trailing stop percentage (2%)
    )

    def __init__(self):
        # Initialize Bollinger Bands indicator
        self.bollinger = bt.indicators.BollingerBands(
            self.data.close, period=self.params.bollinger_period, devfactor=self.params.bollinger_devfactor)

        # Initialize RSI indicator
        self.rsi = bt.indicators.RelativeStrengthIndex(
            self.data.close, period=self.params.rsi_period)

        # Initialize MACD indicator
        self.macd = bt.indicators.MACD(
            self.data.close, period_me1=self.params.macd1, period_me2=self.params.macd2, period_signal=self.params.macdsig)

        # Initialize fast EMA
        self.ema_fast = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.ema_fast)

        # Initialize slow EMA
        self.ema_slow = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.ema_slow)

        # Variables to keep track of orders and prices
        self.order = None
        self.buy_price = None
        self.sell_price = None

    def next(self):
        # Check if there is an open order
        if self.order:
            return

        # Buy signal: price below lower Bollinger Band, RSI oversold, MACD bullish, fast EMA above slow EMA
        if self.data.close < self.bollinger.lines.bot and self.rsi < self.params.rsi_oversold and self.macd.macd > self.macd.signal and self.ema_fast > self.ema_slow:
            self.order = self.buy()
            self.buy_price = self.data.close[0]
            self.sell_price = self.buy_price * (1.0 + self.params.trail_percent)

        # Sell signal: price above upper Bollinger Band, RSI overbought, MACD bearish, fast EMA below slow EMA
        elif self.data.close > self.bollinger.lines.top and self.rsi > self.params.rsi_overbought and self.macd.macd < self.macd.signal and self.ema_fast < self.ema_slow:
            self.order = self.sell()
            self.sell_price = self.data.close[0]
            self.buy_price = self.sell_price * (1.0 - self.params.trail_percent)

    def notify_order(self, order):
        # Log order execution
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price}')
            self.order = None

    def notify_trade(self, trade):
        # Log trade results
        if not trade.isclosed:
            return
        self.log(f'OPERATION PROFIT, GROSS {trade.pnl}, NET {trade.pnlcomm}')

    def log(self, txt, dt=None):
        # Log function for strategy
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(AdvancedComplexStrategy)

    # Load your data here
    data = bt.feeds.YahooFinanceData(dataname='AAPL',
                                     fromdate=datetime(2020, 1, 1),
                                     todate=datetime(2021, 1, 1))
    cerebro.adddata(data)

    # Set initial cash
    cerebro.broker.setcash(10000.0)

    # Run the strategy
    cerebro.run()

    # Plot the results
    cerebro.plot()


'''
1. Bollinger Bands
Bollinger Bands are a type of statistical chart characterizing the prices and volatility over time of a financial instrument or commodity. They consist of three lines:

Middle Band: This is a simple moving average (SMA) of the price, typically over 20 periods.
Upper Band: This is the middle band plus two standard deviations of the price.
Lower Band: This is the middle band minus two standard deviations of the price.
Purpose: Bollinger Bands help identify overbought and oversold conditions. When the price touches the upper band, it may be overbought, and when it touches the lower band, it may be oversold.

2. Relative Strength Index (RSI)
RSI is a momentum oscillator that measures the speed and change of price movements. It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions.

Overbought: RSI above 70 suggests that the asset may be overbought.
Oversold: RSI below 30 suggests that the asset may be oversold.
Purpose: RSI helps confirm the signals given by other indicators like Bollinger Bands. For example, if the price is below the lower Bollinger Band and the RSI is below 30, it strengthens the signal that the asset is oversold.

3. Moving Average Convergence Divergence (MACD)
MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a security’s price. It consists of:

MACD Line: The difference between the 12-period EMA and the 26-period EMA.
Signal Line: A 9-period EMA of the MACD Line.
Histogram: The difference between the MACD Line and the Signal Line.
Purpose: MACD helps identify changes in the strength, direction, momentum, and duration of a trend. When the MACD Line crosses above the Signal Line, it’s a bullish signal (buy). When it crosses below, it’s a bearish signal (sell).

4. Exponential Moving Averages (EMA)
EMA is a type of moving average that places a greater weight and significance on the most recent data points. It reacts more quickly to recent price changes than a simple moving average (SMA).

Fast EMA: A shorter period EMA (e.g., 10 periods).
Slow EMA: A longer period EMA (e.g., 50 periods).
Purpose: EMAs help identify the direction of the trend. When the fast EMA is above the slow EMA, it indicates an uptrend. When the fast EMA is below the slow EMA, it indicates a downtrend.

5. Trailing Stop-Loss
A Trailing Stop-Loss is a type of stop-loss order that moves with the price. It is set at a certain percentage below (for long positions) or above (for short positions) the market price.

Purpose: Trailing stop-loss helps protect profits by allowing the stop-loss level to move with the price as it moves in favor of the trade. If the price reverses by the trailing amount, the position is closed.

6. Dynamic Position Sizing
Dynamic Position Sizing adjusts the size of the position based on the volatility of the asset. Higher volatility may lead to smaller position sizes to manage risk, while lower volatility may allow for larger positions.

Purpose: This helps manage risk by ensuring that the potential loss on any single trade is kept within acceptable limits, regardless of the asset’s volatility.

Putting It All Together
The strategy combines these indicators and mechanisms to make informed trading decisions:

Entry Signal:
Buy: When the price is below the lower Bollinger Band, RSI is below 30, MACD Line is above the Signal Line, and the fast EMA is above the slow EMA.
Sell: When the price is above the upper Bollinger Band, RSI is above 70, MACD Line is below the Signal Line, and the fast EMA is below the slow EMA.
Risk Management:
Trailing Stop-Loss: Protects profits by adjusting the stop-loss level as the price moves in favor of the trade.
Dynamic Position Sizing: Adjusts the position size based on the asset’s volatility to manage risk effectively.

'''


'''
Imports and Class Definition:
import backtrader as bt: Imports the Backtrader library.
class AdvancedComplexStrategy(bt.Strategy): Defines a new strategy class inheriting from bt.Strategy.
Parameters:
params: A tuple containing the parameters for the strategy, such as periods for Bollinger Bands, RSI, MACD, EMAs, and the trailing stop percentage.
Initialization (__init__ method):
Initializes the indicators (Bollinger Bands, RSI, MACD, EMAs) using the parameters defined.
Sets up variables to keep track of orders and prices.
Next (next method):
Checks if there is an open order. If there is, it returns without doing anything.
Defines the conditions for buying and selling based on the indicators:
Buy: When the price is below the lower Bollinger Band, RSI is oversold, MACD is bullish, and the fast EMA is above the slow EMA.
Sell: When the price is above the upper Bollinger Band, RSI is overbought, MACD is bearish, and the fast EMA is below the slow EMA.
Order Notification (notify_order method):
Logs the execution of buy and sell orders.
Trade Notification (notify_trade method):
Logs the profit or loss of closed trades.
Logging (log method):
A helper method to log messages with timestamps.
Main Execution:
Sets up the Cerebro engine, adds the strategy, loads the data, sets the initial cash, runs the strategy, and plots the results.
This should give you a comprehensive understanding of how the strategy works. If you have any more questions or need further clarification, feel free to ask!
'''