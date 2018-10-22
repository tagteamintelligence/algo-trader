import oandapyV20
from Classes import oandadata, oandaconditions
from Classes.order import oandaorders
import math

class Strategy():
	"""


	"""
	def __init__(self, client, accountID, data, instrument):
		self.client = client
		self.accountID = accountID
		self.data = data
		self.instrument = instrument