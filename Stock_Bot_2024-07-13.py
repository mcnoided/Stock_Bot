from  matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
import time
import os

def covariance(stock1, stock2, days):
    stock1_p = stock1[-days:]
    stock2_p = stock2[-days:]

    stock1_r = stock1_p[1:] - stock1_p[:-1]
    stock2_r = stock2_p[1:] - stock2_p[:-1]

    mu1 = np.mean(stock1_r)
    mu2 = np.mean(stock2_r)

    return np.dot(stock1_r-mu1, stock2_r-mu2)/(days-1)

def correlation(stock1, stock2, days):
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

    ratio = stock1[-days-1:]/stock2[-days-1:]
    mu = np.mean(ratio[:-1])
    std = np.std(ratio[:-1])
    if std == 0:
        return 0
    return (ratio[-1]-mu)/std

def z_score_info(stock1, stock2, days):
    current = z_score(stock1, stock2, days)
    n = 1
    if np.abs(current) > 0.5:
        while np.abs(z_score(stock1[:-n], stock2[:-n], days)) > 0.5:
            n += 1
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
        try:
            ticker = yf.Ticker(self.ticker)
        except:
            return 'ticker not found'
        self.info = ticker.info
        self.marketcap = self.info['marketCap']
        clear = True
        period = '1d'
        try:
            old_hist = pd.read_csv('stocks/'+self.ticker+'.txt', header=None, index_col=None)
            last_date = old_hist.iloc[-1][0]
        except:
            clear = False
            period = '1y'
            print(f'{self.ticker} not found. Creating file')
        else:
            print(f'{self.ticker}')

        try:
            hist = ticker.history(period=period).loc[:,'Close']
        except:
            return 'no data'

        if clear == True:
            try:
                index = hist.index.get_loc(last_date)
                hist = hist.iloc[index+1:]
            except:
                return 'delisted'

        hist.to_csv('stocks/'+self.ticker+'.txt', mode='a', header=False)
        try:
            self.data = pd.read_csv('stocks/'+self.ticker+'.txt', header=None, index_col=None)
        except:
            return 'no csv'
        updated_hist = self.data[1].tolist()
        self.history = np.array(updated_hist[-days:])
        if self.history.size < days:
            return 'not enough data'
        self.price = self.history[-1]
        if self.price < 5:
            return 'penny stock'
        return 0

