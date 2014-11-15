import numpy as np
cimport numpy as np
DATETIME_DTYPE = np.datetime64

def shift_months()


def get_next_cashflow_date(np.datetime64 settle_date, int delay, int offset_months=0):    
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
    cdef int delay_plus_one = delay+1
    cdef int day = settle_date.day
    cdef offset = 1 + offset_months if (delay_plus_one <= day) and (delay > 0)\
                    else offset_months
    date = settle_date + relativedelta(months=offset)
    date = date.replace(day=delay_plus_one)
    return date
