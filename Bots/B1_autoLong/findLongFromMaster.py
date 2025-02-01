import pandas as pd

# I want to get all the longs from thins

data = pd.read_csv('../Processed_Stuff/MASTER_MONTH_RANKINGS.csv')
master_file_path = '300_Longs.csv'

# Filter out rows where years is lower than 3
filtered_data = data[data['years'] >= 5]
filtered_data = filtered_data[filtered_data['avg_vol'] >= 100000]

# Define a function to check if the values are generally decreasing with some flexibility
def is_generally_decreasing(row, allowed_increases=3):
    values = row[['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']]
    increases = sum(x < y for x, y in zip(values, values[1:]))
    return increases <= allowed_increases

# Apply the function to filter the rows
filtered_data = filtered_data[filtered_data.apply(is_generally_decreasing, axis=1)]

# Get the names of the longs
Longs = filtered_data['name']

# Save the longs to a csv file
Longs.to_csv(master_file_path, index=False)

# Print all the filtered data
print(Longs)