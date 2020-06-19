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
import Lib_Market_Akit_new_format as IAL_App
#import App_daily_portfolio_feed as Asset_App
import Lib_Corp_Model_new_format as Corp
import Class_Corp_Model_new_format as Corpclass
import Lib_BSCR_Model_new_format as BSCR
import Lib_Utility as Util
import App_daily_portfolio_feed_new_format as Asset_App
import Config_BSCR as BSCR_Cofig
import User_Input_Dic_new_format as UI
import IALPython3 as IAL
#from _Class_Corp_Model import LiabAnalytics
import pandas as pd
import math as math
from pandas.tseries.offsets import YearEnd

import Config_EBS_Dashboard as cfg_EBS
import Config_Scenarios as Scen_Cofig
import Class_Scenarios as Scen_class
import Lib_Corp_Model_Attribution as liab_att
import asset_attribution_new_format as asset_att


if __name__ == "__main__":
    
#============================ Model ==========================#
#                                                             |
    Model_to_Run   = "Estimate" # "Actual" or "Estimate"        |
#                                                             |
#======================= Stress testing ======================#
#                                                             |       
    Stress_testing = False # True or False                     |
    Asset_est = 'Bond_Object' # 'Bond_Object' or 'Dur_Conv'   |
#                                                             | 
#=========================== Swithch =========================#
#                                                             |       
    Der_1_day_lag_fix = 'No' # "Yes" or 'No'                  |
#                                                             |    
#=============================================================#    
       
    work_dir       = 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\2020Q1'
    
    input_work_dir = r'L:\\DSA Re\\Workspace\\Production\\2020_Q1\\BMA Best Estimate\\Step 2 Python Parallel\\Main_Run_v003\\Input'      # Only for Act Model
    input_fileName = r'.\Input_1Q20.xlsx'
    manual_input_file = pd.ExcelFile(input_work_dir + '//Input_1Q20.xlsx') 
    Time_0_asset_filename = r'.\Asset with exclusion (cash and STI).xlsx'    # 1Q20 input   # Only for Act Model
    alba_filename = r'.\ALBA bucketed risks 2020Q1.xlsx'                     # 1Q20 input   # Only for Act Model, to load ALBA duration into asset holdings.
    SFS_File = r'L:\\DSA Re\\Workspace\\Production\2020_Q1\\BMA Best Estimate\\Step 2 Python Parallel\\Main_Run_v003\\Input\\SFS_1Q20.xlsx'           # Only for Act Model
    
    BMA_curve_dir  = 'L:\DSA Re\\Workspace\Production\EBS Dashboard\Python_Code\BMA_Curves'    
    asset_workDir  = r'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\Asset_Holding_Feed'
    concentration_Dir = r'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\Asset_Holding_Feed\\concentration_risk'
    
    Dashboard_output_folder = 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\Dashboard_outputs'
    EBS_output_folder = r'L:\\DSA Re\\Workspace\\Production\2020_Q1\\BMA Best Estimate\\Step 2 Python Parallel\\Main_Run_v003\\Output'
    
    curveType        = "Treasury"
    numOfLoB         = 45
    Proj_Year        = 69
    ccy              = "USD"
    bindingScen          = 1
    bindingScen_Discount = 1
    base_GBP         = 1.243677702 # 4Q18: 1.2755; # 1Q19: 1.3004; 2Q19: 1.26977; 3Q19: 1.2299; 4Q19: 1.3263791128; 1Q20: 1.243677702
