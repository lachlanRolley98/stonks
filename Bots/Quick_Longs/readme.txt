yeah so first you wana go into Modules GetData
Then run the GetData
Then run it again but first ctrl f and replace all NASDAQ with NYSE or visa versa
Those two will propulate Historical_Data/IBK_Today(NASDAQ/NYSE) with heaps of JSONS of all the stocks
Then you can go into this folders test.py and run the code
Once again you gota Ctrl f and switch between NASDAQ and NYSE
This will make 2 output files that have the rundown on how the stocks are
The logic is with the
bollinger_score -  we wana buy when at the bottom of this bad boy
trend_score - this looks at the last 3ish days and sees it the stock is trending up - just basic maths to see if line go up
rsi_score - not too sure what this does, think it will be usefull to detect when to sell - will probs remove
so_score - This guys a beast, if its bellow 20, its probs also bellow boiler band so wana buy. Sell when above
Havent automated buying/selling. Basically do all this then choose what to do from the list

Ok i changed it so can just run the get data once however it will take like 25 mins but do both exchanges. Made a super long delay to stop asyncronos errors pulling wrong stock
Now just gota get the logic right for the bot and presto
When i descide to actually automate this, make sure before you buy the stock to do a single pull of the data and check its baseing everything off the right stuff