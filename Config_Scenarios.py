# -*- coding: utf-8 -*-
"""
Created on Thu May 23 16:00:37 2019

@author: seongpar
"""
#import os
#import pandas as pd

Base = { 'Scen_Name'               : 'Base',
         'IR_Stress_Type'          : 'Parallel' ,
         'IR_Parallel_Shift_bps'   : 0,
         'Credit_Spread_Shock_bps' : {'AAA': 0, # AIG Derived Rating
                                      'AA' : 0,
                                      'A'  : 0,
                                      'BBB': 0,
                                      'BB' : 0,
                                      'B'  : 0,
                                      'CCC': 0,
                                      'CC' : 0,
                                      'C'  : 0,
                                      'D'  : 0,
                                  'Average': 0},     
         'Alts_Retrun'             : 0,
         'MLIII_Return'            : 0,
         'PC_PYD'                  : 0,
         'Liab_Spread_Beta'        : 0.65,
         'LT_Reserve'              : 0,
         'Longevity shock'         : 0,
         'Mortality shock'         : 0,	
         'Expense shock_Permanent' : 0,	
         'Expense shock_Inflation' : 0,	
         'Lapse shock'             : 0,	
         'Morbidity shock'         : 0,	
         'Longevity Trend shock'   : 0
        }


Comp = { 'Scen_Name'               : 'Comprehensive',
         'IR_Stress_Type'          : 'Parallel' ,
         'IR_Parallel_Shift_bps'   : -59,
         'Credit_Spread_Shock_bps' : {'AAA': 34, # AIG Derived Rating
                                      'AA' : 55.20,
                                      'A'  : 62.8,
                                      'BBB': 70,
                                      'BB' : 112.4,
                                      'B'  : 192,
                                      'CCC': 342.4,
                                      'CC' : 342.4,
                                      'C'  : 342.4,
                                      'D'  : 342.4,
                                  'Average': 0},
         'Alts_Retrun'             : -0.1395174,
         'MLIII_Return'            : -0.142767256132,
         'PC_PYD'                  : 0.076405094,
         'Liab_Spread_Beta'        : 0.65,
         'LT_Reserve'              : 0,
         'Longevity shock'         : 0,
         'Mortality shock'         : 0,	
         'Expense shock_Permanent' : 0.05,	
         'Expense shock_Inflation' : 0.03,
         'Lapse shock'             : 0,	
         'Morbidity shock'         : 0,	
         'Longevity Trend shock'   : 0
        }
 
Test = { 'Scen_Name'               : 'Test',    #No. 984
         'IR_Stress_Type'          : 'Parallel' ,
         'IR_Parallel_Shift_bps'   : -88,
         'Credit_Spread_Shock_bps' : {'AAA': 244, # AIG Derived Rating
                                      'AA' : 267,
                                      'A'  : 325,
                                      'BBB': 501,
                                      'BB' : 827,
                                      'B'  : 1088,
                                      'CCC': 2090,
                                      'CC' : 2090,
                                      'C'  : 2090,
                                      'D'  : 2090,
                                  'Average': 0},
         'Alts_Retrun'             : -0.25,
         'MLIII_Return'            : -0.26,
         'PC_PYD'                  : 0.1821,
         'Liab_Spread_Beta'        : 0.65,
         'LT_Reserve'              : 0,
         'Longevity shock'         : 0.0109,
         'Mortality shock'         : 0.0022,	
         'Expense shock_Permanent' : 0.09031,	
         'Expense shock_Inflation' : 0.009,
         'Lapse shock'             : 0.0006,	
         'Morbidity shock'         : 0.205257,	
         'Longevity Trend shock'   : 0.0118
        }        
        
        
