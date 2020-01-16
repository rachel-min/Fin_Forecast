import os

import datetime

# load Corp Model Folder DLL into python
#corp_model_dir = 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code' 
# 1Q19 Est: 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code'
# 2Q19 Act: 'L:\\DSA Re\\Workspace\\Production\2019_Q2\\BMA Best Estimate\\Main_Run_v003\\Step 2 Python Parallel'

# =============================================================================
# corp_model_dir = r'\\10.87.247.17\legacy\DSA Re\Workspace\Production\Corp_Model_v2\Library'
# os.sys.path.append(corp_model_dir)
# =============================================================================
import Lib_Market_Akit as IAL_App
#import App_daily_portfolio_feed as Asset_App
import Lib_Corp_Model as Corp
import Class_Corp_Model as Corpclass
import Lib_BSCR_Model as BSCR
import Lib_Utility as Util
import App_daily_portfolio_feed as Asset_App
import Config_BSCR as BSCR_Cofig
import User_Input_Dic as UI
import IALPython3 as IAL
#from _Class_Corp_Model import LiabAnalytics
import pandas as pd
import math as math
from pandas.tseries.offsets import YearEnd

import Config_EBS_Dashboard as cfg_EBS

if __name__ == "__main__":
    
#============================ Model ==========================#
#                                                             |
    Model_to_Run   = "Estimate" # "Actual" or "Estimate"        |
#                                                             |
#=========================== Swithch =========================#
#                                                             |       
    Der_1_day_lag_fix = 'No' # "Yes" or 'No'                  |
#                                                             |    
#=============================================================#    
       
    work_dir       = 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\2019Q3'
    
    input_work_dir = r'L:\\DSA Re\\Workspace\\Production\\2019_Q3\\BMA Best Estimate\\Step 2 Python Parallel\\Input'                  # Only for Act Model at the moment
    input_fileName = r'.\Input_3Q19_v2.xlsx'
    manual_input_file = pd.ExcelFile(input_work_dir + '//Input_3Q19_v2.xlsx') 
    Time_0_asset_filename = r'.\Asset with exclusion (cash and STI).xlsx'     # 3Q19 input                                            # Only for Act Model at the moment
    alba_filename = r'.\ALBA bucketed risks 2019Q3.xlsx'      # 3Q19 input                                                            # Only for Act Model at the moment
    SFS_File = r'L:\\DSA Re\\Workspace\\Production\2019_Q3\\BMA Best Estimate\\Step 2 Python Parallel\\Input\SFS_3Q19.xlsx'           # Only for Act Model at the moment
    
    BMA_curve_dir  = 'L:\DSA Re\\Workspace\Production\EBS Dashboard\Python_Code\BMA_Curves'    
    asset_workDir  = r'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\Asset_Holding_Feed'
    concentration_Dir = r'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\Asset_Holding_Feed\\concentration_risk'
    
    Dashboard_output_folder = 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\Dashboard_outputs'
    EBS_output_folder = r'L:\\DSA Re\\Workspace\\Production\2019_Q3\\BMA Best Estimate\\Step 2 Python Parallel\\Output'
    
    curveType        = "Treasury"
    numOfLoB         = 45
    Proj_Year        = 70
    ccy              = "USD"
    bindingScen      = 1
    bindingScen_Discount = 1
    base_GBP         = 1.2299 # 4Q18: 1.2755; # 1Q19: 1.3004; 2Q19: 1.26977;3Q19: 1.2299
