

class AdvancedComplexStrategy(bt.Strategy):
    params = (
        ('bollinger_period', 20),
        ('bollinger_devfactor', 2),
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9),
        ('ema_fast', 10),
        ('ema_slow', 50),
        ('trail_percent', 0.02),  # 2% trailing stop
    )

    def __init__(self):
        self.orders = {}  # Dictionary to keep track of orders for each data feed
        self.buy_prices = {}
        self.sell_prices = {}

        for data in self.datas:
            self.orders[data] = None
            self.buy_prices[data] = None
            self.sell_prices[data] = None

            # Initialize indicators for each data feed
            data.bollinger = bt.indicators.BollingerBands(
                data.close, period=self.params.bollinger_period, devfactor=self.params.bollinger_devfactor)
            data.rsi = bt.indicators.RelativeStrengthIndex(
                data.close, period=self.params.rsi_period)
            data.macd = bt.indicators.MACD(
                data.close, period_me1=self.params.macd1, period_me2=self.params.macd2, period_signal=self.params.macdsig)
            data.ema_fast = bt.indicators.ExponentialMovingAverage(
                data.close, period=self.params.ema_fast)
            data.ema_slow = bt.indicators.ExponentialMovingAverage(
                data.close, period=self.params.ema_slow)

    def next(self):
        for data in self.datas:
            if self.orders[data]:
                continue

            if data.close < data.bollinger.lines.bot and data.rsi < self.params.rsi_oversold and data.macd.macd > data.macd.signal and data.ema_fast > data.ema_slow:
                self.orders[data] = self.buy(data=data)
                self.buy_prices[data] = data.close[0]
                self.sell_prices[data] = self.buy_prices[data] * (1.0 + self.params.trail_percent)

            elif data.close > data.bollinger.lines.top and data.rsi > self.params.rsi_overbought and data.macd.macd < data.macd.signal and data.ema_fast < data.ema_slow:
                self.orders[data] = self.sell(data=data)
                self.sell_prices[data] = data.close[0]
                self.buy_prices[data] = self.sell_prices[data] * (1.0 - self.params.trail_percent)

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.data._name}, Price: {order.executed.price}')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.data._name}, Price: {order.executed.price}')
            self.orders[order.data] = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'OPERATION PROFIT, {trade.data._name}, GROSS {trade.pnl}, NET {trade.pnlcomm}')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')



if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(AdvancedComplexStrategy)

    # List of stock symbols to analyze
    stock_symbols = ['AAPL', 'MSFT', 'GOOGL']

    for symbol in stock_symbols:
        data = bt.feeds.YahooFinanceData(dataname=symbol,
                                         fromdate=datetime(2020, 1, 1),
                                         todate=datetime(2021, 1, 1))
        cerebro.adddata(data, name=symbol)

    # Set initial cash
    cerebro.broker.setcash(10000.0)
    
    # Run the strategy
    cerebro.run()
    
    # Plot the results
    cerebro.plot()


'''
Main Execution:
Added a list of stock symbols to analyze.
Loop through the list and add each stock’s data feed to Cerebro.
Strategy Class:
Modified to handle multiple data feeds by initializing indicators for each data feed.
Used dictionaries to keep track of orders, buy prices, and sell prices for each data feed.
Adjusted the next, notify_order, and notify_trade methods to handle multiple data feeds.
This setup allows the strategy to scan and trade multiple stocks simultaneously. If you have any more questions or need further customization, feel free to ask!
'''