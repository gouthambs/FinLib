# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 12:40:10 2014

@author: Gouthaman Balaraman
"""
import unittest
from finlib.equity import MPTStats
from .mockdata import SP500, AAPL, TREASURYRATE
from datetime import date


class MPTStatsTest(unittest.TestCase):
    maxDiff = None
    def test_analytics(self):
        mpt = MPTStats(AAPL, SP500, TREASURYRATE)
        results = mpt.calculate(date(2014, 6, 30), span=60)
        expected_results = {'InformationRatio_M_60': 0.79810119186058026, 'Beta_M_60': 0.93224392818136081,
                            'UpsideCapture_M_60': 1.4036787750142616, 'TrackingError_M_60': 0.22330665892317705,
                            'AnnualizedReturn_M_60': 0.36728868974871376, 'SharpeRatio_M_60': 1.3601833060407424,
                            'RSquared_M_60': 0.23863490127189801, 'Alpha_M_60': 0.17822131063699168,
                            'Momentum_M_60': 3.778604707486017,
                            'StandardDeviation_M_60': 0.25570896877103694, 'TreynorRatio_M_60': 0.37309019668894428,
                            'SortinoRatio_M_60': 2.2842438222622872, 'DownsideCapture_M_60': 0.77822666050279499}

        self.assertDictEqual(results, expected_results)

    def test_momentum_only(self):
        mpt = MPTStats(AAPL, SP500, TREASURYRATE)
        results = mpt.calculate(date(2014, 6, 30), span=60, calc_code=MPTStats.MOMENTUM)
        expected_results = {'InformationRatio_M_60': None, 'Beta_M_60': None,
                            'UpsideCapture_M_60': None, 'TrackingError_M_60': None,
                            'AnnualizedReturn_M_60': 0.36728868974871376, 'SharpeRatio_M_60': None,
                            'RSquared_M_60': None, 'Alpha_M_60': None,
                            'Momentum_M_60': 3.778604707486017, 'StandardDeviation_M_60': None,
                            'TreynorRatio_M_60': None, 'SortinoRatio_M_60': None,
                            'DownsideCapture_M_60': None}
        self.assertDictEqual(results, expected_results)