#    curr_GBP         = 1.26977 # IAL_App.get_GBP_rate(EBS_Calc_Date, curvename = 'FX.USDGBP.SPOT.BASE')
    liab_spread_beta = 0.65 

    Regime = "Current" # "Current" or "Future"  
    PC_method = "Bespoke" # "Bespoke" or "BMA" 
    
    CF_Database    = 'alm'
    CF_Database    =  r'L:\DSA Re\Workspace\Production\2019_Q3\BMA Best Estimate\Main_Run_v003\0_CORP_20190903_00_AggregateCFs_Result.accdb'
    # 4Q18: r'L:\DSA Re\Workspace\Production\2018_Q4\BMA Best Estimate\Main_Run_v007_Fulton\0_Baseline_Run\0_CORP_20190420_00_AggregateCFs_Result.accdb'
    # 1Q19: r'L:\DSA Re\Workspace\Production\2019_Q1\BMA Best Estimate\Main_Run_v002\0_CORP_20190510_00_AggregateCFs_Result.accdb'
    # 2Q19: r'L:\DSA Re\Workspace\Production\2019_Q2\BMA Best Estimate\Main_Run_v003\0_CORP_20190510_00_AggregateCFs_Result.accdb'
    # 3Q19: r'L:\DSA Re\Workspace\Production\2019_Q3\BMA Best Estimate\Main_Run_v003\0_CORP_20190903_00_AggregateCFs_Result.accdb'
    
    cash_flow_freq = 'A'
    CF_TableName   = "I_LBA____092019____________00"
    
    # 4Q18: "I_LBA____122018____________00"
    # 1Q19: "I_LBA____032019____________00"
    # 2Q19: "I_LBA____062019____________00"
    # 3Q19: "I_LBA____092019____________00"
    
    Step1_Database =r'L:\DSA Re\Workspace\Production\2019_Q3\BMA Best Estimate\Main_Run_v003\1_CORP_20191028_00_Output.accdb'
    # 4Q18: r'L:\DSA Re\Workspace\Production\2018_Q4\BMA Best Estimate\Main_Run_v007_Fulton\0_Baseline_Run\1_CORP_20190412_00_Output.accdb'
    # 1Q19: r'L:\DSA Re\Workspace\Production\2019_Q1\BMA Best Estimate\Main_Run_v002\1_CORP_20190510_00_Output.accdb'
    # 2Q19: r'L:\DSA Re\Workspace\Production\2019_Q2\BMA Best Estimate\Main_Run_v003\1_CORP_20190510_00_Output.accdb'
    # 3Q19: r'L:\DSA Re\Workspace\Production\2019_Q3\BMA Best Estimate\Main_Run_v003\1_CORP_20191028_00_Output.accdb'

    Disc_rate_TableName    = 'O_DIS____092019_092019_____00'    
    PVBE_TableName         = "O_PVL____092019_092019_____01"
    
    # Estimate Model Only
    BSCRRisk_agg_TableName = 'O_PVA____092019_092019_____01'
    BSCRRisk_LR_TableName  = 'O_PVA____092019_092019_____04'
    BSCRRisk_PC_TableName  = 'O_PVA____092019_092019_____07'   
#     1Q19:'O_PVA____032019_032019_____11' / 'O_PVA____032019_032019_____14' / 'O_PVA____032019_032019_____17'
    

#   run set up
    valDate    = datetime.datetime(2019, 9, 30) ### to be consistent with Step 2
    Price_Date = [datetime.datetime(2019, 7, 31),
                  datetime.datetime(2019, 8, 31)] ### for illiquidity impact estimation
    
