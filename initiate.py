import time
from Classes import oandaconnect, oandadata
from Strategies import consolidatingtrending as st

instruments = ["AUD_JPY","AUD_USD","CAD_JPY","CHF_JPY","EUR_AUD","EUR_CAD","EUR_CHF",
	"EUR_GBP","EUR_JPY","EUR_NZD","EUR_USD","GBP_AUD","GBP_CAD","GBP_CHF","GBP_JPY",
	"GBP_USD","NZD_JPY","NZD_USD","USD_CAD","USD_CHF","USD_JPY"]

params1 = {
	"count":150,
	"granularity":"D"
}
params2 = {
	"count":150,
	"granularity":"H4"
}
params3 = {
	"count":150,
	"granularity":"H1"
}



if __name__ == '__main__':
	try:
		connect = oandaconnect.OandaConnect()
		connect.login()
		client, accountID = connect.client, connect.accountID
		while True:
			for x in range(len(instruments)):
				if time.localtime()[3] == 13 and time.localtime()[4] == 57 and time.localtime()[5] == x:
					try:
						data = oandadata.CandleData(client, instrument=instruments[x], params=params1)				
						######
						strategy = st.ConsolidatingTrending(client, accountID, data, instruments[x])	
						######
						strategy.run()
						if x == len(instruments)-1: print("\n Daily Wave Cleared @ "+time.asctime(), "\n") 
					except Exception as e:
						print (e) 

				if ((time.localtime()[3]+1)%4==2 or time.localtime()[3]==1)  and time.localtime()[4] == 58 and time.localtime()[5] == x:
					try:
						data = oandadata.CandleData(client, instrument=instruments[x], params=params2)
						######	
						strategy = st.ConsolidatingTrending(client, accountID, data, instruments[x])
						######
						strategy.run()
						if x == len(instruments)-1: print("\n4 Hour Wave Cleared @ "+time.asctime(), "\n") 
					except Exception as e:
						print (e)

				if time.localtime()[4] == 59 and time.localtime()[5] == x:
					try:
						data = oandadata.CandleData(client, instrument=instruments[x], params=params3)
						######
						strategy = st.ConsolidatingTrending(client, accountID, data, instruments[x])
						######
						strategy.run()
						if x == len(instruments)-1: print("\n1 Hour Wave Cleared @ "+time.asctime(), "\n") 
					except Exception as e:
						print (e) 
			time.sleep(1)
	except KeyboardInterrupt:
		print("\n")