import json

class StochasticOscillator:
    def __init__(self, json_file):
        with open(json_file, 'r') as file:
            self.data = json.load(file)

    def calculate_stochastic_oscillator(self, period=14):
        close_prices = [day['close'] for day in self.data]
        if len(close_prices) < period:
            return []
        lows = [min([day['low'] for day in self.data[i:i+period]]) for i in range(len(self.data)-period+1)]
        highs = [max([day['high'] for day in self.data[i:i+period]]) for i in range(len(self.data)-period+1)]
        stochastic_oscillator = [(close_prices[i+period-1] - lows[i]) / (highs[i] - lows[i]) * 100 for i in range(len(lows))]
        return stochastic_oscillator

    def calculate_stochastic_score(self, period=14):
        stochastic_oscillator = self.calculate_stochastic_oscillator(period)
        if not stochastic_oscillator:
            return 0  # Return a default score if there is no data

        # Calculate the score based on Stochastic Oscillator
        if stochastic_oscillator[-1] < 20:
            stochastic_score = 10  # Strong buy signal
        elif stochastic_oscillator[-1] > 80:
            stochastic_score = 1  # Strong sell signal
        else:
            stochastic_score = 10 - 9 * (stochastic_oscillator[-1] - 20) / 60

        return round(stochastic_score)
