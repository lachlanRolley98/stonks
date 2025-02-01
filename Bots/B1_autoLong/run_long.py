

from get_historical_data import get_historical_stock_data




# Example usage
if __name__ == "__main__":
    historical_data = get_historical_stock_data("NOW", output_size="compact")
    if "error" not in historical_data:
        print(f"Fetched {len(historical_data)} records for NOW.")
        print(historical_data[:5])  # Display the first 5 records
    else:
        print(historical_data)
