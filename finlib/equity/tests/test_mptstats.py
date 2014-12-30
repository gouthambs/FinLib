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

    def test_analytics(self):
        mpt = MPTStats(AAPL, SP500, TREASURYRATE)
        results = mpt.calculate(date(2014, 6, 30), span=60)
        expected_results = {'InformationRatio_M_60': 0.79810119186058026, 'Beta_M_60': 0.93224392818136081,
                            'UpsideCapture_M_60': 140.36787750142616, 'TrackingError_M_60': 22.330665892317704,
                            'AnnualizedReturn_M_60': 36.728868974871375, 'SharpeRatio_M_60': 1.3601833060407424,
                            'RSquared_M_60': 23.863490127189802, 'Alpha_M_60': 17.822131063699167,
                            'Momentum_M_60': 377.8604707486017, 'StandardDeviation_M_60': 25.570896877103692,
                            'TreynorRatio_M_60': 0.37309019668894428, 'SortinoRatio_M_60': 2.2842438222622872,
                            'DownsideCapture_M_60': 77.822666050279494}
        self.assertDictEqual(results, expected_results)
