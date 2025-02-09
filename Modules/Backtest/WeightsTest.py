import os
import json
import pandas as pd
from tqdm import tqdm
from itertools import product
from multiprocessing import Pool, cpu_count
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
best_params = pd.read_csv(best_params_file).iloc[0]

# Extract optimized values
best_buy_threshold = int(best_params["Buy Threshold"])
best_bb_threshold = float(best_params["BB Threshold"])
best_macd_fast = int(best_params["MACD Fast"])
best_macd_slow = int(best_params["MACD Slow"])
best_rsi_period = int(best_params["RSI Period"])
best_sma_short = int(best_params["SMA Short"])
best_sma_long = int(best_params["SMA Long"])

# Folder containing stock JSON files
stock_folder = '../../Historical_Data/IBK_Today_NASDAQ/'

# Get list of stock files
json_files = [f for f in os.listdir(stock_folder) if f.endswith('.json')]

# Define stop-loss & take-profit values to test
stop_loss_values = [0.02, 0.05, 0.1]
take_profit_values = [0.05, 0.1, 0.2]

# Multiprocessing setup
num_cores = max(1, cpu_count() // 2)  # Use half the available CPU cores

def run_weight_test(weights):
    bb_w, so_w, rsi_w, sma_w, ema_w, macd_w, atr_w, stop_loss_pct, take_profit_pct = weights

    trade_percentage_gains = []
    total_trades = 0
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

            bb = calculate_Bollinger_score(current_data_dict, best_bb_threshold)
            so = calculate_stochastic_score(current_data_dict)
            rsi = calculate_rsi_score(current_data_dict, best_rsi_period)
            sma = calculate_sma_score(current_data_dict, best_sma_short, best_sma_long)
            ema = calculate_ema_score(current_data_dict, best_sma_short, best_sma_long)
            macd = calculate_macd_score(current_data_dict, best_macd_fast, best_macd_slow)
            atr = calculate_atr_score(current_data_dict)

            current_price = stock_data.at[i, 'close']

            action = determine_action_Weights(
                bb, so, rsi, sma, ema, macd, atr, best_buy_threshold, 3, current_price, buy_price,
                weights={'bb': bb_w, 'so': so_w, 'rsi': rsi_w, 'sma': sma_w,
                         'ema': ema_w, 'macd': macd_w, 'atr': atr_w},
                stop_loss_pct=stop_loss_pct, take_profit_pct=take_profit_pct
            )

            if action == "BUY" and balance >= position_size:
                shares_to_buy = position_size // current_price
                balance -= shares_to_buy * current_price
                positions += shares_to_buy
                buy_price = current_price

            elif action == "SELL" and positions > 0:
                trade_percentage_gain = ((current_price - buy_price) / buy_price) * 100
                trade_percentage_gains.append(trade_percentage_gain)
                balance += positions * current_price
                positions = 0
                buy_price = None
                total_trades += 1

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
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

    return {
        'BB Weight': bb_w,
        'SO Weight': so_w,
        'RSI Weight': rsi_w,
        'SMA Weight': sma_w,
        'EMA Weight': ema_w,
        'MACD Weight': macd_w,
        'ATR Weight': atr_w,
        'Stop Loss %': stop_loss_pct,
        'Take Profit %': take_profit_pct,
        'Total Trades': total_trades,
        'Average Trade Percentage Gain': avg_trade_percentage_gain,
        'Win Rate (%)': win_rate,
        'Max Drawdown (%)': max_drawdown

    }

if __name__ == "__main__":
    weight_combinations = list(product(
        [0.1, 0.2, 0.3], [0.1, 0.15, 0.2], [0.1, 0.2, 0.3], [0.1, 0.15, 0.2],
        [0.05, 0.1, 0.15], [0.1, 0.15, 0.2], [0.01, 0.05, 0.1],
        stop_loss_values, take_profit_values
    ))

    with Pool(processes=num_cores) as pool:
        results = list(tqdm(pool.imap(run_weight_test, weight_combinations), total=len(weight_combinations), desc="Optimizing Weights"))

    pd.DataFrame(results).to_csv('weight_optimization_results.csv', mode='w', header=True, index=False)
    print("Weight optimization completed. Results saved to weight_optimization_results.csv")
