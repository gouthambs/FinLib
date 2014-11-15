# -*- coding: utf-8 -*-
"""
Created on Sun Sep 21 14:09:15 2014

@author: Gouthaman Balaraman
"""

import shelve

import logging




class QuandlCachedData(object):
    _storage = None
    
    def __init__(self, filename,authtoken=None,writeback=True):
        self._filename = filename
        self._writeback = writeback
        self.open_cache()
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
        if not self._is_open:
            self.open_cache()
        import Quandl as ql
        fetch = False
        data = None
        try:
            if self._db.has_key(qcode):
                cache = self._db[qcode]
                if (cache[0]>start_date) or (cache[1]<end_date):
                    fetch = True
                else:
                    data = cache[2]
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
                if data is not None:
                    self._db[qcode] = (start_date, end_date, data)
        except Exception as e:
            logging.exception("Exception fetching %s : %s"%(qcode, str(e)))
            
        #data = self._snap_to_interval(data,start_date, end_date)
        return data.ix[start_date:end_date]
        
        
    def close_cache(self):
        self._db.close()
        self._is_open = False

        
    def open_cache(self):
        self._db = shelve.open(self._filename, writeback=self._writeback)
        self._is_open = True
        
        
if __name__ == '__main__':
    import sys
    import datetime
    import pandas as pd
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.getLogger().setLevel(logging.DEBUG)
    if len(sys.argv)!=5:
        print len(sys.argv)
        print "Usage: tscache <qcode_file> <auth_token> <start_date_YYYYMMDD> <end_date_YYYYMMDD>"
    else:
        try:
            filename = sys.argv[1]
            authtoken= sys.argv[2]
            start_date = datetime.datetime.strptime(str(sys.argv[3]),'%Y%m%d')
            end_date = datetime.datetime.strptime(str(sys.argv[4]),'%Y%m%d')
            cache_file = ".\\stock_cache.db"
            def grab_ticker_list(filename):
                df = pd.read_csv(filename, sep=",")
                df = df.dropna()
                return df
            df = grab_ticker_list(filename)
            #df = df[0:1500]
            tsd = QuandlCachedData(cache_file,authtoken)
            qcodes = df["quandl code"].values
            ctr = 0
            num = len(qcodes)
            print qcodes
        
            for qcode in qcodes:
                ctr +=1
                
                data = tsd.fetch_data(qcode, start_date, end_date, 11)
                tsd.close_cache()
                q,r = divmod(ctr,10)
                if r==0:
                    print "Finished %d of %d"%(ctr,num)
        except Exception as e:
            logging.error("Error running cache %s"%str(e))
        finally:
            tsd.close()