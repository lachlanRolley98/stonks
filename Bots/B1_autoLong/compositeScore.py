import pandas as pd

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

# Read the CSV file into a DataFrame
df = pd.read_csv('output.csv')

# Apply the calculate_composite_score function to each row and create a new column for the composite score
df['Composite'] = df.apply(lambda row: calculate_composite_score(row['MA'], row['MACD'], row['Boiler'], row['StoOsc'], row['RSI']), axis=1)

# Save the updated DataFrame to a new CSV file
df.to_csv('output_with_composite.csv', index=False)

print("Processing complete. Results saved to output_with_composite.csv")
