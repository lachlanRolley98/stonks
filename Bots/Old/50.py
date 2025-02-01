import pandas as pd
import os

# Define the folder containing the data files
folder_path = 'Historical_Data/'
output_folder = 'Processed_Stuff/'
output_file = os.path.join(output_folder, 'top50Stocks.csv')

# Create the output directory if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Initialize a list to store stocks with favorable moving averages and other criteria
good_stocks = []

# Function to check if moving averages indicate a good stock
def is_good_stock(data):
    if data['50_MA'].iloc[-1] > data['200_MA'].iloc[-1] and data['Close/Last'].iloc[-1] > data['200_MA'].iloc[-1]:
        return True
    return False

# Function to check additional criteria
def meets_additional_criteria(data):
    # Example criteria: RSI between 30 and 70
    rsi_50 = calculate_rsi(data['Close/Last'], period=50)
    rsi_200 = calculate_rsi(data['Close/Last'], period=200)
    if 30 < rsi_50 < 70 and 30 < rsi_200 < 70:
        return True
    return False

# Function to calculate RSI (Relative Strength Index)
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

# Process each file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)

        # Load the historical data
        try:
            data = pd.read_csv(file_path, engine='python')
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue

        # Ensure the 'Close/Last' column is treated as a string
        data['Close/Last'] = data['Close/Last'].astype(str)

        # Remove the dollar sign and convert to float
        data['Close/Last'] = data['Close/Last'].str.replace('$', '', regex=False).astype(float)

        # Calculate moving averages
        data['50_MA'] = data['Close/Last'].rolling(window=50).mean()
        data['200_MA'] = data['Close/Last'].rolling(window=200).mean()

        # Calculate RSI values
        rsi_50 = calculate_rsi(data['Close/Last'], period=50)
        rsi_200 = calculate_rsi(data['Close/Last'], period=200)
        rsi_diff = rsi_50 - rsi_200

        # Check if the stock has favorable moving averages and meets additional criteria
        if is_good_stock(data) and meets_additional_criteria(data):
            stock_name = filename.split('.')[0]
            good_stocks.append({
                'Stock': stock_name,
                '50_MA': data['50_MA'].iloc[-1],
                '200_MA': data['200_MA'].iloc[-1],
                'RSI_50': rsi_50,
                'RSI_200': rsi_200,
                'RSI_Diff': rsi_diff,
                'Reason': '50_MA > 200_MA, Close > 200_MA, and RSI between 30 and 70'
            })

# Convert the list of good stocks to a DataFrame
good_stocks_df = pd.DataFrame(good_stocks)

# Filter the top 50 stocks by RSI_DIFF
top_50_stocks = good_stocks_df.nlargest(50, 'RSI_Diff')

# Save the filtered DataFrame to a CSV file
top_50_stocks.to_csv(output_file, index=False)

print(f"Top 50 stocks to consider buying have been saved to {output_file}")
