# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 15:25:31 2014

@author: Gouthaman Balaraman
"""

import Quandl as ql
import pandas as pd
import numpy as np
import datetime
import dutil

data = ql.get("WIKI/ADT", column=11, trim_start='2008-01-01', 
              trim_end='2014-08-31')

index_data = ql.get("YAHOO/INDEX_SPY", column=6, trim_start='2008-01-01', 
              trim_end='2014-08-31')
              
rfr_data = ql.get("USTREASURY/YIELD", column=1, trim_start='2008-01-01', 
              trim_end='2014-08-31')



              
class MPTStats(object):
    ALPHA = 1
    BETA = 2
    R2 = 4
    SHARPE_RATIO = 8
    SORTINO_RATIO = 16
    TREYNOR_RATIO = 32
    INFORMATION_RATIO = 64
    MOMENTUM = 128
    ANNUALIZED_RETURN = 256
    STANDARD_DEVIATION = 512
    UPSIDE_CAPTURE = 1024
    DOWNSIDE_CAPTURE = 2048
    TRACKING_ERROR = 4096
    CALC_ALL = 8191
    CALC_CAPM = ALPHA + BETA + R2
    
    ALLOWED_FREQ = set(['D','M'])#,'W','Q','A'])
    
    _dt_map = {'M':1./12.,'D':1./250.}
    
    
    
    def __init__(self, stock_series, bench_series, rfrate_series):
        """
        stock_series : Adjusted close price for stock
        bench_series : Adjusted close price for benchmark
        rfrate_series: Risk Free Rate in annualized terms and fraction units 
        """
        self.stock_series = stock_series
        self.bench_series = bench_series
        self.rfrate_series = rfrate_series
        self._join_clean_datasets()        
        
        
    def _join_clean_datasets(self):
        '''
        Join the three time series data sets, clean by filling holes using ffill and bfill
        '''
        self.df = pd.DataFrame({"s_adjclose":self.stock_series,
                                "b_adjclose":self.bench_series,
                                "rfrate": self.rfrate_series})
        self.df = self.df[["s_adjclose", "b_adjclose", "rfrate"]].fillna(method="ffill")
        self.df = self.df[["s_adjclose", "b_adjclose", "rfrate"]].fillna(method="bfill")
        
        
    def calculate(self, asof_date, calc_code=CALC_ALL, freq='M', span = 36):
        self._validate_parameters(asof_date, calc_code, freq, span)
        if isinstance(asof_date, datetime.date):
            asof_date = datetime.datetime.combine(asof_date, datetime.datetime.min.time())
        suffix = "_"+freq+"_"+str(span)
        dfsamp = self._prepare_data(freq)
        span_sdate, span_edate = self._get_start_end_dates(asof_date, freq, span)
        dfslc = self._slice_df_to_dates(dfsamp, span_sdate, span_edate)
        
        exc_stock_returns = (dfslc["s_returns"] - dfslc["rfrate"]*self._dt).values
        exc_bench_returns = (dfslc["b_returns"] - dfslc["rfrate"]*self._dt).values
        
        result = {}
        alpha = beta = stnddev = r2 = sharpe = treyr = trackerr = infor = \
        sortr = momentum = annualized_return = upside = downside =  np.NaN
        if (span_sdate>=self.stock_series.index[0]) and \
            (span_edate<=self.stock_series.index[-1]):
        #if (len(dfslc) == span) or (freq=='D'):
            if len(exc_stock_returns) == len(exc_bench_returns) :
                covmat  = np.cov(exc_stock_returns, exc_bench_returns)
                beta    = covmat[0,1]/covmat[1,1] # OLS estimation
                stock_mean_return = np.mean(exc_stock_returns)
                bench_mean_return = np.mean(exc_bench_returns)
                alpha = (stock_mean_return - beta*bench_mean_return)/self._dt   # annualized here
                sd = np.sqrt(covmat[0,0])  
                ddof = len(exc_stock_returns) -1
                fit = alpha*self._dt + beta*exc_bench_returns
                sse = np.sum(np.power(fit-exc_stock_returns,2)) 
                r2 = 1.0 - sse/(covmat[0,0]*ddof) if ddof != 0 else 0.0
                sharpe = stock_mean_return/(sd*self._sqrtdt)
                treyr   = stock_mean_return/beta/self._dt
                excret  = dfslc["s_returns"].values - dfslc["b_returns"].values                      
                sd_exc  = np.std(excret,ddof=1) # unbiased
                trackerr = (sd_exc/self._sqrtdt)
                infor   = alpha/trackerr
                MAR = dfslc["rfrate"].mean()*self._dt
                semistd = self._get_semistd(dfslc["s_returns"].values, MAR)
                sortr   = (dfslc["s_returns"].mean()-MAR)/(semistd*self._sqrtdt)
                stnddev = sd/self._sqrtdt
            if calc_code & (self.MOMENTUM | self.ANNUALIZED_RETURN):
                momentum,annualized_return = self._calc_span_return(span, freq, span_sdate, span_edate)           
            if calc_code & (self.UPSIDE_CAPTURE | self.DOWNSIDE_CAPTURE ):
                upside, downside = self._calc_updown_capture(dfslc, self._dt)
                
        result = {"Alpha"+suffix : alpha*100., 
                  "Beta"+suffix : beta, 
                  "StandardDeviation"+suffix : stnddev*100.0, 
                  "RSquared"+suffix : r2*100.0, 
                  "SharpeRatio"+suffix : sharpe, 
                  "TreynorRatio"+suffix : treyr,
                  "TrackingError"+suffix : trackerr*100, 
                  "InformationRatio"+suffix : infor, 
                  "SortinoRatio"+suffix : sortr,
                  "Momentum"+suffix : momentum*100.0, 
                  "AnnualizedReturn"+suffix : annualized_return*100,
                  "UpsideCapture"+suffix : upside*100, 
                  "DownsideCapture"+suffix : downside*100
                  }
        return result
        
    @staticmethod
    def _calc_updown_capture(df,dt):
        def calc_ratio(df,dt):
            ratio = 0.0
            if len(df)>0:
                i_cumprod = np.prod(df["b_returns"]+1.0)
                s_cumprod = np.prod(df["s_returns"]+1.0)
                expon = 12.0*dt/len(df)
                ratio = (pow(s_cumprod, expon)- 1.0) /( pow(i_cumprod, expon) - 1.0)
            return ratio
            
        udf = df[df["b_returns"]>0.0]
        ddf = df[df["b_returns"]<0.0]
        uratio = calc_ratio(udf, dt)
        dratio = calc_ratio(ddf, dt)
        return (uratio, dratio)        
    
    def _calc_span_return(self, span, freq, span_sdate, span_edate):
        srs = self.stock_series
        orig_startdate = startdate = span_sdate if freq=='D' else dutil.get_month_end(span_sdate)
        stid    = srs.index.searchsorted(startdate)
        endid   = min(srs.index.searchsorted(span_edate,side='left'),len(srs)-1)        
        if (srs.index[stid].to_datetime()>startdate) and (stid>0) :
            stid = stid - 1
        if srs.index[endid].to_datetime() > span_edate:
            endid = endid - 1
        mmntm   = srs.iloc[endid]/srs.iloc[stid]-1
        startdate = srs.index[stid]
        enddate = srs.index[endid]
        n = span/12
        annualized_return = pow( 1.0 + mmntm, 1.0/(n) ) - 1
        threshold = 4
        insuff_points = (( abs( (startdate - orig_startdate).days )>threshold )or \
                ( abs( (span_edate - enddate).days )>threshold ))
        mmntm = np.NaN if  insuff_points else mmntm
        annualized_return = np.NaN if insuff_points else annualized_return
        return (mmntm, annualized_return)        
        
    @staticmethod
    def _get_semistd(arr,mar):
        arr = arr[arr<mar]
        return np.std(arr,ddof=1)
        
    @staticmethod
    def _slice_df_to_dates(df, span_sdate, span_edate):
        stid  = df.index.searchsorted(span_sdate, side='right')
        endid = df.index.searchsorted(span_edate,side='right')
        dfsamp = df[stid:endid]
        return dfsamp
        
    @staticmethod
    def _get_start_end_dates(asof_date, freq, span):
        if freq == 'D':
            span_edate = asof_date
        if freq == 'M':
            mend = dutil.get_month_end(asof_date)
            if mend == asof_date:
                span_edate = asof_date
            else:
                span_edate = dutil.get_month_end(dutil.shift_months(asof_date, -1))
            
        span_sdate = dutil.shift_months(span_edate, -1*span)
        return span_sdate, span_edate
        
        
    def _validate_parameters(self, asof_date, calc_code, freq, span):
        if (not isinstance(asof_date,datetime.date) ) and (not isinstance(asof_date, datetime.datetime)):
            raise TypeError("Argument 'asof_date' is not of type datetime or date" )
        if not isinstance(freq,str):
            raise TypeError("Argument 'freq' must be of type str")
        if freq not in self.ALLOWED_FREQ:
            raise ValueError("Invalid frequency '%s' in argument 'freq'"%(freq))
        if not isinstance(calc_code, int):
            raise TypeError("Argument 'code' must be of type int")
        if calc_code<1 or calc_code>self.CALC_ALL:
            raise ValueError("Invalid value %d for calc_code"%(calc_code))
        if span<=0:
            raise ValueError("Argument 'span' has to be greater than 0")

        
    def _prepare_data(self, freq):
        if freq == 'D':
            dfsamp = self.df
        else:
            dfsamp = self.df.resample(freq,how={'s_adjclose' : 'last',\
                'b_adjclose': 'last', 'rfrate' : np.mean } )
                
        dfsamp[['s_returns','b_returns']] = \
            dfsamp[['s_adjclose','b_adjclose']]/dfsamp.shift(1)[['s_adjclose','b_adjclose']]-1.
        dfsamp = dfsamp.dropna()
        self._dt = self._dt_map.get(freq)
        self._sqrtdt = np.sqrt(self._dt)
        return dfsamp
        
        
if __name__ == '__main__':
    mpt = MPTStats(data["Adj. Close"], index_data["Adjusted Close"], rfr_data["1 Mo"]*0.01)
    result = mpt.calculate(datetime.date(2014,8,31),span=60, freq='D')
    print result

        