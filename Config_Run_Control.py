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
version['2018Q4_Base'].proj_schedule[1]['dividend_schedule']     = 'Y'
version['2018Q4_Base'].proj_schedule[1]['dividend_schedule_amt'] = 500000000
version['2018Q4_Base'].proj_schedule[2]['dividend_schedule']     = 'Y'
version['2018Q4_Base'].proj_schedule[2]['dividend_schedule_amt'] = 1000000000
version['2018Q4_Base'].proj_schedule[3]['dividend_schedule']     = 'Y'
version['2018Q4_Base'].proj_schedule[3]['dividend_schedule_amt'] = 1000000000