# No correlation is between -0.3 and 0.3, no stock is cheaper than $5
tickers = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSM', 'BRK-B', 'LLY', 'AVGO', 'TSLA', 'NVO', 'JPM', 'WMT', 'V', 'XOM', 'UNH', 'ASML', 'MA',
           'ORCL', 'PG', 'COST', 'JNJ', 'HD', 'BAC', 'MRK', 'ABBV', 'AMD', 'CVX', 'NFLX', 'TM', 'KO', 'ADBE', 'CRM', 'AZN', 'SAP', 'SHEL', 'NVS', 'QCOM', 'PEP', 'TMUS', 'LIN', 'WFC', 'TMO', 'FMX', 'AMAT', 'PDD', 'ACN', 'CSCO', 'ARM', 'MCD', 'TXN', 'DHR', 'ABT', 'GE', 'INTU', 'DIS', 'AMGN', 'VZ', 'AXP', 'MS', 'IBM', 'PFE', 'CAT', 'PM', 'HSBC', 'ISRG', 'TTE', 'RY', 'GS', 'NOW', 'NEE', 'BX', 'UBER', 'CMCSA', 'SPGI', 'BHP', 'MU', 'INTC', 'UL', 'LRCX', 'HON', 'UNP', 'SCHW', 'RTX', 'T', 'BKNG', 'COP', 'ETN', 'LOW', 'MUFG', 'SYK', 'TJX', 'SNY', 'VRTX', 'C', 'ELV', 'PGR', 'BLK', 'BUD', 'REGN', 'UPS', 'ADI', 'SONY', 'KLAC', 'BSX', 'BA', 'ANET', 'PLD', 'NKE', 'RIO', 'LMT', 'PANW', 'TOELY', 'MMC', 'IBN', 'CB', 'KKR', 'MDT', 'DELL', 'DE', 'UBS', 'TD', 'PBR', 'ADP', 'BP', 'AMT', 'ABNB', 'CI', 'SNPS', 'CFRUY', 'CRWD', 'SCCO', 'FI', 'MDLZ', 'MELI', 'SO', 'GILD', 'CDNS', 'RELX', 'WM', 'ICE', 'INFY', 'SHOP', 'APH', 'BMY', 'SHECY', 'HCA', 'SBUX', 'ZTS', 'MO', 'DUK', 'MCO', 'CL', 'GSK', 'CMG', 'SHW', 'GD', 'TT', 'CNQ', 'RACE', 'CP', 'ENB', 'EQIX', 'CNI', 'EQNR', 'TRI', 'GLNCY', 'MCK', 'MBGYY', 'FDX', 'FCX', 'EOG', 'DEO', 'CTAS', 'CVS', 'ITW', 'BTI', 'NXPI', 'CME', 'TDG', 'TGT', 'ECL', 'BN', 'MAR', 'APO', 'PH', 'CEG', 'PNC', 'SLB', 'CSX', 'USB', 'BDX', 'MSI', 'EMR', 'AON', 'NOC', 'NU', 'EPD', 'MRVL', 'RSG', 'BMO', 'PYPL', 'WELL', 'PLTR', 'BBVA', 'ORLY', 'ITUB', 'WDAY', 'SPOT', 'NGG', 'CARR', 'ROP', 'STLA', 'ING', 'AJG', 'MPC', 'APD', 'BNS', 'MMM', 'PSX', 'AMX', 'EW', 'SPG', 'ET', 'HLT', 'GM', 'PCAR', 'OXY', 'CRH', 'ADSK', 'NEM', 'COIN', 'TFC', 'F', 'COF', 'DLR', 'CPRT', 'PSA', 'SMCI', 'AFL', 'WMB', 'HMC', 'MET', 'IBKR', 'AIG', 'BAESY', 'ROST', 'MCHP', 'MNST', 'NSC', 'AZO', 'MFC', 'DHI', 'E', 'VALE', 'SU', 'SRE', 'OKE', 'TTD', 'VLO', 'O', 'TRV', 'AEP', 'TEL', 'KMB', 'STZ', 'JCI', 'MRNA', 'PCG', 'TEAM', 'SNOW', 'WCN', 'CM', 'HUM', 'BK', 'HES', 'FTNT', 'DSCSY', 'DXCM', 'URI', 'GWW', 'KMI', 'ALC', 'CCI', 'ARES', 'KDP', 'LHX', 'AMP', 'PRU', 'COR', 'DASH', 'CHTR', 'D', 'DDOG', 'MPLX', 'TAK', 'SE', 'ALL', 'BCS', 'DKILY', 'PAYX', 'CODYY', 'FIS', 'LEN', 'RCL', 'MPWR', 'SQ', 'ODFL', 'LNG', 'IDXX', 'TRP', 'OTIS', 'HLN', 'IQV', 'FERG', 'VRSK', 'AME', 'MSCI', 'IR', 'KHC', 'EA', 'BSBR', 'GLW', 'PWR', 'CPNG', 'CMI', 'FICO', 'PEG', 'STM', 'KR', 'A', 'NUE', 'HSY', 'PPERY', 'WDS', 'AEM', 'IMO', 'DOW', 'CVE', 'FAST', 'YUM', 'EL', 'FANG', 'ACGL', 'CTVA', 'GEHC', 'LULU', 'NDAQ', 'CNC', 'FLUT', 'HPQ', 'SYY', 'NWG', 'GIS', 'EXC', 'VRT', 'EXR', 'CTSH', 'IT', 'BIIB', 'BKR', 'WIT', 'MLM', 'CCEP', 'KVUE', 'DD', 'XYL', 'VMC', 'ALNY', 'DB', 'DFS', 'HWM', 'TCOM', 'ON', 'QSR', 'GRMN', 'ADM', 'VST', 'GOLD', 'ED', 'LVS', 'ROK', 'EFX', 'LYB', 'ATEYY', 'CSGP', 'PPG', 'VICI', 'VEEV', 'XEL', 'CDW', 'HIG', 'ZS', 'SVNDY', 'BCE', 'GFS', 'HAL', 'TRGP', 'FUJIY', 'AVB', 'RMD', 'PINS', 'DG', 'SLF', 'MTD', 'DVN', 'DAL', 'WAB', 'ANSS', 'ORAN', 'EIX', 'CBRE', 'TSCO', 'CHT', 'NET', 'IRM', 'RKT', 'ARGX', 'ICLR', 'RYAAY', 'SNAP', 'HEI', 'HPE', 'NTAP', 'ASX', 'EBAY', 'APP', 'FRFHF', 'WTW', 'WPM', 'CCL', 'AWK', 'TTWO', 'PUK', 'FTV', 'IX', 'TROW', 'BRO', 'EQR', 'FITB', 'CHD', 'MTB', 'WDC', 'TECK', 'WEC', 'OWL', 'FCNCA', 'DOV', 'PHG', 'NVR', 'HUBS', 'IFF', 'RBLX', 'CQP', 'FSLR', 'RJF', 'GPN', 'FNV', 'VOD', 'KEYS', 'TER', 'NTR', 'WST', 'ROL', 'BR', 'VLTO', 'MSTR', 'PHM', 'GIB', 'CCJ', 'KB', 'DTE', 'ETR', 'DLTR', 'CAH', 'STT', 'EC', 'TU', 'TW', 'FE', 'LI', 'DECK', 'ZBH', 'SBAC', 'STX', 'AXON', 'SYM', 'LYV', 'MBLY', 'INVH', 'SMPNY', 'PBA', 'TYL', 'ARE', 'STE', 'ENTG', 'PKX', 'VTR', 'PTC', 'PSTG', 'ERIC', 'ES', 'WY', 'PPL', 'UMC', 'CUK', 'BF-B', 'BNTX', 'MKL', 'HUBB', 'CSL', 'STLD', 'BAH', 'TSN', 'IOT', 'GDDY', 'WRB', 'LDOS', 'CTRA', 'LII', 'LPLA', 'RCI', 'HOOD', 'FTS', 'WSO', 'SYF', 'AEE', 'PFG', 'K', 'APTV', 'TLK', 'CPAY', 'WSM', 'ALGN', 'HDELY', 'CHKP', 'SHG', 'HBAN', 'CNP', 'ULTA', 'MKC', 'ERIE', 'CINF', 'BEKE', 'GPC', 'RF', 'ILMN', 'AER', 'BALL', 'TDY', 'ESS', 'BBY', 'WLK', 'MDB', 'CRBG', 'MT', 'TPL', 'CMS', 'ATO', 'KOF', 'OMC', 'BAX', 'WBD', 'WAT', 'HOLX', 'CBOE', 'NTRS', 'DKNG', 'NMR', 'EME', 'BLDR', 'SWKS', 'BEP', 'VRSN', 'J', 'ZM', 'AVY', 'COO', 'IHG', 'EXPD', 'CFG', 'LH', 'TS', 'MAA', 'EXPE', 'ZBRA', 'HRL', 'L', 'MOH', 'JBHT', 'DKS', 'TXT', 'CLX', 'RS', 'DRI', 'DPZ', 'RIVN', 'GMAB', 'NRG', 'EG', 'ZTO', 'PKG', 'EQT', 'BGNE', 'LUV', 'EBR', 'NWSA', 'FOXA', 'SUI', 'RPRX', 'FDS', 'BMRN', 'MRO', 'BURL', 'BG', 'DGX', 'OKTA', 'BAM', 'WMG', 'GEN', 'TPG', 'RTO', 'SSNC', 'AMH', 'WES', 'H', 'UDR', 'IEX', 'CVNA', 'CG', 'MAS', 'TRU', 'MANH', 'OC', 'CE', 'ENPH', 'UAL', 'IP', 'VIV', 'NBIX', 'RYAN', 'BSY', 'AVTR', 'GFI', 'UTHR', 'GFL', 'RBA', 'DOC', 'AKAM', 'MGM', 'PODD', 'SRPT', 'NTNX', 'LOGI', 'KEY', 'AMCR', 'SNA', 'RPM', 'FNF', 'RGA', 'JHX', 'NTRA', 'TRMB', 'AGR', 'LNT', 'BIP', 'GGG', 'KIM', 'PR', 'EQH', 'CPB', 'RVTY', 'NDSN', 'CASY', 'BLD', 'CAG', 'TOST', 'BAP', 'NI', 'MEDP', 'SWK', 'CELH', 'AES', 'VTRS', 'NVT', 'DT', 'THC', 'JBL', 'PNR', 'ARCC', 'ELS', 'PAA', 'BOUYY', 'EDU', 'CF', 'ALLY', 'WPC', 'TFII', 'MORN', 'OVV', 'HST', 'GLPI', 'CNA', 'MGA', 'AOS', 'USFD', 'EVRG', 'SUZ', 'CNH', 'WMS', 'KMX', 'SNN', 'INSM', 'YUMC', 'INCY', 'BCH', 'DVA', 'UHS', 'TOL', 'XPO', 'AU', 'LAMR', 'CLH', 'ESTC', 'RKUNY', 'BEN', 'POOL', 'FLEX', 'AZPN', 'JNPR', 'SQM', 'SAIA', 'BJ', 'JKHY', 'TECH', 'SJM', 'VIVHY', 'UWMC', 'REG', 'CPT', 'ACM', 'ONON', 'QRVO', 'UHAL', 'CYBR', 'MNDY', 'COHR', 'FMS', 'RNR', 'ZI', 'EMN', 'ELF', 'FTI', 'ZG', 'ALB', 'CHWY', 'RL', 'BXP', 'GWRE', 'LKQ', 'ONTO', 'FIX', 'ACI', 'LW', 'WING', 'YPF', 'AEG', 'KGC', 'TXRH', 'LECO', 'DOCU', 'APA', 'IPG', 'EPAM', 'NICE', 'CHK', 'ITT', 'REXR', 'WTRG', 'JEF', 'TTEK', 'GME', 'CW', 'CRL', 'TAP', 'WWD', 'SBS', 'CHRD', 'OLED', 'ALLE', 'TFX', 'AMKR', 'EWBC', 'AFG', 'CTLT', 'BIRK', 'APG', 'CUBE', 'WPP', 'SCI', 'SKX', 'CHDN', 'FND', 'SN', 'CNM', 'JLL', 'CHRW', 'FFIV', 'PAG', 'CX', 'HTHT', 'AR', 'TPR', 'XP', 'NLY', 'HII', 'PFGC', 'WBA', 'FTAI', 'CAVA', 'UI', 'MUSA', 'STN', 'TWLO', 'UNM', 'SNX', 'BRKR', 'CACI', 'BPYPP', 'BSAC', 'MMYT', 'LNW', 'GMED', 'HLI', 'MKSI', 'WYNN', 'FUTU', 'COKE', 'TTC', 'PCOR', 'ATR', 'KEP', 'RRX', 'ASR', 'DINO', 'DOX', 'QGEN', 'WIX', 'PNW', 'WFRD', 'AFRM', 'APPF', 'GPS', 'CART', 'PCVX', 'ANF', 'CCK', 'LEGN', 'FHN', 'MOS', 'BWXT', 'RGLD', 'TKO', 'FN', 'PPC', 'GNRC', 'KNSL', 'HESM', 'ROKU', 'FRT', 'SEIC', 'CGNX', 'EGP', 'YMM', 'OHI', 'ALV', 'X', 'PAAS', 'PSO', 'EVR', 'DCI', 'KBR', 'NYT', 'COTY', 'ARMK', 'SF', 'CROX', 'AIZ', 'FBIN', 'DSGX', 'EHC', 'LNTH', 'BZ', 'TPX', 'ROIV', 'INFA', 'ORI', 'TREX', 'CZR', 'OTEX', 'PSN', 'WCC', 'BIO', 'RBC', 'MTCH', 'ITCI', 'ESLT', 'EXAS', 'CR', 'HSIC', 'BBWI', 'PAYC', 'EDR', 'DUOL', 'MTSI', 'ALTR', 'SFM', 'MTZ', 'XPEV', 'GPK', 'LSCC', 'CIB', 'GTLB', 'WF', 'PRI', 'SKM', 'RRC', 'PARA', 'PAC', 'GLOB', 'HAS', 'MKTX', 'NNN', 'CHE', 'DAY', 'CFLT', 'KNX', 'NCLH', 'IEP', 'FLR', 'GNTX', 'WBS', 'GL', 'ASND', 'FCN', 'AXTA', 'COLD', 'VIPS', 'PCTY', 'LBRDA', 'MHK', 'DLB', 'SWN', 'WEX', 'EXP', 'LEVI', 'MTDR', 'SUN', 'ENSG', 'CLF', 'INGR', 'MSA', 'DDS', 'AYI', 'CERE', 'BWA', 'TIMB', 'HLNE', 'CBSH', 'BPMC', 'LSXMA', 'NXT', 'SSD', 'HRB', 'AGNC', 'AIT', 'TX', 'CMA', 'PHYS', 'OGE', 'TKC', 'WAL', 'AAON', 'ATI', 'BRBR', 'VOYA', 'NOV', 'CRUS', 'WSC', 'SOFI', 'AGCO', 'IVZ', 'SPSC', 'PEN', 'FSV', 'UFPI', 'DBX', 'PATH', 'KEX', 'CLS', 'AM', 'VNOM', 'BRX', 'DRS', 'AA', 'FMC', 'RGEN', 'RMBS', 'BROS', 'RVMD', 'SPXC', 'BERY', 'LAD', 'LBTYA', 'AAL', 'OSK', 'ZION', 'STAG', 'IONS', 'AGI', 'GRFS', 'CCCS', 'CIVI', 'DTM', 'CIEN', 'FR', 'NVMI', 'ETSY', 'ELAN', 'ESI', 'MIDD', 'HCP', 'CACC', 'HALO', 'ALSN', 'AN', 'W', 'MLI', 'BPOP', 'ADT', 'HR', 'HQY', 'GKOS', 'LEA', 'MTN', 'FYBR', 'JAZZ', 'SUM', 'EXEL', 'GIL', 'NGKSY', 'IBP', 'CYTK', 'KT', 'BFAM', 'RHI', 'CFR', 'PLNT', 'VKTX', 'NSIT', 'LFUS', 'BNRE', 'ARW', 'TAL', 'U', 'PNFP', 'POST', 'ADC', 'GGAL', 'GTLS', 'STWD', 'LSTR', 'RLI', 'HMY', 'FLS', 'WTFC', 'S', 'KVYO', 'NE', 'WFG', 'CMC', 'AZEK', 'SSB', 'MUR', 'TRNO', 'MTH', 'WTS', 'ENLC', 'CIGI', 'MDGL', 'GLBE', 'TMHC', 'SNV', 'CHX', 'GXO', 'VNT', 'ESNT', 'BECN', 'OLLI', 'ALGM', 'ACHC', 'ST', 'PB', 'PVH', 'FRPT', 'FOUR', 'DAR', 'SMMT', 'OBDC', 'BOKF', 'KD', 'RHP', 'LKNCY', 'SMAR', 'SQSP', 'MNSO', 'CAE', 'LPX', 'CWST', 'RRR', 'AXS', 'JXN', 'MASI', 'MTG', 'NOVT', 'CHH', 'SAIC', 'BXSL', 'WH', 'VNO', 'WHR', 'CAMT', 'OMF', 'VVV', 'TKR', 'FAF', 'PDI', 'ESAB', 'SITE', 'SIGI', 'VERX', 'MAT', 'ONB', 'G', 'MOD', 'BMI', 'NXST', 'FIVE', 'JHG', 'FSK', 'REYN', 'KRYS', 'OLN', 'ETRN', 'MOG-A', 'DJT', 'PHI', 'ELP', 'BEPC', 'BLCO', 'STVN', 'LYFT', 'R', 'VRNS', 'KBH', 'VMI', 'HXL', 'SRCL', 'PUTKY', 'VAL', 'RCM', 'COOP', 'MARA', 'BILL', 'BYD', 'ERJ', 'FSS', 'CADE', 'CVLT', 'M', 'CRS', 'BCPC', 'STEP', 'FG', 'RITM', 'XRAY', 'OGN', 'QLYS', 'MMS', 'LNC', 'AL', 'MGY', 'NSA', 'EXLS', 'FUN', 'AMG', 'SWX', 'PSLV', 'FRO', 'FNB', 'EPRT', 'ZWS', 'VFC', 'CBT', 'SM', 'ATKR', 'MDU', 'TENB', 'KRG', 'AWI', 'BBIO', 'LANC', 'THO', 'NFG', 'TNET', 'SEE', 'CWAN', 'DY', 'BC', 'MMSI', 'GATX', 'TDW', 'SSL', 'NUVL', 'CRDO', 'DOCS', 'SATS', 'CWEN', 'PEGA', 'VRN', 'PFSI', 'HOMB', 'OPCH', 'EXPO', 'AVAV', 'RDN', 'DOOO', 'ACT', 'CRSP', 'OZK', 'CSAN', 'BMA', 'SON', 'RH', 'UGI', 'IDA', 'USM', 'ACLS', 'ABG', 'APLS', 'SEM', 'CEF', 'BCC', 'AVT', 'PBF', 'ITRI', 'ASH', 'RNA', 'VRRM', 'SLM', 'FCFS', 'BIPC', 'TMDX', 'CRC', 'ALK', 'EEFT', 'FIZZ', 'ESGR', 'COLM', 'FORM', 'MSGS', 'SLGN', 'BCO', 'POR', 'IBRX', 'PI', 'BGC', 'UBSI', 'PECO', 'FLO', 'NVEI', 'HOG', 'PAGP', 'FELE', 'CNXC', 'HIMS', 'THG', 'CRVL', 'HAE', 'GBCI', 'ORA', 'RIG', 'TSEM', 'IMVT', 'COLB', 'MAIN', 'PJT', 'BVN', 'AGO', 'URBN', 'FUL', 'FFIN', 'PII', 'MSM', 'NJR', 'CSWI', 'RDNT', 'IRT', 'RYN', 'UMBF', 'HGV', 'AQN', 'HWC', 'JOBY', 'MATX', 'KNF', 'AEIS', 'WU', 'DNB', 'SNDR', 'NXE', 'TIGO', 'LOPE', 'MC', 'GBDC', 'ENS', 'SKY', 'POWI', 'PAGS', 'ACIW', 'IAC', 'STNG', 'NFE', 'GTES', 'DYN', 'AEO', 'ACA', 'CRNX', 'STNE', 'ASGN', 'IGT', 'CPRI', 'KRC', 'INSP', 'ALIT', 'SPR', 'CPA', 'NTCOY', 'SIG', 'IPGP', 'PTEN', 'WK', 'AMR', 'AXSM', 'BLKB', 'RARE', 'AVNT', 'GPI', 'CNX', 'NOG', 'ALKS', 'SLG', 'ITGR', 'OSCR', 'BRZE', 'QTWO', 'GOLF', 'KMPR', 'HUN', 'SANM', 'AB', 'FROG', 'BKH', 'ASO', 'BDC', 'LITE', 'STR', 'BOOT', 'HGTY', 'IPAR', 'SLAB', 'CNS', 'NNI', 'FRSH', 'TPH', 'CLVT', 'VLY', 'MRUS', 'DIOD', 'PRGO', 'CBZ', 'LTH', 'PWSC', 'ZETA', 'CTRE', 'KAI', 'IBOC', 'ABCB', 'LAZ', 'HRI', 'JWN', 'AI', 'TGS', 'BOX', 'ALE', 'GH', 'NCNO', 'OGS', 'SMPL', 'INST', 'TEX', 'HL', 'TFSL', 'SHAK', 'CAR', 'AAP', 'OTTR', 'SFBS', 'SBRA', 'KTB', 'MHO', 'CUZ', 'HP', 'STRL', 'HBM', 'HASI', 'CC', 'PIPR', 'GLNG', 'SHC', 'SR', 'SMG', 'SDRL', 'NEOG', 'OMAB', 'SYNA', 'HCC', 'QS', 'VIRT', 'ARWR', 'PRKS', 'WHD', 'MAC', 'PRCT', 'TRMD', 'AX', 'PBH', 'AXNX', 'SITM', 'HHH', 'APLE', 'NEA', 'CLSK', 'PNM', 'LBRT', 'DXC', 'KFY', 'RUSHA', 'SAM', 'DV', 'HTGC', 'WEN', 'RUN', 'SRAD', 'ENV', 'ATHM', 'EGO', 'BHVN', 'PRMW', 'NSP', 'MEOH', 'WD', 'GMS', 'TGTX', 'PAM', 'SKYW', 'YETI', 'ALRM', 'TNL', 'TEO', 'DNLI', 'BSM', 'SXT', 'MAN', 'BNL', 'AROC', 'BXMT', 'TDC', 'CXT', 'JOE', 'IIPR', 'GT', 'VCTR', 'ASB', 'GFF', 'SHOO', 'GHC', 'EPR', 'AMED', 'CORT', 'FLNC', 'NPO', 'ARLP', 'ACLX', 'SGRY', 'JJSF', 'TFPM', 'UNF', 'ABM', 'AUB', 'RXO', 'SITC', 'AESI', 'UCBI', 'QFIN', 'EURN', 'FULT', 'NARI', 'VSH', 'IRDM', 'ICUI', 'FOLD', 'PENN', 'NHI', 'KTOS', 'PCH', 'FBP', 'NWE', 'KWR', 'CNO', 'SWTX', 'ASAN', 'ASTS', 'GBTG', 'XENE', 'IOSP', 'TWST', 'CALM', 'DNP', 'IDCC', 'IRTC', 'BRC', 'HCM', 'IESC', 'WDFC', 'FIBK', 'VAC', 'WOLF', 'CCOI', 'CRK', 'OR', 'FIVN', 'IDYA', 'GDRX', 'CVCO', 'BANF', 'UAA', 'VC', 'HI', 'BUR', 'PK', 'TCBI', 'DOCN', 'MCY', 'HIW', 'SKT', 'PLXS', 'CDP', 'CWT', 'BE', 'JBT', 'ENVX', 'ALKT', 'MWA', 'BL', 'SEB', 'MLCO', 'TNDM', 'ESE', 'LRN', 'REZI', 'ACAD', 'BHF', 'CEIX', 'GEF', 'ROAD', 'EAT', 'WSFS', 'ABR', 'LXP', 'APAM', 'ESRT', 'ADMA', 'KLIC', 'NVST', 'ARCH', 'PLTK', 'MANU', 'CATY', 'AGYS', 'AWR', 'MLTX', 'BTU', 'AZTA', 'NMIH', 'ZGN', 'IIJIY', 'ACVA', 'FHI', 'MGEE', 'GPOR', 'DEI', 'FHB', 'BAK', 'RYTM', 'CAAP', 'VTMX', 'USAC', 'ASAI', 'DORM', 'YOU', 'CSQ', 'MORF', 'INSW', 'AVA', 'MOR', 'NAD', 'MQ', 'INTR', 'GVA', 'CSTM', 'ADX', 'HAYW', 'CCS', 'NABL', 'SG', 'BHC', 'LIVN', 'GRBK', 'PRIM', 'SLVM', 'STRA', 'BBAR', 'NOMD', 'IFS', 'GTBIF', 'SBLK', 'MTX', 'AIN', 'HUBG', 'SIMO', 'RIOT', 'FTDR', 'CBU', 'XPRO', 'VECO', 'NMRK', 'PGNY', 'NVG', 'UEC', 'GNW', 'CDE', 'MODG', 'MGRC', 'RNG', 'CARG', 'CNK', 'PRFT', 'CWK', 'EXG', 'LCII', 'KOS', 'GOGL', 'TROX', 'ESBA', 'ATAT', 'EBC', 'ATGE', 'AIR', 'INTA', 'AGIO', 'BATRA', 'ARCB', 'AMK', 'MIR', 'NEP', 'CLDX', 'AY', 'OUT', 'APGE', 'PTCT', 'WNS', 'RKLB', 'PATK', 'KNTK', 'DBRG', 'TGLS', 'AMBA', 'BWIN', 'AVDX', 'OII', 'DFH', 'RPD', 'WLY', 'KSS', 'ENOV', 'TRIP', 'RELY', 'TGNA', 'AGL', 'NWL', 'CVBF', 'ICFI', 'SNEX', 'CVI', 'PRK', 'WAFD', 'JPC', 'CXM', 'UCTT', 'MP', 'CPK', 'OSIS', 'ATMU', 'TRN', 'NZF', 'NTLA', 'PAY', 'UE', 'PSMT', 'YELP', 'MYRG', 'GPCR', 'FCPT', 'CERT', 'LION', 'IART', 'CLBT', 'TDS', 'VCEL', 'BOH', 'KYMR', 'PPBI', 'APPN', 'SFNC', 'BKU', 'UFPT', 'MYGN', 'SMTC', 'DLO', 'PSEC', 'BWLP', 'SPB', 'PRGS', 'LAUR', 'STAA', 'FL', 'EQX', 'LGIH', 'IOVA', 'WOR', 'ROG', 'UPST', 'AZZ', 'FA', 'UTG', 'CENT', 'EVH', 'MTRN', 'BFH', 'GDS', 'ODD', 'KGS', 'UTF', 'CRTO', 'WERN', 'ERO', 'CCU', 'GSHD', 'CMPR', 'BANC', 'CRI', 'ETY', 'ARHS', 'JAMF', 'RNW', 'CALX', 'MCW', 'HNI', 'JANX', 'FFBC', 'INDB', 'TNK', 'FTRE', 'AMRX', 'PTY', 'PYCR', 'ADUS', 'TAC', 'TBBK', 'CRGY', 'ROCK', 'VSTO', 'ZD', 'SBCF', 'VZIO', 'MRVI', 'ZIM', 'ADNT', 'TALO', 'SHO', 'BEAM', 'SPNT', 'PRVA', 'TTMI', 'GRND', 'GO', 'TR', 'IREN', 'USLM', 'AKR', 'ENR', 'B', 'EPAC', 'PDCO', 'PTGX', 'EWTX', 'CNMD', 'RAMP', 'DRVN', 'LFST', 'PTVE', 'BOWL', 'PLMR', 'LSPD', 'VERA', 'GDV', 'HTH', 'FLYW', 'QDEL', 'RCKT', 'NXRT', 'EQC', 'EVCM', 'PFS', 'VYX', 'GEO', 'EVTC', 'LGF-A', 'ALG', 'ARCO', 'RXRX', 'SXI', 'FRME', 'EE', 'PLUS', 'TFIN', 'GTX', 'TXG', 'HTLF', 'AGM', 'TSLX', 'SPNS', 'IBTX', 'HWKN', 'NEXT', 'YY', 'ASTH', 'NATL', 'MBIN', 'SNDX', 'RXST', 'FIHL', 'GOF', 'HPK', 'NSSC', 'PD', 'EPC', 'ARVN', 'PAYO', 'USA', 'BKE', 'FOXF', 'CEPU', 'SWI', 'RSI', 'THS', 'PINC', 'SEMR', 'IMCR', 'PAX', 'VRNT', 'SPT', 'SCL', 'MGNI', 'FBK', 'ASPN', 'TNC', 'DKL', 'AG', 'MLKN', 'CAKE', 'VEON', 'JBLU', 'VSAT', 'NBTB', 'CPRX', 'PHIN', 'HRMY', 'LMAT', 'LILA', 'TRMK', 'MBC', 'CABO', 'SVV', 'AVPT', 'GCMG', 'NVCR', 'AMPH', 'JBI', 'NVAX', 'KMT', 'STGW', 'NAMS', 'EXPI', 'AMN', 'STC', 'WRBY', 'MXL', 'NHC', 'SAH', 'VITL', 'CMRE', 'SJW', 'KAR', 'NEO', 'MRCY', 'SONO', 'OFG', 'NMRA', 'HLX', 'ECAT', 'CLM', 'SFL', 'RNST', 'NUV', 'BCAT', 'KYN', 'BANR', 'GLPG', 'TCNNF', 'HURN', 'ENVA', 'AAT', 'HLMN', 'SOUN', 'EXTR', 'WMK', 'VET', 'ZLAB', 'DFIN', 'EVT', 'LGND', 'MIRM', 'DRH', 'KRP', 'GSBD', 'WSBC', 'LPG', 'CENX', 'CUBI', 'GNL', 'VCYT', 'DHT', 'DAN', 'COCO', 'DAC', 'GEL', 'MSGE', 'IVT', 'POWL', 'TIXT', 'DAVA', 'AKRO', 'SAND', 'OI', 'CODI', 'COHU', 'UPBD', 'NAC', 'VGR', 'DNUT', 'NTB', 'HEES', 'MLNK', 'VRNA', 'RVT', 'CNXN', 'IONQ', 'KROS', 'FOR', 'VRTS', 'SLNO', 'BMEZ', 'KURA', 'BIGZ', 'VSEC', 'SEDG', 'LZB', 'NAVI', 'CLBK', 'OSW', 'ANDE', 'TY', 'KN', 'PLAB', 'LOB', 'CARCY', 'BORR', 'FSM', 'ROIC', 'VTLE', 'ALHC', 'PWP', 'MGPI', 'CHCO', 'BMBL', 'RQI', 'BBUC', 'AMRC', 'PAR', 'LEG', 'VSTS', 'VIAV', 'GAB', 'ETV', 'THRM', 'PEB', 'TDOC', 'DO', 'BLBD', 'VRE', 'CHEF', 'RUM', 'VSCO', 'NGVT', 'ARRY', 'AFYA', 'CTS', 'AHL-PC', 'EFSC', 'AVDL', 'ARLO', 'HOLI', 'NBHC', 'VVX', 'OXM', 'VICR', 'KNSA', 'WT', 'LKFN', 'SUPN', 'NMM', 'AMC', 'BSTZ', 'SDGR', 'NVEE', 'IAS', 'WGO', 'BDJ', 'WKC', 'LBPH', 'RC', 'LTC', 'SYBT', 'NWBI', 'HPH', 'XHR', 'GTY', 'MNKD', 'FCF', 'ATEC', 'PLAY', 'SPHR', 'OCSL', 'HPP', 'BCYC', 'DBD', 'CGAU', 'RLJ', 'SGH', 'SCS', 'PDO', 'BLMN', 'OXLC', 'CASH', 'LVWR', 'STER', 'LADR', 'INDV', 'KRO', 'ARI', 'BBU', 'BLTE', 'GLP', 'KALU', 'SAFE', 'ACMR', 'UPWK', 'SKWD', 'ETG', 'HLIO', 'CXW', 'BCRX', 'INMD', 'SYRE', 'HELE', 'DK', 'DSGR', 'STEW', 'JBGS', 'BHE', 'BTDR', 'CDRE', 'FBNC', 'PRG', 'INFN', 'HIMX', 'BUSE', 'PDFS', 'PZZA', 'BXMX', 'DNOW', 'NWN', 'FLNG', 'FINV', 'PRDO', 'USPH', 'HLIT', 'HYT', 'DVAX', 'ELME', 'HUT', 'SILV', 'MRTN', 'MAG', 'TWO', 'ODP', 'IMKTA', 'KLG', 'CLMT', 'TCBK', 'BTT', 'GBX', 'SSTK', 'WABC', 'SRCE', 'BKD', 'GOTU', 'PARR', 'NRIX', 'KEN', 'RCUS', 'HMN', 'ARDX', 'KW', 'DEA', 'HOPE', 'AHCO', 'DSL', 'WINA', 'XRX', 'ICHR', 'FDMT', 'TASK', 'STBA', 'ANIP', 'SGML', 'BST', 'NMFC', 'ZUO', 'REVG', 'APOG', 'DAWN', 'MMI', 'VTEX', 'MEG', 'WKME', 'FSCO', 'NTCT', 'LMND', 'OEC', 'GCT', 'AMWD', 'SA', 'ESTA', 'BFS', 'TRUP', 'NIC', 'MCRI', 'DMLP', 'STEL', 'PMT', 'VIR', 'CET', 'LNN', 'ALEX', 'IMTX', 'TGI', 'UDMY', 'CARS', 'QQQX', 'SANA', 'WTTR', 'RES', 'MOMO', 'ACDC', 'IE', 'ARQT', 'JMIA', 'CRCT', 'CSGS', 'AIV', 'CSWC', 'NRP', 'GOOS', 'UTZ', 'GAM', 'ADEA', 'OMCL', 'CMTG', 'PRTA', 'BV', 'HE', 'GIC', 'SLCA', 'CRAI', 'NTST', 'VBTX', 'JELD', 'KFRC', 'GES', 'GIII', 'XNCR', 'AILE', 'SASR', 'NMZ', 'HY', 'SPH', 'UMH', 'TPC', 'BRCC', 'DOLE', 'UVV', 'JFR', 'GOGO', 'OCUL', 'NFJ', 'NVGS', 'BLX', 'CAL', 'JKS', 'EOS', 'CNNE', 'OPRA', 'PHR', 'PRM', 'SMR', 'CIM', 'SHCO', 'SII', 'IRON', 'DCBO', 'PBI', 'PRO', 'GENI', 'ALX', 'ATRC', 'SAFT', 'CSIQ', 'EVV', 'SEAT', 'PSFE', 'MFA', 'ELVN', 'COUR', 'RVLV', 'NRDS', 'TRNS', 'LOMA', 'PLYA', 'FPF', 'AORT', 'SBH', 'MRC', 'CNTA', 'AOSL', 'TARS', 'LZ', 'CSR', 'JBSS', 'INDI', 'EIG', 'PTA', 'SCSC', 'BY', 'PEBO', 'SHLS', 'EFC', 'UUUU', 'EEX', 'ECVT', 'RBCAA', 'IRWD', 'SILK', 'MTAL', 'SPRY', 'GABC', 'GYRE', 'ARR', 'SCVL', 'BBDC', 'BCSF', 'DQ', 'FBRT', 'GSM', 'AMSC', 'MUC', 'QCRH', 'CALT', 'MDRX', 'INVA', 'CRSR', 'ECPG', 'HLF', 'NBXG', 'COLL', 'PX', 'FDP', 'HIBB', 'ULH', 'MDXG', 'RSKD', 'GPRE', 'NN', 'THR', 'BHLB', 'TNGX', 'TYRA', 'AGRO', 'PDX', 'TRS', 'BBN', 'NAPA', 'LC', 'PLYM', 'OMI', 'AMPL', 'NEXA', 'SSRM', 'RNP', 'SCHL', 'BTZ', 'GRC', 'OBK', 'RLAY', 'WWW', 'PFBC', 'ATEN', 'MFIC', 'CLB', 'MSEX', 'IRS', 'FSLY', 'AHH', 'GB', 'KARO', 'REAX', 'PDS', 'PUBM', 'COGT', 'OCFC', 'CECO', 'EYE', 'PCRX', 'PDM', 'SBOW', 'CMCO', 'IMOS', 'DLX', 'CGEM', 'NRK', 'EDN', 'VTOL', 'EH', 'WNC', 'AGX', 'DESP', 'XPEL', 'SBGI', 'LQDA', 'FWRG', 'HTLD', 'SHEN', 'AVNS', 'PHVS', 'ATSG', 'BLFS', 'GATO', 'JACK', 'TCPC', 'FSUN', 'SBR', 'PLSE', 'GSL', 'IDT', 'ROOT', 'CGBD', 'ARIS', 'RPAY', 'ETW', 'OKLO', 'HCI', 'TTGT', 'HQH', 'BRDG', 'FIP', 'DX', 'HOV', 'SDA', 'CBRL', 'CWH', 'FIGS', 'PGY', 'AOD', 'CHI', 'PCT', 'RWT', 'AWF', 'NX', 'IMAX', 'BZH', 'MTUS', 'CII', 'SVC', 'MQY', 'BSIG', 'CRML', 'GNK', 'PUMP', 'MUI', 'BELFA', 'TILE', 'TH', 'WEST', 'SLRC', 'DCO', 'ETNB', 'UTL', 'BASE', 'FVRR', 'UTI', 'ABVX', 'CHY', 'MATV', 'DNTH', 'ALGT', 'GRNT', 'THQ', 'QNST', 'AMAL', 'MESO', 'WGS', 'APLD', 'GDEN', 'ACEL', 'HSTM', 'SBSI', 'ECC', 'AMSF', 'BBSI', 'USNA', 'CURV', 'CRF', 'ZIP', 'FBMS', 'BXC', 'DGII', 'BFC', 'NOVA', 'SXC', 'DCOM', 'PRAX', 'HROW', 'NYAX', 'CDNA', 'BJRI', 'MAX', 'DRD', 'VRDN', 'AUPH', 'ASC', 'AXL', 'FMBH', 'GDYN', 'UAN', 'BRKL', 'BRSP', 'RDFN', 'ANAB', 'WLKP', 'AMTB', 'MNTK', 'HCSG', 'CATX', 'EOI', 'SLP', 'PRAA', 'AMRK', 'CTBI', 'KIDS', 'TXO', 'ENFN', 'REX', 'ERII', 'PFLT', 'PRLB', 'BCX', 'ML', 'HZO', 'CTKB', 'ATEX', 'IMNM', 'RDWR', 'PFC', 'CLW', 'CBL', 'MATW', 'SUPV', 'WDI', 'CFFN', 'DLY', 'KOP', 'EVRI', 'WRLD', 'CNOB', 'BHRB', 'JQC', 'EMBC', 'ASTL', 'HAYN', 'EIM', 'XPOF', 'PNTG', 'TK', 'CAPL', 'MYI', 'PLRX', 'AIO', 'SKE', 'IIIV', 'TVTX', 'CINT', 'KELYA', 'EVER', 'WVE', 'UNFI', 'VLRS', 'ATRO', 'HUMA', 'PRME', 'STOK', 'CFB', 'VTS', 'PCN', 'DXPE', 'KRNT', 'INNV', 'METC', 'RGR', 'HTD', 'FFC', 'TMP', 'TRIN', 'VVI', 'IGR', 'NVRI', 'TRTX', 'HA', 'CCAP', 'NBR', 'ETD', 'EOLS', 'FCBC', 'LEU', 'RA', 'PAHC', 'SAGE', 'CRESY', 'NXP', 'ASTE', 'AVO', 'UVSP', 'LPRO', 'RYI', 'URGN', 'ZYME', 'ARKO', 'WSR', 'SRRK', 'VMO', 'OLMA', 'MEGI', 'OSBC', 'CHCT', 'EXAI', 'EGY', 'PAXS', 'MCBS', 'MBWM', 'MNRO', 'DMRC', 'BIOX', 'IGIC', 'LMB', 'IFN', 'KREF', 'BOE', 'PHAT', 'CION', 'PETQ', 'GSBC', 'EFXT', 'SNCY', 'DSP', 'MLYS', 'ORIC', 'MBUU', 'HBT', 'NPWR', 'CGC', 'DAKT', 'NIE', 'WEAV', 'HFWA', 'CVLG', 'NDMO', 'ABL', 'STKL', 'CLCO', 'IMXI', 'FLWS', 'AC', 'SWBI', 'MLR', 'NR', 'CCB', 'HSII', 'TPB', 'YEXT', 'SPTN', 'MHD', 'DH', 'STRW', 'ARCT', 'CCD', 'HAIN', 'FNA', 'TIPT', 'INN', 'FLGT', 'REPX', 'RGNX', 'KRUS', 'FDUS', 'SMP', 'PFN', 'LQDT', 'XMTR', 'BGS', 'NKX', 'APLT', 'VEL', 'ASIX', 'SSYS', 'GHRS', 'MUJ', 'ATXS', 'SIGA', 'THRY', 'CMPO', 'EGBN', 'IIIN', 'HCKT', 'GMRE', 'NMCO', 'CELC', 'SIBN', 'SB', 'CPF', 'LRMR', 'AIRJ', 'VREX', 'MD', 'SRDX', 'CEM', 'PEO', 'GOOD', 'ETJ', 'ANNX', 'ITOS', 'GPRK', 'IRMD', 'BWMN', 'GRPN', 'LDP', 'BHK', 'IIM', 'LEGH', 'BYON', 'HBNC', 'OFIX', 'IBCP', 'VINP', 'BIGC', 'TREE', 'PDT', 'PRA', 'TRDA', 'NYMT', 'OUST', 'EWCZ', 'BTO', 'BME', 'DRQ', 'FTEL', 'BFST', 'REPL', 'CATC', 'MMU', 'KRT', 'TRST', 'EBF', 'OBE', 'CASS', 'CRBP', 'FPI', 'GLDD', 'PTLO', 'BH-A', 'PML', 'VGM', 'EMD', 'BGY', 'AMBC', 'MOV', 'STK', 'VKQ', 'TERN', 'MERC', 'YORW', 'GRVY', 'BIT', 'PACK', 'EQBK', 'CLFD', 'LXU', 'PRTC', 'PBT', 'EZPW', 'FRPH', 'DOYU', 'HTBK', 'ORRF', 'UHT', 'MLAB', 'KE', 'NRC', 'SAVA', 'NGNE', 'BWMX', 'BGB', 'FWRD', 'HTBI', 'NGVC', 'PEPG', 'TWI', 'NOAH', 'ALT', 'CGNT', 'VERV', 'IQI', 'LASR', 'ORC', 'QTRX', 'TBLD', 'UVE', 'YMAB', 'GTN', 'MGIC', 'ACTG', 'MNMD', 'FTHY', 'SLRN', 'WIW', 'UFCS', 'SOI', 'MITK', 'OCS', 'MUX', 'SMBC', 'RILY', 'NUS', 'EBS', 'NPK', 'CDMO', 'MCB', 'FNKO', 'EMO', 'GLAD', 'HAFC', 'FSBC', 'LAND', 'IGMS', 'OPY', 'ALEC', 'SMWB', 'NXJ', 'BLE', 'FC', 'KALV', 'HPS', 'NOA', 'GDOT', 'CSTL', 'ZIMV', 'TMCI', 'GAIN', 'CAC', 'BUI', 'GUG', 'LIND', 'SOHU', 'BRY', 'PLOW', 'VCV', 'PNNT', 'HONE', 'DSU', 'DIAX', 'DIN', 'OFLX', 'BLW', 'MCBC', 'ACIC', 'THW', 'BALY', 'MYD', 'MSBI', 'GHY', 'GFR', 'EYPT', 'THRD', 'MYE', 'OLP', 'ITRN', 'BAND', 'ATLC', 'BTMD', 'MEI', 'NNOX', 'FMNB', 'RSVR', 'ZEUS', 'CCBG', 'OSPN', 'VYGR', 'GLASF', 'WASH', 'LENZ', 'LE', 'SD', 'RDW', 'ASGI', 'FULC', 'CCRN', 'ELYM', 'CEVA', 'CTLP', 'CMPS', 'RMT', 'THFF', 'NQP', 'INOD', 'FRA', 'MVF', 'MMD', 'VHI', 'EHAB', 'IVR', 'NBB', 'SPFI', 'TRC', 'GLRE', 'SEZL', 'TBPH', 'BYND', 'GUT', 'AROW', 'CHW', 'AGS', 'WLFC', 'CMP', 'NPFD', 'NFBK', 'HPI', 'ICG', 'MUA', 'ODC', 'NML', 'RWAY', 'RDUS', 'BFK', 'JPI', 'PFIS', 'EDIT', 'HRZN', 'KODK', 'DAVE', 'MLP', 'AMCX', 'WOW', 'NKLA', 'QURE', 'CCNE', 'AEHR', 'WLDN', 'NKTX', 'ISD', 'SRI', 'ALNT', 'CLDT', 'VALU', 'DGICA', 'GNE', 'SMBK', 'ZUMZ', 'LYTS', 'ONEW', 'NMAI', 'NTGR', 'ADTN', 'PKST', 'ISPR', 'ETO', 'JILL', 'HFRO', 'TSAT', 'CRD-A', 'BHB', 'NEXN', 'SENEA', 'PGC', 'ETB', 'CWCO', 'BOC', 'AVK', 'EVN', 'CSV', 'CTO', 'CRMT', 'VPG', 'KRNY', 'ESQ', 'FSD', 'BVS', 'RICK', 'DBI', 'KRRO', 'SNDA', 'CABA', 'HQL', 'IGD', 'SHBI', 'CHUY', 'FFIC', 'MYN', 'VKI', 'ALXO', 'RMR', 'ALRS', 'EAD', 'ENGN', 'HVT', 'CDLX', 'DFP', 'PSTL', 'PRTH', 'DHIL', 'ARTNA', 'LOVE', 'PERI', 'FFA', 'ANIK', 'VLGEA', 'PTSI', 'HDSN', 'AURA', 'ACRE', 'XFLT', 'FFWM', 'MTW', 'SMHI', 'MPB', 'DPG', 'LEO', 'LINC', 'TYG', 'CVGW', 'SGU', 'HIPO', 'EFR', 'GBAB', 'KIO', 'SDHY', 'HCAT', 'RNAC', 'MOFG', 'ASA', 'LMNR', 'KTF', 'MCI', 'PPTA', 'SMLP', 'GNTY', 'MODV', 'XPER', 'RBB', 'TITN', 'IPX', 'JOUT', 'HSHP', 'BFZ', 'HPF', 'TRML', 'AXGN', 'MCS', 'CARE', 'SGHT', 'BGR', 'CWBC', 'AAOI', 'CCCC', 'DENN', 'SOR', 'KMDA', 'AMWL', 'SHYF', 'ACP', 'AVNW', 'NAN', 'RYAM', 'ASLE', 'RDVT', 'EFT', 'PANL', 'MEC', 'TCRX', 'BBW', 'ARDC', 'RGP', 'RFMZ', 'BSRR', 'VRCA', 'BBCP', 'NWPX', 'CYRX', 'ATNI', 'VNDA', 'LSEA', 'BWB', 'JRI', 'CCSI', 'ITIC', 'SCM', 'MIY', 'FOF', 'NVRO', 'GHI', 'NEWT', 'AUDC', 'CVEO', 'HBCP', 'AGEN', 'LXFR', 'SKYT', 'IMMR', 'SLDB', 'FORR', 'HEAR', 'BRT', 'MHN', 'ASG', 'LOCO', 'RRBI', 'TWN', 'ACB', 'FARO', 'IPI', 'PFL', 'NBH', 'LTCN', 'AFB', 'MPX', 'NPCT', 'SPOK', 'TTSH', 'NREF', 'PMO', 'RFI', 'FISI', 'GCO', 'SAR', 'LAW', 'AAN', 'FINS', 'SGC', 'MCFT', 'AMSWA', 'NODK', 'FMAO', 'NL', 'ACNB', 'ENTA', 'GTE', 'TCBX', 'APEI', 'TPVG', 'BCHG', 'WTBA', 'OIA', 'NYXH', 'FBIZ', 'GAMB', 'GHM', 'PMTS', 'RMM', 'AIP', 'CPZ', 'JSPR', 'TBI', 'JWSM', 'PKOH', 'UHG', 'BGH', 'EBTC', 'QUAD', 'BMRC', 'BYM', 'CBNK', 'SPXX', 'TRAK', 'ZYXI', 'JGH', 'BRW', 'AOMR', 'RCS', 'HNRG', 'ABXXF', 'UNTY', 'REFI', 'FHTX', 'DSM', 'OBIO', 'SRG', 'BSVN', 'NATH', 'ALIM', 'JRVR', 'ALTG', 'BGT', 'NCA', 'TTEC', 'GWRS', 'BOOM', 'FSBW', 'OBT', 'TCMD', 'GENC', 'IBEX', 'PMM', 'LUNG', 'SBT', 'NATR', 'BDTX', 'DOMO', 'FRST', 'CZNC', 'PKE', 'AMPY', 'VBNK', 'ORN', 'AEF', 'CTR', 'KNOP', 'RM', 'ESEA', 'FNLC', 'INO', 'PBFS', 'SPIR', 'GRIN', 'GENK', 'MCR', 'RLGT', 'IIF', 'MAMA', 'MG', 'DBL', 'MBI', 'RMAX', 'SCD', 'RIV', 'WSBF', 'FCT', 'EOT', 'TRTL', 'PMX', 'BLZE', 'HYI', 'FTF', 'INBK', 'MVBF', 'BNY', 'SLAM', 'ZTR', 'PLAO', 'BCAL', 'TEI', 'LFMD', 'BKT', 'OOMA', 'ERC', 'USCB', 'VMD', 'ONTF', 'TCI', 'USAP', 'GASS', 'IRBT', 'ZVRA', 'MXF', 'CBUS', 'RLTY', 'EVI', 'RCKY', 'AGD', 'NUW', 'ANGO', 'FLIC', 'MTRX', 'UTMD', 'HBB', 'SSBK', 'PMF', 'ARL', 'CIVB', 'RNGR', 'JCE', 'PCYO', 'GOCO', 'PSF', 'SMTI', 'INSE', 'TECX', 'EPIX', 'EVM', 'NGS', 'SFST', 'FSTR', 'GLO', 'JMSB', 'ACRV', 'SMLR', 'NECB', 'ALAR', 'GPJA', 'AVD', 'HMST', 'MVT', 'CBAN', 'CLAR', 'PINE', 'CPS', 'VIRC', 'AFT', 'NXDT', 'FUND', 'MQT', 'CNDA', 'KFS', 'JRS', 'BLFY', 'MSB', 'RCEL', 'MUE', 'PHT', 'FF', 'ASUR', 'MFM', 'GCTS', 'AEYE', 'PCB', 'DCTH', 'MOLN', 'LGI', 'BPRN', 'ATNM', 'PROF', 'ACV', 'NTG', 'SABA', 'BYRN', 'JOF', 'PLL', 'PBPB', 'EOD', 'STRS', 'AIF', 'TSBK', 'RGCO', 'NPCE', 'BNED', 'ABEO', 'NC', 'INGN', 'TCX', 'CLPT', 'MITT', 'NHS', 'SHIP', 'HIE', 'MED', 'MHI', 'EIC', 'PLBC', 'CMCL', 'PDLB', 'HRTG', 'NPV', 'BKN', 'TDF', 'CPSS', 'CTGO', 'NWFL', 'PKBK', 'ETX', 'SNBR', 'CIO', 'COFS', 'CAF', 'GLSI', 'OPP', 'OVLY', 'EMF', 'MAV', 'SERA', 'MIO', 'JYNT', 'JAKK', 'DMB', 'PSIX', 'ALCO', 'FFNW', 'FET', 'FVCB', 'LCNB', 'PNRG', 'PEGR', 'SEVN', 'PVBC', 'PCK', 'MX', 'VRA', 'WIA', 'ONIT', 'VNJA', 'CALB', 'IGI', 'MFIN', 'BCBP', 'EGAN', 'BWFG', 'CVRX', 'GDO', 'OTLK', 'MDWD', 'BSL', 'VBF', 'SNFCA', 'PTMN', 'MASS', 'OPRX', 'EPM', 'FLL', 'CSTE', 'ATLX', 'ATLO', 'ENJ', 'SKYE', 'PCQ', 'CADL', 'ENX', 'MBCN', 'MPV', 'ESCA', 'VABK', 'TWIN', 'ULBI', 'LWAY', 'HGLB', 'HCVI', 'INMB', 'AFCG', 'TLYS', 'RELL', 'INSI', 'QRHC', 'HQI', 'FENC', 'HYB', 'EP', 'FT', 'CVGI', 'LFCR', 'TG', 'LCUT', 'MYFW', 'LAKE', 'STHO', 'TSQ', 'ADVM', 'FLC', 'PZC', 'CTRN', 'EVBN', 'AKA', 'CBH', 'DM', 'RIGL', 'MPA', 'NFYS', 'BSEM', 'EVE', 'BGX', 'EHI', 'MRCC', 'QUIK', 'TEAF', 'ISTR', 'SYRS', 'NNY', 'TLSI', 'IDE', 'SSTI', 'OPBK', 'TBRG', 'DLHC', 'PWOD', 'ANVS', 'GRX', 'WNEB', 'UEIC', 'SAMG', 'EDF', 'CFFI', 'BMN', 'MSD', 'MCN', 'DMF', 'SPCE', 'MHF', 'SPE', 'TATT', 'HOFT', 'FTK', 'DTI', 'SMID', 'EVG', 'CSPI', 'RCMT', 'INFU', 'GGT', 'PEBK', 'LOGC', 'INTT', 'RDCM', 'BWG', 'FNRN', 'EARN', 'FUNC', 'BVFL', 'GF', 'IDR', 'PESI', 'TAYD', 'MRAM', 'CMT', 'PFD', 'IGA', 'DMO', 'RMMZ', 'BTA', 'BFAC', 'GLQ', 'INSG', 'FINW', 'NAZ', 'BRAG', 'DCF', 'FMN', 'SKIL', 'PHYT', 'VFL', 'JHS', 'CRVO', 'KF', 'UBFO', 'GEOS', 'MRBK', 'ELMD', 'FSFG', 'WEA', 'HEQ', 'FBYD', 'RMGCF', 'PHD', 'SRV', 'FRAF', 'MPAA', 'BBXIA', 'BSET', 'RCFA', 'BRWC', 'CFBK', 'SKLZ', 'NVCT', 'WHG', 'CCFN', 'PLCE', 'OFS', 'ESOA', 'JHI', 'BYNO', 'PAI', 'ECBK', 'PCF', 'ECF', 'CGO', 'CDAQ', 'NIM', 'RTC', 'CFFS', 'SPPP', 'BKKT', 'SBI', 'MVO', 'PFO', 'CATO', 'SFBC', 'KSM', 'PLMI', 'AOUT', 'ACR', 'SWZ', 'HMNF', 'FNWD', 'WPRT', 'LARK', 'AXR', 'NMT', 'GECC', 'COYA', 'EBMT', 'UFI', 'CCIF', 'CNVCF', 'NXG', 'FRD', 'RMI', 'CHN', 'ACNT', 'GIFI', 'EVF', 'NMI', 'CSBB', 'HNW', 'JLS', 'IHD', 'EMYB', 'HURC', 'BEEM', 'TZOO', 'ASYS', 'CCRD', 'UNB', 'RFM', 'SNCR', 'TBMC', 'BOWN', 'SRTS', 'ISSC', 'VSEE', 'GGZ', 'TPZ', 'SGA', 'RRGB', 'ACRG', 'AUID', 'GDL', 'BGSF', 'MPTI', 'BCV', 'SILC', 'FNWB', 'GNT', 'ERH', 'PCM', 'BMBN', 'VOC', 'BNTC', 'SRBK', 'VTSI', 'PGP', 'TTOO', 'VGI', 'MHH', 'GLU', 'JEQ', 'FEIM', 'NXC', 'PNI', 'PSBQ', 'DOMA']
