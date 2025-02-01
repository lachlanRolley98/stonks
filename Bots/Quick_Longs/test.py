import json
import os
from Modules.Signals import (
    calculate_Bollinger_score,
    calculate_sma_score,
    calculate_macd_score,
    calculate_rsi_score,
    calculate_stochastic_score
)

# Example usage
with open('../../Historical_Data/IBK_Today/ABR.json', 'r') as file:
    data = json.load(file)

# First need to get all the data from the stock market
# you need to run ibk in GetData folder - shall change this later but for now thats the go.


# Then we can grab all the data from inside the folder Historical_Data/IBK_Today and do stuff with it


for filename in os.listdir('../../Historical_Data/IBK_Today'):
    if filename.endswith('.json'):
        file_path = os.path.join('../../Historical_Data/IBK_Today', filename)
    with open(file_path, 'r') as file:
        data = json.load(file)
    # print(f"got data for {filename}")






    # reurns 10 if price it at the bottom of the bollinger band
    bb = calculate_Bollinger_score(data)
    # returns 10 if the price is above the 20 day moving average
    sma = calculate_sma_score(data)
    # returns ONLY 10, 5 or 1 depending if the macd is above the signal line
    macd = calculate_macd_score(data)
    # returns 10 if the rsi is above 70
    rsi = calculate_rsi_score(data)
    # returns 10 if the stochastic oscillator is below 20
    so = calculate_stochastic_score(data)