import yfinance as yf
import numpy as np

def covariance(stock1, stock2, days):
    days = min(len(stock1), len(stock2), days)

    stock1_p = stock1[-days:]
    stock2_p = stock2[-days:]

    stock1_r = stock1_p[1:] - stock1_p[:-1]
    stock2_r = stock2_p[1:] - stock2_p[:-1]

    mu1 = np.mean(stock1_r)
    mu2 = np.mean(stock2_r)

    return np.dot(stock1_r-mu1, stock2_r-mu2)/(days-1)

days = 180

class Stock:
    def __init__(self,ticker):
        self.ticker = ticker
        self.info = None
        self.history = None
        self.price = None
        self.marketcap = None

    def update(self):
        print(f'{self.ticker}')
        try:
            ticker = yf.Ticker(self.ticker)
        except:
            return 'ticker not found'
        try:
            self.info = ticker.info
        except:
            return 'no info'
        self.marketcap = self.info['marketCap']
        period = '1y'
        try:
            hist = ticker.history(period=period).loc[:,'Close']
        except:
            return 'no data'

        try:
            self.info['dividendYield']
        except:
            return 'no dividend'
        else:
            if self.info['dividendYield'] < 0.045:
                return 'low dividend'
            if self.info['dividendYield'] > 0.1:
                return 'high dividend'

        self.history = np.array(hist[-days:])
        if self.history.size < 180:
            return 'not enough data'
        self.price = self.history[-1]
        if self.price < 5:
            return 'penny stock'
        return 0

risk_free = 0.04495  # US 1-year treasury
def tangency(tickers, returns):
    size = len(tickers)
    stocks = []
    for i in range(size):
        print(f'{i+1}/{size}: ')
        stock = Stock(tickers[i])
        exception = stock.update()
        if exception != 0:
            print(exception)
        else:
            stocks.append(stock)
        print('')
    segment_size = len(stocks)
    tickers = [stock.ticker for stock in stocks]

    cov_matrix = np.zeros((segment_size,segment_size))

    for i in range(segment_size):
        print(i)
        print(stocks[i].ticker)
        print('\n')
        for j in range(i,segment_size):
            cov = covariance(stocks[i].history, stocks[j].history, 180)

            cov_matrix[i][j] = cov
            cov_matrix[j][i] = cov

    A = np.block([[2*cov_matrix, -returns.reshape((segment_size,1)), -np.ones((segment_size,1))],
                  [returns.reshape((1,segment_size)), 0, 0],
                  [np.ones((1,segment_size)), 0, 0]])

    portfolio = None
    portfolio_risk = 0
    portfolio_return = 0
    max_k = 0
    markowitz_risk = []
    markowitz_return = []
    for mu in np.linspace(returns.min(), returns.max(), 100):
        b = np.zeros(segment_size+2)
        b[-1] = 1
        b[-2] = mu
        sol = np.linalg.solve(A, b)
        omega = sol[:-2]

        risk = omega.transpose() @ cov_matrix @ omega
        k = (mu-risk_free)/risk

        markowitz_risk.append(risk)
        markowitz_return.append(mu)

        if k > max_k:
            max_k = k
            portfolio = omega
            portfolio_risk = risk
            portfolio_return = mu
    return tickers, portfolio, portfolio_risk, portfolio_return, markowitz_risk, markowitz_return, returns, cov_matrix
