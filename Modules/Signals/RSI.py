# This momentum oscillator measures the speed and change of price movements.
# It ranges from 0 to 100 and helps identify overbought or oversold conditions.
# Values above 70 indicate overbought conditions, while values below 30 indicate oversold conditions

import json

def calculate_rsi(data, period=14):
    close_prices = [day['close'] for day in data]
    deltas = [close_prices[i] - close_prices[i-1] for i in range(1, len(close_prices))]
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    rs = avg_gain / avg_loss
    rsi = [100 - (100 / (1 + rs))]
    for i in range(period, len(close_prices) - 1):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        rs = avg_gain / avg_loss
        rsi.append(100 - (100 / (1 + rs)))
    return rsi

# Calculate Score based on RSI
def calculate_rsi_score(data, period=14):
    rsi = calculate_rsi(data, period)

    # Calculate the score based on RSI
    if rsi[-1] < 30:
        rsi_score = 10  # Strong buy signal
    elif rsi[-1] > 70:
        rsi_score = 1  # Strong sell signal
    else:
        rsi_score = 10 - 9 * (rsi[-1] - 30) / 40

    return round(rsi_score)

# # Example usage
# with open('../../Bots/B1_autoLong/300_100/ABR.json', 'r') as file:
#     data = json.load(file)

#print(calculate_rsi(data))
#print(calculate_rsi_score(data))