#    curr_GBP         = 1.26977 # IAL_App.get_GBP_rate(EBS_Calc_Date, curvename = 'FX.USDGBP.SPOT.BASE')
#    liab_spread_beta = 0.65 

    Regime = "Current" # "Current" or "Future"  
    PC_method = "Bespoke" # "Bespoke" or "BMA" 
    
    CF_Database = 'alm'
    CF_Database =  r'L:\DSA Re\Workspace\Production\2020_Q1\BMA Best Estimate\Main_Run_v003\0_CORP_20190903_00_AggregateCFs_Result.accdb'
    # 4Q18: r'L:\DSA Re\Workspace\Production\2018_Q4\BMA Best Estimate\Main_Run_v007_Fulton\0_Baseline_Run\0_CORP_20190420_00_AggregateCFs_Result.accdb'
    # 1Q19: r'L:\DSA Re\Workspace\Production\2019_Q1\BMA Best Estimate\Main_Run_v002\0_CORP_20190510_00_AggregateCFs_Result.accdb'
    # 2Q19: r'L:\DSA Re\Workspace\Production\2019_Q2\BMA Best Estimate\Main_Run_v003\0_CORP_20190510_00_AggregateCFs_Result.accdb'
    # 3Q19: r'L:\DSA Re\Workspace\Production\2019_Q3\BMA Best Estimate\Main_Run_v003\0_CORP_20190903_00_AggregateCFs_Result.accdb'
    # 4Q19: r'L:\DSA Re\Workspace\Production\2019_Q4\BMA Best Estimate\Main_Run_v001\Profit Center\0_CORP_20190903_00_AggregateCFs_Result.accdb' 
    
    cash_flow_freq = 'A'
    CF_TableName   = "I_LBA____032020____________00"
    
    # 4Q18: "I_LBA____122018____________00"
    # 1Q19: "I_LBA____032019____________00"
    # 2Q19: "I_LBA____062019____________00"
    # 3Q19: "I_LBA____092019____________00"
    
    Step1_Database = r'L:\DSA Re\Workspace\Production\2020_Q1\BMA Best Estimate\Main_Run_v003\1_CORP_20200116_00_Output.accdb'
    # 4Q18: r'L:\DSA Re\Workspace\Production\2018_Q4\BMA Best Estimate\Main_Run_v007_Fulton\0_Baseline_Run\1_CORP_20190412_00_Output.accdb'
    # 1Q19: r'L:\DSA Re\Workspace\Production\2019_Q1\BMA Best Estimate\Main_Run_v002\1_CORP_20190510_00_Output.accdb'
    # 2Q19: r'L:\DSA Re\Workspace\Production\2019_Q2\BMA Best Estimate\Main_Run_v003\1_CORP_20190510_00_Output.accdb'
    # 3Q19: r'L:\DSA Re\Workspace\Production\2019_Q3\BMA Best Estimate\Main_Run_v003\1_CORP_20191028_00_Output.accdb'
    # 4Q19: r'L:\DSA Re\Workspace\Production\2019_Q4\BMA Best Estimate\Main_Run_v001\Profit Center\1_CORP_20200116_00_Output.accdb'

    Disc_rate_TableName    = 'O_DIS____032020_032020_____00'    
    PVBE_TableName         = "O_PVL____032020_032020_____01"
    
    # Estimate Model Only
    BSCRRisk_agg_TableName = 'O_PVA____032020_032020_____01'
    BSCRRisk_LR_TableName  = 'O_PVA____032020_032020_____04'
    BSCRRisk_PC_TableName  = 'O_PVA____032020_032020_____07'   
#     1Q19:'O_PVA____032019_032019_____11' / 'O_PVA____032019_032019_____14' / 'O_PVA____032019_032019_____17'
    
    ## Estimate Model Only, OAS file needs to be updated quarterly
    OAS_fileName = r'.\OAS-20Q1.xlsx'
    # 4Q19: r'.\OAS-Q4_update.xlsx'
    # 3Q19: r'.\OAS-q3.xlsx'


#   run set up
    valDate    = datetime.datetime(2020, 3, 31) ### to be consistent with Step 2
    Price_Date = [datetime.datetime(2019, 10, 31),
                  datetime.datetime(2019, 11, 30),
                  datetime.datetime(2019, 12, 31),
                  datetime.datetime(2020, 1, 31),
                  datetime.datetime(2020, 2, 29),
                  datetime.datetime(2020, 3, 31), 
                  datetime.datetime(2020, 4, 30),      
                  datetime.datetime(2020, 5, 29),      
                  datetime.datetime(2020, 5, 31),      
                           
                  ] ### for illiquidity impact estimation
       
    Scen_results = {}
    _loadBase = True
    
    if Stress_testing:       
        # Define Stress Scenarios                
        Stress_Scen = [
                        # 'Base',
                        # 'Testing',
                        # 'Today_March_6th_IR',
                        # 'Today_March_6th_CS',
                        # 'Today_March_6th',
                        # 'Today_March_10th',
                        # 'ERM_Longevity_1_in_100',
                        # 'ERM_PC_1_in_100',
                        # 'ERM_Alts_1_in_100',
                        # 'ERM_MLIII_1_in_100',
                        # 'ERM_Mort_1_in_100',
                        # 'ERM_Expense_1_in_100',
                        # 'ERM_Lapse_1_in_100',
                        # 'ERM_Morb_1_in_100',
                        # 'ERM_Longevity_Trend_1_in_100',
                        # 'SFP',
                        # 'Comp',
                        # 'COVID_19',
                        # 'ERM_IR_1_in_100_up',
                        # 'ERM_IR_1_in_100_dn',
                        # 'ERM_CS_1_in_100_up',
                        # 'ERM_CS_1_in_100_dn',               
                      ]
        
    else:
        Stress_Scen = ['Base']
    
    for each_Scen in Stress_Scen:
        Scen_results[each_Scen] = {}
        Scen = getattr(Scen_Cofig, each_Scen) 
        
        liab_spread_beta = Scen['Liab_Spread_Beta']
        print('liab_spread_beta is ' + str(liab_spread_beta))
