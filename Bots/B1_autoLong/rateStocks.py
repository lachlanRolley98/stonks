import os
import pandas as pd
from BoilerBands import BoilerBands
from MA import MA
from MACD import MACD
from RSI import RSI
from StochasticOscillator import StochasticOscillator

# Define the folder containing the JSON files
folder_path = '300_100'

# Initialize an empty list to store the results
results = []

# Define the calculate_composite_score function
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

# Iterate through each JSON file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)

        # Extract the name of the JSON file without the .json extension
        name = os.path.splitext(filename)[0]

        # Create instances of each class with the JSON file
        boiler_bands = BoilerBands(file_path)
        ma = MA(file_path)
        macd = MACD(file_path)
        rsi = RSI(file_path)
        stochastic_oscillator = StochasticOscillator(file_path)

        # Calculate the scores
        boiler_score = boiler_bands.calculate_score()
        ma_score = ma.calculate_sma_score(window=20)
        macd_score = macd.calculate_macd_score()
        rsi_score = rsi.calculate_rsi_score()
        stoosc_score = stochastic_oscillator.calculate_stochastic_score()

        # Calculate the composite score
        composite_score = calculate_composite_score(ma_score, macd_score, boiler_score, stoosc_score, rsi_score)

        # Append the results to the list
        results.append([name, boiler_score, ma_score, macd_score, rsi_score, stoosc_score, composite_score])

# Create a DataFrame from the results
df = pd.DataFrame(results, columns=['name', 'Boiler', 'MA', 'MACD', 'RSI', 'StoOsc', 'Composite'])

# Sort the DataFrame by the composite score in descending order
df = df.sort_values(by='Composite', ascending=False)

# Save the DataFrame to a CSV file
df.to_csv('output.csv', index=False)

print("Processing complete. Results saved to output.csv")