#%%
    if Model_to_Run == "Estimate": ### EBS Dashboard Model
           
        EBS_Cal_Dates_all = [
#                             datetime.datetime(2019, 9, 18),
#                             datetime.datetime(2019, 9, 19),
#                             datetime.datetime(2019, 9, 20),
                             datetime.datetime(2019, 9, 30),
                             ]
    
         #    Market Factors
        eval_dates = [ valDate ] + Price_Date + EBS_Cal_Dates_all
        eval_dates = list(set(eval_dates))
        
        market_factor        = IAL_App.Set_Dashboard_MarketFactors(eval_dates, curveType, 10, "BBB", 'A', IAL_App.KRD_Term, "USD")
        market_factor_GBP_IR = IAL_App.Set_Dashboard_MarketFactors(eval_dates, curveType, 10, "BBB", 'A', IAL_App.KRD_Term, "GBP")                
        credit_spread        = Asset_App.Set_weighted_average_OAS(valDate,EBS_Cal_Dates_all,asset_workDir)       
        market_factor_c      =  pd.merge(market_factor,credit_spread,left_on='val_date',right_on = 'ValDate')
        
        AssetRiskCharge = BSCR_Cofig.asset_charge(asset_workDir, 'Mapping.xlsx')
        
        EBS_DB_results = {}
                
        for index, EBS_Calc_Date in enumerate(EBS_Cal_Dates_all):

            BMA_curve_file = 'BMA_Curves_' + valDate.strftime('%Y%m%d') + '.xlsx' 
            asset_fileName = r'.\Asset_Holdings_' + EBS_Calc_Date.strftime('%Y%m%d') + '.xlsx'
            
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
            # Set daily asset holdings
            work_EBS_DB.set_asset_holding(asset_workDir, asset_fileName, asset_fileName_T_plus_1, Price_Date, market_factor)  
            Asset_Est = work_EBS_DB.asset_holding

            # Set LOB Definition, get LBA CFs + GOE, time 0 PVBE/RM/TP
            work_EBS_DB.set_base_cash_flow(valDate, CF_Database, CF_TableName, Step1_Database, PVBE_TableName, bindingScen, numOfLoB, Proj_Year, work_dir, cash_flow_freq)
            A_Est = work_EBS_DB.liability['base']

            # Calcualte time 0 OAS, Duration and Convexity etc.
            work_EBS_DB.set_base_liab_value(valDate, curveType, base_GBP, numOfLoB, "BBB")
            B_Est = work_EBS_DB.liability['base']

            # Time 0 PVBE, RM and TP summary: Agg/LT/PC            
            work_EBS_DB.set_base_liab_summary(numOfLoB)
            C_Est = work_EBS_DB.liab_summary['base']
            
            # Calcualte PVBE @ reval_date          
            work_EBS_DB.run_dashboard_liab_value(valDate, EBS_Calc_Date, curveType, numOfLoB, market_factor_c, liab_spread_beta)

            # preliminary liability summary
            work_EBS_DB.set_dashboard_liab_summary(numOfLoB) 

            # projection dates and ir curve
            nested_proj_dates =[]
            date_end = valDate+YearEnd(Proj_Year+1)
            nested_proj_dates.extend(list(pd.date_range(EBS_Calc_Date, date_end, freq=cash_flow_freq)))
            irCurve_USD_eval = IAL_App.createAkitZeroCurve(EBS_Calc_Date, curveType, "USD")
            irCurve_GBP_eval = IAL_App.load_BMA_Std_Curves(valDate,"GBP",EBS_Calc_Date)
            
            # nested PVBE
            for t, each_date in enumerate(nested_proj_dates): 
                work_EBS_DB.run_projection_liab_value(valDate, each_date, curveType, numOfLoB, market_factor_c,  liab_spread_beta, IAL_App.KRD_Term,  irCurve_USD_eval,irCurve_GBP_eval, base_GBP,EBS_Calc_Date)            
            
            # rearrange PVBE projection
            zz = Corp.projection_summary(work_EBS_DB.liability,nested_proj_dates)
            
            # Calcualte BSCR @ reval_date (in progress)
            work_EBS_DB.run_estimate_BSCR(numOfLoB, Proj_Year, Regime, PC_method, concentration_Dir)
            E_Est = work_EBS_DB.BSCR        
            
            # Calcualte RM @ reval_date (in progress)
            work_EBS_DB.run_RiskMargin(valDate, Proj_Year, Regime, BMA_curve_dir)
            E1_Est = work_EBS_DB.RM
            
            # Calcualte TP @ reval_date (in progress)                       
            work_EBS_DB.run_TP(numOfLoB, Proj_Year)
            E2_Est = work_EBS_DB.liability['dashboard']
                  
            # reval_date PVBE, RM and TP summary: Agg/LT/PC (in progress)
            work_EBS_DB.set_dashboard_liab_summary(numOfLoB) 
            F = work_EBS_DB.liab_summary['dashboard']
                    
            work_EBS_DB.run_dashboard_EBS(numOfLoB, market_factor) ### Vincent 06/28/2019 - LTIC revaluation
            work_EBS_DB.set_base_BSCR(Step1_Database, BSCRRisk_agg_TableName, BSCRRisk_LR_TableName, BSCRRisk_PC_TableName, Regime)
            work_EBS_DB.run_BSCR_dashboard(Regime)
            
            ### @@@ TEST run_BSCR_new_regime @@@ ###
            work_EBS_DB.run_BSCR_new_regime(numOfLoB, Proj_Year, Regime, PC_method, curveType, base_GBP, CF_Database, CF_TableName, Step1_Database, work_dir, cash_flow_freq, BMA_curve_dir, Disc_rate_TableName, market_factor)
            
            EBS_DB_results[EBS_Calc_Date] = work_EBS_DB
