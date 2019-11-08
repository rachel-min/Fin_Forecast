# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 01:07:39 2019

@author: seongpar
"""
import Class_CFO as cfo
import datetime as dt


version = { '2018Q4_Base' : cfo.run_control(val_date   = dt.datetime(2018, 12, 31), 
                                            date_start = dt.datetime(2019, 12, 31), 
                                            date_end   = dt.datetime(2039, 12, 31),
                                            freq       = 'A'),

            '2019Q1_Base' : cfo.run_control(val_date   = dt.datetime(2019,  3, 31), 
                                            date_start = dt.datetime(2019, 12, 31), 
                                            date_end   = dt.datetime(2039, 12, 31),
                                            freq       = 'A')
            }


### Update assumptions as needed #####

# Dividend Schedule
version['2018Q4_Base'].proj_schedule[1]['dividend_schedule']     = 'Y'
version['2018Q4_Base'].proj_schedule[1]['dividend_schedule_amt'] = 500000000
version['2018Q4_Base'].proj_schedule[2]['dividend_schedule']     = 'Y'
version['2018Q4_Base'].proj_schedule[2]['dividend_schedule_amt'] = 1000000000
version['2018Q4_Base'].proj_schedule[3]['dividend_schedule']     = 'Y'
version['2018Q4_Base'].proj_schedule[3]['dividend_schedule_amt'] = 1000000000


# Initial and Ultimate Spread
version['2018Q4_Base'].initial_spread = {
    'Term' : [1,	2,	3,	5,	7,	10,	20,	30 ],
    'AAA'  : [ 0.0016,	0.0028,	0.0035,	0.0037,	0.0042,	0.0054,	0.0069,	0.0084 ],
    'AA'   : [ 0.0019,	0.0034,	0.0042,	0.0048,	0.0055,	0.007,	0.0085,	0.0099 ],
    'A'	   : [ 0.0023,	0.0042,	0.0052,	0.0062,	0.0095,	0.0109,	0.0105,	0.0127 ],
    'BBB'  : [ 0.0044,	0.0082,	0.0092,	0.0114,	0.0156,	0.0162,	0.0161,	0.0183 ],
    'BB'   : [ 0.012,	0.0162,	0.0193,	0.0234,	0.0267,	0.0306,	0.0337,	0.0368 ],
    'B'	   : [ 0.0183,	0.0237,	0.0277,	0.0331,	0.0373,	0.0421,	0.046,	0.0499 ],
    'CCC'  : [ 0.0546,	0.0579,	0.0602,	0.0631,	0.0655,	0.0684,	0.0705,	0.0726 ]
}

version['2018Q4_Base'].ultimate_spread = {
    'Term' : [1,	2,	3,	5,	7,	10,	20,	30 ],
    'AAA'  : [ 0.0049,	0.0053,	0.0058,	0.0065,	0.0066,	0.0062,	0.0065,	0.008],
    'AA'   : [ 0.0053,	0.0059,	0.0066,	0.0076,	0.0081,	0.0081,	0.0091,	0.0107 ],
    'A'	   : [ 0.0073,	0.0081,	0.009,	0.0106,	0.0114,	0.0117,	0.0134,	0.0154 ],
    'BBB'  : [ 0.0123,	0.0136,	0.0149,	0.0173,	0.0187,	0.0196,	0.0219,	0.0238 ],
    'BB'   : [ 0.0295,	0.0311,	0.0328,	0.0357,	0.0375,	0.0386,	0.0407,	0.0421 ],
    'B'	   : [ 0.0492,	0.0569,	0.059,	0.0626,	0.0647,	0.0661,	0.068,	0.0681 ],
    'CCC'  : [ 0.1221,	0.1255,	0.1269,	0.1288,	0.1287,	0.1263,	0.1196,	0.1129 ]
}
