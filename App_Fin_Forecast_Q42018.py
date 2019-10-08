# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 17:11:06 2019

@author: seongpar
"""
#import os
#os.chdir(r'\\10.87.247.17\legacy\DSA Re\Workspace\Production\Corp_Model_v2\Library')
import time
import os
import Class_CFO as cfo
import datetime as dt
import Lib_Market_Akit   as IAL_App
import Lib_Corp_Model as Corp

#import redshift_database as db
#import pandas as pd
#import Lib_Corp_Model as Corp
file_dir = os.getcwd()

startT = time.time()
#Config - Neeed to link to RedShift
actual_estimate = "Estimate"
valDate         = dt.datetime(2018, 12, 28)
date_start      = dt.datetime(2019, 12, 31)
date_end        = dt.datetime(2039, 12, 31)
freq            = 'A'
scen            = 'Base'


CF_Database    = r'L:\DSA Re\Workspace\Production\2018_Q4\BMA Best Estimate\Main_Run_v007_Fulton\0_Baseline_Run\0_CORP_20190420_00_AggregateCFs_Result.accdb'
CF_TableName   = "I_LBA____122018____________00"                  
Proj_TableName = "I_LBA____122018____________00"                  

Step1_Database = r'L:\DSA Re\Workspace\Production\2018_Q4\BMA Best Estimate\Main_Run_v007_Fulton\0_Baseline_Run\1_CORP_20190412_00_Output.accdb'
PVBE_TableName = "O_PVL____122018_122018_____01"
bindingScen      = 0
numOfLoB         = 45
Proj_Year        = 70
work_dir       = r'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\2018Q4'

cash_flow_freq = 'A'

curveType        = "Treasury"
base_GBP         = 1.2755 # 4Q18: 1.2755; 1Q19: 1.3004; 2Q19: 1.26977    
liab_spread_beta = 0.65

liab_val_base = {
    'CF_Database'    : CF_Database, 
    'CF_TableName'   : CF_TableName, 
    'Step1_Database' : Step1_Database, 
    'PVBE_TableName' : PVBE_TableName, 
    'bindingScen'    : bindingScen, 
    'numOfLoB'       : numOfLoB, 
    'Proj_Year'      : Proj_Year, 
    'work_dir'       : work_dir, 
    'cash_flow_freq' : cash_flow_freq,
    'curve_type'     : curveType,
    'base_GBP'       : base_GBP,
    'liab_benchmark' : "BBB",
    'liab_spread_beta': liab_spread_beta,
    'cf_proj_end_date': dt.datetime(2089, 12, 31),
    'recast_risk_margin' : 'N'
}

liab_val_alt = None

proj_cash_flows_input = {
    'CF_Database'    : CF_Database, 
    'CF_TableName'   : Proj_TableName, 
    'Step1_Database' : Step1_Database, 
    'PVBE_TableName' : PVBE_TableName, 
    'projScen'       : 0, 
    'numOfLoB'       : numOfLoB, 
    'Proj_Year'      : Proj_Year, 
    'work_dir'       : work_dir, 
    'cash_flow_freq' : cash_flow_freq,
}

liab_val_alt = None

# Step3 inputs (from work dir)
Scalar_fileName = 'Scalar_Step3.xlsx'
LOC_assumption_fileName = 'LOC_Step3.xlsx'

loc_input = {
        'tier2_limit'          : 2/3,
        'tier3_limit_1'        : 0.1765,
        'tier3_limit_2'        : 2/3,
        'target_capital_ratio' : 150 / 100,
        'capital_surplus_life' : 1498468069,
        'capital_surplus_pc'   : 1541220172
        }



#%%
if __name__ == '__main__':

    print('Start Projection')


#   This should go to an economic scenario generator module - an illustration with the base case only
#    base_irCurve_USD = IAL_App.createAkitZeroCurve(valDate, curveType, "USD")
    base_irCurve_USD = IAL_App.load_BMA_Risk_Free_Curves(valDate)  
    base_irCurve_GBP = IAL_App.load_BMA_Std_Curves(valDate,"GBP",valDate)

    test_results = {}

#   Initializing CFO
    cfo_work = cfo.cfo(valDate, date_start, freq, date_end, scen, actual_estimate, liab_val_base, liab_val_alt, proj_cash_flows_input)
    cfo_work.load_dates()
    cfo_work.init_fin_proj()

#   Set the liability valuation cash flows
    cfo_work.set_base_cash_flow()
    cfo_work.set_base_liab_value()
    cfo_work.set_base_liab_summary()
    cfo_work.run_TP_forecast(input_irCurve_USD = base_irCurve_USD, input_irCurve_GBP = base_irCurve_GBP)

#   forcasting
    cfo_work.set_forecasting_scalar(Scalar_fileName, work_dir)
    cfo_work.set_LOC_Assumption(LOC_assumption_fileName, work_dir)
    cfo_work.set_base_projection()
    
    cfo_work.run_fin_forecast()

    test_results['test'] = cfo_work
        
    print('End Projection')
    print('Total time: %.2d'%(time.time() - startT))
    
    os.chdir(file_dir)
#  
## validation
#    excel_out_file = '.\EBS_Liab_Output_pvbe_' + valDate.strftime('%Y%m%d') + '_'  + '.xlsx' 
#    pvbe_output = Corp.exportLobAnalytics_proj(cfo_work, excel_out_file, work_dir)
#    
# # validation_Reinsurance Settlement Forecast
#    excel_out_file_reins = '.\Forecast_Output_Reins_' + valDate.strftime('%Y%m%d') + '_'  + '.xlsx' 
#    reins_output = Corp.exportReinsSettlm_proj(cfo_work, excel_out_file_reins, work_dir)
#    
#    print('Excel Output files created for Validation')