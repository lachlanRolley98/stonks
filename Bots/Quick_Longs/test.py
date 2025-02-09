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

# First need to get all the data from the stock market
# you need to run ibk in GetData folder - shall change this later but for now thats the go.

# Initialize an empty list to store the results of the signal analysis
results = []
# Define the calculate_composite_score function
# Example of score calculation
def calculate_composite_scoreX(ma_score, macd_score, bollinger_score, stochastic_score, rsi_score, trend_score, stock_name):
    base_weights = [0.1, 0.25, 0.2, 0.15, 0.3]  # SMA, MACD, Bollinger, Stochastic, RSI
    # If at bottom of Bollinger Band and trending strongly up, increase weight
    if bollinger_score == 10 and trend_score > 7:
        print(f"{stock_name} is rebounding from the bottom! Increasing Bollinger weight.")
        base_weights[2] += 0.1  # Boost Bollinger weight

    # Normalize weights
    total_weight = sum(base_weights)
    normalized_weights = [weight / total_weight for weight in base_weights]

    composite_score = (
        ma_score * normalized_weights[0] +
        macd_score * normalized_weights[1] +
        bollinger_score * normalized_weights[2] +
        stochastic_score * normalized_weights[3] +
        rsi_score * normalized_weights[4]
    )

    return round(composite_score, 2)


# This one seems to find stocks at the top of the top of the boiler bands moving up - to test
def calculate_composite_score(bollinger_score, trend_score, so_score):
    # Ok so I want to filter out only things have are a 6 to 10 in boiler band
    # It also has to have a trend score greater than 6
    # after that so is just a bonus
    score = -1
    if bollinger_score >= 6 and trend_score >= 3.5:

        weights = [0.4, 0.4, 0.2]  # 40% Bollinger, 40% Trend, 20% SO   (Change this to something better)
        score = (
            bollinger_score * weights[0] +
            trend_score * weights[1] +
            so_score * weights[2]
        )

    return round(score, 2)


# Then we can grab all the data from inside the folder Historical_Data/IBK_Today and do stuff with it
# Run through all the files in the folder
for filename in os.listdir('../../Historical_Data/IBK_Today_NYSE'):
    if filename.endswith('.json'):
        file_path = os.path.join('../../Historical_Data/IBK_Today_NYSE', filename)
    # get data out of the file
    with open(file_path, 'r') as file:
        data = json.load(file)
    #print(f"got data for {filename}")
    #grab stok name for later
    stock_name = os.path.splitext(filename)[0]
    #delte the file if it is empty
    if len(data) < 20:
        print(f"Deleting empty file: {filename}")
        os.remove(file_path)
        continue

    # ok now we want to perform some analysis on the data
    # returns 10 if the price is above the 20 day moving average
    sma = calculate_sma_score(data)
    # returns ONLY 10, 5 or 1 depending if the macd is above the signal line
    macd = calculate_macd_score(data)
    # reurns 10 if price it at the bottom of the bollinger band
    bb = calculate_Bollinger_score(data)
    # returns 10 if the stochastic oscillator is below 20
    so = calculate_stochastic_score(data)
    # returns 10 if the rsi is less than 30 (verry oversold)
    rsi = calculate_rsi_score(data)
    # returns a score between 0 and 10 based on the strength of the upward trend 5 is flat
    tu = calculate_trending_up_score(data)

    # Calculate the composite score
    composite_score = calculate_composite_score(bb, tu, so)

    # Append the results to the list
    results.append([stock_name, bb, tu, so, composite_score])

# Create a DataFrame from the results
df = pd.DataFrame(results, columns=['name', 'bb', 'tu', 'so', 'composite_score'])
# Sort the DataFrame by the composite score in descending order
df = df.sort_values(by='composite_score', ascending=False)
# Save the DataFrame to a CSV file
df.to_csv('output_NYSE.csv', index=False)
#Finished
print("Processing complete. Results saved to output_NYSE.csv")