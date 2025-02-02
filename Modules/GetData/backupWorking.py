from ibapi.client import *
from ibapi.wrapper import *
from ibapi.ticktype import TickTypeEnum
import time
import threading
import pandas as pd
import json
from datetime import datetime
import pytz
import os
from queue import Queue

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []
        self.success = False
        self.req_completed = threading.Event()
        self.mycontract = None  # Define mycontract as a class attribute
        self.queue = Queue()  # Initialize a queue to manage requests

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
        if self.data:  # Check if the data is not empty
            save_path = '../../Historical_Data/IBK_Today_NASDAQ'
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            with open(f"{save_path}/{self.mycontract.symbol}.json", "w") as f:
                json.dump(self.data, f, indent=4)
            print(f"Data saved to {save_path}/{self.mycontract.symbol}.json")
        else:
            print(f"No data for {self.mycontract.symbol}, JSON file not created.")
        self.success = True
        self.req_completed.set()

    def disconnect(self):
        self.done = True
        EClient.disconnect(self)
        if self.success:
            print(f"Success: {self.mycontract.symbol}")
        else:
            print(f"Fail: {self.mycontract.symbol}")

app = TestApp()
app.connect("127.0.0.1", 7496, 0)
threading.Thread(target=app.run).start()
time.sleep(1)

app.mycontract = Contract()
app.mycontract.secType = "STK"
app.mycontract.currency = "USD"
app.mycontract.exchange = "NASDAQ"
app.mycontract.primaryExchange = "NASDAQ"

sydney_tz = pytz.timezone('Australia/Sydney')
sydney_time = datetime.now(sydney_tz)
us_eastern_tz = pytz.timezone('US/Eastern')
us_eastern_time = sydney_time.astimezone(us_eastern_tz)
formatted_time = us_eastern_time.strftime("%Y%m%d %H:%M:%S US/Eastern")

data = pd.read_csv('../../Historical_Data/NASDAQ_Longs.csv')

def request_data(stock_name):
    app.mycontract.symbol = stock_name
    app.data = []
    app.success = False
    app.req_completed.clear()
    print(f"Requesting data for {stock_name}...")
    app.reqHistoricalData(app.nextID(), app.mycontract, formatted_time, "100 D", "1 day", "TRADES", 1, 1, False, [])
    app.req_completed.wait(timeout=60)  # Increase the timeout duration

def process_queue():
    while not app.queue.empty():
        stock_name = app.queue.get()
        retries = 3
        while retries > 0:
            request_data(stock_name)
            if app.success:
                break
            else:
                retries -= 1
                print(f"Retrying for {stock_name}... {retries} retries left")
        app.queue.task_done()  # Mark the task as done
        time.sleep(2)  # Add a pause between requests

# Add stock names to the queue
for stock_name in data.iloc[:, 0]:
    app.queue.put(stock_name)

# Start processing the queue
process_queue()

app.disconnect()