#%%
        if Model_to_Run == "Estimate": ### EBS Dashboard Model
            print('Running EBS Dashboard for Scenario ' + Scen['Scen_Name'])
            
            EBS_Cal_Dates_all = [
    #                             datetime.datetime(2019, 9, 18),
    #                             datetime.datetime(2019, 9, 19),
    #                             datetime.datetime(2019, 9, 20),
#                                 datetime.datetime(2019, 9, 30),
#                                 datetime.datetime(2019, 12, 31),
#                            datetime.datetime(2020, 1, 1),
#                            datetime.datetime(2020, 1, 2),
#                            datetime.datetime(2020, 1, 3),
#                            datetime.datetime(2020, 1, 7),
#                            datetime.datetime(2020, 1, 8),
#                            datetime.datetime(2020, 1, 9),
#                            datetime.datetime(2020, 1, 10),
#                            datetime.datetime(2020, 1, 13),
#                            datetime.datetime(2020, 1, 14),
#                            datetime.datetime(2020, 1, 15),
#                            datetime.datetime(2020, 1, 17),
#                            datetime.datetime(2020, 1, 20),
#                            datetime.datetime(2020, 1, 21),
#                            datetime.datetime(2020, 1, 22),
#                            datetime.datetime(2020, 1, 23),
#                            datetime.datetime(2020, 1, 24),
#                            datetime.datetime(2020, 1, 27),
#                            datetime.datetime(2020, 1, 28),
#                            datetime.datetime(2020, 1, 29),
#                            datetime.datetime(2020, 1, 30),
#                            datetime.datetime(2020, 1, 31),
#                            datetime.datetime(2020, 2, 3),
#                            datetime.datetime(2020, 2, 4),
#                            datetime.datetime(2020, 2, 5),
#                            datetime.datetime(2020, 2, 6),
#                            datetime.datetime(2020, 2, 7),
#                            datetime.datetime(2020, 2, 10),
#                            datetime.datetime(2020, 2, 11),
#                            datetime.datetime(2020, 2, 12),
#                            datetime.datetime(2020, 2, 13),
#                            datetime.datetime(2020, 2, 14),
#                            datetime.datetime(2020, 2, 17),
#                            datetime.datetime(2020, 2, 18),
#                            datetime.datetime(2020, 2, 19),
#                            datetime.datetime(2020, 2, 20),
#                            datetime.datetime(2020, 2, 21),
#                            datetime.datetime(2020, 2, 24),
#                            datetime.datetime(2020, 2, 25),   
#                            datetime.datetime(2020, 2, 26),  
#                             datetime.datetime(2020, 2, 27), 
#                             datetime.datetime(2020, 2, 28), 
#                             datetime.datetime(2020, 3, 2),
#                             datetime.datetime(2020, 3, 3),
#                             datetime.datetime(2020, 3, 4),
#                             datetime.datetime(2020, 3, 5),
#                             datetime.datetime(2020, 3, 6),
#                             datetime.datetime(2020, 3, 9),
#                             datetime.datetime(2020, 3, 10),
#                             datetime.datetime(2020, 3, 11),
#                             datetime.datetime(2020, 3, 12),
#                             datetime.datetime(2020, 3, 13),
#                             datetime.datetime(2020, 3, 16),
#                             datetime.datetime(2020, 3, 17),
#                             datetime.datetime(2020, 3, 18),
#                             datetime.datetime(2020, 3, 19),
#                             datetime.datetime(2020, 3, 20),
#                             datetime.datetime(2020, 3, 23),
#                             datetime.datetime(2020, 3, 24),
#                             datetime.datetime(2020, 3, 25),
#                             datetime.datetime(2020, 3, 26),
#                             datetime.datetime(2020, 3, 27),
#                             datetime.datetime(2020, 3, 30),
#                             datetime.datetime(2020, 3, 31),
                             datetime.datetime(2020, 4, 30),
                             datetime.datetime(2020, 5, 28),
#                             datetime.datetime(2020, 5, 29),
                             datetime.datetime(2020, 5, 31),
#                             datetime.datetime(2020, 6, 1),
#                             datetime.datetime(2020, 6, 3),
#                             datetime.datetime(2020, 6, 4),
#                             datetime.datetime(2020, 6, 5),
#                             datetime.datetime(2020, 6, 8),
#                             datetime.datetime(2020, 6, 9),
#                             datetime.datetime(2020, 6, 10),
#                             datetime.datetime(2020, 6, 11),
#                             datetime.datetime(2020, 6, 12),
                                 
                                 ]
        
             #    Market Factors
            eval_dates = [ valDate ] + Price_Date + EBS_Cal_Dates_all
            eval_dates = list(set(eval_dates))
            
            market_factor        = IAL_App.Set_Dashboard_MarketFactors(eval_dates, curveType, 10, "BBB", 'A', IAL_App.KRD_Term, "USD")