#            EBS_output        = Corp.export_Dashboard(EBS_Calc_Date, "Estimate", work_EBS_DB.EBS, work_EBS_DB.BSCR_Dashboard, EBS_output_folder, Regime)
#            BSCRDetail_output = Corp.export_BSCRDetail(EBS_Calc_Date, "Estimate", work_EBS_DB.BSCR_Dashboard, EBS_output_folder, Regime)
            print('EBS Dashboard: ', EBS_Calc_Date.strftime('%Y%m%d'), ' has been completed')
#            work_EBS_DB.export_LiabAnalytics(work_EBS_DB.liability['dashboard'], excel_out_file, work_dir, valDate, EBS_Calc_Date)
            
    ###-----------------------------------------------------------------------------------------------------------------------------------------------------###
    
    elif Model_to_Run == "Actual":  ### EBS Reporting Model
        print('Running EBS Reporting ...')
        
        EBS_Report = Corpclass.EBS_Dashboard(valDate, "Actual", valDate)  
        
        # Set LOB Definition, get LBA CFs + GOE - Vincent 07/02/2019
        print('LOB Definition ...')
        EBS_Report.set_base_cash_flow(valDate, CF_Database, CF_TableName, Step1_Database, PVBE_TableName, bindingScen, numOfLoB, Proj_Year, work_dir, cash_flow_freq) 
        A = EBS_Report.liability['base']
        
        # MircoStrategy Asset info 
        print('Loading Asset Info ...')  
        AssetRiskCharge = BSCR_Cofig.asset_charge(input_work_dir, input_fileName)
        
        ### Testing: 1) 1st valDate to be changed to eval_date 2) to be put in class.set_asset_holding
        EBS_asset_Input = Asset_App.actual_portfolio_feed(valDate, valDate, input_work_dir, Time_0_asset_filename, alba_filename, output = 0)
        
        Asset_adjustment = Asset_App.Asset_Adjustment_feed(manual_input_file.parse('Asset_Adjustment')) 
        
        print('Loading SFS Balance Sheet ...')  
        EBS_Report.set_sfs(SFS_File) # Vincent update - using SFS class 07/30/2019
        S1 = EBS_Report.SFS
        
        # Calculate PVBE and projections thereof - Vincent 07/02/2019
        print('PVBE Calculation ...')
        EBS_Report.run_PVBE(valDate, numOfLoB, Proj_Year, bindingScen_Discount, BMA_curve_dir, Step1_Database, Disc_rate_TableName, base_GBP)
        B = EBS_Report.liability['base'] 
    
        # Calculate BSCR and projections thereof - Vincent 07/09/2019
        print('BSCR Calculation Iteration ' + str(EBS_Report.Run_Iteration) + '...')
        EBS_Report.run_BSCR(numOfLoB, Proj_Year, input_work_dir, EBS_asset_Input, Asset_adjustment, AssetRiskCharge, Regime, PC_method)
        B1 = EBS_Report.BSCR
        
        print('Risk Margin Calculation...')
        EBS_Report.run_RiskMargin(valDate, Proj_Year, Regime, BMA_curve_dir)
        B2 = EBS_Report.RM
     
        print('TP Calculation...')
        EBS_Report.run_TP(numOfLoB, Proj_Year)
        B3 = EBS_Report.liability['base']
          
        # PVBE, BSCR and TP summary: Agg/LT/PC - Vincent 07/08/2019
        print('Generating Liability Summary ...')
        EBS_Report.set_base_liab_summary(numOfLoB)
        C = EBS_Report.liab_summary['base']
            
        # Set up EBS - Vincent 07/08/2019
        print('Generating EBS ...')
        EBS_Report.run_base_EBS(EBS_asset_Input, Asset_adjustment) # Vincent updated 07/17/2019
        E = EBS_Report.EBS
        
        # Calculate BSCR (Equity, IR and Market BSCR) - Vincent 07/30/2019
        print('BSCR Calculation Iteration ' + str(EBS_Report.Run_Iteration) + '...')
        EBS_Report.run_BSCR(numOfLoB, Proj_Year, input_work_dir, EBS_asset_Input, Asset_adjustment, AssetRiskCharge, Regime, PC_method)
        B1 = EBS_Report.BSCR
        
        ### @@@ TEST run_BSCR_new_regime @@@ ###
        EBS_Report.run_BSCR_new_regime(numOfLoB, Proj_Year, Regime, PC_method, curveType, base_GBP, CF_Database, CF_TableName, Step1_Database, work_dir, cash_flow_freq, BMA_curve_dir, Disc_rate_TableName, market_factor = [], input_work_dir = input_work_dir, EBS_asset_Input = EBS_asset_Input, Asset_adjustment = Asset_adjustment, AssetRiskCharge = AssetRiskCharge)
        
        # Calculate ECR % (Step 2) - Vincent 07/18/2019
        EBS_Report.run_BSCR_dashboard(Regime)
        F = EBS_Report.BSCR_Dashboard
        
        EBS_output        = Corp.export_Dashboard(valDate, "Actual", E, F, EBS_output_folder, Regime)
        BSCRDetail_output = Corp.export_BSCRDetail(valDate, "Actual", F, EBS_output_folder, Regime)
   
        B_dic = pd.DataFrame()
        for idx in range(1, numOfLoB + 1, 1):
                res = B[idx].EBS_PVBE
                res = pd.DataFrame(res.items(), columns = ['Time', 'PVBE'])
                res['LOB'] = idx
                B_dic = B_dic.append(res)
    
        B_dic_oas = pd.DataFrame()
        for idx in range(1, numOfLoB + 1, 1):
                res = {'OAS': [B[idx].OAS]}
                res = pd.DataFrame(res)
                res['LOB'] = idx
                B_dic_oas = B_dic_oas.append(res)
