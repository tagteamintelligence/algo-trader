import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
from Classes.order import oandaorders

class OandaConditions():
	"""


	"""
	def __init__(self, client, accountID, instrument, granularity):
		self.client = client
		self.accountID = accountID
		self.granularity = granularity
		self.instrument = instrument
		self.params = {
			"instrument": instrument
		}
	
	def getcsvID(self):
		fromCSV = oandaorders.OandaOrders(self.client, self.accountID)
		csvID = fromCSV.getid(self.granularity, self.instrument)
		return csvID[0]

	def canorder(self):
		csvID = self.getcsvID()
		tradeList =  trades.TradesList(accountID=self.accountID, params=self.params)
		orderList = orders.OrderList(accountID=self.accountID, params=self.params)
		self.client.request(tradeList)
		self.client.request(orderList)
		try:
			tradeIDList = [x['id'] for x in tradeList.response['trades']]
			orderIDList = [x['id'] for x in orderList.response['orders']]
			if csvID not in tradeIDList:
				if csvID not in orderIDList:
					return True
			return False
		except Exception:
			print("ordernow error")


	def canclose(self):
		csvID = self.getcsvID()
		tradeList =  trades.TradesList(accountID=self.accountID, params=self.params)
		self.client.request(tradeList)
		try:
			tradeIDList = [x['id'] for x in tradeList.response['trades']]
			if csvID in tradeIDList:
				return True
			return False
		except Exception:
			print("closenow error")

	def isorderpending(self):
		csvID = self.getcsvID()
		orderList = orders.OrderList(accountID=self.accountID, params=self.params)
		self.client.request(orderList)
		try:
			orderIDList = [x['id'] for x in orderList.response['orders']]
			if csvID in orderIDList:
				return True
			return False
		except Exception:
			print("isorderpending error")