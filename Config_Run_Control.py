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

# LOC SFS Limit
version['2018Q4_Base'].proj_schedule[1]['LOC_SFS_Limit']  = 0.248285375
version['2018Q4_Base'].proj_schedule[2]['LOC_SFS_Limit']  = 0.252029898
version['2018Q4_Base'].proj_schedule[3]['LOC_SFS_Limit']  = 0.285955276
version['2018Q4_Base'].proj_schedule[4]['LOC_SFS_Limit']  = 0.38330347
version['2018Q4_Base'].proj_schedule[5]['LOC_SFS_Limit']  = 0.441096663
version['2018Q4_Base'].proj_schedule[6]['LOC_SFS_Limit']  = 0.460419183
version['2018Q4_Base'].proj_schedule[7]['LOC_SFS_Limit']  = 0.470052356
version['2018Q4_Base'].proj_schedule[8]['LOC_SFS_Limit']  = 0.462474131
version['2018Q4_Base'].proj_schedule[9]['LOC_SFS_Limit']  = 0.448079715
version['2018Q4_Base'].proj_schedule[10]['LOC_SFS_Limit'] = 0.42905067
version['2018Q4_Base'].proj_schedule[11]['LOC_SFS_Limit'] = 0.401161493
version['2018Q4_Base'].proj_schedule[12]['LOC_SFS_Limit'] = 0.374517694
version['2018Q4_Base'].proj_schedule[13]['LOC_SFS_Limit'] = 0.354974144
version['2018Q4_Base'].proj_schedule[14]['LOC_SFS_Limit'] = 0.312988995
version['2018Q4_Base'].proj_schedule[15]['LOC_SFS_Limit'] = 0.298355834
version['2018Q4_Base'].proj_schedule[16]['LOC_SFS_Limit'] = 0.301492895
version['2018Q4_Base'].proj_schedule[17]['LOC_SFS_Limit'] = 0.294050736
version['2018Q4_Base'].proj_schedule[18]['LOC_SFS_Limit'] = 0.284305953
version['2018Q4_Base'].proj_schedule[19]['LOC_SFS_Limit'] = 0.274386361
version['2018Q4_Base'].proj_schedule[20]['LOC_SFS_Limit'] = 0.264800284
version['2018Q4_Base'].proj_schedule[21]['LOC_SFS_Limit'] = 0.257449286
#version['2018Q4_Base'].proj_schedule[22]['LOC_SFS_Limit'] = 0.253203818
#version['2018Q4_Base'].proj_schedule[23]['LOC_SFS_Limit'] = 0.248658944
#version['2018Q4_Base'].proj_schedule[24]['LOC_SFS_Limit'] = 0.240894683
#version['2018Q4_Base'].proj_schedule[25]['LOC_SFS_Limit'] = 0.235788524
#version['2018Q4_Base'].proj_schedule[26]['LOC_SFS_Limit'] = 0.224783331
#version['2018Q4_Base'].proj_schedule[27]['LOC_SFS_Limit'] = 0.218340687
#version['2018Q4_Base'].proj_schedule[28]['LOC_SFS_Limit'] = 0.214482419
#version['2018Q4_Base'].proj_schedule[29]['LOC_SFS_Limit'] = 0.209553337
#version['2018Q4_Base'].proj_schedule[30]['LOC_SFS_Limit'] = 0.208785641
#version['2018Q4_Base'].proj_schedule[31]['LOC_SFS_Limit'] = 0.211190424
#version['2018Q4_Base'].proj_schedule[32]['LOC_SFS_Limit'] = 0.210920573
#version['2018Q4_Base'].proj_schedule[33]['LOC_SFS_Limit'] = 0.216687659
#version['2018Q4_Base'].proj_schedule[34]['LOC_SFS_Limit'] = 0.222172075
#version['2018Q4_Base'].proj_schedule[35]['LOC_SFS_Limit'] = 0.227580018
#version['2018Q4_Base'].proj_schedule[36]['LOC_SFS_Limit'] = 0.232088173
#version['2018Q4_Base'].proj_schedule[37]['LOC_SFS_Limit'] = 0.236832925
#version['2018Q4_Base'].proj_schedule[38]['LOC_SFS_Limit'] = 0.241751243
#version['2018Q4_Base'].proj_schedule[39]['LOC_SFS_Limit'] = 0.245726161
#version['2018Q4_Base'].proj_schedule[40]['LOC_SFS_Limit'] = 0.248599255
#version['2018Q4_Base'].proj_schedule[41]['LOC_SFS_Limit'] = 0.248058163
#version['2018Q4_Base'].proj_schedule[42]['LOC_SFS_Limit'] = 0.246790226
#version['2018Q4_Base'].proj_schedule[43]['LOC_SFS_Limit'] = 0.24740993
#version['2018Q4_Base'].proj_schedule[44]['LOC_SFS_Limit'] = 0.247595613
#version['2018Q4_Base'].proj_schedule[45]['LOC_SFS_Limit'] = 0.247582842
#version['2018Q4_Base'].proj_schedule[46]['LOC_SFS_Limit'] = 0.244536254
#version['2018Q4_Base'].proj_schedule[47]['LOC_SFS_Limit'] = 0.254065247
#version['2018Q4_Base'].proj_schedule[48]['LOC_SFS_Limit'] = 0.246678196
#version['2018Q4_Base'].proj_schedule[49]['LOC_SFS_Limit'] = 0.242226328
#version['2018Q4_Base'].proj_schedule[51]['LOC_SFS_Limit'] = 0.242866482
#version['2018Q4_Base'].proj_schedule[52]['LOC_SFS_Limit'] = 0.244004135
#version['2018Q4_Base'].proj_schedule[53]['LOC_SFS_Limit'] = 0.301949013
#version['2018Q4_Base'].proj_schedule[54]['LOC_SFS_Limit'] = 0.244575476
#version['2018Q4_Base'].proj_schedule[55]['LOC_SFS_Limit'] = 0.244081956
#version['2018Q4_Base'].proj_schedule[56]['LOC_SFS_Limit'] = 0.243021021
#version['2018Q4_Base'].proj_schedule[57]['LOC_SFS_Limit'] = 0.250817216
#version['2018Q4_Base'].proj_schedule[58]['LOC_SFS_Limit'] = 0.252697673
#version['2018Q4_Base'].proj_schedule[59]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[60]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[61]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[62]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[63]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[64]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[65]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[66]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[67]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[68]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[69]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[70]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[71]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[72]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[73]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[74]['LOC_SFS_Limit'] = 0.200005319
#version['2018Q4_Base'].proj_schedule[75]['LOC_SFS_Limit'] = 0.200006653
#version['2018Q4_Base'].proj_schedule[76]['LOC_SFS_Limit'] = 0.200011781
#version['2018Q4_Base'].proj_schedule[77]['LOC_SFS_Limit'] = 0.2
#version['2018Q4_Base'].proj_schedule[78]['LOC_SFS_Limit'] = 0.2
#version['2018Q4_Base'].proj_schedule[79]['LOC_SFS_Limit'] = 0.2
#version['2018Q4_Base'].proj_schedule[80]['LOC_SFS_Limit'] = 0.2


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
