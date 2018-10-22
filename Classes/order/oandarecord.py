import oandapyV20
import oandapyV20.endpoints.accounts as accounts
import pandas as pd
import csv

class Recorder():
	"""docstring for ClassName"""
	def __init__(self, client, accountID, transID, granularity, trend):
		self.client = client
		self.accountID = accountID
		self.lastTransactionID = int(transID) - 1
		self.granularity = granularity
		self.trend = trend
		self.params = {
			"sinceTransactionID" : self.lastTransactionID
		}

	def closing(self):
		r = accounts.AccountChanges(accountID=self.accountID, params=self.params)
		self.client.request(r)
		closetrades = r.response['changes']['tradesClosed']
		df = pd.DataFrame(closetrades)
		if self.trend == 0: 
			t = "Consolidating"
		elif self.trend == 1:
			t = "Trending"
		df['granularity'] = pd.Series(self.granularity)
		df['trend'] = pd.Series(t)
		with open("Data/closedtrades.csv",'a') as data:
			df.to_csv(data, header=False, index=False)