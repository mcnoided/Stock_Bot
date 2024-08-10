import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
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

def correlation(stock1, stock2, days):
    days = min(len(stock1),len(stock2),days)

    stock1_p = stock1[-days:]
    stock2_p = stock2[-days:]

    stock1_r = stock1_p[1:]-stock1_p[:-1]
    stock2_r = stock2_p[1:]-stock2_p[:-1]

    s_xy = np.sum(stock1_r*stock2_r)

    s_x = np.sum(stock1_r)
    s_y = np.sum(stock2_r)

    s_x2 = np.sum(stock1_r**2)
    s_y2 = np.sum(stock2_r**2)

    n = days
    return (n*s_xy - s_x*s_y)/np.sqrt((n*s_x2 - s_x**2)*(n*s_y2 - s_y**2))

def z_score(stock1, stock2, days):
    # assuming a very high correlation
    # z-score > 2: sell stock1, buy stock2
    # z-score < -2: buy stock1, sell stock2

    days = min(len(stock1), len(stock2), days)

    ratio = stock1[-days-1:]/stock2[-days-1:]
    mu = np.mean(ratio[:-1])
    std = np.std(ratio[:-1])
    if std == 0:
        return 0
    return (ratio[-1]-mu)/std

def z_score_info(stock1, stock2, days):
    days = max(len(stock1), len(stock2), days)

    current = z_score(stock1, stock2, days)
    n = 1
    if np.abs(current) > 0.5:
        while np.abs(z_score(stock1[:-n], stock2[:-n], days)) > 0.5:
            n += 1
            if n > 14:
                return current, 1, 0, 0
    ratio = stock1[-1]/stock2[-1]
    normal_ratio = stock1[-n]/stock2[-n]

    c = ratio/normal_ratio
    root = np.sqrt(c)
    s1_gain = 1/root-1
    s2_gain = root-1
    return current, n, s1_gain, s2_gain

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

        self.history = np.array(hist[-days:])
        if self.history.size < 180:
            return 'not enough data'
        self.price = self.history[-1]
        if self.price < 5:
            return 'penny stock'
        return 0

