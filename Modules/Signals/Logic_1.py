import json
import os
import pandas as pd
from Modules.Signals import (
    calculate_Bollinger_score,
    calculate_sma_score,
    calculate_macd_score,
    calculate_rsi_score,
    calculate_stochastic_score,
    calculate_trending_up_score
)

# Define buy/sell decision logic
def determine_action(bollinger_score, trend_score, so_score, buy, current_price, buy_price=None, stop_loss_pct=0.05, take_profit_pct=0.1):
    score = -1

    weights = [0.3, 0.3, 0.4]  # 30% Bollinger, 30% Trend, 40% SO

    score = (bollinger_score * weights[0]) + (trend_score * weights[1]) + (so_score * weights[2])


    score = round(score, 2)

    # Check for BUY signal
    if score >= buy:
        return "BUY"

    # If we have a position (buy_price is set), check stop-loss and take-profit
    if buy_price is not None:
        stop_loss_price = buy_price * (1 - stop_loss_pct)
        take_profit_price = buy_price * (1 + take_profit_pct)

        if current_price <= stop_loss_price:
            return "SELL"  # Trigger stop-loss
        elif current_price >= take_profit_price:
            return "SELL"  # Trigger take-profit

    # Default to HOLD if no other conditions met
    return "HOLD"



def process_stock_data(folder_path, output_file):
    results = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)

            with open(file_path, 'r') as file:
                data = json.load(file)

            stock_name = os.path.splitext(filename)[0]

            if len(data) < 20:
                print(f"Deleting empty file: {filename}")
                os.remove(file_path)
                continue

            sma = calculate_sma_score(data)
            macd = calculate_macd_score(data)
            bb = calculate_Bollinger_score(data)
            so = calculate_stochastic_score(data)
            rsi = calculate_rsi_score(data)
            tu = calculate_trending_up_score(data)

            action = determine_action(bb, tu, so)

            results.append([stock_name, bb, tu, so, action])

    df = pd.DataFrame(results, columns=['name', 'bollinger_score', 'trend_score', 'stochastic_score', 'action'])
    df.to_csv(output_file, index=False)
    print(f"Processing complete. Results saved to {output_file}")


# Process NYSE data
# process_stock_data('../../Historical_Data/IBK_Today_NYSE', 'output_NYSE.csv')

# Process NASDAQ data
# process_stock_data('../../Historical_Data/IBK_Today_NASDAQ', 'output_NASDAQ.csv')
