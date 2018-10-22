import oandapyV20
import oandapyV20.endpoints.instruments as instruments

class OandaData():
	"""
	Class used to obtain and update data of referenced instrument
	and timeframe. 

	Inputs: Client Information (Login), Currency Pair (Instrument), Params (optional request parameters)

	Outputs appropriate data.

	"""
	def __init__(self, client, instrument, params):
		self.client = client
		self.instrument = instrument
		self.params = params

class CandleData(OandaData):
	"""
	Child Class can be called to obtain candlestick data from OandaData parent class

	"""
	def __init__(self, client, instrument, params):
		self.candles = []
		self.granularity = params['granularity']
		super().__init__(client, instrument, params)

	def candle_data(self):
		get_candles = instruments.InstrumentsCandles(instrument = self.instrument, params = self.params)
		self.client.request(get_candles)
		self.candles = get_candles.response['candles']
		return self.candles

	def candle_mid(self):
		candleMid = [x['mid'] for x in self.candle_data()]
		return candleMid
	
	def candle_volume(self):
		candleVol = [x['volume'] for x in self.candle_data()]
		return candleVol
	
	def candle_complete(self):
		candleComp = [x['complete'] for x in self.candle_data()]
		return candleComp