# No correlation is between -0.3 and 0.3, no stock is cheaper than $5
tickers = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSM', 'BRK-B', 'LLY', 'AVGO', 'TSLA', 'NVO', 'JPM', 'WMT', 'V', 'XOM', 'UNH', 'ASML', 'MA',
           'ORCL', 'PG', 'COST', 'JNJ', 'HD', 'BAC', 'MRK', 'ABBV', 'AMD', 'CVX', 'NFLX', 'TM', 'KO', 'ADBE', 'CRM', 'AZN', 'SAP', 'SHEL', 'NVS', 'QCOM', 'PEP', 'TMUS', 'LIN', 'WFC', 'TMO', 'FMX', 'AMAT', 'PDD', 'ACN', 'CSCO', 'ARM', 'MCD', 'TXN', 'DHR', 'ABT', 'GE', 'INTU', 'DIS', 'AMGN', 'VZ', 'AXP', 'MS', 'IBM', 'PFE', 'CAT', 'PM', 'HSBC', 'ISRG', 'TTE', 'RY', 'GS', 'NOW', 'NEE', 'BX', 'UBER', 'CMCSA', 'SPGI', 'BHP', 'MU', 'INTC', 'UL', 'LRCX', 'HON', 'UNP', 'SCHW', 'RTX', 'T', 'BKNG', 'COP', 'ETN', 'LOW', 'MUFG', 'SYK', 'TJX', 'SNY', 'VRTX', 'C', 'ELV', 'PGR', 'BLK', 'BUD', 'REGN', 'UPS', 'ADI', 'SONY', 'KLAC', 'BSX', 'BA', 'ANET', 'PLD', 'NKE', 'RIO', 'LMT', 'PANW', 'TOELY', 'MMC', 'IBN', 'CB', 'KKR', 'MDT', 'DELL', 'DE', 'UBS', 'TD', 'PBR', 'ADP', 'BP', 'AMT', 'ABNB', 'CI', 'SNPS', 'CFRUY', 'CRWD', 'SCCO', 'FI', 'MDLZ', 'MELI', 'SO', 'GILD', 'CDNS', 'RELX', 'WM', 'ICE', 'INFY', 'SHOP', 'APH', 'BMY', 'SHECY', 'HCA', 'SBUX', 'ZTS', 'MO', 'DUK', 'MCO', 'CL', 'GSK', 'CMG', 'SHW', 'GD', 'TT', 'CNQ', 'RACE', 'CP', 'ENB', 'EQIX', 'CNI', 'EQNR', 'TRI', 'GLNCY', 'MCK', 'MBGYY', 'FDX', 'FCX', 'EOG', 'DEO', 'CTAS', 'CVS', 'ITW', 'BTI', 'NXPI', 'CME', 'TDG', 'TGT', 'ECL', 'BN', 'MAR', 'APO', 'PH', 'CEG', 'PNC', 'SLB', 'CSX', 'USB', 'BDX', 'MSI', 'EMR', 'AON', 'NOC', 'NU', 'EPD', 'MRVL', 'RSG', 'BMO', 'PYPL', 'WELL', 'PLTR', 'BBVA', 'ORLY', 'ITUB', 'WDAY', 'SPOT', 'NGG', 'CARR', 'ROP', 'STLA', 'ING', 'AJG', 'MPC', 'APD', 'BNS', 'MMM', 'PSX', 'AMX', 'EW', 'SPG', 'ET', 'HLT', 'GM', 'PCAR', 'OXY', 'CRH', 'ADSK', 'NEM', 'COIN', 'TFC', 'F', 'COF', 'DLR', 'CPRT', 'PSA', 'SMCI', 'AFL', 'WMB', 'HMC', 'MET', 'IBKR', 'AIG', 'BAESY', 'ROST', 'MCHP', 'MNST', 'NSC', 'AZO', 'MFC', 'DHI', 'E', 'VALE', 'SU', 'SRE', 'OKE', 'TTD', 'VLO', 'O', 'TRV', 'AEP', 'TEL', 'KMB', 'STZ', 'JCI', 'MRNA', 'PCG', 'TEAM', 'SNOW', 'WCN', 'CM', 'HUM', 'BK', 'HES', 'FTNT', 'DSCSY', 'DXCM', 'URI', 'GWW', 'KMI', 'ALC', 'CCI', 'ARES', 'KDP', 'LHX', 'AMP', 'PRU', 'COR', 'DASH', 'CHTR', 'D', 'DDOG', 'MPLX', 'TAK', 'SE', 'ALL', 'BCS', 'DKILY', 'PAYX', 'CODYY', 'FIS', 'LEN', 'RCL', 'MPWR', 'SQ', 'ODFL', 'LNG', 'IDXX', 'TRP', 'OTIS', 'HLN', 'IQV', 'FERG', 'VRSK', 'AME', 'MSCI', 'IR', 'KHC', 'EA', 'BSBR', 'GLW', 'PWR', 'CPNG', 'CMI', 'FICO', 'PEG', 'STM', 'KR', 'A', 'NUE', 'HSY', 'PPERY', 'WDS', 'AEM', 'IMO', 'DOW', 'CVE', 'FAST', 'YUM', 'EL', 'FANG', 'ACGL', 'CTVA', 'GEHC', 'LULU', 'NDAQ', 'CNC', 'FLUT', 'HPQ', 'SYY', 'NWG', 'GIS', 'EXC', 'VRT', 'EXR', 'CTSH', 'IT', 'BIIB', 'BKR', 'WIT', 'MLM', 'CCEP', 'KVUE', 'DD', 'XYL', 'VMC', 'ALNY', 'DB', 'DFS', 'HWM', 'TCOM', 'ON', 'QSR', 'GRMN', 'ADM', 'VST', 'GOLD', 'ED', 'LVS', 'ROK', 'EFX', 'LYB', 'ATEYY', 'CSGP', 'PPG', 'VICI', 'VEEV', 'XEL', 'CDW', 'HIG', 'ZS', 'SVNDY', 'BCE', 'GFS', 'HAL', 'TRGP', 'FUJIY', 'AVB', 'RMD', 'PINS', 'DG', 'SLF', 'MTD', 'DVN', 'DAL', 'WAB', 'ANSS', 'ORAN', 'EIX', 'CBRE', 'TSCO', 'CHT', 'NET', 'IRM', 'RKT', 'ARGX', 'ICLR', 'RYAAY', 'SNAP', 'HEI', 'HPE', 'NTAP', 'ASX', 'EBAY', 'APP', 'FRFHF', 'WTW', 'WPM', 'CCL', 'AWK', 'TTWO', 'PUK', 'FTV', 'IX', 'TROW', 'BRO', 'EQR', 'FITB', 'CHD', 'MTB', 'WDC', 'TECK', 'WEC', 'OWL', 'FCNCA', 'DOV', 'PHG', 'NVR', 'HUBS', 'IFF', 'RBLX', 'CQP', 'FSLR', 'RJF', 'GPN', 'FNV', 'VOD', 'KEYS', 'TER', 'NTR', 'WST', 'ROL', 'BR', 'VLTO', 'MSTR', 'PHM', 'GIB', 'CCJ', 'KB', 'DTE', 'ETR', 'DLTR', 'CAH', 'STT', 'EC', 'TU', 'TW', 'FE', 'LI', 'DECK', 'ZBH', 'SBAC', 'STX', 'AXON', 'SYM', 'LYV', 'MBLY', 'INVH', 'SMPNY', 'PBA', 'TYL', 'ARE', 'STE', 'ENTG', 'PKX', 'VTR', 'PTC', 'PSTG', 'ERIC', 'ES', 'WY', 'PPL', 'UMC', 'CUK', 'BF-B', 'BNTX', 'MKL', 'HUBB', 'CSL', 'STLD', 'BAH', 'TSN', 'IOT', 'GDDY', 'WRB', 'LDOS', 'CTRA', 'LII', 'LPLA', 'RCI', 'HOOD', 'FTS', 'WSO', 'SYF', 'AEE', 'PFG', 'K', 'APTV', 'TLK', 'CPAY', 'WSM', 'ALGN', 'HDELY', 'CHKP', 'SHG', 'HBAN', 'CNP', 'ULTA', 'MKC', 'ERIE', 'CINF', 'BEKE', 'GPC', 'RF', 'ILMN', 'AER', 'BALL', 'TDY', 'ESS', 'BBY', 'WLK', 'MDB', 'CRBG', 'MT', 'TPL', 'CMS', 'ATO', 'KOF', 'OMC', 'BAX', 'WBD', 'WAT', 'HOLX', 'CBOE', 'NTRS', 'DKNG', 'NMR', 'EME', 'BLDR', 'SWKS', 'BEP', 'VRSN', 'J', 'ZM', 'AVY', 'COO', 'IHG', 'EXPD', 'CFG', 'LH', 'TS', 'MAA', 'EXPE', 'ZBRA', 'HRL', 'L', 'MOH', 'JBHT', 'DKS', 'TXT', 'CLX', 'RS', 'DRI', 'DPZ', 'RIVN', 'GMAB', 'NRG', 'EG', 'ZTO', 'PKG', 'EQT', 'BGNE', 'LUV', 'EBR', 'NWSA', 'FOXA', 'SUI', 'RPRX', 'FDS', 'BMRN', 'MRO', 'BURL', 'BG', 'DGX', 'OKTA', 'BAM', 'WMG', 'GEN', 'TPG', 'RTO', 'SSNC', 'AMH', 'WES', 'H', 'UDR', 'IEX', 'CVNA', 'CG', 'MAS', 'TRU', 'MANH', 'OC', 'CE', 'ENPH', 'UAL', 'IP', 'VIV', 'NBIX', 'RYAN', 'BSY', 'AVTR', 'GFI', 'UTHR', 'GFL', 'RBA', 'DOC', 'AKAM', 'MGM', 'PODD', 'SRPT', 'NTNX', 'LOGI', 'KEY', 'AMCR', 'SNA', 'RPM', 'FNF', 'RGA', 'JHX', 'NTRA', 'TRMB', 'AGR', 'LNT', 'BIP', 'GGG', 'KIM', 'PR', 'EQH', 'CPB', 'RVTY', 'NDSN', 'CASY', 'BLD', 'CAG', 'TOST', 'BAP', 'NI', 'MEDP', 'SWK', 'CELH', 'AES', 'VTRS', 'NVT', 'DT', 'THC', 'JBL', 'PNR', 'ARCC', 'ELS', 'PAA', 'BOUYY', 'EDU', 'CF', 'ALLY', 'WPC', 'TFII', 'MORN', 'OVV', 'HST', 'GLPI', 'CNA', 'MGA', 'AOS', 'USFD', 'EVRG', 'SUZ', 'CNH', 'WMS', 'KMX', 'SNN', 'INSM', 'YUMC', 'INCY', 'BCH', 'DVA', 'UHS', 'TOL', 'XPO', 'AU', 'LAMR', 'CLH', 'ESTC', 'RKUNY', 'BEN', 'POOL', 'FLEX', 'AZPN', 'JNPR', 'SQM', 'SAIA', 'BJ', 'JKHY', 'TECH', 'SJM', 'VIVHY', 'UWMC', 'REG', 'CPT', 'ACM', 'ONON', 'QRVO', 'UHAL', 'CYBR', 'MNDY', 'COHR', 'FMS', 'RNR', 'ZI', 'EMN', 'ELF', 'FTI', 'ZG', 'ALB', 'CHWY', 'RL', 'BXP', 'GWRE', 'LKQ', 'ONTO', 'FIX', 'ACI', 'LW', 'WING', 'YPF', 'AEG', 'KGC', 'TXRH', 'LECO', 'DOCU', 'APA', 'IPG', 'EPAM', 'NICE', 'CHK', 'ITT', 'REXR', 'WTRG', 'JEF', 'TTEK', 'GME', 'CW', 'CRL', 'TAP', 'WWD', 'SBS', 'CHRD', 'OLED', 'ALLE', 'TFX', 'AMKR', 'EWBC', 'AFG', 'CTLT', 'BIRK', 'APG', 'CUBE', 'WPP', 'SCI', 'SKX', 'CHDN', 'FND', 'SN', 'CNM', 'JLL', 'CHRW', 'FFIV', 'PAG', 'CX', 'HTHT', 'AR', 'TPR', 'XP', 'NLY', 'HII', 'PFGC', 'WBA', 'FTAI', 'CAVA', 'UI', 'MUSA', 'STN', 'TWLO', 'UNM', 'SNX', 'BRKR', 'CACI', 'BPYPP', 'BSAC', 'MMYT', 'LNW', 'GMED', 'HLI', 'MKSI', 'WYNN', 'FUTU', 'COKE', 'TTC', 'PCOR', 'ATR', 'KEP', 'RRX', 'ASR', 'DINO', 'DOX', 'QGEN', 'WIX', 'PNW', 'WFRD', 'AFRM', 'APPF', 'GPS', 'CART', 'PCVX', 'ANF', 'CCK', 'LEGN', 'FHN', 'MOS', 'BWXT', 'RGLD', 'TKO', 'FN', 'PPC', 'GNRC', 'KNSL', 'HESM', 'ROKU', 'FRT', 'SEIC', 'CGNX', 'EGP', 'YMM', 'OHI', 'ALV', 'X', 'PAAS', 'PSO', 'EVR', 'DCI', 'KBR', 'NYT', 'COTY', 'ARMK', 'SF', 'CROX', 'AIZ', 'FBIN', 'DSGX', 'EHC', 'LNTH', 'BZ', 'TPX', 'ROIV', 'INFA', 'ORI', 'TREX', 'CZR', 'OTEX', 'PSN', 'WCC', 'BIO', 'RBC', 'MTCH', 'ITCI', 'ESLT', 'EXAS', 'CR', 'HSIC', 'BBWI', 'PAYC', 'EDR', 'DUOL', 'MTSI', 'ALTR', 'SFM', 'MTZ', 'XPEV', 'GPK', 'LSCC', 'CIB', 'GTLB', 'WF', 'PRI', 'SKM', 'RRC', 'PARA', 'PAC', 'GLOB', 'HAS', 'MKTX', 'NNN', 'CHE', 'DAY', 'CFLT', 'KNX', 'NCLH', 'IEP', 'FLR', 'GNTX', 'WBS', 'GL', 'ASND', 'FCN', 'AXTA', 'COLD', 'VIPS', 'PCTY', 'LBRDA', 'MHK', 'DLB', 'SWN', 'WEX', 'EXP', 'LEVI', 'MTDR', 'SUN', 'ENSG', 'CLF', 'INGR', 'MSA', 'DDS', 'AYI', 'CERE', 'BWA', 'TIMB', 'HLNE', 'CBSH', 'BPMC', 'LSXMA', 'NXT', 'SSD', 'HRB', 'AGNC', 'AIT', 'TX', 'CMA', 'PHYS', 'OGE', 'TKC', 'WAL', 'AAON', 'ATI', 'BRBR', 'VOYA', 'NOV', 'CRUS', 'WSC', 'SOFI', 'AGCO', 'IVZ', 'SPSC', 'PEN', 'FSV', 'UFPI', 'DBX', 'PATH', 'KEX']
