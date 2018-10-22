import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.transactions as trans
from Classes import oandadata
from Classes.order import oandarecord
import time
import pandas as pd
import csv
import math

class OandaOrders():
	"""
	Creates order objects with login info

	"""
	def __init__(self, client, accountID):
		self.client = client
		self.accountID = accountID

	def saveid(self, response):
		granularity = response[0] 
		instrument = response[1]
		orderID = response[2]
		trend = response[3]
		df = self.getids()
		if trend == 'consolidating':
			df.loc[granularity,instrument]['Consolidating'] = orderID
		elif trend == 'trending':
			df.loc[granularity,instrument]['Trending'] = orderID
		
		df.to_csv("Data/tradeid.csv", sep=',', encoding='utf-8', index_label="Granularity")

	def getids(self):
		df = pd.read_csv('Data/tradeid.csv', index_col=[0], header=[0,1], dtype="object")
		return df

	def getid(self,granularity, instrument):
		df = self.getids()
		csvID = df.loc[granularity, instrument]
		for i, x in enumerate(csvID):
			if not pd.isnull(x):
				return (x, i)
		return (x, 'NaN')

	def updateids(self, instrument, granularity):
		df = self.getids()
		csvID = self.getid(granularity, instrument)
		params = {
			"instrument": instrument
		}
		o = orders.OrderList(self.accountID, params=params)
		t = trades.TradesList(self.accountID, params=params)
		self.client.request(o)
		self.client.request(t)
		orderlist = [x['id'] for x in o.response['orders']]
		tradelist = [x['id'] for x in t.response['trades']]
		if csvID[0] in orderlist:
			return
		elif csvID[0] in tradelist:
			return
		else:
			for x in tradelist:
				p = {
					'id':x
				}
				t = trans.TransactionDetails(self.accountID, p['id'])
				self.client.request(t)
				orderID = t.response['transaction']['orderID']
				if orderID == csvID[0]:
					if csvID[1] == 0:
						df.loc[granularity,instrument]['Consolidating'] = x
					elif csvID[1] == 1:
						df.loc[granularity,instrument]['Trending'] = x
					df.to_csv("Data/tradeid.csv", sep=',', encoding='utf-8', index_label="Granularity")
					return
	
	def resetid(self, granularity, instrument):
			df = self.getids()
			idloc = self.getid(granularity, instrument)
			if idloc[1] == 0:
				df.loc[granularity,instrument]['Consolidating'] = 'NaN'
			elif idloc[1] == 1:
				df.loc[granularity,instrument]['Trending'] = 'NaN'
			df.to_csv("Data/tradeid.csv", sep=',', encoding='utf-8', index_label="Granularity")
			return
	
	def longnotshort(self, instrument, granularity):
		getid = self.getid(granularity, instrument)
		csvID = getid[0]
		t = trans.TransactionDetails(self.accountID, csvID)
		self.client.request(t)
		return int(t.response['transaction']['units']) > 0
		 


