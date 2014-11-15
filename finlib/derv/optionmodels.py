# -*- coding: utf-8 -*-
"""
Created on Wed Oct 29 04:13:54 2014

@author: Gouthaman Balaraman
"""
import numpy as np



class Option(object):
    _option_types = set(["Call", "Put"])
    def __init__(self,**kwargs):
        """
        The constructor for the option
        
        Parameters
        ----------
        strike_price : double
                       The strike price of the option
        spot_price : double
                     The spot price of the option
        maturity_date : datetime.date or datetime.datetime
                        The maturity date of the option
        volatility : double
                     The volatility of the underlying in decimal units
        option_type : str, default "Call"
                      The type of the option, either Call or Put
                             
            
        """
        self.strike_price = kwargs["strike_price"]
        self.spot_price = kwargs["spot_price"]
        self.maturity_date = kwargs["maturity_date"]
        self.volatility = kwargs["volatility"]
        self.option_type = kwargs.get("option_type","Call")
        assert self.option_type in self._option_types
        
        
        
        


class BinomialTree(object):
    
    def __init__(self,num_steps):
        """
        Initializes the recombining binomial tree class
        
        Parameters
        ----------
        num_steps : int
                    The numbers of steps in a binomial tree        
        
        """
        self._num_nodes = num_steps*(num_steps+1)/2
        self._nodes = np.zeros(self._num_nodes)
        
    def __getitem__(self, index):
        """
        The accessor to the binomial tree. For performance reasons, this
        method does no error checking. If the binomial tree has 'n' steps, then
        the index two-tuple will be of the form (i,j) satisfying the condition
        0 <= i <= (n-1) and 0 <= j <= i.
        
        Parameters
        ----------
        index : tuple
                A two-tuple that gives access to the node positioned at index
        """
        
        i,j = index
        ix = i*(i+1)/2 + j 
        #print ix
        return self._nodes[ix]
        
    def __setitem__(self, index, value):
        """
        The setter to the binomial tree. For performance reasons, this
        method does no error checking. If the binomial tree has 'n' steps, then
        the index two-tuple will be of the form (i,j) satisfying the condition
        0 <= i <= (n-1) and 0 <= j <= i.
        
        Parameters
        ----------
        index : tuple
                A two-tuple that gives access to the node positioned at index
        value : double
                The value to be set at the given index
        """
        i,j = index
        ix = i*(i+1)/2 + j 
        #print ix
        self._nodes[ix] = value
        
        
        
class BlackScholesEngine(object):
    
    def __init__(self):
        pass
    
    def calculate(self, option, calc_date, rf_rate=0.0):
        assert type(option) == Option
        from scipy.stats import norm
        dt = (option.maturity_date - calc_date).days/365
        sqrt_dt =  np.sqrt(dt)
        sig_fac = option.volatility*sqrt_dt
        d1 = 1.0/sig_fac*(np.log(option.spot_price/option.strike_price) 
                    + (rf_rate + option.volatility*option.volatility/2.0)*dt  )
        d2 = d1 - sig_fac
        
    
    
        
if __name__ == '__main__':
    bt = BinomialTree(5)
    #bt[5]
    