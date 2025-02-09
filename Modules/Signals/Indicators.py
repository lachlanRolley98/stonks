import statistics

def calculate_sma(data, window):
    """Calculates Simple Moving Average."""
    close_prices = [day['close'] for day in data if 'close' in day]

    if len(close_prices) < window:
        return []  # Not enough data to calculate SMA

    sma = [sum(close_prices[i:i+window])/window for i in range(len(close_prices)-window+1)]
    return sma

def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    close_prices = [day['close'] for day in data if 'close' in day]
    if len(close_prices) < window:
        return [], []  # Not enough data to calculate Bollinger Bands

    sma = calculate_sma(data, window)
    std_dev = [statistics.stdev(close_prices[i:i+window]) for i in range(len(sma))]

    upper_band = [sma[i] + num_std_dev * std_dev[i] for i in range(len(sma))]
    lower_band = [sma[i] - num_std_dev * std_dev[i] for i in range(len(sma))]

    return upper_band, lower_band

def calculate_Bollinger_score(current_data_dict, bb_threshold, window=20, num_std_dev=2):
    close_prices = [day['close'] for day in current_data_dict if 'close' in day]
    if len(close_prices) < window:
        return 5  # Default to neutral if not enough data

    current_price = close_prices[-1]
    upper_band, lower_band = calculate_bollinger_bands(current_data_dict, window, num_std_dev)

    if not upper_band or not lower_band:
        return 5  # Default to neutral if bands cannot be calculated

    if current_price < lower_band[-1] * (1 - bb_threshold):
        score = 10
    elif current_price > upper_band[-1] * (1 + bb_threshold):
        score = 1
    else:
        score = 10 - 9 * (current_price - lower_band[-1]) / (upper_band[-1] - lower_band[-1])

    return round(score, 2)

def calculate_stochastic_score(data, k_period=14, d_period=3):
    if len(data) < k_period:
        return 5  # Default to neutral if not enough data

    close_prices = [day['close'] for day in data if 'close' in day]
    high_prices = [day['high'] for day in data if 'high' in day]
    low_prices = [day['low'] for day in data if 'low' in day]

    highest_high = max(high_prices[-k_period:])
    lowest_low = min(low_prices[-k_period:])
    current_close = close_prices[-1]

    if highest_high - lowest_low == 0:
        return 5  # Avoid division by zero

    k_value = (current_close - lowest_low) / (highest_high - lowest_low) * 100
    score = 10 - (k_value / 100) * 10

    return round(score, 2)

def calculate_rsi_score(data, rsi_period=14):
    close_prices = [day['close'] for day in data if 'close' in day]
    if len(close_prices) < rsi_period + 1:
        return 5  # Default to neutral if not enough data

    gains = []
    losses = []
    for i in range(-rsi_period, 0):
        change = close_prices[i] - close_prices[i - 1]
        if change > 0:
            gains.append(change)
        else:
            losses.append(abs(change))

    avg_gain = sum(gains) / rsi_period if gains else 0
    avg_loss = sum(losses) / rsi_period if losses else 0

    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    score = 10 - (rsi / 100) * 10
    return round(score, 2)

def calculate_sma_score(data, sma_short, sma_long):
    """
    Scores based on the position of the short-term SMA relative to the long-term SMA.
    """
    if len(data) < sma_long:
        return 5  # Neutral score if insufficient data

    short_sma = calculate_sma(data, sma_short)
    long_sma = calculate_sma(data, sma_long)

    if not short_sma or not long_sma:
        return 5  # Return neutral score if SMA can't be calculated

    if short_sma[-1] > long_sma[-1]:
        return 10  # Strong bullish signal
    elif short_sma[-1] < long_sma[-1]:
        return 1   # Bearish signal
    else:
        return 5   # Neutral

def calculate_ema(data, window):
    close_prices = [day['close'] for day in data if 'close' in day]
    if len(close_prices) < window:
        return []  # Not enough data to calculate EMA

    ema = [close_prices[0]]
    multiplier = 2 / (window + 1)
    for price in close_prices[1:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    return ema

def calculate_ema_score(data, sma_short=10, sma_long=50):
    short_ema = calculate_ema(data, sma_short)
    long_ema = calculate_ema(data, sma_long)

    if not short_ema or not long_ema:
        return 5  # Default to neutral if not enough data

    score = 10 if short_ema[-1] > long_ema[-1] else 0
    return score

def calculate_macd_score(data, macd_fast=12, macd_slow=26, macd_signal=9):
    fast_ema = calculate_ema(data, macd_fast)
    slow_ema = calculate_ema(data, macd_slow)

    if not fast_ema or not slow_ema:
        return 5  # Default to neutral if not enough data

    macd_line = [fast - slow for fast, slow in zip(fast_ema[-len(slow_ema):], slow_ema)]
    signal_line = calculate_ema([{'close': val} for val in macd_line], macd_signal)

    if not signal_line:
        return 5  # Default to neutral if signal line can't be calculated

    score = 10 if macd_line[-1] > signal_line[-1] else 0
    return score

def calculate_true_range(data):
    true_ranges = []
    for i in range(1, len(data)):
        high = data[i].get('high', 0)
        low = data[i].get('low', 0)
        prev_close = data[i - 1].get('close', 0)

        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        true_ranges.append(tr)
    return true_ranges

def calculate_atr_score(data, atr_period=14):
    true_ranges = calculate_true_range(data)
    if len(true_ranges) < atr_period:
        return 5  # Default to neutral if not enough data

    atr = sum(true_ranges[-atr_period:]) / atr_period
    last_tr = true_ranges[-1]

    score = 10 - (last_tr / atr) * 10
    return max(0, min(10, round(score, 2)))
