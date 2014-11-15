__author__ = 'gbalaraman'
from dateutil.relativedelta import  relativedelta
import pandas as pd
import numpy as np
import logging
_logger = logging.getLogger("FinLib")


class CashFlow(object):

    def __init__(self):
        pass


#class CashFlow

class CashflowGenerator(object):
    def __init__(self):
        pass

    def _allocate_cashflows(self, wam, start_date, columns):
        df = pd.DataFrame(index=pd.DatetimeIndex(start=start_date, periods=wam, freq='M'),
                          columns=columns, dtype=float)
        return df

    @staticmethod
    def get_next_cashflow_date(settle_date, delay, offset_months=0):
        """
        Calculate the next cashflow date from a give settlement date
        :param settle_date: Settlement date
        :type settle_date: datetime
        :param delay: Days delay
        :type delay: unsigned int
        :param offset_months: Offset in months
        :type offset_months: int
        :return: The next cashflow date for the given settlement date
        """
        delay_plus_one = delay+1
        day = settle_date.day
        offset = 1 + offset_months if (delay_plus_one <= day) and (delay > 0) else offset_months
        date = settle_date + relativedelta(months=offset)
        date = date.replace(day=delay_plus_one)
        return date






class FRMCashflowGenerator(CashflowGenerator):

    def __init__(self, data_dict):
        """

        :param data_dict: Required items are: coupon, wam, wala, term, settle_date

        :return:
        """
        self.data_dict = data_dict

    def _prepare(self):
        try:
            frequency = self.data_dict.get("frequency", 12)

            coupon = self.data_dict["coupon"]
            gwac = self.data_dict["gwac"]
            self._net_per_period = coupon/(100.0*frequency)
            self._gross_per_period = gwac/(100.0*frequency)

            self._wam  = self.data_dict["wam"]
            self._wala = self.data_dict["wala"]
            self._term = self.data_dict["term"]
            self._settle_date = self.data_dict["settle_date"]
            self._settle_balance = self.data_dict["current_balance"]
            # optional

            self._delay = self.data_dict.get("delay", 0)
            self._amort_wam = self.data_dict.get("amortwam", self._wam)

            self._cpn_to_period = np.power(self._gross_per_period + 1.0, self._wala)
            self._cpn_to_life = np.power(self._gross_per_period + 1.0, self._wala + self._amort_wam)
        except KeyError as e:
            _logger.exception(str(e))
            raise e

    def generate_cashflow(self):
        self._prepare()
        self._columns = ("ScheduledPrincipal", "Prepayments", "TotalPrincipal", 
                         "Interest", "Total", "Balance")
        cf_start_date = self.get_next_cashflow_date(self._settle_date, self._delay)
        df = self._allocate_cashflows(self._wam,cf_start_date, self._columns)
        return self._do_cashflow_calculation(df)

    def _do_cashflow_calculation(self, df):
        curr_balance = self._settle_balance
        cpn_to_period = self._cpn_to_period

        for i in np.arange(0, self._wam):
            #cf_date = self.get_next_cashflow_date(self._settle_date, self._delay, i)
            interest = curr_balance * self._net_per_period
            scheduled = curr_balance*self._gross_per_period/(self._cpn_to_life/cpn_to_period - 1.0)
            total = interest + scheduled
            #"Date", "Principal", "Interest", "Prepayments", "Loss", "Total", "Balance"
            df.ix[i] = (scheduled, 0.0, scheduled, interest, total, curr_balance - scheduled)
            curr_balance -= scheduled
            cpn_to_period *= (1.0 + self._gross_per_period)
        return df