#%% Vincent - Stress Scenario    
                
#if __name__ == "__main__":
##    work_dir  = 'C:\\Users\\jizhu\\Desktop\\Python script\\EBS Dashboard\\EC'
#
#    ### 1. Import Scenario Mapping - Define Scenarios
#    M_Stress_Scen = Corp.set_stress_scenarios(work_dir)
#    
#    for EBS_Calc_Date in EBS_Cal_Dates_all:
#            
#        stress_scen = 702 ### to-do: LOOP all the Stress Scenarios: {for key, value in M_Stress_Scen.items()}
#         
#        ### 2. Stess Liability Tech Prov for each Scen
#        ### 2.1 Stressed IR curve for each Scen  
#        Scen_market_factor = IAL_App.Set_Dashboard_Shock_MarketFactors(eval_dates, M_Stress_Scen, stress_scen, market_factor, curveType, curr_GBP, 10, "BBB", IAL_App.KRD_Term)
#
#        ### 2.2 Stressed PVBE ==> modify Lib_Corp_Molde.Run_Liab_DashBoard
#        work_EBS_DB.run_dashboard_stress_liab_value(valDate, EBS_Calc_Date, curveType, numOfLoB, Scen_market_factor, stress_scen, M_Stress_Scen, liab_spread_beta)
#        
#### Validation ###
#    work_liab_stress =  work_EBS_DB.liability[stress_scen]
#    work_liab_base = work_EBS_DB.liability['base']
#        
#    tech_prov_base =[]
#    for idx in range(1, numOfLoB + 1, 1):
#        tech_prov_base.append(work_liab_base[idx].technical_provision)
#        
#    tech_prov =[]
#    for idx in range(1, numOfLoB + 1, 1):
#        tech_prov.append(work_liab_stress[idx].technical_provision)
#            
#    oas_base =[]
#    for idx in range(1, numOfLoB + 1, 1):
#        oas_base.append(work_liab_base[idx].OAS)
#        
#    oas =[]
#    for idx in range(1, numOfLoB + 1, 1):
#        oas.append(work_liab_stress[idx].OAS)
            
