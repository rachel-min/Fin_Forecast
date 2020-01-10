# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 16:17:32 2019

@author: xiagao
"""

import pandas as pd
import inspect

class basic_fin_account(object):
    
    #_log = {} # Must be private variable
    
    def __init__(self):
        self._log = {}
    
    _not_addable = ['AccountName', 'lobName', 'OpRisk_Chage_pct']
    
    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name.startswith("_") or name in self._not_addable:
            return
        _fun = inspect.currentframe().f_back.f_code.co_name
        if name in self._log.keys():
            self._log[name].append(_fun)
        else:
            self._log[name] = [_fun]

    def trace(self, name):
        if name in self._log.keys():
            return pd.unique(self._log[name])
        else:
            return "Variable don't exist or no record !"
    
    def _summary(self):
        fin_items = vars(self)
        for k in list(fin_items):
            if k in ['AccountName', 'lobName'] or k[0] == '_':
                fin_items.pop(k)
        return pd.Series(fin_items)
   
    def _aggregate(self, individual_obj, exceptions = []):
        
        if type(self) != type(individual_obj):
            raise(TypeError('Merging different types of account!'))
        
        _not_addable = exceptions + self._not_addable

        fin_items = vars(individual_obj)
        for k in fin_items.keys():
            if k in _not_addable or k[0] == '_':
                continue
            try:
                setattr(self, k, getattr(self, k) + getattr(individual_obj, k))
            except(AttributeError):
                print(self.AccountName, 'Individual LOB has no item', k)
            
