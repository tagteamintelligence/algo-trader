import oandapyV20
import math
import pandas as pd

class STO():
	"""
	Collective of stochastics

	"""
	def __init__(self, df, nK, nD,  nS=3):
		self.df = df
		self.nK = nK
		self.nD = nD
		self.nS = nS

	def calculate(self):
		SOk = pd.Series((self.df['c'] - self.df['l'].rolling(self.nK).min()) / (self.df['h'].rolling(self.nK).max() - self.df['l'].rolling(self.nK).min()), name = 'SOk')
		SOd = pd.Series(SOk.rolling(self.nD).mean(), name = 'SOd')
		SOk = SOk.rolling(self.nS).mean()
		SOd = SOd.rolling(self.nS).mean()
		self.df = self.df.join(SOk)
		self.df = self.df.join(SOd)
		return self.df