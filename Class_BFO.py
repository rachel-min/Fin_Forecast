# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 16:17:32 2019

@author: xiagao
"""

import pandas as pd

class basic_fin_account(object):
    
    _not_addable = ['AccountName', 'lobName', 'OpRisk_Chage_pct']
    
    def _summary(self):
        fin_items = vars(self)
        for k in list(fin_items):
            if k in ['AccountName', 'lobName'] or k[0] == '_':
                fin_items.pop(k)
        return pd.Series(fin_items)
   
    def _aggregate(self, individual_obj, exceptions = []):
        
        if type(self) != type(individual_obj):
            raise(TypeError('Merging different types of account!'))
        
        self._not_addable += exceptions

        fin_items = vars(individual_obj)
        for k in fin_items.keys():
            if k in self._not_addable or k[0] == '_':
                continue
            try:
                setattr(self, k, getattr(self, k) + getattr(individual_obj, k))
            except(AttributeError):
                print('Individual LOB has no item', k)
            
