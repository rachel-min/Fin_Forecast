import os
import pandas as pd
import datetime
import numpy as np
from pandas.tseries.offsets import MonthEnd
os.sys.path
# load akit DLL into python
akit_dir = 'C:/AKit v4.1.0/BIN'
os.sys.path.append(akit_dir)
import MktPython3 as MKT
import IALPython3 as IAL

tsyCurveDict = {'USD': 'IR.USD.GOVT.NOMINAL.ZERO.BASE',
                'EUR': 'IR.EUR.GOVT.NOMINAL.ZERO.BASE',
                'GBP': 'IR.GBP.GOVT.NOMINAL.ZERO.BASE',
                'JPY': 'IR.JPY.GOVT.NOMINAL.ZERO.BASE',
                'AUD': 'IR.AUD.GOVT.NOMINAL.ZERO.BASE'}

swapCurveDict = {'USD': 'IR.USD.LIBOR.3M.ZERO.BASE',
                 'EUR': 'IR.EUR.EURIBOR.6M.ZERO.BASE',
                 'GBP': 'IR.GBP.LIBOR.6M.ZERO.BASE',
                 'JPY': 'IR.JPY.LIBOR.6M.ZERO.BASE',
                 'AUD': 'IR.AUD.BBSW.6M.ZERO.BASE'}


CreditYieldDict = {'AAA' : 'CR.USD.CORP.ALLSEC.AAA.ZERO.BASE',
                   'AA'  : 'CR.USD.CORP.ALLSEC.AA.ZERO.BASE',
                   'A'   : 'CR.USD.CORP.ALLSEC.A.ZERO.BASE',
                   'BBB' : 'CR.USD.CORP.ALLSEC.BBB.ZERO.BASE',
                   'BB'  : 'CR.USD.CORP.ALLSEC.BB.ZERO.BASE',
                   'CCC' : 'CR.USD.CORP.ALLSEC.CCC.ZERO.BASE' }

marketIndexDict = {'US_Equity' : "EQ.USD.IDX.SPX.SPOT.BASE"}

PE_Return_Model = {'alpha' : 0.016, 'beta': 0.8 }

BMA_ccy_map     = {'USD': 'BMA risk free', "GBP" : 'UK'}
BMA_curve_dir   = 'L:\DSA Re\Workspace\Production\EBS Dashboard\Python_Code\BMA_Curves'

BMA_curve_file  = {datetime.datetime(2018, 12, 28): 'BMA_Curves_20181228.xlsx',
                   datetime.datetime(2018, 12, 31): 'BMA_Curves_20181231.xlsx',
                   datetime.datetime(2019, 3, 29) : 'BMA_Curves_20190329.xlsx',
                   datetime.datetime(2019, 3, 31) : 'BMA_Curves_20190331.xlsx',
                   datetime.datetime(2019, 6, 28) : 'BMA_Curves_20190628.xlsx',
                   datetime.datetime(2019, 6, 30) : 'BMA_Curves_20190630.xlsx',
                   datetime.datetime(2019, 9, 30) : 'BMA_Curves_20190930.xlsx',
                   datetime.datetime(2019, 12, 31): 'BMA_Curves_20191231.xlsx'}

BMA_ALM_BSCR_shock_file = 'ALM BSCR Shock.xlsx'

KRD_Term        = {"1M"  : 1/12,
                   "2M"  : 2/12,
                   "3M"  : 3/12,
                   "6M"  : 6/12,
                   "9M"  : 9/12,
                   "1Y"  : 1,
                   "2Y"  : 2,
                   "3Y"  : 3,
                   "5Y"  : 5,
                   "7Y"  : 7,
                   "10Y" : 10,
                   "15Y" : 15,
                   "20Y" : 20,
                   "30Y" : 30}
# Get GBP Rate
def get_GBP_rate(EBS_Calc_Date, curvename):
    
    GBP_rate = 1 / MKT.TSR.MarketData(curvename, EBS_Calc_Date, "V")[0]
    
    return GBP_rate

