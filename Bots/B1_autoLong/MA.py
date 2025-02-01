import json

class MA:
    def __init__(self, json_file):
        with open(json_file, 'r') as file:
            self.data = json.load(file)

    def calculate_sma(self, window):
        close_prices = [day['close'] for day in self.data]
        if len(close_prices) < window:
            return []
        sma = [sum(close_prices[i:i+window])/window for i in range(len(close_prices)-window+1)]
        return sma

    def calculate_sma_score(self, window):
        if not self.data:
            return 0  # Return a default score if there is no data
        sma = self.calculate_sma(window)
        if not sma:
            return 0  # Return a default score if there is not enough data to calculate SMA
        current_price = self.data[-1]['close']

        # Calculate the score based on SMA
        if current_price > sma[-1]:
            sma_score = 10  # Strong buy signal
        elif current_price < sma[-1]:
            sma_score = 1  # Strong sell signal
        else:
            sma_score = 5  # Neutral signal

        return round(sma_score)