#            market_factor_GBP_IR = IAL_App.Set_Dashboard_MarketFactors(eval_dates, curveType, 10, "BBB", 'A', IAL_App.KRD_Term, "GBP")                
            market_factor_GBP     = IAL_App.Set_Dashboard_MarketFactors(eval_dates, "Swap", 10, "BBB", 'A', IAL_App.KRD_Term, "GBP")
            market_factor_att        = IAL_App.Set_Dashboard_MarketFactors(eval_dates, curveType, 10, "BBB", 'A', IAL_App.KRD_Term_new_format, "USD")

        # Update OAS and MV for illiquid assets
#            Asset_App.update_illiquid_oas(EBS_Cal_Dates_all, asset_workDir, market_factor,Price_Date, write_to_excel = 1)

#         ## Asset attribution
#            asset_attribution = asset_att.Run_asset_Attribution(valDate, market_factor_att, EBS_Cal_Dates_all, Price_Date, asset_workDir)
#            asset_att.exportasset_Att(asset_attribution, EBS_Cal_Dates_all, work_dir)
#
        # get OAS change from asset attribution
#            load_oas_change   = Asset_App.load_asset_OAS(EBS_Cal_Dates_all, asset_workDir, asset_attribution,OAS_fileName)
            asset_OAS            = Asset_App.Set_weighted_average_OAS(valDate,EBS_Cal_Dates_all,asset_workDir,OAS_fileName)       
            market_factor_c      =  pd.merge(market_factor,asset_OAS,left_on='val_date',right_on = 'ValDate')

    
            AssetRiskCharge = BSCR_Cofig.asset_charge(asset_workDir, 'Mapping.xlsx')
            
            EBS_DB_results = {}
                    
            for index, EBS_Calc_Date in enumerate(EBS_Cal_Dates_all):
        
                BMA_curve_file = 'BMA_Curves_' + valDate.strftime('%Y%m%d') + '.xlsx' 
                asset_fileName = r'.\Asset_Holdings_' + EBS_Calc_Date.strftime('%Y%m%d') + '_update_oas.xlsx'
                deri_fileName = r'.\Asset_Holdings_' + EBS_Calc_Date.strftime('%Y%m%d') + '.xlsb'
                
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
                csv_out_file   = work_dir + '\EBS_Liab_Output_' + valDate.strftime('%Y%m%d') + '_' + EBS_Calc_Date.strftime('%Y%m%d') + '.csv'
                # Set the base line cash flows and valuations
                work_EBS_DB = Corpclass.EBS_Dashboard(EBS_Calc_Date, "Estimate", valDate, Stress_testing)
                
                # Set daily asset holdings
                work_EBS_DB.set_asset_holding(asset_workDir, asset_fileName, asset_fileName_T_plus_1, Price_Date, market_factor)  
                Asset_Est = work_EBS_DB.asset_holding
                # add derivative to the asset holding
                if EBS_Calc_Date >= datetime.datetime(2020,4,30):
                    work_EBS_DB.set_derivative_charge(asset_workDir,deri_fileName)
                
                
                # Stressed Asset info 
                if Stress_testing:
                    print('Calculating Stressed Asset Info for ' + str(EBS_Calc_Date) + '...')
                    credit_shock_Map = pd.DataFrame(Scen)['Credit_Spread_Shock_bps']
                    credit_shock_Map = credit_shock_Map.append(pd.Series(data = {'NA-BBB': credit_shock_Map['BBB'], 0: credit_shock_Map['BBB'] }, name = 'Credit_Spread_Shock_bps')) # Map AIG Derived Rating: NA(i.e. =0) to BBB
                    
                    try:
                        Asset_Est = Asset_Est.drop(columns = ['Credit_Spread_Shock_bps'], axis = 1)                   
                    except:
                        pass
                    
                    Asset_Est = Asset_Est.merge(credit_shock_Map, how='left', left_on=['Derived Rating Modified'], right_on = credit_shock_Map.index)
                    
                    Scen['Credit_Spread_Shock_bps']['Average'] = sum(Asset_Est['FIIndicator'] * Asset_Est['Market Value with Accrued Int USD GAAP'] * Asset_Est['Credit_Spread_Shock_bps']) / \
                                                                 sum(Asset_Est['FIIndicator'] * Asset_Est['Market Value with Accrued Int USD GAAP']) # for spread shock on liability
                    print('Average credit shock is ' + str(Scen['Credit_Spread_Shock_bps']['Average']) )
                    
                    work_EBS_DB.stressed_asset_holding = Asset_App.stressed_actual_portfolio_feed(Asset_Est, Scen, valDate, Asset_est)                                             
                    Asset_Est_Stressed = work_EBS_DB.stressed_asset_holding
                
                # Set LOB Definition, get LBA CFs + GOE, time 0 PVBE/RM/TP
                work_EBS_DB.set_base_cash_flow(valDate, CF_Database, CF_TableName, Step1_Database, PVBE_TableName, bindingScen, numOfLoB, Proj_Year, work_dir, cash_flow_freq, Scen)