# Need to go to the library
def createAkitZeroCurve(valDate, curveType = "Treasury", ccy= "USD", rating = "BBB", rollforward = "N", rollforward_date = datetime.datetime(2100, 12, 31), IR_shift = 0, shock_type = 0):
    if curveType == "Treasury":
        curveName = tsyCurveDict.get(ccy)

    elif curveType == "Swap":
        curveName = swapCurveDict.get(ccy)

    elif curveType == "Credit":
        curveName = CreditYieldDict.get(rating)

    # Get curve market data from TSR
    curveTerms = MKT.TSR.MarketData(curveName, valDate, "T")
    
    if shock_type != 0:
        os.chdir(BMA_curve_dir)
        work_shock_file     = pd.ExcelFile(BMA_ALM_BSCR_shock_file)
        work_ALM_BSCR_shock = pd.read_excel(work_shock_file, sheet_name = ccy)
        shock          = pd.DataFrame(work_ALM_BSCR_shock[shock_type])
        shock['Tenor'] = shock.index
        
        base_curve           = pd.DataFrame(MKT.TSR.MarketData(curveName, valDate, "V"))
        base_curve['Tenor'] = np.ceil(base_curve.index/12) - 1
        base_curve['Tenor'] = base_curve['Tenor'].clip(lower = 0)
        
        shocked_curve               = base_curve.merge(shock, how='left', on='Tenor')
        shocked_curve['curveRates'] = shocked_curve[0] + shocked_curve[shock_type] * 100
        
        curveRates = list(shocked_curve['curveRates'])
        
    else:
        curveRates = MKT.TSR.MarketData(curveName, valDate, "V")
    
    curveRates_shift = [x + IR_shift / 100.0 for x in curveRates]

    if rollforward == "Y":
        curve_base_date = rollforward_date
    else:
        curve_base_date = valDate

    # Build curve
    curveHandle = IAL.YieldCurve.createFromZeroRates(
        curve_base_date,
        IAL.Util.addTerms(curve_base_date, curveTerms),
        IAL.Util.scale(curveRates_shift, 0.01),
        "CONTINUOUS", "N", "ACT/365", "FF")

    return curveHandle

def Set_Dashboard_MarketFactors(eval_dates, curveType, proxy_term = 7, rating = "BBB", rating_A = "A", KRD_Term = KRD_Term, Currency = "USD"):
    
    colNames      = ['val_date', 'Term', 'IR',"Credit_Rate", "Credit_Spread", 'GBP', 'SPX']
    
    for key, value in KRD_Term.items():
        colNames.append("IR_" + key)    
    
    colNames.append("Credit_Rate_A")
    colNames.append("Credit_Spread_A")
    
    market_factor = pd.DataFrame([],columns = colNames)

    for valDate in eval_dates:
        irCurve          = createAkitZeroCurve(valDate, curveType, Currency)
        CreditCurve      = createAkitZeroCurve(valDate, "Credit", Currency, rating)
      
#        for Y in range (1,11):
#            ir_rate          = irCurve.zeroRate(Y * 365)
#            print(ir_rate)

        ir_rate          = irCurve.zeroRate(proxy_term)            
        credit_rate      = CreditCurve.zeroRate(proxy_term )
        credit_spread    = (credit_rate - ir_rate)*10000
        spx              = get_market_data(valDate, 'US_Equity')
        
        curr_GBP         = get_GBP_rate(valDate, curvename = 'FX.USDGBP.SPOT.BASE')
        
        each_market_data = [valDate, proxy_term, ir_rate, credit_rate, credit_spread, curr_GBP, spx]
        
        
        for key, value in KRD_Term.items():
            each_market_data.append( irCurve.zeroRate(value) )
        
        CreditCurve_A      = createAkitZeroCurve(valDate, "Credit", Currency, rating_A)
        credit_rate_A      = CreditCurve_A.zeroRate(proxy_term )
        credit_spread_A    = (credit_rate_A - ir_rate)*10000
        each_market_data.append(credit_rate_A)
        each_market_data.append(credit_spread_A)
        
        market_factor = market_factor.append(pd.DataFrame([each_market_data], columns = colNames), ignore_index = True)
   
    return market_factor


