# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 17:11:06 2019

@author: seongpar
"""
#import os
#os.chdir(r'\\10.87.247.17\legacy\DSA Re\Workspace\Production\Corp_Model_v2\Library')
import time
import os
import pandas as pd
import Class_CFO as cfo
import datetime as dt
import Lib_Market_Akit   as IAL_App
import Lib_Corp_Model as Corp
import App_daily_portfolio_feed as Asset_App
import Config_Run_Control as run_control

#import redshift_database as db
#import pandas as pd
#import Lib_Corp_Model as Corp
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
#LOC_assumption_fileName = 'LOC_Step3.xlsx'
#TargetCapital_fileName = 'CapitalRatio_Step3.xlsx'
SurplusSplit_fileName = 'SurplusSplit_LR_PC_Step3.xlsx'
ML3_fileName = 'ML_III_Input_Step3.xlsx'

control_fileName = 'ControlInput_Step3.xlsx'

Asset_holding_fileName    = 'Asset_4Q18_v3.xlsx'
Asset_adjustment_fileName = 'Asset_Adjustment_4Q18.xlsx'
Mapping_filename          = 'Mapping.xlsx' 
SFS_BS_fileName           = 'SFS_4Q18.xlsx'
alba_filename             = None    

Regime = 'Current'

#loc_input = pd.read_excel(work_dir + '/' + control_fileName, index_col = 0, header = None)
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
                       run_control_ver=run_control_ver)
    #cfo_work.load_dates() # Moved to init
    cfo_work.init_fin_proj()
    cfo_work._run_control = run_control.version[run_control_ver]
    print("Initialization done")
    midT = time.time()
#   Set the liability valuation cash flows
    cfo_work.set_base_cash_flow()
    cfo_work.set_base_liab_value(base_irCurve_USD, base_irCurve_GBP)
    cfo_work.set_base_liab_summary()
    print("Liability analysis done, time used: %.2fs" %(time.time() - midT))
    midT = time.time()
    
    cfo_work.run_TP_forecast(input_irCurve_USD = base_irCurve_USD, input_irCurve_GBP = base_irCurve_GBP)
    print("TP forecast done, time used: %.2fs" %(time.time() - midT))
    midT = time.time()
    
#   forcasting
    cfo_work.set_forecasting_inputs_control(control_fileName, work_dir)
    cfo_work.set_forecasting_scalar(Scalar_fileName, work_dir)
#    cfo_work.set_LOC_Assumption(LOC_assumption_fileName, work_dir)
#    cfo_work.set_tarcap_Assumption(TargetCapital_fileName, work_dir)
    cfo_work.set_surplus_split(SurplusSplit_fileName, work_dir)
    cfo_work.set_ML3(ML3_fileName, work_dir)
    cfo_work.set_base_projection()
    
    Asset_holding    = Asset_App.actual_portfolio_feed(valDate, valDate, work_dir, Asset_holding_fileName, Mapping_filename, alba_filename, output = 0, ratingMapFile = '.\Rating_Mapping.xlsx')
    Asset_adjustment = Asset_App.Asset_Adjustment_feed(work_dir, Asset_adjustment_fileName) 

    print("Asset holding loaded, time used: %.2fs" %(time.time() - midT))
    midT = time.time()
    
    cfo_work.run_fin_forecast(Asset_holding, Asset_adjustment, base_irCurve_USD, Regime, work_dir)
#    cfo_work.run_fin_forecast_stepwise(Asset_holding, Asset_adjustment, base_irCurve_USD, Regime, work_dir)
    print("Forecasting done, time used: %.2fs" %(time.time() - midT))
    midT = time.time()
    
    print('End Projection')
    print('Total time: %.2fs' %(time.time() - startT))
    #%%
    test_results['test'] = cfo_work

    example_dashboard_obj = cfo_work.fin_proj[0]['Forecast']
    example_dashboard_obj.print_accounts('EBS_IS', 'Agg')
    
    #%% New export
    Corp.exportBase(cfo_work, 'EBS_IS_test.xlsx', file_dir, 'EBS_IS', lobs = ['Agg'], output_all_LOBs = 0, output_type = 'xlsx')
    Corp.exportBase(cfo_work, 'EBS_test.xlsx', file_dir, 'EBS', lobs = ['Agg'], output_all_LOBs = 0, output_type = 'xlsx')
    Corp.exportBase(cfo_work, 'BSCR_test.xlsx', file_dir, 'BSCR_Dashboard', lobs = ['Agg'], output_all_LOBs = 0, output_type = 'xlsx')
    
    
    os.chdir(file_dir)
    

#  
## validation
#   cfo_work.fin_proj[0]['Forecast'].run_base_EBS(Asset_holding, Asset_adjustment) 
#    excel_out_file = '.\EBS_Liab_Output_pvbe_' + valDate.strftime('%Y%m%d') + '_'  + '.xlsx' 
#    pvbe_output = Corp.exportLobAnalytics_proj(cfo_work, excel_out_file, work_dir)
#    
## validation_Reinsurance Settlement Forecast
#    excel_out_file_reins = '.\Forecast_Output_Reins_' + valDate.strftime('%Y%m%d') + '_'  + '.xlsx' 
#    reins_output = Corp.exportReinsSettlm_proj(cfo_work, excel_out_file_reins, work_dir)
#    
## validation_Taxable Income Forecast
#    excel_out_file_taxis = '.\Forecast_Output_Tax_IS_' + valDate.strftime('%Y%m%d') + '_'  + '.xlsx' 
#    taxis_output = Corp.exportTaxableIncome_proj(cfo_work, excel_out_file_taxis, work_dir)
    
#    print('Excel Output files created for Validation')