#                A_Est = work_EBS_DB.liability['base']
    
                # Calculate time 0 OAS, Duration and Convexity etc.
                work_EBS_DB.set_base_liab_value(valDate, curveType, base_GBP, numOfLoB, "BBB")
#                B_Est = work_EBS_DB.liability['base']
    
                # Time 0 PVBE, RM and TP summary: Agg/LT/PC            
                work_EBS_DB.set_base_liab_summary(numOfLoB)
#                C_Est = work_EBS_DB.liab_summary['base']
                
                # Calculate PVBE @ reval_date          
                work_EBS_DB.run_dashboard_liab_value(valDate, EBS_Calc_Date, curveType, numOfLoB, market_factor_c, liab_spread_beta)
                
                # # Set stressed curve
                # work_scen = Scen_class.Scenario(valDate, EBS_Calc_Date, Scen)
                # work_scen.setup_scen()
                
                # projection dates and ir curve
                nested_proj_dates =[]
                date_end = valDate+YearEnd(Proj_Year+1)
                if EBS_Calc_Date == EBS_Calc_Date + YearEnd(0): #identify if the revaluation date is also year end
                    date_end = EBS_Calc_Date+YearEnd(Proj_Year+1)
                    nested_proj_dates.extend(list(pd.date_range(EBS_Calc_Date+YearEnd(1), date_end, freq=cash_flow_freq)))
                else:
                    date_end = valDate+YearEnd(Proj_Year+1)
                    nested_proj_dates.extend(list(pd.date_range(EBS_Calc_Date, date_end, freq=cash_flow_freq)))
                
