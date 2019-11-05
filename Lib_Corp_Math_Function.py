# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 17:13:30 2019

@author: seongpar
"""


def Step_Range_Factor(amount, range_factor):
   
    agg_value        = 0
    agg_value_factor = 0
    
    for range_key, range_value in range_factor.items():
        each_value        = min(range_key, amount) - agg_value
        each_value_factor = each_value * range_value

        agg_value        += each_value
        agg_value_factor += each_value_factor

    return agg_value_factor


