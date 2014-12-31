# -*- coding: utf-8 -*-
"""
Created on Sun Nov 02 04:53:45 2014

@author: Goutham
"""

import unittest
from finlib.derv.optionmodels import BinomialTree



class BinomialTreeTest(unittest.TestCase):
    
    
    
    def test_allocation(self):
        bt = BinomialTree(10)
        expected_length = 10*(11)/2
        self.assertEqual(len(bt._nodes),expected_length,
                         "Incorrect memory size")

    def test_setitem(self):
        bt = BinomialTree(10)
        for i in range(10):
            for j in range(i):
                bt[i,j] = i*j
        
        for i in range(10):
            for j in range(i):
                self.assertEqual(bt._nodes[i*(i+1)/2 + j], i*j)
                
    def test_getitem(self):
        bt = BinomialTree(10)
        for i in range(10):
            for j in range(i):
                bt[i,j] = i*j
        
        for i in range(10):
            for j in range(i):
                self.assertEqual(bt._nodes[i*(i+1)/2 + j], bt[i,j])
                self.assertEqual(i*j, bt[i,j])
        