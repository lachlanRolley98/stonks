#These are volatility bands placed above and below a moving average.
#  They help identify overbought and oversold conditions and can be used to generate buy/sell signals when the price touches or crosses the bands

# calculate_Bollinger_score will return a score between 1 and 10 based on the current price's position relative to the Bollinger Bands. 10 means its low in the band

import json

# Calculate Simple Moving Average (SMA)
def calculate_sma(data, window):
    close_prices = [day['close'] for day in data]
    sma = [sum(close_prices[i:i+window])/window for i in range(len(close_prices)-window+1)]
    return sma

# Calculate Bollinger Bands
def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    close_prices = [day['close'] for day in data]
    sma = calculate_sma(data, window)
    std_dev = [sum([(close_prices[i+j] - sma[i])**2 for j in range(window)])**0.5 / window for i in range(len(sma))]
    upper_band = [sma[i] + num_std_dev * std_dev[i] for i in range(len(sma))]
    lower_band = [sma[i] - num_std_dev * std_dev[i] for i in range(len(sma))]
    return upper_band, lower_band

# Calculate Score
def calculate_Bollinger_score(data, window=20, num_std_dev=2):
    close_prices = [day['close'] for day in data]
    current_price = close_prices[-1]
    sma = calculate_sma(data, window)
    upper_band, lower_band = calculate_bollinger_bands(data, window, num_std_dev)

    # Calculate the score based on Bollinger Bands
    if current_price < lower_band[-1]:
        score = 10  # Strong buy signal
    elif current_price > upper_band[-1]:
        score = 1  # Strong sell signal
    else:
        # Calculate a score based on the distance from the bands
        score = 10 - 9 * (current_price - lower_band[-1]) / (upper_band[-1] - lower_band[-1])

    # Adjust the score based on other factors (e.g., trend, volume)
    # For simplicity, we'll just return the Bollinger Bands score here
    return round(score)

# Example usage
# with open('../../Bots/B1_autoLong/300_100/ABR.json', 'r') as file:
#     data = json.load(file)

# print(calculate_bollinger_bands(data))
# print(calculate_Bollinger_score(data))