def load_BMA_Std_Curves(valDate, ccy, revalDate, rollforward = "N", rollforward_date = datetime.datetime(2100, 12, 31), IR_shift = 0, shock_type = 0):

    curr_dir = os.getcwd()
    os.chdir(BMA_curve_dir)
    fileName = BMA_curve_file[valDate]
    work_BMA_file = pd.ExcelFile(fileName)
    work_BMA_curves = pd.read_excel(work_BMA_file)
    work_ccy        = BMA_ccy_map[ccy]
        
    work_maturity = work_BMA_curves['Maturity']
    
    if shock_type != 0:
        work_shock_file     = pd.ExcelFile(BMA_ALM_BSCR_shock_file)
        work_ALM_BSCR_shock = pd.read_excel(work_shock_file, sheet_name = ccy)
        work_rates          = (work_BMA_curves[work_ccy] + work_ALM_BSCR_shock[shock_type]) * 100

    else:
        work_rates = work_BMA_curves[work_ccy] * 100
    
    curve_terms      = []
    curve_term_years = []
    for key, value in work_maturity.items():
        each_term_ary = value.split()
        each_term     = each_term_ary[0] + "Y"
        curve_terms.append(each_term)
        curve_term_years.append(each_term_ary[0])
    
    if valDate == revalDate:
        calc_rates = work_rates 

    else:
        irCurve_val   = createAkitZeroCurve(valDate, "Swap", ccy)
        irCurve_reval = createAkitZeroCurve(revalDate, "Swap", ccy)
           
        reval_rates = []
        
        term_count = len(curve_terms)
        
        for idx in range(0, term_count, 1):    
            val_rate    = work_rates[idx]
            each_term   = float(curve_term_years[idx])
            
            # reflect rate changes up to 30 year ternor and then stay constant
            if idx <= 29:
                swap_change = (irCurve_reval.zeroRate(each_term) - irCurve_val.zeroRate(each_term)) * 100
                
            reval_rates.append( val_rate + swap_change )
        
        calc_rates = reval_rates

    if rollforward == "Y":
        curve_base_date = rollforward_date
    else:
        curve_base_date = revalDate

    curveRates_shift = [x + IR_shift / 100.0 for x in calc_rates]

    curveHandle = IAL.YieldCurve.createFromZeroRates(
        curve_base_date,
        IAL.Util.addTerms(curve_base_date, curve_terms),
        IAL.Util.scale(curveRates_shift, 0.01),
        "CONTINUOUS", "N", "ACT/365", "FF")
    
    os.chdir(curr_dir)
    return curveHandle

def load_BMA_Risk_Free_Curves(valDate): ### Kellie update 07/03/2019

    curr_dir = os.getcwd()
    os.chdir(BMA_curve_dir)
    
    fileName = BMA_curve_file[valDate]
    work_BMA_file = pd.ExcelFile(fileName)
    work_BMA_curves = pd.read_excel(work_BMA_file)
    
    work_maturity = work_BMA_curves['Maturity']
    work_rates    = work_BMA_curves['BMA risk free'] * 100
    
    curve_terms      = []
    curve_term_years = []
    
    for key, value in work_maturity.items():
        each_term_ary = value.split()
        each_term     = each_term_ary[0] + "Y"
        curve_terms.append(each_term)
        curve_term_years.append(each_term_ary[0])

    curveHandle = IAL.YieldCurve.createFromZeroRates(
        valDate,
        IAL.Util.addTerms(valDate, curve_terms),
        IAL.Util.scale(work_rates, 0.01),
        "CONTINUOUS", "N", "ACT/365", "FF")
   
    os.chdir(curr_dir)
    return curveHandle

