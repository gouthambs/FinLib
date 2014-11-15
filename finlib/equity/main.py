# -*- coding: utf-8 -*-
"""
Created on Sat Sep 20 22:18:11 2014

@author: Gouthaman Balaraman
"""

import threading
import Queue
import sys
import Quandl as ql
import pandas as pd
from mptstats import MPTStats
import numpy as np
import timeit
import datetime
import logging
import dutil

logging.getLogger().addHandler(logging.StreamHandler())
_logger= logging.getLogger("Main")

def grab_ticker_list(filename):
    df = pd.read_csv(filename, sep=",")
    df = df.dropna()
    return df
    
class Worker(threading.Thread):
    _itemlist = ["Alpha", "Beta","StandardDeviation","RSquared","SharpeRatio",
                  "TreynorRatio", "TrackingError", "InformationRatio", 
                  "SortinoRatio", "Momentum", "AnnualizedReturn", "UpsideCapture", 
                  "DownsideCapture" ]
    _lock = threading.Lock()
    
    def __init__ (self, job_queue, trim_start, trim_end, calc_params, authtoken, fp):
        self.job_queue = job_queue
        self.trim_start = trim_start
        self.trim_end = trim_end
        self.calc_params = calc_params
        self.authtoken = authtoken
        self.index_data = ql.get("YAHOO/INDEX_SPY", column=6, trim_start=self.trim_start, 
              trim_end=self.trim_end, authtoken=self.authtoken)
        self.index_data = self.index_data["Adjusted Close"]
        self.rfr_data = ql.get("USTREASURY/YIELD", column=1, trim_start=self.trim_start, 
              trim_end=self.trim_end, authtoken=self.authtoken)
        self.rfr_data = self.rfr_data["1 Mo"]*0.01
        self.fp = fp
        threading.Thread.__init__ (self)
    
    def run(self):        
        while True:
            qcode = "N/A"
            try:
                qcode = self.job_queue.get()
                if qcode:
                    data = ql.get(qcode, column=11, trim_start=self.trim_start, 
                                  trim_end=self.trim_end, authtoken=self.authtoken)
                    mpt = MPTStats(data["Adj. Close"], self.index_data, self.rfr_data)
                    result = mpt.calculate(self.calc_params["calc_date"],\
                        freq=self.calc_params["freq"], span=self.calc_params["span"])
                    ticker = qcode.split("/")[1]
                    csv = self._to_csv(result)
                    with self._lock:
                        self.fp.write(ticker+","+str(self.calc_params["calc_date"])+","+csv+"\n")
            except Exception as e:
                _logger.exception("Error %s for qcode %s"%(str(e), qcode))
            finally:
                self.job_queue.task_done()

    def _to_csv(self,result):
        def _clean_get(val):
            return round(val,2) if not np.isnan(val) else "N/A"
        csvout = ','.join([str(_clean_get(result.get(it,np.nan))) for it in self._itemlist])
        return csvout

        
def launch_jobs(quandl_codes, num_workers, calc_date, authtoken="", freq='M', span=60):
    job_queue = Queue.Queue()
    for b in quandl_codes:
        job_queue.put(b)
    print "Length %d"%job_queue.qsize()
    
    thlist = []
    s_time  = timeit.default_timer()
    fp = open("output.csv","w")
    heading = "Ticker, Date, "+",".join(Worker._itemlist)+"\n"
    fp.write(heading)
    
    s_date = dutil.shift_months(calc_date, -(span+6))
    trim_start = s_date.strftime('%Y-%m-%d')
    trim_end  = calc_date.strftime('%Y-%m-%d')

    calc_param = {"calc_date": calc_date, "freq" : freq, "span":60}
    for i in range(num_workers):
        th = Worker(job_queue, trim_start, trim_end, calc_param, authtoken, fp)
        th.daemon = True
        th.start()
        thlist.append(th)
    print "Finished launching jobs"
    e_time = timeit.default_timer()
    print "Time taken ",(e_time - s_time)
    
    # block until the queue is empty
    job_queue.join()
    

        
        
if __name__ == '__main__':
    filename = sys.argv[1]
    if len(sys.argv)>2:
        authtoken= sys.argv[2]
    else :
        authtoken= None
    df = grab_ticker_list(filename)
    #result = mpt.calculate(datetime.date(2014,8,31),span=12, freq='D')
    l = df["quandl code"].values
    launch_jobs(l, 1, datetime.date(2014,9,30),authtoken)