#%%           
#    work_EBS_DB.export_LiabAnalytics(work_EBS_DB.liability['dashboard'], excel_out_file, work_dir)    
#    work_EBS = work_EBS_DB.EBS
#    work_liab_base = work_EBS_DB.liability['base']
#    work_liab_base_summary = work_EBS_DB.liab_summary['base']
#    work_liab_DB = work_EBS_DB.liability['dashboard']
#    work_liab_db_summary = work_EBS_DB.liab_summary['dashboard']
#    work_asset_holding = work_EBS_DB.asset_holding
#    work_bscr = work_EBS_DB.BSCR_Base
#    work_bscr_db = work_EBS_DB.BSCR_Dashboard
#   
#    test = work_asset_holding.groupby(['Category'])['Market Value USD GAAP'].agg('sum')
    
#    
#    groupByFields = ['Category_f']
#    sumFields = groupByFields.copy()
#    sumFields.append('Market Value USD GAAP')
#    mv = work_asset_holding.loc[pd.notnull(work_asset_holding['Market Value USD GAAP']), sumFields].groupby(groupByFields).sum()

#    work_liab_summry = Corp.summary_liab_analytics(work_liab_DB, numOfLoB)
#    test = work_liab_summry['agg']['PV_BE']
#    work_EBS = Corp.run_EBS_dashboard(work_EBS, {}, work_liab_DB, numOfLoB)
    

#    irCurve_GBP = IAL_App.load_BMA_Std_Curves(valDate, "GBP",valDate)
#    irCurve_GBP_re = IAL_App.load_BMA_Std_Curves(valDate, "GBP",EBS_Calc_Date)    
#    
#    swap_gbp = IAL_App.createAkitZeroCurve(valDate, "Swap", "GBP")
#    swap_gbp_re = IAL_App.createAkitZeroCurve(EBS_Calc_Date, "Swap", "GBP")
#    
#    a = irCurve_GBP.zeroRate(10)
#    b = irCurve_GBP_re.zeroRate(100)
#    
#    c = swap_gbp.zeroRate(10)
#    d = swap_gbp_re.zeroRate(10)
#  
    
#    irCurve_USD = IAL_App.createAkitZeroCurve(valDate, "Treasury", "USD")
#    irCurve = irCurve_USD
#
#    work_liab_base = work_EBS_DB.liability['base']
#    clsLiab  = work_liab_base[12]
#    cf_idx   = clsLiab.cashflow
#    cfHandle = IAL.CF.createSimpleCFs(cf_idx["Period"],cf_idx["aggregate cf"])

