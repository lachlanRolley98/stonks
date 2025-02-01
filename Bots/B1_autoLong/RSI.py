import json

class RSI:
    def __init__(self, json_file):
        with open(json_file, 'r') as file:
            self.data = json.load(file)

    def calculate_rsi(self, period=14):
        close_prices = [day['close'] for day in self.data]
        if len(close_prices) < period:
            return []
        deltas = [close_prices[i] - close_prices[i-1] for i in range(1, len(close_prices))]
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        if avg_loss == 0:
            return [100] * (len(close_prices) - period)  # Return 100 if there are no losses
        rs = avg_gain / avg_loss
        rsi = [100 - (100 / (1 + rs))]
        for i in range(period, len(close_prices) - 1):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            if avg_loss == 0:
                rsi.append(100)  # Return 100 if there are no losses
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))
        return rsi

    def calculate_rsi_score(self, period=14):
        rsi = self.calculate_rsi(period)
        if not rsi:
            return 0  # Return a default score if there is no data

        # Calculate the score based on RSI
        if rsi[-1] < 30:
            rsi_score = 10  # Strong buy signal
        elif rsi[-1] > 70:
            rsi_score = 1  # Strong sell signal
        else:
            rsi_score = 10 - 9 * (rsi[-1] - 30) / 40

        return round(rsi_score)
