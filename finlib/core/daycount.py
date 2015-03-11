__author__ = 'Gouthaman Balaraman'


class DayCount(object):
    """
    Implements the base class for the daycount functionality
    """

    def __init__(self):
        pass

    def days_between(self, date1, date2):
        """

        :param date1:
        :type date1: obj
        :param date2:
        :type date2: obj
        :return:
        """
        raise NotImplementedError("Method days_between needs to be implemented")

    def year_fraction(self):
        raise NotImplementedError("Method year_fraction needs to be implemented")


class Thirty360US(DayCount):

    def days_between(self, date1, date2):
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


class Thirty360EU(DayCount):

    def __init__(self):
        pass

    def days_between(self, date1, date2):
        dd1 = date1.day
        dd2 = date2.day
        mm1 = date1.month
        mm2 = date2.month
        yy1 = date1.year
        yy2 = date2.year

        return 360*(yy2-yy1) + 30*(mm2-mm1-1) + max(0,30-dd1) + min(30,dd2)


class Thirty360IT:

    def __init__(self):
        pass

    def days_between(self, date1, date2):
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





