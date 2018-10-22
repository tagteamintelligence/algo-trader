import oandapyV20
import configparser

class OandaConnect():
	"""
	Connects to the Oanda platform with Log in 
	information via config parser.

	"""
	def __init__(self):
		self.accountID = None
		self.access_token = None
		self.client = None

	def login(self):
		config = configparser.ConfigParser()
		config.read('../config/config_v20.ini')
		self.accountID = config['oanda']['account_id']
		self.access_token = config['oanda']['api_key']
		self.client = oandapyV20.API(access_token=self.access_token)		