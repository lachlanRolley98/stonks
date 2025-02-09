import os
import json
import pandas as pd
from tqdm import tqdm  # For progress bar
from Modules.Signals import (
    calculate_Bollinger_score,
    calculate_trending_up_score,
    calculate_stochastic_score,
    determine_action
)

# Folder containing the JSON files
stock_folder = '../../Historical_Data/IBK_Today_NASDAQ/'

# Initialize output CSV file for backtest results
output_file = 'backtest_results.csv'

# Overwrite the output file with headers at the start of each run
df = pd.DataFrame(columns=['Name', 'Total Buys', 'Total Sells', 'Profit/Loss'])
df.to_csv(output_file, index=False)

# Initialize CSV file for parameter testing
param_output_file = 'parameter_test_results.csv'
param_df = pd.DataFrame(columns=['Buy Threshold', 'Average Buys', 'Average Profit'])
param_df.to_csv(param_output_file, index=False)

# Get list of JSON files
json_files = [f for f in os.listdir(stock_folder) if f.endswith('.json')]

# Loop through all combinations of buy and sell thresholds
for buy_threshold in range(4, 11):  # 4 to 10 inclusive

    # Overwrite the output file for each parameter combination
    df = pd.DataFrame(columns=['Name', 'Total Buys', 'Total Sells', 'Profit/Loss'])

    # Loop through all files with progress bar
    for stock_file in tqdm(json_files, desc=f"Processing Buy={buy_threshold}"):
        stock_path = os.path.join(stock_folder, stock_file)

        # Load stock data
        with open(stock_path, 'r') as file:
            stock_data = pd.DataFrame(json.load(file))

        # Initialize backtest variables
        initial_balance = 10000
        balance = initial_balance
        positions = 0
        total_buys = 0
        total_sells = 0
        buy_price = None  # Track buy price for stop-loss and take-profit

        # Backtest loop
        for i in range(len(stock_data)):
            if i < 20:  # Ensure enough data points for indicators
                continue

            # Slice data up to current day for indicator calculation
            current_data = stock_data.iloc[:i+1]
            current_data_dict = current_data.to_dict(orient='records')

            # Calculate indicators
            bb = calculate_Bollinger_score(current_data_dict)
            tu = calculate_trending_up_score(current_data_dict)
            so = calculate_stochastic_score(current_data_dict)

            # Get current price
            current_price = stock_data.at[i, 'close']

            # Determine action with current thresholds
            action = determine_action(bb, tu, so, buy_threshold,current_price, buy_price)

            # Execute trades
            if action == "BUY" and balance >= current_price and positions == 0:
                positions += 1
                balance -= current_price
                buy_price = current_price  # Set buy price for stop-loss/take-profit logic
                total_buys += 1

            elif action == "SELL" and positions > 0:
                balance += positions * current_price
                positions = 0
                buy_price = None  # Reset buy price after selling
                total_sells += 1

        # Final check to sell any remaining positions at the last available price
        if positions > 0:
            final_price = stock_data.at[len(stock_data)-1, 'close']
            balance += positions * final_price
            total_sells += 1
            positions = 0
            buy_price = None

        # Calculate profit/loss
        profit_loss = balance - initial_balance

        # Prepare data to append to CSV
        stock_name = stock_file.replace('.json', '')
        data_to_append = pd.DataFrame([{
            'Name': stock_name,
            'Total Buys': total_buys,
            'Total Sells': total_sells,
            'Profit/Loss': profit_loss
        }])

        # Append to the DataFrame
        df = pd.concat([df, data_to_append], ignore_index=True)

    # Calculate average profit/loss for this parameter combination
    average_profit_loss = df['Profit/Loss'].mean()
    average_buys = df['Total Buys'].mean()

    # Append parameter results to the parameter CSV
    param_data_to_append = pd.DataFrame([{
        'Buy Threshold': buy_threshold,
        'Average Buys': average_buys,
        'Average Profit': average_profit_loss
    }])

    param_df = pd.concat([param_df, param_data_to_append], ignore_index=True)
    param_df.to_csv(param_output_file, index=False)

# Display final message
print(f"Parameter testing completed. Results saved to {param_output_file}")