#                irCurve_USD_eval = IAL_App.load_BMA_Std_Curves(valDate, "USD", EBS_Calc_Date)
                irCurve_USD_eval = IAL_App.createAkitZeroCurve(EBS_Calc_Date, curveType, "USD")
                irCurve_GBP_eval = IAL_App.load_BMA_Std_Curves(valDate, "GBP", EBS_Calc_Date)
                
                # Calculate PVBE projection
                for t, each_date in enumerate(nested_proj_dates):
                    work_EBS_DB.run_projection_liab_value(valDate, each_date, curveType, numOfLoB, market_factor_c, liab_spread_beta, IAL_App.KRD_Term, irCurve_USD_eval, irCurve_GBP_eval, base_GBP, EBS_Calc_Date)                        
                Corp.projection_summary(work_EBS_DB.liability, nested_proj_dates) # Load EBS_PVBE projection (PVBE_net) into work_EBS_DB.liability['dashboard']
#                D_Est = work_EBS_DB.liability['dashboard']
                
                # Calculate BSCR @ reval_date 
                work_EBS_DB.run_estimate_BSCR(numOfLoB, Proj_Year, Regime, PC_method, concentration_Dir, AssetRiskCharge)
#                D1_Est = work_EBS_DB.BSCR        
                
                # Calculate RM @ reval_date
                work_EBS_DB.run_RiskMargin(valDate, Proj_Year, Regime, BMA_curve_dir, Scen)
#                D2_Est = work_EBS_DB.RM
                
                # Calculate TP @ reval_date                      
                work_EBS_DB.run_TP(numOfLoB, Proj_Year)
#                D3_Est = work_EBS_DB.liability['dashboard']
                      
                # reval_date PVBE, RM and TP summary: Agg/LT/PC
                work_EBS_DB.set_dashboard_liab_summary(numOfLoB) 
#                E_Est = work_EBS_DB.liab_summary['dashboard']
                        
                # Set up EBS
                os.chdir(work_dir)
                work_EBS_DB.run_EBS(Scen, [], [], market_factor)
#                F_Est = work_EBS_DB.EBS
                
                # Run_IR_BSCR_future_regime, with asset_holding_base 
                if Regime == 'Future':
                    work_EBS_DB.run_BSCR_new_regime(Scen, numOfLoB, Proj_Year, Regime, PC_method, curveType, base_GBP, CF_Database, CF_TableName, Step1_Database, work_dir, cash_flow_freq, BMA_curve_dir, Disc_rate_TableName, market_factor_c, Stress_testing = Stress_testing)
              
                # Calculate BSCR @ reval_date (Currency, Equity, IR and Market BSCR)
                work_EBS_DB.run_estimate_BSCR(numOfLoB, Proj_Year, Regime, PC_method, concentration_Dir, AssetRiskCharge)
#                D1_Est = work_EBS_DB.BSCR        
                         
                # Calculate ECR %
                work_EBS_DB.run_BSCR_dashboard(Regime)
#                G = work_EBS_DB.BSCR_Dashboard
                     
                EBS_DB_results[EBS_Calc_Date] = work_EBS_DB
                EBS_output        = Corp.export_Dashboard(EBS_Calc_Date, "Estimate", work_EBS_DB.EBS, work_EBS_DB.BSCR_Dashboard, Dashboard_output_folder, Regime)
                BSCRDetail_output = Corp.export_BSCRDetail(EBS_Calc_Date, "Estimate", work_EBS_DB.BSCR_Dashboard, Dashboard_output_folder, Regime)
                print('EBS Dashboard: ', EBS_Calc_Date.strftime('%Y%m%d'), ' has been completed')
                work_EBS_DB.export_LiabAnalytics(work_EBS_DB.liability['dashboard'], excel_out_file, work_dir, valDate, EBS_Calc_Date,csv_out_file)
            
#                Scen_results[each_Scen][EBS_Calc_Date] = work_EBS_DB 

            liab_attribution = liab_att.Run_Liab_Attribution(valDate, EBS_DB_results, market_factor, market_factor_GBP, numOfLoB)
            liab_att.exportLobLiab(liab_attribution, EBS_Cal_Dates_all, work_dir)