class RequestOrder(OandaOrders):
	"""
	Requests to put an order for a trade through oanda
	Inputs: login info, custom order params
	Outputs: order request, response from oanda as print

	"""
	def __init__(self, client, accountID, params):
		self.params = params
		super().__init__(client, accountID)
	
	def requestorder(self):
		orderData = {
		"order": {
			"price": str(self.params['price']),
			"stopLossOnFill": {
				"timeInForce": "GTC",
				"price": str(round(self.params['stopLoss'], 3))
				},
			"timeInForce": "GTC",
			"instrument": self.params['instrument'],
			"units": str(self.ordersize()),
			"type": "STOP",
			"positionFill": "DEFAULT"
			}
		}
		newOrder = orders.OrderCreate(accountID=self.accountID, data=orderData)
		self.client.request(newOrder)
		response = newOrder.response
		shortresponse = (self.params['granularity'], self.params['instrument'], response['orderCreateTransaction']['id'],self.params['trend'])
		self.saveid(shortresponse)
		print ("\n", response, "\n")

	def ordersize(self):
		pip_per_100000 = self.pipconvert()
		request = accounts.AccountDetails(accountID=self.accountID)
		accountInfo = self.client.request(request)
		balance = accountInfo['account']['balance']
		if self.params['instrument'].find("JPY") != -1:
			if self.params['orderType'] == 'long':
				orderSize = ((float(balance)*self.params['stake'])/((abs(self.params['price'] - self.params['stopLoss'])*100)*pip_per_100000))*100000
			if self.params['orderType'] == 'short':
				orderSize = ((float(balance)*(-self.params['stake']))/((abs(self.params['price'] - self.params['stopLoss'])*100)*pip_per_100000))*100000
			sizeFix = round(orderSize/1000)*1000
			return sizeFix
		else:
			if self.params['orderType'] == 'long':
				orderSize = ((float(balance)*self.params['stake'])/((abs(self.params['price'] - self.params['stopLoss'])*10000)*pip_per_100000))*100000
			if self.params['orderType'] == 'short':
				orderSize = ((float(balance)*(-self.params['stake']))/((abs(self.params['price'] - self.params['stopLoss'])*10000)*pip_per_100000))*100000
			sizeFix = round(orderSize/1000)*1000
			return sizeFix

	def pipconvert(self):
		pipparams = {
			"count": 1,
			"granularity": self.params['granularity']
		}
		default = ["AUD","EUR","GBP","NZD","USD"] 
		if self.params['instrument'][-3:] in default:  
			data = oandadata.CandleData(self.client, self.params['instrument'][-3:]+"_CAD", pipparams)
			mid = data.candle_mid()
			close = [float(x['c']) for x in mid]
			costperpip = close[0] * 10
			return costperpip
		elif self.params['instrument'][-3:] =="JPY":
			data = oandadata.CandleData(self.client, "CAD_"+self.params['instrument'][-3:], pipparams)
			mid = data.candle_mid()
			close = [float(x['c']) for x in mid]
			costperpip = (1/close[0]) * 1000
			return costperpip
		elif self.params['instrument'][-3:] =="CHF":
			data = oandadata.CandleData(self.client, "CAD_"+self.params['instrument'][-3:], pipparams)
			mid = data.candle_mid()
			close = [float(x['c']) for x in mid]
			costperpip = (1/close[0]) * 10
			return costperpip
		elif self.params['instrument'][-3:] =="CAD":
			costperpip = 10.0
			return costperpip
		else:
			print("pipconvert: ", "Not a valid Currency Pair" )


class CancelOrder(OandaOrders):
	"""
	Requests to cancel a pending order that has yet been filled
	Inputs: login info, params required to obtain targeted orderID (needs instrument)
	Outputs: order cancel request, response from oanda as print

	"""
	def __init__(self, client, accountID, granularity, instrument):
		self.granularity = granularity
		self.instrument = instrument
		super().__init__(client, accountID)

	def cancelorder(self):
		csvID = self.getid(self.granularity, self.instrument)
		orderID = csvID[0]
		orderCancel = orders.OrderCancel(accountID=self.accountID, orderID=orderID)
		self.client.request(orderCancel)
		self.resetid(self.granularity, self.instrument)
		print("\n", orderCancel.response, "\n")

class CloseTrade(OandaOrders):
	"""
	Requests to close an open trade with specified trading id.
	Inputs: login info, params required to obtain targeted orderID (needs instrument)
	Outputs: order cancel request, response from oanda as print

	"""
	def __init__(self, client, accountID, granularity, instrument):
		self.granularity = granularity
		self.instrument = instrument
		super().__init__(client, accountID)

	def closetrade(self):
		csvID = self.getid(self.granularity, self.instrument)
		tradeID = csvID[0]
		close = trades.TradeClose(self.accountID, tradeID)
		self.client.request(close)
		print("\n", close.response, "\n")
		self.resetid(self.granularity, self.instrument)
		transactionID = close.response['orderFillTransaction']['id']
		recorder = oandarecord.Recorder(self.client, self.accountID, transactionID, self.granularity, csvID[1])
		recorder.closing()


#thomasHasABigBoyIdea = {EUR_USD:{consolidate:{H1:0,H4:0,D:0},trending:{H1:0,H4:0,D:0}}}