#    pvbe     = IAL.CF.PVFromCurve(cfHandle, irCurve_GBP, valDate)    
#    pvbe     = IAL.CF.PVFromCurve(cfHandle, irCurve_USD, valDate)    
#    
#    oas      = IAL.CF.OAS(cfHandle, irCurve, valDate, -clsLiab.PV_BE)
#    effDur   = IAL.CF.effDur(cfHandle, irCurve, valDate, oas)
#    ytm      = IAL.CF.YTM(cfHandle, -clsLiab.PV_BE, valDate)
#    conv     = IAL.CF.effCvx(cfHandle, irCurve, valDate, oas)
#    
#    krd = []
#    krd_name = []
#    for key, value in KRD_Term.items():
#        krd.append(IAL.CF.keyRateDur(cfHandle, irCurve_USD, valDate, key, 100))
#        krd_name.append('KRD_' + key)

#Unit Test
#    work_liab_cf       = Corp.get_liab_cashflow(valDate, CF_Database, CF_TableName, Step1_Database, PVBE_TableName, bindingScen, numOfLoB, work_dir)
#    work_liab_cf       = Corp.Set_Liab_Base(valDate, curveType, base_GBP, numOfLoB, work_liab_cf, "BBB")
#    work_liab_ebs      = Corp.Run_Liab_DashBoard(valDate, EBS_Calc_Date, curveType, numOfLoB, work_liab_cf, market_factor, liab_spread_beta)
#    work_asset_holding = Corp.get_asset_holding(valDate, work_dir)
    

   #    zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
#    mv_test = Set_EBS_Base(valDate, work_asset_holding['base'].get_asset_value('asset_holding'))

#    db_asset_holding = Asset_App.daily_portfolio_feed(asset_workDir, asset_fileName,0)
#    
#
##    Run Liability Dashboard
#
#    work_asset_ebs = Corp.Run_Asset_DashBoard(valDate, EBS_Calc_Date, work_asset_holding, market_factor)
#
#    exportLobAnalytics_test(work_liab_base,numOfLoB, work_dir)
#    market_factor = Corp.Set_Dashboard_MarketFactors(valDate, EBS_Calc_Date, curveType, curr_GBP, 5, "A")

#market_Index = MKT.TSR.MarketData(marketIndexDict.get("US_Equity"), valDate)
   
    
#    market_factor_BBB = Corp.Set_Dashboard_MarketFactors(eval_dates, curveType, curr_GBP, 10, "BBB")
#
#    test_spread = market_factor_BBB[(market_factor_BBB['val_date'] == EBS_Calc_Date)].Credit_Spread.values[0]
#    test_spread_base = market_factor_BBB[(market_factor_BBB['val_date'] == valDate)].Credit_Spread.values[0]
#    spread_change = test_spread - test_spread_base    
#    
#    dateTest = valDate + datetime.timedelta(10 * 365)
#    
#    test_curve = IAL_App.createAkitZeroCurve(valDate, "Credit", "USD", "BBB")
##    test_date = IAL.Util.addTerms(valDate, "1Y")
##    rate      = IAL.YieldCurve.zeroRate(test,10,"CONTINUOUS", "N", "ACT/365")
#    rate2      = test_curve.zeroRate(10)
#    
#    
#    fwdRateTest = ac_curve_handle.fwdRate(ini_date + datetime.timedelta(10), ini_date + datetime.timedelta(40))
#
#    Corp.exportLobAnalytics(work_liab_DB, excel_out_file, work_dir)

#    cal_test = work_liab_cf[1].get_cashflow('Liab Cash Flow')
#    cal_test['test'] = cal_test['Total net cashflow'] *2
#    cal_test['cf_acc'] = cal_test['Total net cashflow'] *0
#    
#    for work_t in range(1, 281, 1):
#        if work_t == 1:
#           cal_test.loc[cal_test['Row_No'] == work_t, 'cf_acc'] = cal_test.loc[cal_test['Row_No'] == work_t, 'Total net cashflow']
#        else:
#           cal_test.loc[cal_test['Row_No'] == work_t, 'cf_acc'] = cal_test.loc[cal_test['Row_No'] == work_t, 'Total net cashflow'] + cal_test.loc[cal_test['Row_No'] == work_t-1, 'cf_acc']
#
##    exportLobAnalytics(work_liab_cf)
##    work_dashboard = runEBSDashboard()




