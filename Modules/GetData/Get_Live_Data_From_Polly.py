import requests
import json
import datetime


# auto sign in from edge

# This guy uses polygon.io : https://polygon.io/docs/stocks/getting-started
# you give it a stock and a range and it returns a json
# each json entry contains: heaps of blach shit but we care about result which has
# 'v': volume
# 'vw': volume weighted average price
# 'o': open price
# 'c': close price
# 'h': highest price
# 'l': lowest price
# 't': Unix Msec timestamp for the window
# 'n': number of transaction in the window

def getStockData():
  # Define the API key and the endpoint
  api_key = "a2khPF7NylQ1Tz2j0_qUTggHquqIHK3o"
  url = f"https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2021-01-09/2023-01-08?apiKey={api_key}"

  # Make the GET request
  response = requests.get(url)
  data = response.json()

  # Print the retrieved data
  print(data)


getStockData()


## NOTE THis is how u itterate accross the json

# Sample JSON response
# data = {
#     "request_id": "b84e24636301f19f88e0dfbf9a45ed5c",
#     "results": [
#         {
#             "P": 127.98,
#             "S": 7,
#             "T": "AAPL",
#             "X": 19,
#             "p": 127.96,
#             "q": 83480742,
#             "s": 1,
#             "t": 1617827221349730300,
#             "x": 11,
#             "y": 1617827221349366000,
#             "z": 3
#         },
#         {
#             "P": 129.45,
#             "S": 8,
#             "T": "AAPL",
#             "X": 19,
#             "p": 129.42,
#             "q": 74567412,
#             "s": 1,
#             "t": 1617831221349730300,
#             "x": 11,
#             "y": 1617831221349366000,
#             "z": 3
#         }
#     ],
#     "status": "OK"
# }

# # Extracting the request_id and iterating through results
# request_id = data.get("request_id")
# print(f"Request ID: {request_id}")

# results = data.get("results", [])
# for result in results:
#     q_value = result.get("q")
#     print(f"q: {q_value}")


## NOTE this is how you convert the time to date
# import datetime

# # Your timestamp in milliseconds
# t = 1672376400000

# # Convert milliseconds to seconds
# t_seconds = t / 1000

# # Convert the timestamp to a datetime object
# date_time = datetime.datetime.fromtimestamp(t_seconds)

# # Format the datetime object to your desired format
# formatted_date = date_time.strftime("%d-%m-%Y")

# print(f"Formatted Date: {formatted_date}")
