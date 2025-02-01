# Choosing the right weights for your indicators depends on your trading strategy and the importance you place on each indicator. Here's a general suggestion for weights based on common practices:
# RSI (Relative Strength Index): 0.3
# RSI is a widely used momentum indicator that helps identify overbought and oversold conditions. It can be very effective in spotting potential reversals.
# MACD (Moving Average Convergence Divergence): 0.25
# MACD is a trend-following momentum indicator that shows the relationship between two moving averages. It's useful for identifying changes in the strength, direction, momentum, and duration of a trend.
# Bollinger Bands: 0.2
# Bollinger Bands help identify volatility and potential overbought/oversold conditions. They are useful for spotting price extremes and potential reversals.
# Stochastic Oscillator: 0.15
# The Stochastic Oscillator is another momentum indicator that compares a particular closing price to a range of prices over a certain period. It's useful for identifying overbought and oversold conditions.
# SMA (Simple Moving Average): 0.1
# SMA is a basic trend indicator that smooths out price data to identify the direction of the trend. It's useful for confirming trends and spotting potential reversals.


def calculate_composite_score(ma_score, macd_score, bollinger_score, stochastic_score, rsi_score):
    weights = [0.1, 0.25, 0.2, 0.15, 0.3]  # Weights for SMA, MACD, Bollinger Bands, Stochastic Oscillator, and RSI

    # Ensure the weights sum to 1
    total_weight = sum(weights)
    normalized_weights = [weight / total_weight for weight in weights]

    # Calculate the weighted average score
    composite_score = (
        ma_score * normalized_weights[0] +
        macd_score * normalized_weights[1] +
        bollinger_score * normalized_weights[2] +
        stochastic_score * normalized_weights[3] +
        rsi_score * normalized_weights[4]
    )

    return round(composite_score)

# Example usage
ma_score = 9
macd_score = 8
bollinger_score = 8
stochastic_score = 8
rsi_score = 1

composite_score = calculate_composite_score(ma_score, macd_score, bollinger_score, stochastic_score, rsi_score)
print(composite_score)
