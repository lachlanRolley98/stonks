import os
import pandas as pd

# Paths
downloads_path = r"C:\Users\rolle\Downloads"
nasdaq_nyse_path = r"Processed_Stuff/nasdaq_nyse_all_stocks.csv"
output_path = r"missing_stocks.csv"

# Read the CSV file containing stock names
nasdaq_nyse_df = pd.read_csv(nasdaq_nyse_path)

# Ensure the first column is treated as stock names
stock_names = nasdaq_nyse_df.iloc[:, 0].astype(str).str.strip().str.upper()

# Get the list of Excel files in the Downloads folder
excel_files = [
    os.path.splitext(file)[0].strip().upper()  # Remove the file extension and normalize
    for file in os.listdir(downloads_path)
    if file.endswith(".csv") or file.endswith(".xls")
]

# Find missing stock names
missing_stocks = [name for name in stock_names if name not in excel_files]

# Create a DataFrame for missing stock names
missing_stocks_df = pd.DataFrame(missing_stocks, columns=["Missing Stocks"])

# Write the missing stocks to a CSV file
missing_stocks_df.to_csv(output_path, index=False)

print(f"Missing stocks saved to {output_path}")