tickers.append('')

start = time.time()

num = 1000
stocks = []
total = len(tickers[:num])
for i in range(total):
    print(f'{i+1}/{total}: ')
    stock = Stock(tickers[i])
    stocks.append(stock)
    exception = stock.update()
    if exception != 0:
        print(exception)
    print('')
size = len(stocks)
tickers = [stock.ticker for stock in stocks]

print(f'Array stocks created, time elapsed: {time.time()-start}')
start = time.time()

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

        magnitude = np.abs(corr)
        if magnitude > 0.7 and i != j and (np.abs(z[2]) > 0.0001 or np.abs(z[3]) > 0.0001) and z[1] != 1:
            z_info_matrix[i][j] = (z[1], z[2], z[3])
            z_info_matrix[j][i] = (z[1], z[3], z[2])

        if np.abs(z[0]) >= 2:
            z_matrix[i][j] = z[0]
            z_matrix[j][i] = -z[0]

        corr_matrix[i][j] = corr
        cov_matrix[i][j] = cov

        corr_matrix[j][i] = corr
        cov_matrix[j][i] = cov

print(f'Correlation, covariance and z_score matrices created, time elapsed: {time.time()-start}')

#plt.matshow(corr_matrix, cmap='inferno', vmin=np.min(corr_matrix), vmax=1)
#plt.show()
#plt.matshow(cov_matrix, cmap='inferno', vmin=-2, vmax=30)
#plt.show()
#plt.matshow(np.abs(z_matrix), cmap='inferno', vmin=0, vmax=3)
#plt.show()

corr_df = pd.DataFrame(corr_matrix)
z_df = pd.DataFrame(z_matrix)
#print(corr_df.to_string())
#print(z_df.to_string())

pairs = []
for i in range(size-1):
    for j in range(i+1,size):
        if z_info_matrix[i][j] != 0:
            pairs.append((stocks[i].ticker, stocks[j].ticker, *z_info_matrix[i][j], corr_matrix[i][j], z_matrix[i][j]))

pairs.sort(key=lambda x: x[3])
for i in pairs:
    print(i)
