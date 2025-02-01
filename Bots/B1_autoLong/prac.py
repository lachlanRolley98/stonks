from ibapi.client import *
from ibapi.wrapper import *
from ibapi.ticktype import TickTypeEnum
import time
import threading

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId):
        self.OrderId = orderId

    def nextID(self):
        self.OrderId += 1
        return self.OrderId

    def currentTime(self, time):
        print(time)

    def error(self, reqId, errorCode, errorString):
        print(f"reqID: {reqId} errorCode: {errorCode}, errorString {errorString}")

    def contractDetails(self, reqId, contractDetails):
        attrs = vars(contractDetails)
        #print("\n".join(f"{name}: {value}" for name, value in attrs.items()))
        print(contractDetails.contract)


    def contractDetailsEnd(self, reqId):
        print("End of contract details")

    def tickPrice(self, reqId, tickType, price, attrib):
        print(f" reqID: {reqId}, tickType: {TickTypeEnum.to_str(tickType)}, price: {price}, attrib: {attrib}")

    def tickSize(self, reqId, tickType, size):
        print(f" reqID: {reqId}, tickType: {TickTypeEnum.to_str(tickType)}, size: {size}")

    def headTimestamp(self, reqId, headTimestamp):
        return super().headTimestamp(reqId, headTimestamp)

app = TestApp()
app.connect("127.0.0.1", 7497, 0)

threading.Thread(target=app.run).start()
time.sleep(1)

mycontract = Contract()
mycontract.symbol = "AAPL"
mycontract.secType = "STK"
mycontract.currency = "USD"
mycontract.exchange = "SMART"
mycontract.primaryExchange = "NASDAQ"

#app.reqContractDetails(app.nextID(), mycontract)
app.reqMarketDataType(3)
app.reqMktData(app.nextID(), mycontract, "232", False, False, [])
