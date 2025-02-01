#This momentum indicator compares a stock's closing price to its price range over a specific period.
#  It ranges from 0 to 100 and helps identify overbought or oversold conditions.
#  Values above 80 indicate overbought conditions, while values below 20 indicate oversold conditions

import json

# Calculate Stochastic Oscillator
def calculate_stochastic_oscillator(data, period=14):
    close_prices = [day['close'] for day in data]
    lows = [min([day['low'] for day in data[i:i+period]]) for i in range(len(data)-period+1)]
    highs = [max([day['high'] for day in data[i:i+period]]) for i in range(len(data)-period+1)]
    stochastic_oscillator = [(close_prices[i+period-1] - lows[i]) / (highs[i] - lows[i]) * 100 for i in range(len(lows))]
    return stochastic_oscillator

# Calculate Score based on Stochastic Oscillator
def calculate_stochastic_score(data, period=14):
    stochastic_oscillator = calculate_stochastic_oscillator(data, period)

    # Calculate the score based on Stochastic Oscillator
    if stochastic_oscillator[-1] < 20:
        stochastic_score = 10  # Strong buy signal
    elif stochastic_oscillator[-1] > 80:
        stochastic_score = 1  # Strong sell signal
    else:
        stochastic_score = 10 - 9 * (stochastic_oscillator[-1] - 20) / 60

    return round(stochastic_score)

# Example usage
# with open('../../Bots/B1_autoLong/300_100/ABR.json', 'r') as file:
#     data = json.load(file)

#print(calculate_stochastic_oscillator(data))
#print(calculate_stochastic_score(data))
