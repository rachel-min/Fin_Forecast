# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 00:06:23 2019

@author: seongpar
"""

import datetime as dt
import IALPython3 as IAL
import Lib_Market_Akit as IAL_App
import pandas as pd

##### pull par rates
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


##### generate forward rate term structure
evalDate          = dt.datetime(2019, 9, 30)
endDate          = dt.datetime(2100, 12, 31)
eval_irCurve_USD = IAL_App.createAkitZeroCurve(evalDate, curveType, "USD")
proj_dates       = []
proj_dates.extend(list(pd.date_range(start=evalDate, end=endDate, freq='M')))
proj_fwd_rate    = {}

for each_proj_date in proj_dates:
    fwd_rates = []
    par_dates = IAL.Util.addTerms(each_proj_date, KRD_Term_key)
    for each_date in par_dates:
        fwd_rates.append(base_irCurve_USD.fwdRate(each_proj_date, each_date,"Compounded", "A"))

    proj_fwd_rate.update({each_proj_date : fwd_rates})