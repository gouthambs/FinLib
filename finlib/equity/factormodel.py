# -*- coding: utf-8 -*-
"""
Created on Sun Oct 12 20:29:05 2014

@author: Gouthaman Balaraman
"""

import datetime
import numpy as np
import pandas as pd
import statsmodels.api as sm
from tscache import QuandlCachedData

class QuandlFactorModelDataAdaptor(QuandlCachedData):
    # The data_items are in the form
    # { QuandlKey : { Factor1: (ColumnName, ColumnScaling, transformation), 
    #                 Factor2: (ColumnName, ColumnScaling)}, ListOfColumnNumber}
    # right now column numbers is not supported
    data_items = {
                "FRED/UNRATE" : ({"Unemployment": ('Value', 0.01, None)}, None),
                "UMICH/SOC1"  : ({"ConsumerSentiment":('Index', 1, "rdiff")}, None),
                "KFRENCH/FACTORS_M" : ({"Market" : ('Mkt-RF', 0.01, None),
                                        "Value"  : ('HML', 0.01, None),
                                        "Size"   : ('SMB', 0.01, None)
                                        },None)
                 }
    

    def __init__(self, filename, auth, data_items=None):
        super(self.__class__,self).__init__(filename, auth)
        if data_items is not None:
            self.set_data_items(data_items)
        else:
            self._factor_lookup = self._create_data_item_lookup(self.data_items)

    
    def set_data_items(self, data_items):
        self.data_items = data_items
        self._factor_lookup = self._create_data_item_lookup(data_items)
    
    
    @staticmethod
    def _create_data_item_lookup(data_items):
        return {f:k for k, v in data_items.items() for f in v[0].keys() }
                        
            
    def get_factor_data(self,factors, start_date, end_date, freq="M"):
        gaps = set( factors) - set(self._factor_lookup.keys())
        if len(gaps)>0:
            raise ValueError("Factors not part of item lookup requested")
            
        quandl_keys = {}
        for f in factors:
            qk = self._factor_lookup[f]
            if qk in quandl_keys.keys():
                quandl_keys[qk].append(f)
            else:
                quandl_keys[qk] = [f]
            
        factor_data = {}
        indx = pd.DatetimeIndex(start=start_date, end=end_date, freq='M')
        for qkey,factors in quandl_keys.items():
            data = self.fetch_data(qkey,start_date, end_date)
            for f in factors:
                column_name , column_scale, transformation = self.data_items[qkey][0][f]
                factor_data[f] = data[column_name].reindex(indx, 
                                        method='ffill')*column_scale
                if transformation=="rdiff":
                    factor_data[f] = factor_data[f]/factor_data[f].shift(1)-1
                
        return factor_data
    
    
    def get_adjusted_close(self, ticker, start_date, end_date):
        data = self.fetch_data(ticker, start_date, end_date,11)
        
        return data["Adj. Close"]
        

class EconometricFactorModel(object):
    '''
    SimpleFactorModel uses simple market factors to enhance the beta concept.
    '''
    _factors = ["Unemployment", "ConsumerSentiment", "Market", "Size", "Value"]
    
    def __init__(self, data_getter, start_date, end_date, factors=None):
        self._data_getter = data_getter
        self._start_date = start_date
        self._end_date = end_date
        if factors is not None:
            self._factors = factors
        self._factor_data = data_getter.get_factor_data(self._factors, 
                                                        self._start_date,
                                                        self._end_date)
                                                        
                                                        
    def _prepare_data(self,ticker):
        
        stock_data = self._data_getter.get_adjusted_close(ticker,
                                                          self._start_date, 
                                                          self._end_date)
        self._stock = stock_data.resample('M', how='last')
        self._stock = (self._stock/self._stock.shift(1)-1.0).dropna()        
        df = pd.DataFrame(dict(self._factor_data.items() + 
                                {"Stock":self._stock}.items()))                        
        df = df.dropna()
        X = df[self._factors]
        X = sm.add_constant(X)
        self.factors = X.columns
        Y = df["Stock"]
        return X,Y    
        
    
    def _risk_exposures(self):
        risk = {}
        total_risk = np.var(self._Y*100)*12
        covmat = self._X.cov().values
        nondiv_risk = np.dot(np.dot(self.betas.transpose(),covmat), 
                                         self.betas.values)*12*10000
        risk["TotalRisk"] = np.sqrt(total_risk)
        risk["NonDiversifiableRisk"] = np.sqrt(nondiv_risk)
        risk["DiversifiableRisk"] = np.sqrt(total_risk - nondiv_risk)
        
        return risk
    
    
    def calculate(self, ticker):
        self._X, self._Y = self._prepare_data(ticker)
        est = sm.OLS(self._Y, self._X).fit()
        self._est = est        
        self.betas = self._est.params
        self.stderr = self._est.bse
        self.risk = self._risk_exposures()
          

                            

if __name__ == '__main__':
    def grab_ticker_list(filename):
        df = pd.read_csv(filename, sep=",")
        df = df.dropna()
        return df    
    
    
    import logging    
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.getLogger().setLevel(logging.INFO)
    import sys
    if len(sys.argv) != 3:
        print "Usage: factormodel.py <quandlauth>"
    else:
        try:
            filename = sys.argv[1]
            auth = sys.argv[2]
            f = open("fmoutput.csv","w")
            
            tsd = QuandlFactorModelDataAdaptor(".\\stock_cache.db", auth)
            
            sdate = datetime.datetime(2009,9,30,0,0)
            edate = datetime.datetime(2014,9,30, 0, 0)
            date = edate.strftime('%Y-%m-%d')
            #sdate = datetime.datetime(1999,12,31,0,0)
            #edate = datetime.datetime(2003,12,31, 0, 0)
            fm = EconometricFactorModel(tsd, sdate, edate)
            df = grab_ticker_list(filename)
            l = df["quandl code"].values
            
            f.write("Ticker,Date,Alpha,Unemployment,ConsumerSentiment,Market,Size,ValueGrowth,AlphaStd,UnemploymentStd,ConsumerSentimentStd,MarketStd,SizeStd,ValueGrowthStd,TotalRisk,DiversifiableRisk,NonDiversifiableRisk\n")
            ctr = 0
            for t in l:
                fm.calculate(t)
                wiki,ticker = t.split('/')
                f.write("%s,%s,%s,%s,%s\n"%(ticker,date,\
                                       ",".join([str(round(v,3)) for v in fm.betas.values]),\
                                       ",".join([str(round(v,3)) for v in fm.stderr.values]),\
                                        ",".join([str(round(v,3)) for k,v in fm.risk.items()]))
                        )
                ctr +=1
                if not ctr%50:
                    print "Finished %d"%(ctr)
        except Exception as e:
            logging.exception(str(e))
        finally:
            f.close()
            tsd.close_cache()
        