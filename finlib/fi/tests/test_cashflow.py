__author__ = 'gbalaraman'
from datetime import date
import unittest
from finlib import CashflowGenerator, FRMCashflowGenerator

class CashflowTest(unittest.TestCase):

    def test_next_cashflow_date(self):
        """
        Test that the cashflow date is calculated correctly based on settle
        """
        cf_date = CashflowGenerator.get_next_cashflow_date(settle_date = date(2014,7,31), delay=24)
        self.assertEquals(cf_date, date(2014, 8, 25))
        cf_date = CashflowGenerator.get_next_cashflow_date(settle_date = date(2014,7,1), delay=24)
        self.assertEquals(cf_date, date(2014, 7, 25))



class FRMCashflowGeneratorTest(unittest.TestCase):
    def test_frm_cashflow(self):
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

