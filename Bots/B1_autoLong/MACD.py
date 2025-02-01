# MACDIndicator.py
import json

class MACD:
    def __init__(self, json_file):
        with open(json_file, 'r') as file:
            self.data = json.load(file)

    def calculate_ema(self, data, window):
        close_prices = [day['close'] for day in data]
        ema = [sum(close_prices[:window]) / window]
        multiplier = 2 / (window + 1)
        for price in close_prices[window:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        return ema

    def calculate_macd(self, short_window=12, long_window=26, signal_window=9):
        short_ema = self.calculate_ema(self.data, short_window)
        long_ema = self.calculate_ema(self.data, long_window)
        macd = [short - long for short, long in zip(short_ema[-len(long_ema):], long_ema)]
        signal = self.calculate_ema([{'close': val} for val in macd], signal_window)
        return macd, signal

    def calculate_macd_score(self, short_window=12, long_window=26, signal_window=9):
        macd, signal = self.calculate_macd(short_window, long_window, signal_window)

        # Calculate the score based on MACD
        if macd[-1] > signal[-1]:
            macd_score = 10  # Strong buy signal
        elif macd[-1] < signal[-1]:
            macd_score = 1  # Strong sell signal
        else:
            macd_score = 5  # Neutral signal

        return round(macd_score)
