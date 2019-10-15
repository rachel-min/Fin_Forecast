# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 00:06:23 2019

@author: seongpar
"""

import datetime as dt
import IALPython3 as IAL
import Lib_Market_Akit as IAL_App

valDate          = dt.datetime(2019, 7, 31)
KRD_Term         = IAL_App.KRD_Term
KRD_Term_key     = list(KRD_Term.keys())
par_dates        = IAL.Util.addTerms(valDate, KRD_Term_key)
par_rates        = []
curveType        = "Treasury"
base_irCurve_USD = IAL_App.createAkitZeroCurve(valDate, curveType, "USD")

for each_date in par_dates:
    par_rates.append(base_irCurve_USD.parRate(valDate, each_date, "A"))

print(par_rates)