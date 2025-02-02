from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import Contract
import threading
import time
import pandas as pd
import csv

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
        self.contract_details = None
        self.req_completed = threading.Event()

    def nextValidId(self, orderId):
        self.nextOrderId = orderId

    def contractDetails(self, reqId, contractDetails):
        self.contract_details = contractDetails
        self.req_completed.set()

    def contractDetailsEnd(self, reqId):
        self.req_completed.set()

    def error(self, reqId, errorCode, errorString):
        print(f"Error: {errorCode}, {errorString}")
        self.req_completed.set()

def get_contract_details(symbol):
    app = TestApp()
    app.connect("127.0.0.1", 7496, 0)
    threading.Thread(target=app.run).start()
    time.sleep(1)

    contract = Contract()
    contract.symbol = symbol
    contract.secType = "STK"
    contract.currency = "USD"
    contract.exchange = "SMART"  # Use SMART to get the best available price across multiple exchanges

    app.req_completed.clear()
    app.reqContractDetails(1, contract)
    app.req_completed.wait(timeout=10)

    app.disconnect()
    return app.contract_details

# Read the list of stock names from the CSV file
input_file = '300_Longs.csv'
output_file = 'stock_exchanges.csv'

stock_data = []
with open(input_file, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        stock_name = row[0]
        details = get_contract_details(stock_name)
        if details:
            exchange = details.contract.primaryExchange
            stock_data.append([stock_name, exchange])
        else:
            stock_data.append([stock_name, 'Unknown'])
        time.sleep(5)  # Pause for 5 seconds between requests

# Create a DataFrame and sort by exchange
df = pd.DataFrame(stock_data, columns=['Stock Name', 'Exchange'])
df = df.sort_values(by='Exchange')

# Save the sorted data to a new CSV file
df.to_csv(output_file, index=False)

print(f"Stock exchange information saved to {output_file}")
