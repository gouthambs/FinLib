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
        expected_results = {'informationRatioM60': 0.79810119186058026, 'betaM60': 0.93224392818136081,
                            'upsideCaptureM60': 1.4036787750142616, 'trackingErrorM60': 0.22330665892317705,
                            'annualizedReturnM60': 0.36728868974871376, 'sharpeRatioM60': 1.3601833060407424,
                            'rSquaredM60': 0.23863490127189801, 'alphaM60': 0.17822131063699168,
                            'momentumM60': 3.778604707486017,
                            'standardDeviationM60': 0.25570896877103694, 'treynorRatioM60': 0.37309019668894428,
                            'sortinoRatioM60': 2.2842438222622872, 'downsideCaptureM60': 0.77822666050279499}

        for key in expected_results.keys():
            e = expected_results[key]
            r = results[key]
            self.assertAlmostEqual(e, r, 15, "Failed for %s: expected %17.16f got %17.16f" % (key,e, r))
        

    def test_momentum_only(self):
        mpt = MPTStats(AAPL, None, None)
        results = mpt.calculate(date(2014, 6, 30), span=60, calc_code=MPTStats.MOMENTUM)
        expected_results = {'informationRatioM60': None, 'betaM60': None,
                            'upsideCaptureM60': None, 'trackingErrorM60': None,
                            'annualizedReturnM60': 0.36728868974871376, 'sharpeRatioM60': None,
                            'rSquaredM60': None, 'alphaM60': None,
                            'momentumM60': 3.778604707486017, 'standardDeviationM60': None,
                            'treynorRatioM60': None, 'sortinoRatioM60': None,
                            'downsideCaptureM60': None}

        for key in ['momentumM60', 'annualizedReturnM60']:
            e = expected_results[key]
            r = results[key]
            self.assertAlmostEqual(e, r, 15, "Failed for %s: expected %17.16f got %17.16f" % (key,e, r))
            
        allkeys = expected_results.keys()
        allkeys.remove('momentumM60')
        allkeys.remove('annualizedReturnM60')
        for key in allkeys:
            self.assertEqual(results[key],None, "%s value is not None" % key)

