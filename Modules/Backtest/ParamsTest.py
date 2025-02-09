import os
import json
import pandas as pd
from tqdm import tqdm
from itertools import product
from multiprocessing import Pool, cpu_count
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

# Folder containing stock JSON files
stock_folder = '../../Historical_Data/IBK_Today_NASDAQ/'

# Get list of stock files
json_files = [f for f in os.listdir(stock_folder) if f.endswith('.json')]

# Define stop-loss & take-profit values to test
stop_loss_values = [0.02, 0.05, 0.1]
take_profit_values = [0.05, 0.1, 0.2]

# Multiprocessing setup
num_cores = max(1, cpu_count() // 2)  # Use half the available CPU cores

def run_parameter_test(params):
    buy_threshold, bb_threshold, macd_fast, macd_slow, rsi_period, sma_short, sma_long, stop_loss_pct, take_profit_pct = params

    trade_percentage_gains = []
    total_buys = 0
    winning_trades = 0
    losing_trades = 0
    balance = 10000  # Initial balance
    max_balance = balance
    max_drawdown = 0
    position_size = balance * 0.1  # Risk 10% of capital per trade

    for stock_file in json_files:
        stock_path = os.path.join(stock_folder, stock_file)

        with open(stock_path, 'r') as file:
            stock_data = pd.DataFrame(json.load(file))

        positions = 0
        buy_price = None

        for i in range(len(stock_data)):
            if i < 20:
                continue

            current_data = stock_data.iloc[:i+1]
            current_data_dict = current_data.to_dict(orient='records')

            bb = calculate_Bollinger_score(current_data_dict, bb_threshold)
            so = calculate_stochastic_score(current_data_dict)
            rsi = calculate_rsi_score(current_data_dict, rsi_period)
            sma = calculate_sma_score(current_data_dict, sma_short, sma_long)
            ema = calculate_ema_score(current_data_dict, sma_short, sma_long)
            macd = calculate_macd_score(current_data_dict, macd_fast, macd_slow)
            atr = calculate_atr_score(current_data_dict)

            current_price = stock_data.at[i, 'close']

            action = determine_action_Params(
                bb, so, rsi, sma, ema, macd, atr, buy_threshold, current_price, buy_price, stop_loss_pct, take_profit_pct
            )

            if action == "BUY" and balance >= position_size:
                shares_to_buy = position_size // current_price
                balance -= shares_to_buy * current_price
                positions += shares_to_buy
                buy_price = current_price
                total_buys += 1

            elif action == "SELL" and positions > 0:
                trade_percentage_gain = ((current_price - buy_price) / buy_price) * 100
                trade_percentage_gains.append(trade_percentage_gain)
                balance += positions * current_price
                positions = 0
                buy_price = None

                if trade_percentage_gain > 0:
                    winning_trades += 1
                else:
                    losing_trades += 1

            if balance > max_balance:
                max_balance = balance

            drawdown = (max_balance - balance) / max_balance * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown

    avg_trade_percentage_gain = sum(trade_percentage_gains) / len(trade_percentage_gains) if trade_percentage_gains else 0
    avg_buys = total_buys / len(json_files) if json_files else 0
    win_rate = (winning_trades / (winning_trades + losing_trades)) * 100 if (winning_trades + losing_trades) > 0 else 0

    return {
        'Buy Threshold': buy_threshold,
        'BB Threshold': bb_threshold,
        'MACD Fast': macd_fast,
        'MACD Slow': macd_slow,
        'RSI Period': rsi_period,
        'SMA Short': sma_short,
        'SMA Long': sma_long,
        'Stop Loss %': stop_loss_pct,
        'Take Profit %': take_profit_pct,
        'Average Buys': avg_buys,
        'Average Trade Percentage Gain': avg_trade_percentage_gain,
        'Win Rate (%)': win_rate,
        'Max Drawdown (%)': max_drawdown
    }

if __name__ == "__main__":
    param_combinations = list(product(
        range(4, 8), [1.5, 2, 2.5, 3], [5, 10, 12], [26, 50, 100], [14, 21], [5, 10, 15], [50, 100, 200],
        stop_loss_values, take_profit_values
    ))

    with Pool(processes=num_cores) as pool:
        results = list(tqdm(pool.imap(run_parameter_test, param_combinations), total=len(param_combinations), desc="Optimizing Parameters"))

    pd.DataFrame(results).to_csv('parameter_test_results.csv', mode='w', header=True, index=False)
    print("Parameter testing completed. Results saved to parameter_test_results.csv")
