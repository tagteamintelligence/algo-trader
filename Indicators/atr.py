import oandapyV20
import math
import pandas as pd

class ATR():
	"""
	ATR indicator

	"""
	def __init__(self, df, n):
		self.df = df
		self.n = n

	def calculate(self):
		i = 0
		TR_l = [0]
		while i < self.df.index[-1]:
			TR = max(self.df.loc[i + 1, 'h'], self.df.loc[i, 'c']) - min(self.df.loc[i + 1, 'l'], self.df.loc[i, 'c'])
			TR_l.append(TR)
			i = i + 1
		TR_s = pd.Series(TR_l)
		ATR = pd.Series(TR_s.ewm(span=self.n, min_periods=self.n).mean(), name='ATR')
		self.df = self.df.join(ATR)
		return self.df