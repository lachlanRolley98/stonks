import statistics

def calculate_sma(data, window):
    close_prices = [day['close'] for day in data]
    sma = [sum(close_prices[i:i+window])/window for i in range(len(close_prices)-window+1)]
    return sma

def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    close_prices = [day['close'] for day in data]
    sma = calculate_sma(data, window)
    std_dev = [statistics.stdev(close_prices[i:i+window]) for i in range(len(sma))]

    upper_band = [sma[i] + num_std_dev * std_dev[i] for i in range(len(sma))]
    lower_band = [sma[i] - num_std_dev * std_dev[i] for i in range(len(sma))]

    return upper_band, lower_band

def calculate_Bollinger_score(data, window=20, num_std_dev=2):
    close_prices = [day['close'] for day in data]
    current_price = close_prices[-1]
    sma = calculate_sma(data, window)
    upper_band, lower_band = calculate_bollinger_bands(data, window, num_std_dev)

    if current_price < lower_band[-1]:
        score = 10
    elif current_price > upper_band[-1]:
        score = 1
    else:
        score = 10 - 9 * (current_price - lower_band[-1]) / (upper_band[-1] - lower_band[-1])

    #print(f"Current Price: {current_price}, Lower Band: {lower_band[-1]}, Upper Band: {upper_band[-1]}, Score: {score}")
    return round(score)