#         Asset attribution
#            asset_attribution = asset_att.Run_asset_Attribution(EBS_DB_results,valDate, market_factor_att, EBS_Cal_Dates_all, Price_Date, asset_workDir)
#            asset_att.exportasset_Att(asset_attribution, EBS_Cal_Dates_all, work_dir)
            
        ###-----------------------------------------------------------------------------------------------------------------------------------------------------###
        
        elif Model_to_Run == "Actual":  ### EBS Reporting Model
            print('Running EBS Reporting for Scenario ' + Scen['Scen_Name'])
            
            if each_Scen in ['ERM_Expense_1_in_100']:  # reload GOE and apply shock
                _loadBase = True
                
            if _loadBase:         
                EBS_Report = Corpclass.EBS_Dashboard(valDate, "Actual", valDate, Stress_testing)
                
                # Set LOB Definition, get LBA CFs + GOE - Vincent 07/02/2019
                print('LOB Definition ...')
                EBS_Report.set_base_cash_flow(valDate, CF_Database, CF_TableName, Step1_Database, PVBE_TableName, bindingScen, numOfLoB, Proj_Year, work_dir, cash_flow_freq, Scen)
                A = EBS_Report.liability['base']
                
                # MircoStrategy Asset info 
                print('Loading Asset Info ...')  
                AssetRiskCharge = BSCR_Cofig.asset_charge(input_work_dir, input_fileName)
                
                ### Testing: 1) 1st valDate to be changed to eval_date 2) to be put in class.set_asset_holding
                EBS_Asset_Input_Base = Asset_App.actual_portfolio_feed(valDate, valDate, input_work_dir, Time_0_asset_filename, alba_filename, output = 0)
                
                Asset_adjustment = Asset_App.Asset_Adjustment_feed(manual_input_file.parse('Asset_Adjustment'))
                
                print('Loading SFS Balance Sheet ...')
                EBS_Report.set_sfs(SFS_File) # Vincent update - using SFS class 07/30/2019
                S1 = EBS_Report.SFS
                
                # Calculate PVBE and projections thereof - Vincent 07/02/2019
                print('PVBE Calculation ...')
                if Stress_testing:
                    # OAS is based on US TSY curve
                    base_scen = Scen_class.Scenario(valDate, valDate, getattr(Scen_Cofig, 'Base'))
                    base_scen.setup_scen()
                    EBS_Report.run_PVBE(valDate, numOfLoB, Proj_Year, bindingScen_Discount, BMA_curve_dir, Step1_Database, Disc_rate_TableName, base_GBP, Stress_testing, base_scen)
                else:
                    base_scen = 0
                    EBS_Report.run_PVBE(valDate, numOfLoB, Proj_Year, bindingScen_Discount, BMA_curve_dir, Step1_Database, Disc_rate_TableName, base_GBP, Stress_testing)
                    
                B = EBS_Report.liability['base']
            
                _loadBase = False
            
            # Stressed Asset info 
            if Stress_testing:
                print('Calculating Stressed Asset Info ...')
                credit_shock_Map = pd.DataFrame(Scen)['Credit_Spread_Shock_bps']
                credit_shock_Map = credit_shock_Map.append(pd.Series(data = {'NA-BBB': credit_shock_Map['BBB'], 0: credit_shock_Map['BBB'] }, name = 'Credit_Spread_Shock_bps')) # Map AIG Derived Rating: NA(i.e. =0) to BBB
                
                try:
                    EBS_Asset_Input_Base = EBS_Asset_Input_Base.drop(columns = ['Credit_Spread_Shock_bps'], axis = 1)
                    
                except:
                    pass
                
                EBS_Asset_Input_Base = EBS_Asset_Input_Base.merge(credit_shock_Map, how='left', left_on=['Derived Rating Modified'], right_on = credit_shock_Map.index)
                
                Scen['Credit_Spread_Shock_bps']['Average'] = sum(EBS_Asset_Input_Base['FIIndicator'] * EBS_Asset_Input_Base['Market Value with Accrued Int USD GAAP'] * EBS_Asset_Input_Base['Credit_Spread_Shock_bps']) / \
                                                             sum(EBS_Asset_Input_Base['FIIndicator'] * EBS_Asset_Input_Base['Market Value with Accrued Int USD GAAP']) # for spread shock on liability
                print('Average credit shock is ' + str(Scen['Credit_Spread_Shock_bps']['Average']) )
                
                EBS_Asset_Input_Stressed = Asset_App.stressed_actual_portfolio_feed(EBS_Asset_Input_Base, Scen, valDate, Asset_est)                                             
                EBS_Asset_Input          = EBS_Asset_Input_Stressed
                
            else:
                EBS_Asset_Input = EBS_Asset_Input_Base
                                  
            # Stressed Liability - instaneous shock
            if Stress_testing:
                print('Stressed PVBE Calculation ...') 
                # Set stressed curve
                work_scen = Scen_class.Scenario(valDate, valDate, Scen)
                work_scen.setup_scen()
                
                # Recalculate stressed PVBE @ valDate       
                EBS_Report.run_dashboard_liab_value(valDate, valDate, curveType, numOfLoB, [], liab_spread_beta, irCurve_USD = work_scen._IR_Curve_USD, irCurve_GBP = work_scen._IR_Curve_GBP, gbp_rate = base_GBP, Scen = Scen)
                B_stress = EBS_Report.liability['stress']
                
            # Calculate BSCR and projections thereof - Vincent 07/09/2019
            EBS_Report.Run_Iteration = 0
            print('BSCR Calculation Iteration ' + str(EBS_Report.Run_Iteration) + '...')
            EBS_Report.run_BSCR(numOfLoB, Proj_Year, input_work_dir, EBS_Asset_Input, Asset_adjustment, AssetRiskCharge, Regime, PC_method)
            B1 = EBS_Report.BSCR
            
            print('Risk Margin Calculation...')
            EBS_Report.run_RiskMargin(valDate, Proj_Year, Regime, BMA_curve_dir, Scen)
            B2 = EBS_Report.RM
         
            print('TP Calculation...')
            EBS_Report.run_TP(numOfLoB, Proj_Year)
            B3 = EBS_Report.liability['base']
              
            # PVBE, BSCR and TP summary: Agg/LT/PC - Vincent 07/08/2019
            print('Generating Liability Summary ...')
            EBS_Report.set_base_liab_summary(numOfLoB)
            C = EBS_Report.liab_summary['base']
            if Stress_testing:
                C_stress = EBS_Report.liab_summary['stress']
                
            # Set up EBS - Vincent 07/08/2019
            print('Generating EBS ...')
            os.chdir(work_dir)
            EBS_Report.run_EBS(Scen, EBS_Asset_Input, Asset_adjustment) # Vincent updated 07/17/2019
            E = EBS_Report.EBS
            
            # Run_IR_BSCR_future_regime, with EBS_Asset_Input_Base 
            print('Running Future Regime IR BSCR ...')
            if Regime == 'Future':
                EBS_Report.run_BSCR_new_regime(Scen, numOfLoB, Proj_Year, Regime, PC_method, curveType, base_GBP, CF_Database, CF_TableName, Step1_Database, work_dir, cash_flow_freq, BMA_curve_dir, Disc_rate_TableName, market_factor = [], input_work_dir = input_work_dir, EBS_Asset_Input = EBS_Asset_Input_Base, Stress_testing = Stress_testing, base_scen = base_scen)
        
            # Calculate BSCR (Currency, Equity, IR and Market BSCR) - Vincent 07/30/2019
            print('BSCR Calculation Iteration ' + str(EBS_Report.Run_Iteration) + '...')
            EBS_Report.run_BSCR(numOfLoB, Proj_Year, input_work_dir, EBS_Asset_Input, Asset_adjustment, AssetRiskCharge, Regime, PC_method)
            B1 = EBS_Report.BSCR
                     
            # Calculate ECR % (Step 2) - Vincent 07/18/2019
            EBS_Report.run_BSCR_dashboard(Regime)
            F = EBS_Report.BSCR_Dashboard
            
            EBS_output        = Corp.export_Dashboard(valDate, "Actual", E, F, EBS_output_folder, Regime, each_Scen)
            BSCRDetail_output = Corp.export_BSCRDetail(valDate, "Actual", F, EBS_output_folder, Regime, each_Scen)
                        
            Scen_results[each_Scen][valDate] = EBS_Report
            
            # B_dic = pd.DataFrame()
            # for idx in range(1, numOfLoB + 1, 1):
            #         res = B_stress[idx].EBS_PVBE
            #         res = pd.DataFrame(res.items(), columns = ['Time', 'PVBE'])
            #         res['LOB'] = idx
            #         B_dic = B_dic.append(res)
            # B_dic = B_dic[B_dic['Time']==0]
            
            # B_rm = pd.DataFrame()
            # for idx in range(1, numOfLoB + 1, 1):
            #         res = {'TP': [B_stress[idx].Technical_Provision]} 
            #         res = pd.DataFrame(res)
            #         res['LOB'] = idx
            #         B_rm= B_rm.append(res)
                    
                    
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
    
    
    
    
