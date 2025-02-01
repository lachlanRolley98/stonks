import pandas as pd

# Load your historical data
data = pd.read_csv('Historical_Data/ZUMZ.csv')

# Remove the dollar sign and convert to float
data['Close/Last'] = data['Close/Last'].str.replace('$', '').astype(float)

# Calculate moving averages
data['50_MA'] = data['Close/Last'].rolling(window=50).mean()
data['200_MA'] = data['Close/Last'].rolling(window=200).mean()

# Plot the moving averages
import matplotlib.pyplot as plt

plt.figure(figsize=(12,6))
plt.plot(data['Date'], data['Close/Last'], label='Close/Last')
plt.plot(data['Date'], data['50_MA'], label='50-Day MA')
plt.plot(data['Date'], data['200_MA'], label='200-Day MA')
plt.legend()
plt.show()
