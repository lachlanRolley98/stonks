import os
import json
import pandas as pd
from tqdm import tqdm
from itertools import product
from Modules.Signals import (
    calculate_Bollinger_score,
    calculate_stochastic_score,
    determine_action_Weights,
    calculate_rsi_score,
    calculate_sma_score,
    calculate_ema_score,
    calculate_macd_score,
    calculate_atr_score
)

# Load best parameters from Best_Consensus_Parameters.csv
best_params_file = "Best_Consensus_Parameters.csv"
best_params = pd.read_csv(best_params_file).iloc[0]  # Read the first row

# Extract the optimized values
best_buy_threshold = int(best_params["Buy Threshold"])
best_bb_threshold = float(best_params["BB Threshold"])
best_macd_fast = int(best_params["MACD Fast"])
best_macd_slow = int(best_params["MACD Slow"])
best_rsi_period = int(best_params["RSI Period"])
best_sma_short = int(best_params["SMA Short"])
best_sma_long = int(best_params["SMA Long"])

# Folder containing stock JSON files
stock_folder = '../../Historical_Data/IBK_Today_NASDAQ/'

# Output file for weight testing results
output_file = 'weight_optimization_results.csv'
df = pd.DataFrame(columns=['Buy Threshold', 'BB Weight', 'SO Weight', 'RSI Weight', 'SMA Weight',
                           'EMA Weight', 'MACD Weight', 'ATR Weight', 'Average Trade Percentage Gain'])
df.to_csv(output_file, index=False)

# Get list of stock files
json_files = [f for f in os.listdir(stock_folder) if f.endswith('.json')]

# Define weight ranges to test
buy_thresholds = [best_buy_threshold]  # Use only the best Buy Threshold
bb_weights = [0.1, 0.2, 0.3]
so_weights = [0.1, 0.15, 0.2]
rsi_weights = [0.1, 0.2, 0.3]
sma_weights = [0.1, 0.15, 0.2]
ema_weights = [0.05, 0.1, 0.15]
macd_weights = [0.1, 0.15, 0.2]
atr_weights = [0.01, 0.05, 0.1]

# Loop through all buy threshold + weight combinations
for buy_threshold, weights in tqdm(product(buy_thresholds,
                                           product(bb_weights, so_weights, rsi_weights, sma_weights,
                                                   ema_weights, macd_weights, atr_weights)),
                                   desc="Optimizing Buy Thresholds & Weights"):

    bb_w, so_w, rsi_w, sma_w, ema_w, macd_w, atr_w = weights

    # Store results for this combination
    total_trade_percentage_gain = 0
    total_trades = 0

    # Loop through all stock files
    for stock_file in json_files:
        stock_path = os.path.join(stock_folder, stock_file)

        # Load stock data
        with open(stock_path, 'r') as file:
            stock_data = pd.DataFrame(json.load(file))

        # Initialize variables for backtesting
        positions = 0
        buy_price = None
        trade_percentage_gains = []

        # Backtest loop
        for i in range(len(stock_data)):
            if i < 20:
                continue

            # Get historical data up to this point
            current_data = stock_data.iloc[:i+1]
            current_data_dict = current_data.to_dict(orient='records')

            # Calculate indicators using the best-found parameters
            bb = calculate_Bollinger_score(current_data_dict, best_bb_threshold)
            so = calculate_stochastic_score(current_data_dict)
            rsi = calculate_rsi_score(current_data_dict, best_rsi_period)
            sma = calculate_sma_score(current_data_dict, best_sma_short, best_sma_long)
            ema = calculate_ema_score(current_data_dict, best_sma_short, best_sma_long)
            macd = calculate_macd_score(current_data_dict, best_macd_fast, best_macd_slow)
            atr = calculate_atr_score(current_data_dict)

            # Get current price
            current_price = stock_data.at[i, 'close']

            # Call determine_action() with weight adjustments & variable buy threshold
            action = determine_action_Weights(
                bb, so, rsi, sma, ema, macd, atr, buy_threshold, 3, current_price, buy_price,
                weights={'bb': bb_w, 'so': so_w, 'rsi': rsi_w, 'sma': sma_w,
                         'ema': ema_w, 'macd': macd_w, 'atr': atr_w}
            )

            # Execute trades
            if action == "BUY" and positions == 0:
                positions += 1
                buy_price = current_price

            elif action == "SELL" and positions > 0:
                trade_percentage_gain = ((current_price - buy_price) / buy_price) * 100
                trade_percentage_gains.append(trade_percentage_gain)
                positions = 0
                buy_price = None

        # Compute average trade percentage gain
        if trade_percentage_gains:
            avg_trade_percentage_gain = sum(trade_percentage_gains) / len(trade_percentage_gains)
        else:
            avg_trade_percentage_gain = 0

        total_trade_percentage_gain += avg_trade_percentage_gain
        total_trades += 1

    # Compute average trade percentage gain for this combination
    average_trade_percentage_gain = total_trade_percentage_gain / total_trades

    # Save result
    data_to_append = pd.DataFrame([{
        'Buy Threshold': buy_threshold,
        'BB Weight': bb_w,
        'SO Weight': so_w,
        'RSI Weight': rsi_w,
        'SMA Weight': sma_w,
        'EMA Weight': ema_w,
        'MACD Weight': macd_w,
        'ATR Weight': atr_w,
        'Average Trade Percentage Gain': average_trade_percentage_gain
    }])

    df = pd.concat([df, data_to_append], ignore_index=True)
    df.to_csv(output_file, index=False)

print("\nOptimization completed. Results saved to weight_optimization_results.csv")
