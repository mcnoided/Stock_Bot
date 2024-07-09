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

    s_xy = np.sum(stock1_r*stock2_r)

    s_x = np.sum(stock1_r)
    s_y = np.sum(stock2_r)

    s_x2 = np.sum(stock1_r**2)
    s_y2 = np.sum(stock2_r**2)

    n = days
    return (n*s_xy-s_x*s_y)/np.sqrt((n*s_x2-s_x**2)*(n*s_y2-s_y**2))

class Stock:
    def __init__(self,ticker):
        self.ticker = ticker
        self.info = None
        self.history = None
        self.updated = True
        self.update()

    def update(self):
        stock = yf.Ticker(self.ticker)
        self.info = stock.info
        clear = True
        period = '1mo'
        try:
            old_hist = pd.read_csv(self.ticker+'.txt', header=None, index_col=None)
            last_date = old_hist.iloc[-1][0]
        except:
            clear = False
            period = '1y'

        hist = stock.history(period=period).loc[:,'Close']

        if clear == True:
            index = hist.index.get_loc(last_date)
            hist = hist.iloc[index+1:]

        hist.to_csv(self.ticker+'.txt', mode='a', header=False)
        self.data = pd.read_csv(self.ticker+'.txt', header=None, index_col=None)
        updated_hist = self.data[1].tolist()
        self.history = np.array(updated_hist[-180:])

tickers = ['AAPL', 'MSFT', 'NVDA', 'GOOG', 'AMZN', 'META', 'TSM', 'BRK-B', 'LLY',
           'TSLA', 'NVO', 'JPM', 'WMT', 'V', 'XOM', 'UNH', 'ASML', 'MA', 'ORCL',
           'PG', 'COST', 'MC.PA', 'JNJ', 'HD', 'MRK', 'BAC', 'NFLX', 'ABBV', 'AMD',
           'CVX', 'TM', 'NESN.SW', 'KO', 'ADBE', 'CRM', 'AZN', 'RMS.PA', 'SAP',
           'OR.PA', 'QCOM', 'SHEL', 'PEP', 'ROG.SW', 'NVS', 'TMUS', 'LIN',
           'WFC', 'TMO', 'AMAT', 'ARM', 'ACN', 'CSCO', 'INTU', 'TXN', 'GE', 'MCD',
           'DHR', 'ABT', 'DIS', 'VZ', 'AXP', 'AMGN', 'MS', 'IBM', 'TTE', 'CAT',
           'HSBC', 'PM', 'PFE', 'ISRG', 'NOW', 'HDB', 'PRX.AS', 'RY', 'IDEXY',
           'SIE.DE', 'GS', 'UBER', 'NEE', 'BHP', 'CMCSA', 'CBA.AX', 'MU']

stocks = []
for ticker in tickers:
    try:
        stocks.append(Stock(ticker))
    except:
        continue

size = len(tickers)
corr_matrix = np.zeros((size,size))
for i in range(size):
    for j in range(size):
        days = min(stocks[i].history.size, stocks[j].history.size, 180)
        corr = correlation(stocks[i],stocks[j],days)
        corr_matrix[i][j] = corr

correlations = []
for i in range(size-1):
    for j in range(i+1,size):
        correlations.append((corr_matrix[i][j],i,j))
correlations.sort(key = lambda x: x[0], reverse=False)

for tri in correlations:
    plt.plot(stocks[tri[1]].history, label=stocks[tri[1]].info['shortName'])
    plt.plot(stocks[tri[2]].history, label=stocks[tri[2]].info['shortName'])
    plt.legend()
    plt.title(f"{stocks[tri[1]].info['shortName']} and {stocks[tri[2]].info['shortName']}\n{tri[0]}")
    plt.show()
    time.sleep(6)
