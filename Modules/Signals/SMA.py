# These are trend-following indicators that smooth out price data to identify the direction of the trend.
# The two main types are the Simple Moving Average (SMA) and the Exponential Moving Average (EMA).
# Combining different time frames can help generate buy/sell signals

# if score is high, the stock price is higher than the average. Low means bellow

import json

def calculate_sma(data, window = 3):
    close_prices = [day['close'] for day in data]
    sma = [sum(close_prices[i:i+window])/window for i in range(len(close_prices)-window+1)]
    return sma

# Calculate Score based on SMA
def calculate_sma_score(data, window):
    sma = calculate_sma(data, window)
    current_price = data[-1]['close']

    # Calculate the score based on SMA
    if current_price > sma[-1]:
        sma_score = 10  # Strong buy signal
    elif current_price < sma[-1]:
        sma_score = 1  # Strong sell signal
    else:
        sma_score = 5  # Neutral signal

    return round(sma_score)

# # Example usage
# with open('../../Bots/B1_autoLong/300_100/ABR.json', 'r') as file:
#     data = json.load(file)

# window = 3
#print(calculate_sma(data, window))
#print(calculate_sma_score(data, window))
