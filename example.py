# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 14:08:51 2014

@author: gbalaraman
"""
import pandas as pd
import numpy as np
from dateutil import relativedelta
from finlib.cashflow import FRMCashflowGenerator
from datetime import date

data_dict = dict(settle_date=date(2014,7,31),
                         gwac=4.005,
                         coupon=3.5,
                         wam=330,
                         wala=24,
                         term=360,
                         current_balance=0.77895414829254150,
                         delay=24
                         )
cfgen = FRMCashflowGenerator(data_dict)
df = cfgen.generate_cashflow()
print df.head()
print df.tail()

from timeit import Timer
setup = """
import numpy as np
import pandas as pd
"""
numpy_code = """
data = np.ones(shape=(360,),dtype=[('A', np.float),('B', np.float),('C', np.float)])
"""
pandas_code ="""
df =pd.DataFrame(np.ones(shape=(360,),dtype=[('A', np.float),('B', np.float),('C', np.float)]))
"""
print "Numpy",min(Timer(numpy_code,setup=setup).repeat(10,1))*10**6,"micro-seconds"
print "Pandas",min(Timer(pandas_code,setup=setup).repeat(10,1))*10**6,"micro-seconds"