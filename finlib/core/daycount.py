__author__ = 'Gouthaman Balaraman'


class DayCount(object):
    """
    Implements the base class for the daycount functionality
    """

    def __init__(self):
        pass

    @classmethod
    def days_between(self, date1, date2):
        """
        The number of days between two dates
        :param date1:
        :type date1: obj
        :param date2:
        :type date2: obj
        :return: Number of days measured as (date2 - date1)
        """
        raise NotImplementedError("Method days_between needs to be implemented")

    @classmethod
    def year_fraction(self):
        raise NotImplementedError("Method year_fraction needs to be implemented")


class Thirty360(DayCount):
    """
    The 30/360 daycount convetion used in the USA
    """

    @classmethod
    def days_between(cls, date1, date2):
        """
        The number of days between two dates
        :param date1:
        :type date1: obj
        :param date2:
        :type date2: obj
        :return: Number of days measured as (date2 - date1)
        """
        dd1 = date1.day
        dd2 = date2.day
        mm1 = date1.month
        mm2 = date2.month
        yy1 = date1.year
        yy2 = date2.year

        if (dd2 == 31) and (dd1 < 30):
            dd2 = 1
            mm2 += 1

        return 360*(yy2-yy1) + 30*(mm2-mm1-1) + max(0, 30-dd1) + min(30, dd2)

    @classmethod
    def year_fraction(cls, date1, date2):
        return float(cls.days_between(date1, date2))/360.0

class ThirtyE360(DayCount):
    """
    The 30E/360 daycount convention used in the Euro region.
    """

    def __init__(self):
        pass

    @classmethod
    def days_between(cls, date1, date2):
        dd1 = date1.day
        dd2 = date2.day
        mm1 = date1.month
        mm2 = date2.month
        yy1 = date1.year
        yy2 = date2.year

        return 360*(yy2-yy1) + 30*(mm2-mm1-1) + max(0, 30-dd1) + min(30, dd2)

    @classmethod
    def year_fraction(cls, date1, date2):
        return float(cls.days_between(date1, date2))/360.0


class ThirtyIT360:
    """
    The 30/360 convention used in Italy
    """

    def __init__(self):
        pass

    @classmethod
    def days_between(cls, date1, date2):
        dd1 = date1.day
        dd2 = date2.day
        mm1 = date1.month
        mm2 = date2.month
        yy1 = date1.year
        yy2 = date2.year

        if (mm1 == 2) and (dd1 > 27):
            dd1 = 30
        if (mm2 == 2) and (dd2 > 27):
            dd2 = 30
        return 360*(yy2-yy1) + 30*(mm2-mm1-1) + max(0, 30-dd1) + min(30, dd2)

    @classmethod
    def year_fraction(cls, date1, date2):
        return float(cls.days_between(date1, date2))/360.0




