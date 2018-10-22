import oandapyV20
from Classes import oandadata, oandaconditions
from Classes.order import oandaorders

from Strategies import strategy as st
from Indicators import atr, stochastics
import pandas as pd

class ConsolidatingTrending(st.Strategy):
	"""docstring for ConsolidatingTrending"""
	p = {
		"sto" : {
			"nK" : 9,
			"nD" : 3,
			"nS" : 3,
			"upperband" : 0.8,
			"lowerband" : 0.2
		},
		"atr" : {
			"period" : 9
		},
		"highlow1" : {
			"period" : 150
		},
		"highlow2" : {
			"period" : 20
		}
	}
	def __init__(self, client, accountID, data, instrument):
		super().__init__(client, accountID, data, instrument)
		self.granularity = data.granularity
		self.mid = data.candle_mid()
		self.high = [float(x['h']) for x in self.mid]
		self.low = [float(x['l']) for x in self.mid]
		self.close = [float(x['c']) for x in self.mid]
		self.sto = None
		self.atr = None
		self.high1, self.low1 = None, None
		self.high2, self.low2 = None, None

	def calculate(self):
		i = -1
		df = pd.DataFrame(self.mid)
		sto = stochastics.STO(df.astype(float), self.p['sto']['nK'], self.p['sto']['nD'], self.p['sto']['nS'])
		ATR = atr.ATR(df.astype(float), self.p['atr']['period'])
		self.sto = sto.calculate()
		self.atr = ATR.calculate()
		self.high1 = max(self.high[i-self.p['highlow1']['period']:i])
		self.low1 = min(self.low[i-self.p['highlow1']['period']:i])
		self.high2 = max(self.high[i-self.p['highlow2']['period']:i])
		self.low2 = min(self.low[i-self.p['highlow2']['period']:i])

	def run(self):
		i = -1
		self.calculate()
		updater = oandaorders.OandaOrders(self.client, self.accountID)
		updater.updateids(self.instrument, self.granularity)
		#print("prev SOk > SOd: "+str(self.sto['SOk'].iloc[i-1] >= self.sto['SOd'].iloc[i-1]), "SOk: "+str(self.sto['SOk'].iloc[i]),"SOd: "+str(self.sto['SOd'].iloc[i]))
		test = oandaconditions.OandaConditions(self.client, self.accountID, self.instrument, self.granularity)
		if test.canorder():
			# Consolidating
			if self.high1 != self.high2 and self.low1 != self.low2:
				if self.sto['SOd'].iloc[i] < self.p['sto']['lowerband']:
					if self.sto['SOk'].iloc[i] > self.sto['SOd'].iloc[i]:
						orderParams = {
						    "price": self.high[i],
						    "stopLoss": (self.low[i]-self.atr['ATR'].iloc[i]),
						    "instrument": self.instrument,
						    "orderType": "long",
						    "stake": 0.001,
						    "granularity":self.granularity,
						    "trend" : "consolidating"
						}
						createOrder = oandaorders.RequestOrder(self.client, self.accountID, orderParams)
						createOrder.requestorder()
						return
				if self.sto['SOd'].iloc[i] > self.p['sto']['upperband']:
					if self.sto['SOk'].iloc[i] < self.sto['SOd'].iloc[i]:
						orderParams = {
						    "price": self.low[i],
						    "stopLoss": (self.high[i]+self.atr['ATR'].iloc[i]),
						    "instrument": self.instrument,
						    "orderType": "short",
						    "stake": 0.001,
						    "granularity":self.granularity,
						    "trend" : "consolidating"
						}
						createOrder = oandaorders.RequestOrder(self.client, self.accountID, orderParams)
						createOrder.requestorder()
						return
			# Trending Up
			if self.high1 == self.high2:
				if self.sto['SOd'].iloc[i] < self.p['sto']['upperband']:
					if self.sto['SOk'].iloc[i] > self.sto['SOd'].iloc[i]:
						orderParams = {
						    "price": self.high[i],
						    "stopLoss": (self.low[i]-self.atr['ATR'].iloc[i]),
						    "instrument": self.instrument,
						    "orderType": "long",
						    "stake": 0.001,
						    "granularity":self.granularity,
						    "trend" : "trending"
						}
						createOrder = oandaorders.RequestOrder(self.client, self.accountID, orderParams)
						createOrder.requestorder()
						return
			# Trending Down
			if self.low1 == self.low2:
				if self.sto['SOd'].iloc[i] > self.p['sto']['lowerband']:
					if self.sto['SOk'].iloc[i] < self.sto['SOd'].iloc[i]:
						orderParams = {
							"price": self.low[i],
							"stopLoss": (self.high[i]+self.atr['ATR'].iloc[i]),
							"instrument": self.instrument,
							"orderType": "short",
							"stake": 0.001,
							"granularity":self.granularity,
							"trend" : "trending"
						}
						createOrder = oandaorders.RequestOrder(self.client, self.accountID, orderParams)
						createOrder.requestorder()
						return
		if test.canclose():
			# Closing Position
			position = oandaorders.OandaOrders(self.client, self.accountID)
			if position.longnotshort(self.instrument, self.granularity):
				if self.sto['SOk'].iloc[i] <= self.sto['SOd'].iloc[i]:
					closeOut = oandaorders.CloseTrade(self.client, self.accountID, self.granularity, self.instrument)
					closeOut.closetrade()
					return	
			if not (position.longnotshort(self.instrument, self.granularity)):
				if self.sto['SOk'].iloc[i] >= self.sto['SOd'].iloc[i]:
					closeOut = oandaorders.CloseTrade(self.client, self.accountID, self.granularity, self.instrument)
					closeOut.closetrade()
					return
				

		if test.isorderpending():
			# Closing Order
			if self.sto['SOk'].iloc[i-1] <= self.sto['SOd'].iloc[i-1]:
				if self.sto['SOk'].iloc[i] >= self.sto['SOd'].iloc[i]:
					cancelOrder = oandaorders.CancelOrder(self.client, self.accountID, self.granularity, self.instrument)
					cancelOrder.cancelorder()
					return
			if self.sto['SOk'].iloc[i-1] >= self.sto['SOd'].iloc[i-1]:
				if self.sto['SOk'].iloc[i] <= self.sto['SOd'].iloc[i]:
					cancelOrder = oandaorders.CancelOrder(self.client, self.accountID, self.granularity, self.instrument)
					cancelOrder.cancelorder()
					return
		print("Completed run on ", self.instrument)