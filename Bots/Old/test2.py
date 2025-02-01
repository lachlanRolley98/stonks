import pandas as pd
import ccxt

# Initialize exchange
exchange = ccxt.binance()

# Fetch historical data
def fetch_data(symbol, timeframe, since):
    return exchange.fetch_ohlcv(symbol, timeframe, since=since)

# Calculate moving averages
def calculate_moving_average(data, window):
    return data['close'].rolling(window=window).mean()

# Example usage
data = fetch_data('BTC/USDT', '1d', exchange.parse8601('2023-01-01T00:00:00Z'))
df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['SMA_20'] = calculate_moving_average(df, 20)

print(df.tail())
