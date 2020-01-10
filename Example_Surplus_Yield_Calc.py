# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 14:44:26 2019

@author: seongpar
"""
import datetime as dt
import Lib_Market_Akit   as IAL_App
import IALPython3 as IAL
import numpy as np

valDate    = dt.datetime(2018, 12, 31)
curveType        = "Treasury"
base_irCurve_USD = IAL_App.load_BMA_Risk_Free_Curves(valDate)  

# Initial and Ultimate Spread
initial_spread = {
    'Term' : [1,	2,	3,	5,	7,	10,	20,	30 ],
    'AAA'  : [ 0.0016,	0.0028,	0.0035,	0.0037,	0.0042,	0.0054,	0.0069,	0.0084 ],
    'AA'   : [ 0.0019,	0.0034,	0.0042,	0.0048,	0.0055,	0.007,	0.0085,	0.0099 ],
    'A'	   : [ 0.0023,	0.0042,	0.0052,	0.0062,	0.0095,	0.0109,	0.0105,	0.0127 ],
    'BBB'  : [ 0.0044,	0.0082,	0.0092,	0.0114,	0.0156,	0.0162,	0.0161,	0.0183 ],
    'BB'   : [ 0.012,	0.0162,	0.0193,	0.0234,	0.0267,	0.0306,	0.0337,	0.0368 ],
    'B'	   : [ 0.0183,	0.0237,	0.0277,	0.0331,	0.0373,	0.0421,	0.046,	0.0499 ],
    'CCC'  : [ 0.0546,	0.0579,	0.0602,	0.0631,	0.0655,	0.0684,	0.0705,	0.0726 ]
}

ultimate_spread = {
    'Term' : [1,	2,	3,	5,	7,	10,	20,	30 ],
    'AAA'  : [ 0.0049,	0.0053,	0.0058,	0.0065,	0.0066,	0.0062,	0.0065,	0.008],
    'AA'   : [ 0.0053,	0.0059,	0.0066,	0.0076,	0.0081,	0.0081,	0.0091,	0.0107 ],
    'A'	   : [ 0.0073,	0.0081,	0.009,	0.0106,	0.0114,	0.0117,	0.0134,	0.0154 ],
    'BBB'  : [ 0.0123,	0.0136,	0.0149,	0.0173,	0.0187,	0.0196,	0.0219,	0.0238 ],
    'BB'   : [ 0.0295,	0.0311,	0.0328,	0.0357,	0.0375,	0.0386,	0.0407,	0.0421 ],
    'B'	   : [ 0.0492,	0.0569,	0.059,	0.0626,	0.0647,	0.0661,	0.068,	0.0681 ],
    'CCC'  : [ 0.1221,	0.1255,	0.1269,	0.1288,	0.1287,	0.1263,	0.1196,	0.1129 ]
}

ultimate_period = 5


# Debugging
FI_surplus_model_port    = {'Port1' : {'Maturity' : 6, 'Rating' : 'A', 'Weight' : 0.5}, 'Port2': {'Maturity' : 6, 'Rating' : 'BBB', 'Weight' : 0.5}}
eval_date  = dt.datetime(2018, 12, 31)
#FI_surplus_model_port    = {'Port1' : {'Maturity' : 6, 'Rating' : 'A', 'Weight' :1.0}}
proj_year_frac = IAL.Date.yearFrac("ACT/365",  valDate, eval_date)
weighted_yield = 0


###self.FI_surplus_model_port    = {'Port1' : {'Maturity' : '6Y', 'Rating' : 'A', 'Weight' : 0.5}, 'Port2': {'Maturity' : '6Y', 'Rating' : 'BBB', 'Weight' : 0.5}}
for each_port, each_target in FI_surplus_model_port.items():
    print(each_port, each_target)
    each_maturity          = each_target['Maturity']
    each_maturity_date     = IAL.Util.addTerms(eval_date, [str(each_maturity) + "Y"])[0]
    #each_maturity_date     = IAL.Util.addTerms(eval_date, [str(1) + "Y"])[0]
    initial_spread_terms   = initial_spread[each_target['Rating']]
    ultimate_spread_terms  = ultimate_spread[each_target['Rating']]
    fwd_rate               = base_irCurve_USD.fwdRate(eval_date, each_maturity_date, 'continuous')
    spread_term            = initial_spread['Term']
    
    each_initial_spread  = np.interp(each_maturity, spread_term, initial_spread_terms)
    each_ultimate_spread = np.interp(each_maturity, spread_term, ultimate_spread_terms)
    each_weighted_spread = np.interp(proj_year_frac, [0, ultimate_period], [each_initial_spread, each_ultimate_spread])
    each_yield           = fwd_rate + each_weighted_spread
    weighted_yield      += each_yield * each_target['Weight']
    print(each_initial_spread, each_ultimate_spread, each_weighted_spread, each_yield, weighted_yield)


test_yield = IAL_App.FI_Yield_Model_Port(valDate,                          \
                                        eval_date,                         \
                                        FI_surplus_model_port,             \
                                        initial_spread,                    \
                                        ultimate_spread,                   \
                                        ultimate_period,                   \
                                        curveType = curveType,             \
                                        base_irCurve_USD = base_irCurve_USD) 
