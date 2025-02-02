
def calculate_trending_up(data, window=5):
    close_prices = [day['close'] for day in data]
    if len(close_prices) < window + 1:
        return 5  # Default to neutral if not enough data
    # Calculate daily price changes over the window
    price_changes = [close_prices[i] - close_prices[i - 1] for i in range(-window, 0)]
    # Compute the average price change
    avg_change = sum(price_changes) / window
    return avg_change


def calculate_trending_up_score(data, window=5):
    """Returns a score (0-10) based on the strength of the upward trend."""
    close_prices = [day['close'] for day in data]
    if len(close_prices) < window + 1:
        return 5  # Default to neutral if not enough data
    # Calculate daily price changes over the window
    price_changes = [close_prices[i] - close_prices[i - 1] for i in range(-window, 0)]
    # Compute the average price change
    avg_change = sum(price_changes) / window
    # Normalize to a score between 0 and 10
    max_possible_change = max(close_prices) * 0.02  # Assume 2% daily movement as a reference
    score = 5 + (avg_change / max_possible_change) * 5  # Scale the score around 5
    # Ensure the score stays between 0 and 10
    return max(0, min(10, round(score, 2)))
