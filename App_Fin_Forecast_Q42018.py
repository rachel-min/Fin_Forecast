# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 17:11:06 2019

@author: seongpar
"""

import time
import os
import pandas as pd
import datetime as dt
import Class_CFO as cfo
import Lib_Market_Akit   as IAL_App
import Lib_Corp_Model as Corp
import App_daily_portfolio_feed as Asset_App
from Config_Run_Control import update_runControl
# from Run_Control_2018Q4_base import update_runControl

file_dir = os.getcwd()


#Config - Neeed to link to RedShift
actual_estimate = "Estimate"
valDate         = dt.datetime(2018, 12, 31)
date_start      = dt.datetime(2019, 12, 31)
date_end        = dt.datetime(2090, 12, 31)
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
    'Recast_Risk_Margin' : 'N'
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

Asset_holding_fileName    = 'Asset_4Q18_v4.xlsx'
#Mapping_filename          = 'Mapping.xlsx' ### Removed
#SFS_BS_fileName           = 'SFS_4Q18.xlsx' ### Replaced by SFS_BS
alba_filename             = None    


Regime = 'Current'

manual_input_file = pd.ExcelFile(work_dir + '//Manual_inputs.xlsx')
run_control_ver = '2018Q4_Base' 


#%%
if __name__ == '__main__':

    print('Start Projection')
    startT = time.time()
#   This should go to an economic scenario generator module - an illustration with the base case only
#    base_irCurve_USD = IAL_App.createAkitZeroCurve(valDate, curveType, "USD")
    base_irCurve_USD = IAL_App.load_BMA_Risk_Free_Curves(valDate)  
    base_irCurve_GBP = IAL_App.load_BMA_Std_Curves(valDate,"GBP",valDate)

    test_results = {}

#   Initializing CFO
    cfo_work = cfo.cfo(val_date=valDate, date_start=date_start, freq=freq, date_end=date_end, 
                       scen=scen, actual_estimate=actual_estimate, 
                       input_liab_val_base=liab_val_base, 
                       input_liab_val_alt=liab_val_alt, 
                       input_proj_cash_flows=proj_cash_flows_input,
                       run_control_ver = run_control_ver)
    #cfo_work.load_dates() # Moved to init
    cfo_work.init_fin_proj()
    update_runControl(cfo_work._run_control)
    cfo_work._run_control.load_excel_input(manual_input_file)
    #cfo_work._run_control = run_control.version[run_control_ver]
    print("Initialization done")
    
    midT = time.time()
#   Set the liability valuation cash flows
    cfo_work.set_base_cash_flow()
    cfo_work.set_base_liab_value(base_irCurve_USD, base_irCurve_GBP) ### This will change working directory
    cfo_work.set_liab_GAAP_base()
    cfo_work.set_base_liab_summary()
    print("Liability analysis done, time used: %.2fs" %(time.time() - midT))
    
    midT = time.time()
    cfo_work.run_TP_forecast(input_irCurve_USD = base_irCurve_USD, input_irCurve_GBP = base_irCurve_GBP)
    print("TP forecast done, time used: %.2fs" %(time.time() - midT))
    
    midT = time.time()
#   forcasting
    cfo_work.set_base_projection()
    print("Projection done, time used: %.2fs" %(time.time() - midT))
    
    midT = time.time()
    Asset_holding    = Asset_App.actual_portfolio_feed(valDate, valDate, work_dir, Asset_holding_fileName, alba_filename, output = 0)
    Asset_adjustment = Asset_App.Asset_Adjustment_feed(manual_input_file.parse('Asset_Adjustment'))     
    print("Asset holding loaded, time used: %.2fs" %(time.time() - midT))
    
    midT = time.time()
    cfo_work.run_fin_forecast(Asset_holding, Asset_adjustment, base_irCurve_USD, Regime, work_dir)
#    cfo_work.run_fin_forecast_stepwise(Asset_holding, Asset_adjustment, base_irCurve_USD, Regime, work_dir)
    print("Forecasting done, time used: %.2fs" %(time.time() - midT))

    print('End Projection')
    print('Total time: %.2fs' %(time.time() - startT))
    #%%
    #test_results['test'] = cfo_work

    finProj = cfo_work.fin_proj[1]['Forecast']   

    #%%Output results
    #Kyle: this will take very long time to run
    write_results = False
    
    if write_results:
        Corp.exportBase(cfo_work, 'EBS_IS_test.xlsx', file_dir, 'EBS_IS', lobs = ['Agg','GI','LT'], output_all_LOBs = 1, output_type = 'xlsx')
        Corp.exportBase(cfo_work, 'EBS_test.xlsx', file_dir, 'EBS', lobs = ['Agg','GI','LT'], output_all_LOBs = 1, output_type = 'xlsx')
        Corp.exportBase(cfo_work, 'BSCR_test.xlsx', file_dir, 'BSCR_Dashboard', lobs = ['Agg','GI','LT'], output_all_LOBs = 0, output_type = 'xlsx')
        Corp.exportBase(cfo_work, 'SFS_IS_test.xlsx', file_dir, 'SFS_IS', lobs = ['Agg','GI','LT'], output_all_LOBs = 1, output_type = 'xlsx')
        Corp.exportBase(cfo_work, 'SFS_test.xlsx', file_dir, 'SFS', lobs = ['Agg','GI','LT'], output_all_LOBs = 1, output_type = 'xlsx')
        Corp.exportBase(cfo_work, 'Reinsurance.xlsx', file_dir, 'Reins', lobs = ['Agg','GI','LT'], output_all_LOBs = 1, output_type = 'xlsx')
        Corp.exportBase(cfo_work, 'Tax_IS_test.xlsx', file_dir, 'Tax_IS', lobs = ['Agg','GI','LT'], output_all_LOBs = 1, output_type = 'xlsx')
        
        #%%Output GAAP margin
        GAAP_margin = {}
        for i in range(1,35):
            GAAP_margin[i] = cfo_work._liab_val_base[i].GAAP_Margin
        
        pd.Series(GAAP_margin).to_excel('Gaap_margin.xlsx', header=False)
        
        os.chdir(file_dir)

        #%%Output PVBE
        pvbe_ratios = {}
        pvbe = {}
        pvbe_sec = {}
        for i in cfo_work.fin_proj.keys():
            #record = cfo_work.fin_proj[i]['Forecast']._records
            #pvbe_ratios[i] = pd.Series(record['each_pvbe_ratio'], index = record['LOBs'])
            _pvbe = []
            _pvbe_sec = []
            for j in range(1, 46):
                _pvbe.append(cfo_work.fin_proj[i]['Forecast'].liability['dashboard'][j].PV_BE_net)
                _pvbe_sec.append(cfo_work.fin_proj[i]['Forecast'].liability['dashboard'][j].PV_BE_sec_net)
            pvbe[i] = pd.Series(_pvbe, index = range(1, 46))
            pvbe_sec[i] = pd.Series(_pvbe_sec, index = range(1, 46))
        
        pvbe_ratios = pd.DataFrame(pvbe_ratios)
        pvbe = pd.DataFrame(pvbe)
        pvbe_sec = pd.DataFrame(pvbe_sec)
        
        #os.chdir(r'\\pnsafsdg01\legacy\Global Profitability Standards and ALM\Legacy Portfolio\SAM RE\FRL Investment ALM\___Temp___\Fin_Forecast')
        pvbe.to_excel('PVBE.xlsx')
        pvbe_sec.to_excel('PVBE_sec.xlsx')


    #%%
    accts = ['BSCR_Dashboard', 'EBS', 'EBS_IS', 'SFS', 'SFS_IS', 'Reins', 'Tax_IS']
    lobLvls = [1, 'LT', 'GI', 'Agg']
