import json

class BoilerBands:
    def __init__(self, json_file):
        with open(json_file, 'r') as file:
            self.data = json.load(file)

    def calculate_sma(self, window):
        close_prices = [day['close'] for day in self.data]
        if len(close_prices) < window:
            return []
        sma = [sum(close_prices[i:i+window])/window for i in range(len(close_prices)-window+1)]
        return sma

    def calculate_bollinger_bands(self, window=20, num_std_dev=2):
        close_prices = [day['close'] for day in self.data]
        sma = self.calculate_sma(window)
        if not sma:
            return [], []
        std_dev = [sum([(close_prices[i+j] - sma[i])**2 for j in range(window)])**0.5 / window for i in range(len(sma))]
        upper_band = [sma[i] + num_std_dev * std_dev[i] for i in range(len(sma))]
        lower_band = [sma[i] - num_std_dev * std_dev[i] for i in range(len(sma))]
        return upper_band, lower_band

    def calculate_score(self, window=20, num_std_dev=2):
        close_prices = [day['close'] for day in self.data]
        if not close_prices:
            return 0  # Return a default score if there is no data
        current_price = close_prices[-1]
        sma = self.calculate_sma(window)
        upper_band, lower_band = self.calculate_bollinger_bands(window, num_std_dev)
        if not upper_band or not lower_band:
            return 0  # Return a default score if there is not enough data to calculate bands

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