tickers.append('')

def tangency(tickers):
    size = len(tickers)
    stocks = []
    print(size)
    for i in range(size):
        print(f'{i+1}/{size}: ')
        stock = Stock(tickers[i])
        exception = stock.update()
        if exception != 0:
            print(exception)
        else:
            stocks.append(stock)
        print('')
    size = len(stocks)
    tickers = [stock.ticker for stock in stocks]

    print(tickers)

    corr_matrix = np.zeros((size,size))
    cov_matrix = np.zeros((size,size))
    z_matrix = np.zeros((size,size))
    z_info_matrix = np.zeros((size,size), dtype=tuple)

    for i in range(size):
        print(i)
        print(stocks[i].ticker)
        print('\n')
        for j in range(i,size):
            corr = correlation(stocks[i].history, stocks[j].history, 180)
            cov = covariance(stocks[i].history, stocks[j].history, 180)
            z = z_score_info(stocks[i].history, stocks[j].history, 50)

            z_info_matrix[i][j] = (z[1], z[2], z[3])
            z_info_matrix[j][i] = (z[1], z[3], z[2])

            if np.abs(z[0]) >= 2:
                z_matrix[i][j] = z[0]
                z_matrix[j][i] = -z[0]

            corr_matrix[i][j] = corr
            cov_matrix[i][j] = cov

            corr_matrix[j][i] = corr
            cov_matrix[j][i] = cov

    returns = np.zeros(size)
    for i in range(size):
        returns[i] = round(stocks[i].info['dividendYield'], 4)

    print(dict(zip(tickers, returns)))

    A = np.block([[2*cov_matrix, -returns.reshape((size,1)), -np.ones((size,1))],
                  [returns.reshape((1,size)), 0, 0],
                  [np.ones((1,size)), 0, 0]])

    risk_free = 0.04495  # US 1-year treasury
    portfolio = None
    portfolio_risk = 0
    portfolio_return = 0
    max_k = 0
    markowitz_risk = []
    markowitz_return = []
    for mu in np.linspace(returns.min(), returns.max(), 100):
        b = np.zeros(size+2)
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
    return tickers, portfolio, portfolio_risk, portfolio_return, markowitz_risk, markowitz_return
