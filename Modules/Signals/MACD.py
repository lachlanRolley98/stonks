# This trend-following momentum indicator shows the relationship between two moving averages of a stock's price.
# The MACD line is the difference between the 12-day EMA and the 26-day EMA, while the signal line is the 9-day EMA of the MACD line.
# Buy signals occur when the MACD line crosses above the signal line, and sell signals occur when it crosses below

import json

import json

# Calculate Exponential Moving Average (EMA)
def calculate_ema(data, window):
    close_prices = [day['close'] for day in data]
    ema = [sum(close_prices[:window]) / window]
    multiplier = 2 / (window + 1)
    for price in close_prices[window:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    return ema

# Calculate MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = calculate_ema(data, short_window)
    long_ema = calculate_ema(data, long_window)
    macd = [short - long for short, long in zip(short_ema[-len(long_ema):], long_ema)]
    signal = calculate_ema([{'close': val} for val in macd], signal_window)
    return macd, signal

# Calculate Score based on MACD
def calculate_macd_score(data, short_window=12, long_window=26, signal_window=9):
    macd, signal = calculate_macd(data, short_window, long_window, signal_window)

    # Calculate the score based on MACD
    if macd[-1] > signal[-1]:
        macd_score = 10  # Strong buy signal
    elif macd[-1] < signal[-1]:
        macd_score = 1  # Strong sell signal
    else:
        macd_score = 5  # Neutral signal

    return round(macd_score)

# Example usage
# with open('../../Bots/B1_autoLong/300_100/ABR.json', 'r') as file:
#     data = json.load(file)
# print(calculate_macd(data))
# print(calculate_macd_score(data))

