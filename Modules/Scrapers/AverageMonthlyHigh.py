import pandas as pd
import os

#testing to see if my com gets deleted

# Define the folder path for the dataset
folder_path = 'Historical_Data'

# File path for AAAAA_MASTER_MONTH_RANKINGS.csv
master_file_path = 'Processed_Stuff/MASTER_MONTH_RANKINGS.csv'

# Get all CSV files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Check if the master file exists and delete it if it does
if os.path.exists(master_file_path):
    os.remove(master_file_path)
    print(f"{master_file_path} deleted.")

# Create a new DataFrame with the correct columns for the master file
columns = ['name', 'years', 'avg_vol'] + list(range(1, 13))  # Use integers for months as column names
master_df = pd.DataFrame(columns=columns)

# Loop over each file in the folder
for file_name in csv_files:
    file_path = os.path.join(folder_path, file_name)

    # Load the dataset with error handling for encoding issues
    try:
        data = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        print(f"Encoding issue with file: {file_name}. Trying fallback encoding.")
        data = pd.read_csv(file_path, encoding='latin1')

    # Preprocess the data
    data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%Y', errors='coerce')  # Convert 'Date' to datetime and handle errors
    data = data.dropna(subset=['Date'])  # Remove rows with invalid dates (NaT)
    data['Year'] = data['Date'].dt.year  # Extract the year
    data['Month'] = data['Date'].dt.month  # Extract the month

    # Remove '$' and convert price-related columns to numeric
    for col in ['Close/Last', 'Open', 'High', 'Low']:
        data[col] = data[col].astype(str).str.replace('$', '', regex=True).astype(float)

    # Calculate the average monthly high prices for each year
    monthly_avg_per_year = data.groupby(['Year', 'Month'])['High'].mean().reset_index()

    # Rank the months within each year by their average high price
    monthly_avg_per_year['Rank'] = monthly_avg_per_year.groupby('Year')['High'].rank(ascending=False)

    # Create a summary table of rankings for each month across years
    monthly_rank_summary = monthly_avg_per_year.groupby('Month')['Rank'].mean().sort_values()

    # Calculate the number of years in the dataset
    num_years = data['Year'].nunique()

    # average volume
    avg_vol = data['Volume'].mean()

    # Prepare data for appending to AAAAA_MASTER_MONTH_RANKINGS.csv
    row_data = {
        'name': file_name.replace('.csv', ''),
        'years': num_years,
        'avg_vol': avg_vol,
        **{month: monthly_rank_summary.get(month, None) for month in range(1, 13)}
    }

    # Append the new row to the master DataFrame
    master_df = pd.concat([master_df, pd.DataFrame([row_data])], ignore_index=True)

    print(f"Data from {file_name} appended.")

# Save the master DataFrame to the CSV file
master_df.to_csv(master_file_path, index=False)

print(f"Final data saved to {master_file_path}")
