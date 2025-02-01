# This bad boy will scrape all the stocks in the CSV file and download the historical data for each stock

import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm  # Import tqdm for progress bar

# Read the CSV file containing stock tickers
df = pd.read_csv('missing_stocks.csv')  # Replace with your actual file path

# Set up Chrome options for Selenium
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (useful for headless mode)
chrome_options.add_argument("--no-sandbox")  # Disable sandbox for better compatibility

# Set up the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Download folder path
download_folder = r"C:\Users\rolle\Downloads"

# Loop over each stock ticker with a progress bar
for ticker in tqdm(df['Symbol'], desc="Processing stocks", unit="stock"):
    try:
        # Construct the URL for the stock
        url = f"https://www.nasdaq.com/market-activity/stocks/{ticker.lower()}/historical"

        # Navigate to the stock's historical data page
        driver.get(url)

        # Wait for the "MAX" button (now "y10") to be clickable
        try:
            max_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jupiter22-tab[data-tab-id='y10']"))
            )
            driver.execute_script("arguments[0].click();", max_button)  # Click using JavaScript
        except Exception as e:
            print(f"Error clicking MAX button for {ticker}: {e}")
            continue

        # Wait for a short delay (adjust timing if necessary)
        time.sleep(2)

        # Wait for the download button to be clickable and click it
        try:
            download_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.historical-download"))
            )
            download_button.click()
        except Exception as e:
            print(f"Error clicking download button for {ticker}: {e}")
            continue

        # Wait for the file to download
        time.sleep(5)

        # Rename the downloaded file to the ticker name
        downloaded_file = max(
            os.listdir(download_folder),
            key=lambda x: os.path.getctime(os.path.join(download_folder, x))
        )
        new_file_name = os.path.join(download_folder, f"{ticker}.csv")
        os.rename(os.path.join(download_folder, downloaded_file), new_file_name)
        print(f"Downloaded and renamed file for {ticker}")

    except Exception as e:
        print(f"Error processing {ticker}: {e}")

# Close the WebDriver after finishing
driver.quit()
