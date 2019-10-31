import os

import datetime

# load Corp Model Folder DLL into python
corp_model_dir = 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code' 
# 1Q19 Est: 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code'
# 2Q19 Act: 'L:\\DSA Re\\Workspace\\Production\2019_Q2\\BMA Best Estimate\\Main_Run_v003\\Step 2 Python Parallel'

os.sys.path.append(corp_model_dir)
import Lib_Market_Akit as IAL_App
#import Lib_Corp_Model as Corp
import Class_Corp_Model as Corpclass
import Config_Scenarios as Scen
import Class_Scenarios as Scen_class
import Class_CFO as cfo
import datetime as dt


#import App_daily_portfolio_feed as Asset_App
#import Lib_BSCR_Model as BSCR
#import Lib_Utility as Util
#import App_daily_portfolio_feed as Asset_App
#import Config_BSCR as BSCR_Cofig
#import User_Input_Dic as UI
#import IALPython3 as IAL
##from _Class_Corp_Model import LiabAnalytics
#import pandas as pd
#import math as math
#
#import Config_EBS_Dashboard as cfg_EBS

if __name__ == "__main__":
    
#============================ Model ==========================#
#                                                             |
#    Model_to_Run   = "Estimate" # "Actual" or "Estimate"      |
#                                                             |
#=========================== Swithch =========================#
#                                                             |       
    Der_1_day_lag_fix = 'No' # "Yes" or 'No'                  |
#                                                             |    
#=============================================================#    
    
    
    work_dir       = 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\2019Q2'   # 1Q; 2Q
    
    input_work_dir = r'L:\\DSA Re\\Workspace\\Production\2019_Q2\\BMA Best Estimate\\Main_Run_v003\\Step 2 Python Parallel\\Input'    # Only for Act Model at the moment
    input_fileName = r'.\Input_v3.xlsx'                                                                                               # Only for Act Model at the moment
    Time_0_asset_filename = r'.\Asset with exclusion.xlsx'                                                                            # Only for Act Model at the moment
    Mapping_filename = r'.\Mapping.xlsx'                                                                                              # Only for Act Model at the moment
    alba_filename = r'.\ALBA bucketed risks 2019Q2.xlsx'                                                                              # Only for Act Model at the moment
    SFS_File = r'L:\\DSA Re\\Workspace\\Production\2019_Q2\\BMA Best Estimate\\Main_Run_v003\\Step 2 Python Parallel\\Input\SFS.xlsx' # Only for Act Model at the moment
    
    BMA_curve_dir  = 'L:\DSA Re\\Workspace\Production\EBS Dashboard\Python_Code\BMA_Curves'    
    asset_workDir  = r'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\Asset_Holding_Feed'
    
    EBS_output_folder = 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\Dashboard_outputs'
    # 'L:\\DSA Re\\Workspace\\Production\\2019_Q2\\BMA Best Estimate\\Main_Run_v003\\Step 2 Python Parallel\\Output'
    
    curveType        = "Treasury"
    numOfLoB         = 45
    Proj_Year        = 70
    ccy              = "USD"
    bindingScen      = 1
    base_GBP         = 1.26977 # 1Q19: 1.3004; 2Q19: 1.26977
#    curr_GBP         = 1.26977 # IAL_App.get_GBP_rate(EBS_Calc_Date, curvename = 'FX.USDGBP.SPOT.BASE')
    liab_spread_beta = 0.65
    
    Regime = "Current" # "Current" or "Future"  
    PC_method = "Bespoke" # "Bespoke" or "BMA" 
    
    CF_Database    = r'L:\DSA Re\Workspace\Production\2019_Q2\BMA Best Estimate\Main_Run_v003\0_CORP_20190510_00_AggregateCFs_Result.accdb'
    # 1Q19: r'L:\DSA Re\Workspace\Production\2019_Q1\BMA Best Estimate\Main_Run_v002\0_CORP_20190510_00_AggregateCFs_Result.accdb'
    # 2Q19: r'L:\DSA Re\Workspace\Production\2019_Q2\BMA Best Estimate\Main_Run_v003\0_CORP_20190510_00_AggregateCFs_Result.accdb'
    
    cash_flow_freq = 'A'
    CF_TableName   = "I_LBA____062019____________00"
    # 1Q19: "I_LBA____032019____________00"
    # 2Q19: "I_LBA____062019____________00"
    
    Step1_Database = r'L:\DSA Re\Workspace\Production\2019_Q2\BMA Best Estimate\Main_Run_v003\1_CORP_20190510_00_Output.accdb'
    # 1Q19: r'L:\DSA Re\Workspace\Production\2019_Q1\BMA Best Estimate\Main_Run_v002\1_CORP_20190510_00_Output.accdb'
    # 2Q19: r'L:\DSA Re\Workspace\Production\2019_Q2\BMA Best Estimate\Main_Run_v003\1_CORP_20190510_00_Output.accdb'
    
    Disc_rate_TableName    = 'O_DIS____062019_062019_____00'    
    PVBE_TableName         = "O_PVL____062019_062019_____01"
    
    # Estimate Model Only
    BSCRRisk_agg_TableName = 'O_PVA____062019_062019_____01'
    BSCRRisk_LR_TableName  = 'O_PVA____062019_062019_____04'
    BSCRRisk_PC_TableName  = 'O_PVA____062019_062019_____07'   
