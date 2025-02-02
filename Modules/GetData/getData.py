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
    def __init__(self, save_path):
        EClient.__init__(self, self)
        self.data = []
        self.success = False
        self.req_completed = threading.Event()
        self.mycontract = None  # Define mycontract as a class attribute
        self.queue = Queue()  # Initialize a queue to manage requests
        self.save_path = save_path  # Set the save path

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
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            with open(f"{self.save_path}/{self.mycontract.symbol}.json", "w") as f:
                json.dump(self.data, f, indent=4)
            print(f"Data saved to {self.save_path}/{self.mycontract.symbol}.json")
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
        time.sleep(5)  # Add a pause between requests


# Initialize the app and connect
save_path = '../../Historical_Data/IBK_Today_NASDAQ'
app = TestApp(save_path)
app.connect("127.0.0.1", 7496, 0)
threading.Thread(target=app.run).start()
time.sleep(1)

app.mycontract = Contract()
app.mycontract.secType = "STK"
app.mycontract.currency = "USD"
app.mycontract.exchange = "NASDAQ"
app.mycontract.primaryExchange = "NASDAQ"  # Ensure the primary exchange is set to NASDAQ

sydney_tz = pytz.timezone('Australia/Sydney')
sydney_time = datetime.now(sydney_tz)
us_eastern_tz = pytz.timezone('US/Eastern')
us_eastern_time = sydney_time.astimezone(us_eastern_tz)
formatted_time = us_eastern_time.strftime("%Y%m%d %H:%M:%S US/Eastern")

# Now we start getting all the stocks from the NASDAQ

data = pd.read_csv('../../Historical_Data/NASDAQ_Longs.csv')

# Add stock names to the queue
for stock_name in data['name']:
    app.queue.put(stock_name)

# Start processing the queue
process_queue()


#OK now at this point we have done all the NASDAQ, now we want to do all the NYSE stocks
# Set the save path here
app.save_path = '../../Historical_Data/IBK_Today_NYSE'
app.mycontract.exchange = "NYSE"
app.mycontract.primaryExchange = "NYSE"  # Ensure the primary exchange is set to NYSE

data = pd.read_csv('../../Historical_Data/NYSE_Longs.csv')

# Add stock names to the queue
for stock_name in data['name']:
    app.queue.put(stock_name)

# Start processing the queue
process_queue()

app.disconnect()
