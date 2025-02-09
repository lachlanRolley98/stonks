import os
import json
import pandas as pd
from tqdm import tqdm  # For progress bar
from Modules.Signals import (
    calculate_Bollinger_score,
    calculate_stochastic_score,
    determine_action_Params,
    calculate_rsi_score,
    calculate_sma_score,
    calculate_ema_score,
    calculate_macd_score,
    calculate_atr_score
)

# Folder containing the JSON files
stock_folder = '../../Historical_Data/IBK_Today_NASDAQ/'

# Initialize CSV file for parameter testing (header written only once)
param_output_file = 'parameter_test_results.csv'
param_df = pd.DataFrame(columns=['Buy Threshold', 'BB Threshold', 'MACD Fast', 'MACD Slow', 'RSI Period', 'SMA Short', 'SMA Long', 'Average Buys', 'Average Trade Percentage Gain'])

# Get list of JSON files
json_files = [f for f in os.listdir(stock_folder) if f.endswith('.json')]

# Write the headers for the parameter file once (this will be done before starting the loop)
param_df.to_csv(param_output_file, mode='w', header=True, index=False)

# Loop through all combinations of parameters with progress bar
for buy_threshold in tqdm(range(4, 8), desc="Testing Parameter Combinations"):  # 4 to 10 inclusive
    for bb_threshold in [1.5, 2, 2.5, 3]:  # Bollinger Bands thresholds
        for macd_fast in [5, 10, 12]:  # MACD fast length
            for macd_slow in [26, 50, 100]:  # MACD slow length
                for rsi_period in [14, 21]:  # RSI period
                    for sma_short in [5, 10, 15]:  # SMA short period
                        for sma_long in [50, 100, 200]:  # SMA long period
                            # Initialize list to store data for the current parameter combination
                            trade_percentage_gains = []
                            total_buys = 0

                            # Loop through all files
                            for stock_file in json_files:
                                stock_path = os.path.join(stock_folder, stock_file)

                                # Load stock data
                                with open(stock_path, 'r') as file:
                                    stock_data = pd.DataFrame(json.load(file))

                                # Initialize backtest variables
                                positions = 0
                                buy_price = None

                                # Backtest loop
                                for i in range(len(stock_data)):
                                    if i < 20:  # Ensure enough data points for indicators
                                        continue

                                    # Slice data up to current day for indicator calculation
                                    current_data = stock_data.iloc[:i+1]
                                    current_data_dict = current_data.to_dict(orient='records')

                                    # Calculate indicators
                                    bb = calculate_Bollinger_score(current_data_dict, bb_threshold)
                                    so = calculate_stochastic_score(current_data_dict)
                                    rsi = calculate_rsi_score(current_data_dict, rsi_period)
                                    sma = calculate_sma_score(current_data_dict, sma_short, sma_long)
                                    ema = calculate_ema_score(current_data_dict, sma_short, sma_long)
                                    macd = calculate_macd_score(current_data_dict, macd_fast, macd_slow)
                                    atr = calculate_atr_score(current_data_dict)

                                    # Get current price
                                    current_price = stock_data.at[i, 'close']

                                    # Determine action
                                    action = determine_action_Params(
                                        bb, so, rsi, sma, ema, macd, atr, buy_threshold, current_price, buy_price
                                    )

                                    # Execute trades
                                    if action == "BUY" and positions == 0:
                                        positions += 1
                                        buy_price = current_price  # Set buy price
                                        total_buys += 1

                                    elif action == "SELL" and positions > 0:
                                        trade_percentage_gain = ((current_price - buy_price) / buy_price) * 100
                                        trade_percentage_gains.append(trade_percentage_gain)
                                        positions = 0
                                        buy_price = None

                            # Calculate average trade percentage gain for this parameter combination
                            avg_trade_percentage_gain = sum(trade_percentage_gains) / len(trade_percentage_gains) if trade_percentage_gains else 0
                            avg_buys = total_buys / len(json_files) if json_files else 0

                            # Append parameter results to the parameter CSV incrementally
                            param_data_to_append = pd.DataFrame([{
                                'Buy Threshold': buy_threshold,
                                'BB Threshold': bb_threshold,
                                'MACD Fast': macd_fast,
                                'MACD Slow': macd_slow,
                                'RSI Period': rsi_period,
                                'SMA Short': sma_short,
                                'SMA Long': sma_long,
                                'Average Buys': avg_buys,
                                'Average Trade Percentage Gain': avg_trade_percentage_gain
                            }])
                            param_data_to_append.to_csv(param_output_file, mode='a', header=False, index=False)

# Final message to indicate completion
print(f"Parameter testing completed. Results saved to {param_output_file}")
