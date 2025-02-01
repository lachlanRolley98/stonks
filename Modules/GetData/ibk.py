from ibapi.client import *
from ibapi.wrapper import *
from ibapi.ticktype import TickTypeEnum
import time
import threading
import pandas as pd
import json
from datetime import datetime
import pytz

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []
        self.success = False
        self.req_completed = threading.Event()

    def nextValidId(self, orderId):
        self.OrderId = orderId

    def nextID(self):
        self.OrderId += 1
        return self.OrderId

    def error(self, reqId, errorCode, errorString):
        if errorCode not in [2104, 2106, 2158]:
            print(f"reqID: {reqId} errorCode: {errorCode}, errorString {errorString}")
            self.success = False
            self.req_completed.set()

    def historicalData(self, reqId, bar):
        self.data.append({
            "date": bar.date,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume
        })

    def historicalDataEnd(self, reqId, start, end):
        print(f"Historical data ended for {reqId}. Start: {start}, End: {end}")
        self.cancelHistoricalData(reqId)
        # Change the path to your desired folder
        save_path = '../../Historical_Data/IBK_Today'  # Path to the folder where you want to save the data
        # Ensure the directory exists
        import os
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        # Save the data to a file in the specified directory
        with open(f"{save_path}/{mycontract.symbol}.json", "w") as f:
            json.dump(self.data, f, indent=4)
        print(f"Data saved to {save_path}/{mycontract.symbol}.json")
        self.success = True
        self.req_completed.set()

    def disconnect(self):
        self.done = True
        EClient.disconnect(self)
        if self.success:
            print(f"Success: {mycontract.symbol}")
        else:
            print(f"Fail: {mycontract.symbol}")

app = TestApp()
app.connect("127.0.0.1", 7497, 0)
threading.Thread(target=app.run).start()
time.sleep(1)

mycontract = Contract()
mycontract.secType = "STK"
mycontract.currency = "USD"
mycontract.exchange = "SMART"
mycontract.primaryExchange = "NASDAQ"

# Get current time in Sydney
sydney_tz = pytz.timezone('Australia/Sydney')
sydney_time = datetime.now(sydney_tz)
# Convert to US Eastern Time
us_eastern_tz = pytz.timezone('US/Eastern')
us_eastern_time = sydney_time.astimezone(us_eastern_tz)
formatted_time = us_eastern_time.strftime("%Y%m%d %H:%M:%S US/Eastern")

data = pd.read_csv('../../Processed_Stuff/300_Longs.csv')

for stock_name in data.iloc[:, 0]:
    mycontract.symbol = stock_name
    app.data = []  # Reset data for each stock
    app.success = False  # Reset success flag for each stock
    app.req_completed.clear()  # Clear the event flag
    app.reqHistoricalData(app.nextID(), mycontract, formatted_time, "100 D", "1 day", "TRADES", 1, 1, False, [])
    app.req_completed.wait()  # Wait for the request to complete

app.disconnect()