def get_market_data(valDate, market_index_type = 'US_Equity'):

    TSR_ticker        = marketIndexDict[market_index_type]
    marekt_index_data = MKT.TSR.MarketData( TSR_ticker, valDate, "V" )
   
    return marekt_index_data[0]
    

def eval_PE_return(eval_date, valDate_base, market_index_type = 'US_Equity'):
#    spx_base    =  get_market_data(valDate_base, market_index_type)
#    spx_current =  get_market_data(eval_date, market_index_type)
#    spx_return  =  spx_current / spx_base - 1
#    return_year_frac = IAL.Date.yearFrac("ACT/365",  valDate_base, eval_date)
#    pe_return  = PE_Return_Model['alpha'] * return_year_frac+  PE_Return_Model['beta'] * spx_return
   
    
    if eval_date == eval_date+MonthEnd(0): ## no adjustment for month end Joanna update 10/10/2019
        pe_return = 0
    elif eval_date >= datetime.datetime(2020,1,1):
        pe_return = 0
    else:
        spx_base    =  get_market_data(valDate_base, market_index_type)
        spx_current =  get_market_data(eval_date, market_index_type)
        spx_return  =  spx_current / spx_base - 1
        return_year_frac = IAL.Date.yearFrac("ACT/365",  valDate_base, eval_date)
        pe_return  = PE_Return_Model['alpha'] * return_year_frac+  PE_Return_Model['beta'] * spx_return
    
    return pe_return

#%% Vincent
def createAkitShockCurve(valDate, M_Stress_Scen, stress_scen, curveType, ccy, rating = 'BBB'):
    if curveType == "Treasury":
        curveName = tsyCurveDict.get(ccy)

    elif curveType == "Swap":
        curveName = swapCurveDict.get(ccy)

#    elif curveType == "Credit":
#        curveName = CreditYieldDict.get(rating)

    # Get curve market data from TSR
    curveTerms = MKT.TSR.MarketData(curveName, valDate, "T")
    curveRates = MKT.TSR.MarketData(curveName, valDate, "V")
    
    ShockRates =  np.array(curveRates) + M_Stress_Scen[stress_scen].scen_Def['IR']/100  
        
    # Build curve
    curveHandle = IAL.YieldCurve.createFromZeroRates(
        valDate,
        IAL.Util.addTerms(valDate, curveTerms),
        IAL.Util.scale(ShockRates, 0.01),
        "CONTINUOUS", "N", "ACT/365", "FF")

    return curveHandle

def Set_Dashboard_Shock_MarketFactors(eval_dates, M_Stress_Scen, stress_scen, market_factor, curveType, curr_GBP, proxy_term, rating = "BBB", KRD_Term = KRD_Term):
    
    colNames      = ['val_date', 'Term', 'IR',"Credit_Rate", "Credit_Spread", 'GBP', 'SPX']
    
    for key, value in KRD_Term.items():
        colNames.append("IR_" + key)    
    
    shock_market_factor = pd.DataFrame([],columns = colNames)

    for valDate in eval_dates:
        irCurve          = createAkitShockCurve(valDate, M_Stress_Scen, stress_scen, curveType, "USD", rating) ### IR shock is applied here
#        CreditCurve      = createAkitShockCurve(valDate, M_Stress_Scen, stress_scen, "Credit", "USD", rating) ### No credit spread shock should be applied here

        ir_rate          = irCurve.zeroRate(proxy_term)            
        credit_rate      = market_factor[market_factor['val_date'] == valDate]['Credit_Rate'].values[0]
        credit_spread    = market_factor[market_factor['val_date'] == valDate]['Credit_Spread'].values[0]
        spx              = get_market_data(valDate, 'US_Equity')
        
        each_market_data = [valDate, proxy_term, ir_rate, credit_rate, credit_spread, curr_GBP, spx]
        
        for key, value in KRD_Term.items():
            each_market_data.append( irCurve.zeroRate(value) )
        
        shock_market_factor = shock_market_factor.append(pd.DataFrame([each_market_data], columns = colNames), ignore_index = True)
   
    return shock_market_factor