#     1Q19:'O_PVA____032019_032019_____11' / 'O_PVA____032019_032019_____14' / 'O_PVA____032019_032019_____17'
    

#   run set up
    valDate    = datetime.datetime(2019, 6, 28) ### to be consistent with Step 2
    Price_Date = [datetime.datetime(2019, 7, 31),
                  datetime.datetime(2019, 8, 31)] ### for illiquidity impact estimation
    
       
    EBS_Cal_Dates_all = [ datetime.datetime(2019, 8, 28) ]

     #    Market Factors
    eval_dates     = [ valDate ] + Price_Date + EBS_Cal_Dates_all
    market_factor         = IAL_App.Set_Dashboard_MarketFactors(eval_dates, curveType, 10, "BBB", IAL_App.KRD_Term, "USD")
    market_factor_GBP_IR  = IAL_App.Set_Dashboard_MarketFactors(eval_dates, curveType, 10, "BBB", IAL_App.KRD_Term, "GBP")


    freq            = 'B'


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

    EBS_DB_results = {}
    
    for index, EBS_Calc_Date in enumerate(EBS_Cal_Dates_all):
#        EBS_Calc_Date  = datetime.datetime(2019, 5, 22)
        BMA_curve_file = 'BMA_Curves_' + valDate.strftime('%Y%m%d') + '.xlsx' 
        asset_fileName = r'.\Asset_Holdings_' + EBS_Calc_Date.strftime('%Y%m%d') + '.xlsx' ### A (actual): .xlsx; B (estimate): _archive.xlsx
        
        try: # try getting T+1 asset holdings to modify the derivative
            if Der_1_day_lag_fix == 'Yes':
                asset_fileName_T_plus_1 = r'.\Asset_Holdings_' + EBS_Cal_Dates_all[index + 1].strftime('%Y%m%d') + '_summary.xlsx'
                print("1-day lag on dervative is fixed for " + str(EBS_Calc_Date) + " based on " + str(EBS_Cal_Dates_all[index + 1]))
                
            elif Der_1_day_lag_fix == 'No':
                asset_fileName_T_plus_1 = r'.\Asset_Holdings_YYYYMMDD_summary.xlsx'
                print("1-day lag on dervative is not fixed for " + str(EBS_Calc_Date))
    
        except:
            asset_fileName_T_plus_1 = r'.\Asset_Holdings_YYYYMMDD_summary.xlsx'
            print("1-day lag on dervative is not fixed for " + str(EBS_Calc_Date))
    
           
        excel_out_file = '.\EBS_Liab_Output_' + valDate.strftime('%Y%m%d') + '_' + EBS_Calc_Date.strftime('%Y%m%d') + '.xlsx'   

        #    Set the base line cash flows and valuations
        work_EBS_DB = Corpclass.EBS_Dashboard(EBS_Calc_Date, "Estimate", valDate)    
        work_EBS_DB.set_base_cash_flow(valDate, CF_Database, CF_TableName, Step1_Database, PVBE_TableName, bindingScen, numOfLoB, Proj_Year, work_dir, cash_flow_freq)
        work_EBS_DB.set_base_liab_value(valDate, curveType, base_GBP, numOfLoB, "BBB")
        work_EBS_DB.set_base_liab_summary(numOfLoB)
        work_EBS_DB.run_dashboard_liab_value(valDate, EBS_Calc_Date, curveType, numOfLoB, market_factor, liab_spread_beta = liab_spread_beta)

        work_EBS_DB.set_dashboard_liab_summary(numOfLoB) 
    
        work_EBS_DB.set_asset_holding(asset_workDir, asset_fileName, asset_fileName_T_plus_1, Price_Date, market_factor)  
        work_EBS_DB.run_dashboard_EBS(numOfLoB, market_factor) ### Vincent 06/28/2019 - LTIC revaluation
        work_EBS_DB.set_base_BSCR(Step1_Database, BSCRRisk_agg_TableName, BSCRRisk_LR_TableName, BSCRRisk_PC_TableName, Regime)
        work_EBS_DB.run_BSCR_dashboard(Regime)
        EBS_DB_results[EBS_Calc_Date] = work_EBS_DB

        Scen_results = {}
        each_scen = Scen.Comp
        work_scen = Scen_class.Scenario(valDate, EBS_Calc_Date, each_scen)
        work_scen.setup_scen()
        Scen_results[EBS_Calc_Date] = work_scen

        stress_results = {}
    
    #   Initializing CFO
        cfo_work = cfo.cfo(valDate, EBS_Calc_Date, freq, EBS_Calc_Date, each_scen['Scen_Name'], 'Estimate', liab_val_base, liab_val_alt, liab_val_base)
        cfo_work.load_dates()
        cfo_work.init_fin_proj()
    
    #   Set the liability valuation cash flows
        cfo_work.set_base_cash_flow()
        cfo_work.set_base_liab_value(work_scen._IR_Curve_USD, work_scen._IR_Curve_GBP)
        cfo_work.set_base_liab_summary()
        cfo_work.run_TP_forecast(input_irCurve_USD = work_scen._IR_Curve_USD, input_irCurve_GBP = work_scen._IR_Curve_GBP)
#    
#    #   forcasting
#        cfo_work.set_base_projection()
#        cfo_work.run_fin_forecast()
#    
        stress_results['test'] = cfo_work
            
    
