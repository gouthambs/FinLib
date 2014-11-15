



import logging
import pandas as pd



class QuandlData(object):
    _storage = None
    
    def __init__(self, cache=None,authtoken=None):
        
        self._db = cache
        self._authtoken = authtoken
        
        
    def _format_date(self, date):
        return date.strftime('%Y-%m-%d')

    @staticmethod
    def _snap_to_interval(df, span_sdate, span_edate):
        stid  = df.index.searchsorted(span_sdate, side='right')
        endid = df.index.searchsorted(span_edate,side='right')
        dfsamp = df[stid:endid]
        return dfsamp
        
    def fetch_data(self, qcode, start_date, end_date, column=None, 
                   transformation=None):
       
        import Quandl as ql
        fetch = False
        data = None
        try:
            if self._db is not None:
                cache = self._db.get(qcode)
                if (cache is None) or (cache[0]>start_date) or \
                    (cache[1]<end_date) or (cache[2]!=column):
                    fetch = True
                else:
                    data = cache[3]
            else:
                fetch = True
        except Exception as e:
            logging.debug("Error happened with db")
            fetch = True
        try:
            if fetch:
                trim_start = self._format_date( start_date )
                trim_end = self._format_date(end_date)
                data = ql.get(qcode, column=column, trim_start=trim_start, 
                                      trim_end=trim_end, authtoken=self._authtoken,
                                      transformation=transformation)
                if (self._db is not None) and (data is not None):
                    self._db[qcode] =  (start_date, end_date, column, data) 
        except Exception as e:
            logging.exception("Exception fetching %s : %s"%(qcode, str(e)))
            
        return data.ix[start_date:end_date]
        
      
      
class QuandlFactorModelData(QuandlData):
    """
    This class is a bridge between the quandl api and the interface
    required by the factor model. The data_items attribute holds a mapping
    between the quandl keys to the factors needed by the model. 
    
    The data_items are in the form
    { QuandlKey : { Factor1: (ColumnName, ColumnScaling, transformation), 
                    Factor2: (ColumnName, ColumnScaling)}, ListOfColumnNumber}
    right now column numbers is not supported
    
    By using a generalized data_items mapping, we can easily play with 
    different combination of factors, or even drop some without losing
    flexibility.
    """    
    
    
    data_items = {
                "FRED/UNRATE" : ({"Unemployment": ('Value', 0.01, None)}, None),
                "UMICH/SOC1"  : ({"ConsumerSentiment":('Index', 1, "rdiff")}, None),
                "KFRENCH/FACTORS_M" : ({"Market" : ('Mkt-RF', 0.01, None),
                                        "Value"  : ('HML', 0.01, None),
                                        "Size"   : ('SMB', 0.01, None)
                                        },None)
                 }
    

    def __init__(self, cache, auth, data_items=None):
        super(self.__class__,self).__init__(cache, auth)
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

        
if __name__ == '__main__':
    #from cache import ShelveCache
    #cache = ShelveCache(filename="D:\\cache.db", writeback=True)
    from shove import Shove
    cache = Shove("zodb:///home/gouthaman/stock.zodb")
    data = QuandlData(cache=cache)
    import datetime
    dd = data.fetch_data("WIKI/WFM", datetime.date(2014,1,1) , datetime.date(2014,7,31),column=11)
    dd = data.fetch_data("WIKI/WFM", datetime.date(2014,1,1) , datetime.date(2014,7,31),column=11)
    cache.close()
    