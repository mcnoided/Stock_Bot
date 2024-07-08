import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np
import time

def correlation(stock1, stock2, days):
    stock1_p = stock1.history[-days:]
    stock2_p = stock2.history[-days:]

    stock1_r = stock1_p[1:]-stock1_p[:-1]
    stock2_r = stock2_p[1:]-stock2_p[:-1]

    return np.dot(stock1_r-np.mean(stock1_r), stock2_r-np.mean(stock2_r))/(days-1)

class Stock:
    def __init__(self,ticker):
        self.ticker = ticker
        self.history = None
        self.updated = True
        self.update()

    def update(self):
        stock = yf.Ticker(self.ticker)
        clear = True
        period = '1mo'
        try:
            old_hist = pd.read_csv(self.ticker+'.txt', header=None, index_col=None)
            last_date = old_hist.iloc[-1][0]
        except:
            clear = False
            period = '2y'

        hist = stock.history(period=period).loc[:,'Close']

        if clear == True:
            index = hist.index.get_loc(last_date)
            hist = hist.iloc[index+1:]

        hist.to_csv(self.ticker+'.txt', mode='a', header=False)
        self.data = pd.read_csv(self.ticker+'.txt', header=None, index_col=None)
        updated_hist = self.data[1].tolist()
        self.history = np.array(updated_hist[-365:])