def determine_action_Params(bb_score, so_score, rsi_score, sma_score, ema_score, macd_score, atr_score,
                     buy_threshold, sell_threshold, current_price, buy_price=None, atr_value=None):
    """
    Optimized function to determine BUY, SELL, or HOLD decision based on weighted indicators.
    """

    # **Adjusted Indicator Weights Based on Optimized Parameters**
    weights = {
        'bb': 0.2, 'so': 0.15, 'rsi': 0.2, 'sma': 0.15,
        'ema': 0.1, 'macd': 0.15, 'atr': 0.05
    }

    # **Calculate the Overall Score**
    total_score = sum([
        bb_score * weights['bb'],
        so_score * weights['so'],
        rsi_score * weights['rsi'],
        sma_score * weights['sma'],
        ema_score * weights['ema'],
        macd_score * weights['macd'],
        atr_score * weights['atr']
    ])
    total_score = round(total_score, 2)

    # **Buy Decision with Stricter Conditions**
    if total_score >= buy_threshold and rsi_score < 7 and so_score > 3 and macd_score > 5:
        return "BUY"

    # **Adaptive Stop-Loss & Take-Profit (Using ATR)**
    if buy_price is not None and atr_value is not None:
        stop_loss_price = buy_price - (atr_value * 2)
        take_profit_price = buy_price + (atr_value * 3)

        if current_price <= stop_loss_price:
            return "SELL"
        elif current_price >= take_profit_price:
            return "SELL"

    # **Sell Decision - Require Stronger Signals**
    if total_score <= sell_threshold and rsi_score > 5 and macd_score < 4:
        return "SELL"

    return "HOLD"

def determine_action_Weights(bb_score, so_score, rsi_score, sma_score, ema_score, macd_score, atr_score,
                     buy_threshold, sell_threshold, current_price, buy_price=None,
                     atr_value=None, weights=None):
    """
    Determines whether to BUY, SELL, or HOLD based on dynamically optimized weights.
    """

    # Default weights if none are provided
    if weights is None:
        weights = {'bb': 0.2, 'so': 0.15, 'rsi': 0.2, 'sma': 0.15,
                   'ema': 0.1, 'macd': 0.15, 'atr': 0.05}

    # Calculate the overall score dynamically using provided weights
    total_score = sum([
        bb_score * weights['bb'],
        so_score * weights['so'],
        rsi_score * weights['rsi'],
        sma_score * weights['sma'],
        ema_score * weights['ema'],
        macd_score * weights['macd'],
        atr_score * weights['atr']
    ])
    total_score = round(total_score, 2)

    # Buy signal with stricter confirmation
    if total_score >= buy_threshold and rsi_score < 7 and so_score > 3 and macd_score > 5:
        return "BUY"

    # Adaptive Stop-Loss & Take-Profit using ATR
    if buy_price is not None and atr_value is not None:
        stop_loss_price = buy_price - (atr_value * 2)
        take_profit_price = buy_price + (atr_value * 3)

        if current_price <= stop_loss_price:
            return "SELL"
        elif current_price >= take_profit_price:
            return "SELL"

    # Sell signal with additional confirmation
    if total_score <= sell_threshold and rsi_score > 5 and macd_score < 4:
        return "SELL"

    return "HOLD"
