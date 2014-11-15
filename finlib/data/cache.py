# -*- coding: utf-8 -*-
"""
Created on Wed Oct 29 04:27:05 2014

@author: Gouthaman Balaraman
"""




class ShelveCache(object):
    
    def __init__(self,**kwargs):
        self._is_open = False
        self.open_cache(**kwargs)
        
    def has_key(self, key):
        self._cache.has_key(key)
        
        
    def get(self,key, default=None):
        
        if self._is_open and self._cache.has_key(key):
            return self._cache[key]
        else:
            return default
            
    def set(self, key, val):
        if self._is_open :
            self._cache[key] = val
        else:
            raise RuntimeError("Shelve cache is not open")
        
    def close_cache(self):
        if self._is_open:
            self._cache.close()
            self._is_open = False
            self._cache = None

        
    def open_cache(self, **kwargs):
        import shelve
        if not self._is_open:
            self._cache = shelve.open(**kwargs)
            self._is_open = True
            
            