def load_BMA_Stress_Curves(valDate, ccy, revalDate, M_Stress_Scen, stress_scen, rollforward = "N", rollforward_date = datetime.datetime(2100, 12, 31)):

    curr_dir = os.getcwd()
    os.chdir(BMA_curve_dir)
    fileName = BMA_curve_file[valDate]
    work_BMA_file = pd.ExcelFile(fileName)
    work_BMA_curves = pd.read_excel(work_BMA_file)
    work_ccy        = BMA_ccy_map[ccy]
    
    work_maturity = work_BMA_curves['Maturity']
    work_rates    = work_BMA_curves[work_ccy] * 100
    
    curve_terms      =[]
    curve_term_years = []
    for key, value in work_maturity.items():
        each_term_ary = value.split()
        each_term     = each_term_ary[0] + "Y"
        curve_terms.append(each_term)
        curve_term_years.append(each_term_ary[0])
    
    if valDate == revalDate:
       calc_rates = work_rates 
       
    else:    

        irCurve_val   = createAkitZeroCurve(valDate, "Swap", "GBP")
        irCurve_reval = createAkitShockCurve(revalDate, M_Stress_Scen, stress_scen, "Swap", "GBP") ### IR shock is applied here
           
        reval_rates = []
        
        term_count = len(curve_terms)
        
        for idx in range(0, term_count, 1):    
            val_rate    = work_rates[idx]
            each_term   = float(curve_term_years[idx])
            
            # reflect rate changes up to 30 year ternor and then stay constant
            if idx <= 29:
                swap_change = (irCurve_reval.zeroRate(each_term) - irCurve_val.zeroRate(each_term)) * 100
                
            reval_rates.append( val_rate + swap_change )
        
        calc_rates = reval_rates


    if rollforward == "Y":
        curve_base_date = rollforward_date
    else:
        curve_base_date = revalDate

    curveHandle = IAL.YieldCurve.createFromZeroRates(
        curve_base_date,
        IAL.Util.addTerms(curve_base_date, curve_terms),
        IAL.Util.scale(calc_rates, 0.01),
        "CONTINUOUS", "N", "ACT/365", "FF")
   
    os.chdir(curr_dir)
    return curveHandle

def FI_Yield_Model_Port(curve_base_date, eval_date,model_port, initial_spread, ultimate_spread, ultimate_period, curveType = 'Treasury', base_irCurve_USD = 0):
    #   This should go to an economic scenario generator module - an illustration with the base case only
    if base_irCurve_USD == 0:
        base_irCurve_USD = createAkitZeroCurve(curve_base_date, curveType, "USD")

    proj_year_frac = IAL.Date.yearFrac("ACT/365",  curve_base_date, eval_date)
    weighted_yield = 0
    
    ###self.FI_surplus_model_port    = {'Port1' : {'Maturity' : '6Y', 'Rating' : 'A', 'Weight' : 0.5}, 'Port2': {'Maturity' : '6Y', 'Rating' : 'BBB', 'Weight' : 0.5}}
    for each_port, each_target in model_port.items():
        each_maturity          = each_target['Maturity']
        each_maturity_date     = IAL.Util.addTerms(eval_date, [str(each_maturity) + "Y"])[0]
        initial_spread_terms   = initial_spread[each_target['Rating']]
        ultimate_spread_terms  = ultimate_spread[each_target['Rating']]
        fwd_rate               = base_irCurve_USD.fwdRate(eval_date, each_maturity_date, 'continuous')
        spread_term            = initial_spread['Term']
        
        each_initial_spread  = np.interp(each_maturity, spread_term, initial_spread_terms)
        each_ultimate_spread = np.interp(each_maturity, spread_term, ultimate_spread_terms)
        each_weighted_spread = np.interp(proj_year_frac, [0, ultimate_period], [each_initial_spread, each_ultimate_spread])
        each_yield           = fwd_rate + each_weighted_spread
        weighted_yield      += each_yield * each_target['Weight']
    
    return weighted_yield
