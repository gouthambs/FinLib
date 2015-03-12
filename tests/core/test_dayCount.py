from unittest import TestCase

__author__ = 'Gouthaman Balaraman'

from finlib.core.daycount import DayCount, Thirty360, ThirtyE360, ThirtyIT360
import datetime as dt


class TestDayCount(TestCase):

    def test_days_between(self):
        dc = DayCount
        with self.assertRaises(NotImplementedError) as context:
            dc.days_between(dt.date(2014, 1, 1), dt.date(2014, 1, 5))

    def test_year_fraction(self):
        dc = DayCount()
        with self.assertRaises(NotImplementedError) as context:
            dc.year_fraction()


class TestThirty360(TestCase):

    def _results_days_between(self):
        return [4, 6, 30, 360, 154, 30, 27]

    def _setup_daycout(self):
        self.dc = Thirty360

    def setUp(self):
        self.dates = [(dt.date(2014, 1, 1), dt.date(2014, 1, 5)),
                      (dt.date(2014, 2, 25), dt.date(2014, 3, 1)),
                      (dt.date(2014, 3, 1), dt.date(2014, 4, 1)),
                      (dt.date(2014, 1, 1), dt.date(2015, 1, 1)),
                      (dt.date(2014, 1, 1), dt.date(2014, 6, 5)),
                      (dt.date(2014, 7, 1), dt.date(2014, 7, 31)),
                      (dt.date(2014, 2, 1), dt.date(2014, 2, 28))]
        self._setup_daycout()

    def test_days_between(self):
        res = self._results_days_between()
        for i, dates in enumerate(self.dates):
            days = self.dc.days_between(dates[0], dates[1])
            self.assertEquals(days, res[i])

    def test_year_fraction(self):
        res = self._results_days_between()
        for i, dates in enumerate(self.dates):
            yf = self.dc.year_fraction(dates[0], dates[1])
            self.assertEquals(yf, res[i]/360.0)


class TestThirtyE360(TestThirty360):

    def _results_days_between(self):
        return [4, 6, 30, 360, 154, 29, 27]

    def _setup_daycout(self):
        self.dc = ThirtyE360

class TestThirtyIT360(TestThirty360):

    def _results_days_between(self):
        return [4, 6, 30, 360, 154, 29, 29]

    def _setup_daycout(self):
        self.dc = ThirtyIT360