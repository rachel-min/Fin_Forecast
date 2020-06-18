# -*- coding: utf-8 -*-
"""
Created on Fri May 17 17:36:26 2019

@author: seongpar
"""

# import os
# =============================================================================
# corp_model_dir = 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code'
# os.sys.path.append(corp_model_dir)
# =============================================================================
from Class_BFO import basic_fin_account
import App_daily_portfolio_feed as Asset_App
import Lib_Corp_Model as Corp
import Lib_BSCR_Model as Bscr
import Lib_Market_Akit   as IAL_App
import datetime
import User_Input_Dic as UI
import copy
# EBS Acount Entry
class EBS_Dashboard(object):
    def __init__(self, eval_date, actual_estimate, liab_base_date, Stress_testing = False):
        self.eval_date       = eval_date
        self.actual_estimate = actual_estimate
        self.liab_base_date  = liab_base_date
        self.stress_testing  = Stress_testing
        self.EBS             = {'Agg' : EBS_Account("Agg"),'LT' : EBS_Account("LT") , 'GI' : EBS_Account("GI") }
        self.EBS_IS          = {'Agg' : EBS_IS("Agg"),     'LT' : EBS_IS("LT") ,      'GI' : EBS_IS("GI") }
        self.Reins           = {'Agg' : Reins_Settlement("Agg"), 'LT' : Reins_Settlement("LT") , 'GI' : Reins_Settlement("GI") }        
        self.SFS             = {'Agg' : SFS_Account("Agg"),'LT' : SFS_Account("LT") , 'GI' : SFS_Account("GI") } ### Vincent 07/30/2019
        self.SFS_IS          = {'Agg' : SFS_IS("Agg"),'LT' : SFS_IS("LT") , 'GI' : SFS_IS("GI") } ### SWP 9/29/2019
        self.Tax_IS          = {'Agg' : Taxable_Income("Agg"),'LT' : Taxable_Income("LT") , 'GI' : Taxable_Income("GI") } ### April 9/30/2019
        self.LOC             = LOC_Account()
        
        self.asset_holding   = {}
        self.liability       = {}
        self.liab_summary    = {}
        self.BSCR_Base       = {'Agg' : BSCR_Analytics("Agg"),'LT' : BSCR_Analytics("LT") , 'GI' : BSCR_Analytics("GI") }
        self.BSCR_Dashboard  = {'Agg' : BSCR_Analytics("Agg"),'LT' : BSCR_Analytics("LT") , 'GI' : BSCR_Analytics("GI") }
        self.BSCR            = {}  ### Vincent 07/09/2019
        self.RM              = {}
        self.Run_Iteration   = 0   ### Vincent 07/30/2019
        
        self._records        = {'LOBs':[]}  ### Kyle 12/05/2019 for validation use
        
        self.stressed_asset_holding = {} ### Vincent 05/18/2020
        
    def set_sfs(self, SFS_File):
        self.SFS = Corp.set_SFS_BS(self.SFS, SFS_File)
        
    def set_asset_holding(self, workDir, fileName, asset_fileName_T_plus_1, Price_Date, market_factor, output = 0, mappingFile = '.\Mapping.xlsx', ratingMapFile = '.\Rating_Mapping.xlsx'):
        self.asset_holding = Asset_App.daily_portfolio_feed(self.eval_date, self.liab_base_date, workDir, fileName, asset_fileName_T_plus_1, Price_Date, market_factor, output, mappingFile, ratingMapFile)       

    def set_base_cash_flow(self, valDate, CF_Database, CF_TableName, Step1_Database, PVBE_TableName, bindingScen, numOfLoB, Proj_Year, work_dir, freq, Scen): ### Vincent 07/02/2019
        self.liability['base'] = Corp.get_liab_cashflow(self.actual_estimate, valDate, CF_Database, CF_TableName, Step1_Database, PVBE_TableName, bindingScen, numOfLoB, Proj_Year, work_dir, freq, Scen = Scen)
  
    def set_base_liab_value(self, valDate, curveType, curr_GBP, numOfLoB, rating = "BBB", irCurve_USD = 0, irCurve_GBP = 0):
        self.liability['base'] = Corp.Set_Liab_Base(valDate, curveType, curr_GBP, numOfLoB, self.liability['base'], rating, irCurve_USD = irCurve_USD, irCurve_GBP = irCurve_GBP)

    def set_base_liab_summary(self, numOfLoB):
        if self.stress_testing:
            self.liab_summary['stress'] = Corp.summary_liab_analytics(self.liability['stress'], numOfLoB)
        # always generate liab_summary['base'], which is needed in new IR BSCR
        self.liab_summary['base'] = Corp.summary_liab_analytics(self.liability['base'], numOfLoB)

    def run_dashboard_liab_value(self, valDate, EBS_Calc_Date, curveType, numOfLoB, market_factor, liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term, irCurve_USD = 0, irCurve_GBP = 0, gbp_rate = 0, Scen = 0):
        if self.stress_testing:
            if self.actual_estimate == 'Actual':
                self.liability['stress'] = copy.deepcopy(self.liability['base'])
                for idx in range(1, numOfLoB + 1, 1):       
                    self.liability['stress'][idx].cashflow = self.liability['stress'][idx].cashflow[0]
                    self.liability['stress'][idx].OAS_alts = self.liability['stress'][idx].OAS            
            self.liability['stress'] = Corp.Run_Liab_DashBoard(valDate, EBS_Calc_Date, curveType, numOfLoB, self.liability['stress'], market_factor, liab_spread_beta = liab_spread_beta, KRD_Term = KRD_Term, irCurve_USD = irCurve_USD, irCurve_GBP = irCurve_GBP, gbp_rate = gbp_rate, Scen = Scen)
            self.liability['stress'][34].PV_BE += UI.ALBA_adj * (self.actual_estimate == 'Actual') # under 'Estimate', ALBA_adj is added in run_TP.
        elif not self.stress_testing:
            self.liability['dashboard'] = Corp.Run_Liab_DashBoard(valDate, EBS_Calc_Date, curveType, numOfLoB, self.liability['base'], market_factor, liab_spread_beta = liab_spread_beta, KRD_Term = KRD_Term, irCurve_USD = irCurve_USD, irCurve_GBP = irCurve_GBP, gbp_rate = gbp_rate)

    def run_projection_liab_value(self, valDate, EBS_Calc_Date, curveType, numOfLoB, market_factor, liab_spread_beta, KRD_Term, irCurve_USD, irCurve_GBP, gbp_rate, eval_date):
        self.liability[EBS_Calc_Date] = Corp.Run_Liab_DashBoard(valDate, EBS_Calc_Date, curveType, numOfLoB, self.liability['base'], market_factor,  liab_spread_beta, KRD_Term,  irCurve_USD, irCurve_GBP, gbp_rate, eval_date)
        
    def run_liab_dashboard_GAAP_disc(self, t, current_date):
        Corp.Run_Liab_DashBoard_GAAP_Disc(t, current_date, self.liability['dashboard'],self.liability['base'])

    ### Vincent ###
    def run_dashboard_stress_liab_value(self, valDate, EBS_Calc_Date, curveType, numOfLoB, Scen_market_factor, stress_scen, M_Stress_Scen, liab_spread_beta = 0.65):
        self.liability[stress_scen] = Corp.Run_Stress_Liab_DashBoard(valDate, EBS_Calc_Date, curveType, numOfLoB, self.liability['base'], Scen_market_factor, stress_scen, M_Stress_Scen, liab_spread_beta)
    ### --- ###
        
    def set_dashboard_liab_summary(self, numOfLoB):
        self.liab_summary['dashboard'] = Corp.summary_liab_analytics(self.liability['dashboard'], numOfLoB)
        
#    def run_dashboard_EBS(self, numOfLoB, market_factor):  ### Vincent 06/28/2019 - LTIC revaluation
#        self.EBS = Corp.run_EBS_dashboard(self.liab_base_date, self.eval_date, self.EBS, self.asset_holding, self.liab_summary['dashboard'], numOfLoB, market_factor)
#        
    def run_EBS(self, Scen, EBS_asset_Input, AssetAdjustment, market_factor = []):  ### Vincent 07/17/2019 - Step 2 EBS
        if self.stress_testing == 'Step_3':
            self.EBS = Corp.run_EBS(self.liab_base_date, self.eval_date, self.EBS, Scen, self.liab_summary['base'], EBS_asset_Input, AssetAdjustment, self.SFS, market_factor)
        elif self.stress_testing:
            if self.actual_estimate == 'Estimate':
                self.EBS = Corp.run_EBS(self.liab_base_date, self.eval_date, self.EBS, Scen, self.liab_summary['stress'], self.asset_holding, AssetAdjustment, self.SFS, market_factor)
            elif self.actual_estimate == 'Actual':
                self.EBS = Corp.run_EBS(self.liab_base_date, self.eval_date, self.EBS, Scen, self.liab_summary['stress'], EBS_asset_Input, AssetAdjustment, self.SFS, market_factor)
        elif not self.stress_testing:
            if self.actual_estimate == 'Estimate':
                self.EBS = Corp.run_EBS(self.liab_base_date, self.eval_date, self.EBS, Scen, self.liab_summary['dashboard'], self.asset_holding, AssetAdjustment, self.SFS, market_factor)
            elif self.actual_estimate == 'Actual':
                self.EBS = Corp.run_EBS(self.liab_base_date, self.eval_date, self.EBS, Scen, self.liab_summary['base'], EBS_asset_Input, AssetAdjustment, self.SFS, market_factor)
        self.Run_Iteration += 1
       
    def set_base_BSCR(self, Step1_Database, BSCRRisk_agg_TableName, BSCRRisk_LR_TableName, BSCRRisk_PC_TableName, Regime):
        self.BSCR_Base = Corp.Set_BSCR_Base(self.BSCR_Base, Step1_Database, BSCRRisk_agg_TableName, BSCRRisk_LR_TableName, BSCRRisk_PC_TableName, Regime)

    def run_BSCR_dashboard(self, Regime):
        if self.stress_testing:
            self.BSCR_Dashboard = Corp.run_BSCR_dashboard(self.BSCR_Dashboard, self.BSCR, self.EBS, self.liab_summary['stress'], self.liab_summary['stress'], self.actual_estimate, Regime)
        elif not self.stress_testing:
            if self.actual_estimate == 'Estimate':
                self.BSCR_Dashboard = Corp.run_BSCR_dashboard(self.BSCR_Dashboard, self.BSCR, self.EBS, self.liab_summary['base'], self.liab_summary['dashboard'], self.actual_estimate, Regime)            
            elif self.actual_estimate == 'Actual': ### Vincent 07/18/2019 - Step 2
                self.BSCR_Dashboard = Corp.run_BSCR_dashboard(self.BSCR_Dashboard, self.BSCR, self.EBS, self.liab_summary['base'], self.liab_summary['base'], self.actual_estimate, Regime)
  
    def run_estimate_BSCR(self, numOfLoB, Proj_Year, Regime, PC_method, Con_risk_work_dir, AssetRiskCharge): 
        # if self.stress_testing:
        if self.Run_Iteration == 0:
            self.BSCR['BSCR_Mort']      = Bscr.BSCR_Mort_Risk(self.liability['dashboard'], numOfLoB, Proj_Year, self.eval_date)        # Mortality BSCR
            self.BSCR['BSCR_Long']      = Bscr.BSCR_Long_Risk_Charge(self.liability['dashboard'], numOfLoB, Proj_Year, self.eval_date) # Longevity BSCR
            self.BSCR['BSCR_Morb']      = Bscr.BSCR_Morb_Charge(self.liability['dashboard'], numOfLoB, Proj_Year)                      # Morbidity BSCR
            self.BSCR['BSCR_Other']     = Bscr.BSCR_Other_Charge(self.liability['dashboard'], numOfLoB, Proj_Year)                     # Other BSCR
            self.BSCR['BSCR_Stoploss']  = Bscr.BSCR_Stoploss_Charge(self.liability['dashboard'], numOfLoB, Proj_Year)                  # Stoploss BSCR
            self.BSCR['BSCR_Riders']    = Bscr.BSCR_Riders_Charge(self.liability['dashboard'], numOfLoB, Proj_Year)                    # Riders BSCR
            self.BSCR['BSCR_VA']        = Bscr.BSCR_VA_Charge(self.liability['dashboard'], numOfLoB, Proj_Year)                        # VA BSCR
            self.BSCR['BSCR_LT']        = Bscr.BSCR_LT_Charge(self.BSCR, Proj_Year, Regime)                                            # LT BSCR        
            self.BSCR['BSCR_PC']        = Bscr.BSCR_PC_Res_Charge(self.liability['dashboard'], numOfLoB, Proj_Year, Regime, PC_method) # PC Reserve BSCR        
            self.BSCR['BSCR_FI']        = Bscr.BSCR_FI_Risk_Charge(self.asset_holding, UI.EBS_Inputs[self.liab_base_date]['GI']['Loan_Receivable_charge'], self.liab_base_date)     # Fixed Income Investment Risk BSCR
            self.BSCR['BSCR_ConRisk']   = Bscr.BSCR_Con_Risk_Charge(self.liab_base_date, self.eval_date, self.asset_holding, Con_risk_work_dir, Regime, AssetAdjustment = 'Estimate')     # Concentration Risk
        elif self.Run_Iteration == 1: # Run these BSCR after EBS being generated [EBS DTA is required]
            self.BSCR['BSCR_Ccy']       = Bscr.BSCR_Ccy(self.asset_holding,self.liability['dashboard'])                                          # Currency Risk
            # if Regime == 'Future':
            #     self.BSCR['BSCR_IR'] = self.BSCR['BSCR_IR_New_Regime']
            # elif Regime == 'Current':
            self.BSCR['BSCR_IR']     = Bscr.BSCR_IR_Risk_Actual(self.EBS, self.liab_summary['dashboard'])                                        # Interest rate risk
            self.BSCR['BSCR_Eq']     = Bscr.BSCR_Equity_Risk_Charge(self.EBS, self.asset_holding, self.actual_estimate, AssetRiskCharge, Regime, self.eval_date) # Equity Investment risk BSCR
            self.BSCR['BSCR_Market'] = Bscr.BSCR_Market_Risk_Charge(self.BSCR, Regime, self.liab_base_date)                                                   # Market risk BSCR

    
    def print_accounts(self, accountType, lobName):
        # Currently support EBS_Account, BSCR_Analytics, Reins_Settlement, EBS_IS, SFS_Account, SFS_IS, Taxable_Income
        # Lob name can be 1-45, LT, GI or Agg
        acc = getattr(self, accountType)
        return acc[lobName]._summary()
    
    @staticmethod
    def export_LiabAnalytics(work_liab_analytics, outFileName, work_dir, valDate, EBS_Calc_Date, csv_file):
        Corp.exportLobAnalytics(work_liab_analytics, outFileName, work_dir, valDate, EBS_Calc_Date, csv_file)
        
    ### Vincent 07/02/2019; revised on 07/08/2019: liability['EBS_reporting'] ==> liability['base'];
    def run_PVBE(self, valDate, numOfLoB, Proj_Year, bindingScen, BMA_curve_dir, Step1_Database, Disc_rate_TableName, base_GBP, Stress_testing, base_scen = 0): 
        self.liability['base'] = Corp.run_EBS_PVBE(self.liability['base'], valDate, numOfLoB, Proj_Year, bindingScen, BMA_curve_dir, Step1_Database, Disc_rate_TableName, base_GBP, Stress_testing, base_scen)
        
    ### Vincent update 07/30/2019
    def run_BSCR(self, numOfLoB, Proj_Year, input_work_dir, EBS_asset_Input, AssetAdjustment, AssetRiskCharge, Regime, PC_method): 
        if self.stress_testing:
            if self.Run_Iteration == 0:
                self.BSCR['BSCR_Mort']      = Bscr.BSCR_Mort_Risk(self.liability['stress'], numOfLoB, Proj_Year, self.eval_date)        # Mortality BSCR
                self.BSCR['BSCR_Long']      = Bscr.BSCR_Long_Risk_Charge(self.liability['stress'], numOfLoB, Proj_Year, self.eval_date) # Longevity BSCR
                self.BSCR['BSCR_Morb']      = Bscr.BSCR_Morb_Charge(self.liability['stress'], numOfLoB, Proj_Year)                      # Morbidity BSCR
                self.BSCR['BSCR_Other']     = Bscr.BSCR_Other_Charge(self.liability['stress'], numOfLoB, Proj_Year)                     # Other BSCR
                self.BSCR['BSCR_Stoploss']  = Bscr.BSCR_Stoploss_Charge(self.liability['stress'], numOfLoB, Proj_Year)                  # Stoploss BSCR
                self.BSCR['BSCR_Riders']    = Bscr.BSCR_Riders_Charge(self.liability['stress'], numOfLoB, Proj_Year)                    # Riders BSCR
                self.BSCR['BSCR_VA']        = Bscr.BSCR_VA_Charge(self.liability['stress'], numOfLoB, Proj_Year)                        # VA BSCR
                self.BSCR['BSCR_LT']        = Bscr.BSCR_LT_Charge(self.BSCR, Proj_Year, Regime)                                         # LT BSCR        
                self.BSCR['BSCR_PC']        = Bscr.BSCR_PC_Res_Charge(self.liability['stress'], numOfLoB, Proj_Year, Regime, PC_method) # PC Reserve BSCR        
                self.BSCR['BSCR_FI']        = Bscr.BSCR_FI_Risk_Charge(EBS_asset_Input, AssetAdjustment, self.liab_base_date)                                # Fixed Income Investment Risk BSCR
                self.BSCR['BSCR_ConRisk']   = Bscr.BSCR_Con_Risk_Charge(self.liab_base_date, self.eval_date, EBS_asset_Input, input_work_dir, Regime, AssetAdjustment)     # Concentration Risk
            elif self.Run_Iteration == 1: # Run these BSCR after EBS being generated [EBS DTA is required]
                self.BSCR['BSCR_Ccy']    = Bscr.BSCR_Ccy(EBS_asset_Input, self.liability['stress'])                                       # Currency Risk
                if Regime == 'Future':
                    self.BSCR['BSCR_IR'] = self.BSCR['BSCR_IR_New_Regime']
                elif Regime == 'Current':
                    self.BSCR['BSCR_IR'] = Bscr.BSCR_IR_Risk_Actual(self.EBS, self.liab_summary['stress'], AssetAdjustment)                  # Interest rate risk
                self.BSCR['BSCR_Eq']     = Bscr.BSCR_Equity_Risk_Charge(self.EBS, EBS_asset_Input, AssetAdjustment, AssetRiskCharge, Regime) # Equity Investment risk BSCR
                self.BSCR['BSCR_Market'] = Bscr.BSCR_Market_Risk_Charge(self.BSCR, Regime, self.liab_base_date)                                                   # Market risk BSCR        
        elif not self.stress_testing:        
            if self.Run_Iteration == 0:
                self.BSCR['BSCR_Mort']      = Bscr.BSCR_Mort_Risk(self.liability['base'], numOfLoB, Proj_Year, self.eval_date)        # Mortality BSCR
                self.BSCR['BSCR_Long']      = Bscr.BSCR_Long_Risk_Charge(self.liability['base'], numOfLoB, Proj_Year, self.eval_date) # Longevity BSCR
                self.BSCR['BSCR_Morb']      = Bscr.BSCR_Morb_Charge(self.liability['base'], numOfLoB, Proj_Year)                      # Morbidity BSCR
                self.BSCR['BSCR_Other']     = Bscr.BSCR_Other_Charge(self.liability['base'], numOfLoB, Proj_Year)                     # Other BSCR
                self.BSCR['BSCR_Stoploss']  = Bscr.BSCR_Stoploss_Charge(self.liability['base'], numOfLoB, Proj_Year)                  # Stoploss BSCR
                self.BSCR['BSCR_Riders']    = Bscr.BSCR_Riders_Charge(self.liability['base'], numOfLoB, Proj_Year)                    # Riders BSCR
                self.BSCR['BSCR_VA']        = Bscr.BSCR_VA_Charge(self.liability['base'], numOfLoB, Proj_Year)                        # VA BSCR
                self.BSCR['BSCR_LT']        = Bscr.BSCR_LT_Charge(self.BSCR, Proj_Year, Regime)                                       # LT BSCR        
                self.BSCR['BSCR_PC']        = Bscr.BSCR_PC_Res_Charge(self.liability['base'], numOfLoB, Proj_Year, Regime, PC_method) # PC Reserve BSCR        
                self.BSCR['BSCR_FI']        = Bscr.BSCR_FI_Risk_Charge(EBS_asset_Input, AssetAdjustment, self.liab_base_date)                              # Fixed Income Investment Risk BSCR
                self.BSCR['BSCR_ConRisk']   = Bscr.BSCR_Con_Risk_Charge(self.liab_base_date, self.eval_date, EBS_asset_Input, input_work_dir, Regime, AssetAdjustment)     # Concentration Risk
            elif self.Run_Iteration == 1: # Run these BSCR after EBS being generated [EBS DTA is required]
                self.BSCR['BSCR_Ccy']    = Bscr.BSCR_Ccy(EBS_asset_Input, self.liability['base'])                                         # Currency Risk
                if Regime == 'Future':
                    self.BSCR['BSCR_IR'] = self.BSCR['BSCR_IR_New_Regime']
                elif Regime == 'Current':
                    self.BSCR['BSCR_IR'] = Bscr.BSCR_IR_Risk_Actual(self.EBS, self.liab_summary['base'], AssetAdjustment)                    # Interest rate risk
                self.BSCR['BSCR_Eq']     = Bscr.BSCR_Equity_Risk_Charge(self.EBS, EBS_asset_Input, AssetAdjustment, AssetRiskCharge, Regime) # Equity Investment risk BSCR
                self.BSCR['BSCR_Market'] = Bscr.BSCR_Market_Risk_Charge(self.BSCR, Regime, self.liab_base_date)                                                   # Market risk BSCR
        
    def run_BSCR_new_regime(self, Scen, numOfLoB, Proj_Year, Regime, PC_method, curveType, base_GBP, CF_Database, CF_TableName, Step1_Database, work_dir, freq, BMA_curve_dir, Disc_rate_TableName, market_factor = [], input_work_dir = 0, EBS_Asset_Input = 0, Stress_testing = 0, base_scen = 0): 
        self.BSCR['BSCR_IR_New_Regime'] = Bscr.BSCR_IR_New_Regime(self.liab_base_date, self, Scen, curveType, numOfLoB, market_factor, base_GBP, CF_Database, CF_TableName, Step1_Database, Proj_Year, work_dir, freq, BMA_curve_dir, Disc_rate_TableName, EBS_Asset_Input, Stress_testing, base_scen)  
                  
    ### Xi 07/12/2019
    def run_RiskMargin(self, valDate, Proj_Year, Regime, BMA_curve_dir, Scen):
        self.RM = Corp.run_RM(self.BSCR, valDate, Proj_Year, Regime, BMA_curve_dir, self.eval_date, Scen = Scen)
    
    ### Vincent 07/15/2019    
    def run_TP(self, numOfLoB, Proj_Year):    
        if self.stress_testing:
            if self.actual_estimate == 'Actual':
                self.liability['stress'] = Corp.run_TP(self.liability['stress'], self.BSCR, self.RM, numOfLoB, Proj_Year) 
            elif self.actual_estimate == 'Estimate':
                self.liability['stress'] = Corp.run_TP(self.liability['stress'], self.BSCR, self.RM, numOfLoB, Proj_Year, curveType = "Treasury", valDate = self.liab_base_date, EBS_Calc_Date =self.eval_date)
        if not self.stress_testing:
            if self.actual_estimate == 'Actual':
                self.liability['base'] = Corp.run_TP(self.liability['base'], self.BSCR, self.RM, numOfLoB, Proj_Year) 
            elif self.actual_estimate == 'Estimate':
                self.liability['dashboard'] = Corp.run_TP(self.liability['dashboard'], self.BSCR, self.RM, numOfLoB, Proj_Year, curveType = "Treasury", valDate = self.liab_base_date, EBS_Calc_Date =self.eval_date)
            
# EBS Acount Entry
class EBS_Account(basic_fin_account):

    __slot__ = ['AccountName', #Always on the top
                'Acc_Int_Liab',
                'ALBA_Adjustment',
                'Alts_Inv_Surplus',
                'Amount_Due_Other',
                'Capital_Surplus',
                'Capital_Surplus_bef_Div',
                'Cash',
                'Current_Tax_Payble',
                'Derivative_Dur',
                'Derivative_IR01',
                'Div_Cap_EBS_Excess',
                'Div_Cap_SFS_Cap',
                'Div_Cap_SFS_CnS',
                'Div_Cap_SFS_Earnings',
                'Dividend_Payment',
                'DTA_DTL',
                'FI_Dur',
                'Fixed_Inv_Surplus',
                'Fixed_Inv_Surplus_bef_Div',
                'FWA_BV',
                'FWA_MV',
                'FWA_MV_FI',
                'FWA_MV_Alts',
                'FWA_Acc_Int',
                'FWA_Policy_Loan',
                'FWA_tot',
                'GAAP_GRE_FMV_adj',
                'GAAP_Derivative_adj',
                'GOE_Provision',
                'LOC',
                'LTIC',
                'Net_Settlement_Payble',
                'Net_Settlement_Receivable',
                'Other_Assets',
                'Other_Assets_adj',
                'Other_Liab',
                'PV_BE',
                'Risk_Margin',
                'STAT_Security_adj',
                'Surplus_Asset_Acc_Int',
                'Target_Capital',
                'Technical_Provision',
                'Total_Liab_Econ_Capital_Surplus',
                'Total_Liab_Econ_Capital_Surplus_bef_Div',
                'Total_Assets',
                'Total_Assets_bef_Div',
                'Total_Assets_excl_LOCs',
                'Total_Assets_excl_LOCs_bef_Div',
                'Total_Invested_Assets',
                'Total_Invested_Assets_LOB',
                'Total_Invested_Assets_bef_Div',
                'Total_Liabilities'
                ]
    
    def __init__(self, AccountName):
        super().__init__()
        for item in self.__slot__:
            setattr(self, item, 0)
        self.AccountName = AccountName
       
# Liability Class
class LiabAnalyticsUnit (object):

    def __init__(self, lobName):
        self.lobName    = lobName
        self.LOB_Def    = {}
        self.cashflow   = {}
        self.PV_BE      = 0
        self.PV_BE_net  = 0
        self.PV_BE_sec  = 0
        self.PV_BE_sec_net = 0
        self.PV_GOE     = 0 # Kyle update 10/10/2019
        self.PV_BE_30_m = 0
        self.PV_BE_30_p = 0
        self.Risk_Margin = 0
        self.Technical_Provision = 0
        self.OAS = 0
        self.ccy_rate = 0
        self.duration = 0
        self.convexity = 0
        self.YTM = 0
        self.net_cf = 0
        self.PV_BE_net = 0
        self.PC_PVBE_BSCR = {}
        self.Face_Amount = 0
        self.NAAR = 0
        self.Longevity_BSCR = {}
        self.KRD            = {}
        self.EBS_PVBE       = {} ### Vincent update 07/03/2019
        self.EBS_RM         = {}
        self.EBS_TP         = {}
        self.cashflow_runoff     = 0   #Joanna update 02/26/2020
        #### GAAP Items ########
        self.GAAP_Reserve   = 0
        self.Def_Gain_liab  = 0 
        self.GAAP_IRR       = 0
        self.GAAP_Margin    = 0
        self.GAAP_Reserve_disc    = 0        
        self.GAAP_Reserve_rollfwd = 0

        
    def set_LOB_Def(self, name, value):
        self.LOB_Def[name] = value

    def get_LOB_Def(self,name):
        return self.LOB_Def[name]
    
    def set_KRD_value(self, name, value):
        self.KRD[name] = value

    def get_KRD_value(self, name, value):
        return self.KRD[name]


class BSCR_Analytics (basic_fin_account):

    
    def __init__(self, lobName):
        super().__init__()
        self.lobName    = lobName
        self.FI_Risk = 0
        self.Equity_Risk = 0
        self.IR_Risk = 0
        self.Currency_Risk = 0
        self.Concentration_Risk = 0
        self.Market_Risk = 0  ### Vincent 07/18/2019
        
        self.Net_Credit_Risk = 0
        self.Premium_Risk = 0
        self.Reserve_Risk = 0
        self.Cat_Risk = 0
        
        self.Mortality_Risk = 0
        self.StopLoss_Risk = 0
        self.Riders_Risk = 0
        self.Morbidity_Risk = 0
        self.Longevity_Risk = 0
        self.VA_Guarantee_Risk = 0
        self.OtherInsurance_Risk = 0
        self.LT_Risk = 0    ### Vincent 07/18/2019
        
        self.BSCR_Bef_Correlation = 0
        self.Net_Market_Risk = 0
        self.Net_Credit_Risk = 0
        self.Net_PC_Insurance_Risk = 0
        self.Net_LT_Insurance_Risk = 0
        self.BSCR_Aft_Correlation = 0        
        self.OpRisk_Chage_pct = 0.05 # Kyle 10/11/2019 Marked as not addable
        self.OpRisk_Chage = 0
        self.BSCR_Bef_Tax_Adj = 0
        self.Tax_Credit = 0
        self.BSCR_Aft_Tax_Adj = 0
        self.BSCR_Div = 0
        self.TAC = 0
        self.ECR_Ratio = 0
        self.ECR_Ratio_SA =0 
        
        self.PV_BE = 0
        self.Risk_Margin = 0
        self.Technical_Provision = 0
        self.FI_MV = 0
        self.Alts_MV = 0
        self.FI_Dur = 0
        self.Liab_Dur = 0
        self.LOC = 0
        self.DTA = 0
        self.tax_sharing = 0   ## Xi 07/18/2019
        
 
class SFS_Account(basic_fin_account):
    
    __slot__ = ['AccountName', #Always on the top
                'Alts_Inv_Surplus',
                'AOCI',
                'APIC',
                'Amounts_due_to_related_Parties_Other',
                'Amounts_due_to_related_Parties_Settlement',
                'Bonds_AFS',
                'Cash',
                'Common_Stock',
                'Current_Tax_Payable',
                'DTA',
                'DTA_DTL',
                'DTL',
                'Deferred_Gain_on_Reinsurance',
                'Dividend_Payment',
                'Fixed_Inv_Surplus',
                'FWA_BV',
                'FWA_Embedded_Derivative',
                'FWA_Host',
                'FWA_MV',
                'Future_Policyholders_Benefits',
                'GAAP_IRR',
                'GAAP_Margin',
                'GAAP_Reserve',
                'GAAP_Reserve_disc',
                'GAAP_Reserve_rollfwd',
                'LOC',
                'Liability_for_Unpaid_Losses_and_Claim_adj_exp',
                'Loan_Receivable',
                'Other_Assets',
                'Other_Invested_Assets',
                'Other_Liabilities',
                'Policyholder_Contract_Deposits',
                'Retained_Earnings',
                'Short_Term_Investments',
                'Total_Assets',
                'Total_Equity',
                'Total_Funds_Withheld_Assets',
                'Total_Invested_Assets_LOB',
                'Total_Investments',
                'Total_Liabilities',
                'Total_Liabilities_and_Equity',
                'Unearned_Premiums',
                'Unrealized_Capital_Gain'
                ]
    
    def __init__(self, AccountName):
        super().__init__()
        for item in self.__slot__:
            setattr(self, item, 0)
        self.AccountName = AccountName
        

class Reins_Settlement(basic_fin_account):

    def __init__(self, AccountName):

        super().__init__()
        self.AccountName = AccountName
        
        # Revenues
        self.Premiums = 0
        self.NII_ABR_USSTAT = 0
        self.PL_interest= 0     ## calculated field
        self.Chng_IMR = 0   ## calculated field
        self.Impairment_reversal = 0
        self.Investment_Expense = 0     ## calculated field
        
        # Expenses
        self.Death_Claims = 0
        self.Maturities = 0
        self.Surrender = 0
        self.Dividends = 0
        self.Annuity_Claims = 0
        self.AH_Claims = 0
        self.PC_Claims = 0
        self.Reins_gain = 0
        self.Reins_liab = 0
        self.Commissions = 0
        self.Maint_Expense = 0
        self.Premium_Tax = 0
        self.Agg_Expense = 0
        self.Guaranty_assess = 0
        self.Surplus_particip = 0
        self.Extra_oblig = 0
        
        # Balances
        self.Total_STAT_reserve_BOP = 0
        self.Net_STAT_reserve_BOP = 0
        self.CFT_reserve_BOP = 0
        self.UPR_BOP = 0
        self.IMR_BOP = 0
        self.PL_balance_BOP = 0
        self.Total_STAT_BVA_BOP = 0
        self.Total_STAT_reserve_EOP = 0
        self.Net_STAT_reserve_EOP = 0
        self.CFT_reserve_EOP = 0
        self.UPR_EOP = 0
        self.IMR_EOP = 0
        self.PL_balance_EOP = 0
        self.Total_STAT_BVA_EOP = 0
        
        # Settlement calculated fields
        self.Amount_toReins = 0
        self.Amount_toCeding = 0
        self.Chng_PL = 0
        self.Net_cash_settlement = 0
        self.Withdrawal_byReins = 0
        self.Net_payment_toReins = 0
        
        # For Investment Expense (PC) Calc Only
        self.Total_MV_BOP = 0
        self.Total_MV_EOP = 0
        
class EBS_IS(basic_fin_account):

    def __init__(self, AccountName):
        
        super().__init__()
        self.AccountName = AccountName
        
        # Underwriting revenues
        self.Premiums = 0
        self.Total_Income = 0
        self.Decr_Unearned_Premiums = 0
        
        # Underwriting expenses
        self.Death_Claims = 0
        self.Maturities = 0
        self.Surrender = 0
        self.Dividends = 0
        self.Annuity_Claims = 0
        self.AH_Claims = 0
        self.PC_Claims = 0
        self.Commissions = 0
        self.Premium_Tax = 0
        self.Chng_TP = 0
        self.Chng_PVBE = 0
        self.Chng_RM = 0
        self.Total_Disbursement = 0
        
        self.Net_underwriting_Profit = 0
        
        # Combined operation expenses
        self.Maint_Expense = 0
        self.GOE_F = 0
        self.Operating_Expense = 0
        
        # Net investment income
        self.NII_tot = 0
        self.NII_ABR_GAAP = 0
        self.NII_Surplus = 0
        self.NII_Surplus_FI = 0
        self.Yield_Surplus_FI = 0
        self.NII_Surplus_Alt = 0   
        self.Coupon_Surplus_Alt = 0   
        self.MtM_Surplus_Alt = 0   
        self.Redemp_Surplus_Alt = 0   

        self.Investment_Expense_tot = 0          
        self.Investment_Expense_fwa = 0  
        self.Investment_Expense_Surplus = 0
        self.Investment_Expense_Surplus_FI = 0
        self.Investment_Expense_Surplus_alt = 0
        
        # Other
        self.Other_Income = 0
        self.URCGL = 0
        self.RCGL_ED = 0
        self.LOC_cost = 0

        self.Income_before_Tax_LOB = 0
        self.Income_Tax_LOB = 0
        self.Income_after_Tax_LOB = 0

        self.Income_before_Tax_Surplus = 0
        self.Income_Tax_Surplus        = 0
        self.Income_after_Tax_Surplus  = 0        

        self.Income_before_Tax = 0
        self.Income_Tax = 0
        self.Income_after_Tax = 0

        self.DTA_Change = 0        


class SFS_IS(basic_fin_account):

    def __init__(self, AccountName):
        
        super().__init__()
        self.AccountName = AccountName
        
        # Underwriting revenues
        self.Premiums = 0
        self.Decr_Unearned_Premiums = 0
        self.Total_Income       = 0
        
        # Underwriting expenses
        self.Death_Claims = 0
        self.Maturities = 0
        self.Surrender = 0
        self.Dividends = 0
        self.Annuity_Claims = 0
        self.AH_Claims = 0
        self.PC_Claims = 0
        self.Commissions = 0
        self.Premium_Tax = 0
        self.Chng_GAAPRsv = 0
        self.Total_Disbursement = 0
        
        self.Net_underwriting_Profit = 0
        
        # Combined operation expenses
        self.Maint_Expense = 0
        self.GOE_F = 0
        self.Operating_Expense = 0
        
        # Net investment income
        self.NII_tot = 0
        self.NII_ABR_GAAP = 0
        self.NII_Surplus = 0
        self.NII_Surplus_FI = 0
        self.Yield_Surplus_FI = 0
        self.NII_Surplus_Alt = 0   
        self.Coupon_Surplus_Alt = 0   
        self.MtM_Surplus_Alt = 0   
        self.Redemp_Surplus_Alt = 0   

        self.Investment_Expense_tot = 0          
        self.Investment_Expense_fwa = 0  
        self.Investment_Expense_Surplus = 0
        self.Investment_Expense_Surplus_FI = 0
        self.Investment_Expense_Surplus_alt = 0
        
        # Other
        self.Amort_deferred_gain = 0
        self.URCGL = 0
        self.RCGL_ED = 0
        self.LOC_cost = 0
        self.Other_Income = 0        
        
        self.Income_before_Tax_LOB = 0
        self.Income_Tax_LOB = 0
        self.Income_after_Tax_LOB = 0

        self.Income_before_Tax_Surplus = 0
        self.Income_Tax_Surplus        = 0
        self.Income_after_Tax_Surplus  = 0        
        
        self.Income_before_Tax = 0
        self.Income_Tax = 0
        self.Income_after_Tax = 0

        self.DTA_Change = 0        
        
        self.UPR_BOP = 0
        self.UPR_EOP = 0
        self.Deferred_Gain_on_Reinsurance = 0
        
           
class Taxable_Income(basic_fin_account):

    def __init__(self, AccountName):
        
        super().__init__()
        self.AccountName = AccountName

        # Revenues
        self.Premiums = 0
        self.NII_ABR_USSTAT = 0
        
        # Expenses
        self.Death_Claims = 0
        self.Maturities = 0
        self.Surrender = 0
        self.Dividends = 0
        self.Annuity_Claims = 0
        self.AH_Claims = 0
        self.PC_Claims = 0
        self.Commissions = 0
        self.Maint_Expense = 0
        self.Premium_Tax = 0
        self.GOE_F = 0
        self.Chng_Taxbasis = 0
        self.LOC_cost = 0
        self.Other_Income = 0
        
        # Summary iteams
        self.Net_underwriting_Profit = 0
        self.Total_Income  = 0
        self.Total_Disbursement = 0
        self.Operating_Expense = 0
        
        # Balances
        self.Tax_reserve_BOP = 0
        self.Tax_reserve_EOP = 0
        self.Tax_basis_BOP = 0
        self.Tax_basis_EOP = 0

        # Settlement calculated fields
        self.Tax_exempt_interest = 0
        self.DAC_cap_amort = 0   

        self.NII_tot = 0
        self.NII_Surplus = 0
        self.NII_Surplus_FI = 0
        self.Yield_Surplus_FI = 0
        self.NII_Surplus_Alt = 0   
        self.Coupon_Surplus_Alt = 0   
        self.MtM_Surplus_Alt = 0   
        self.Redemp_Surplus_Alt = 0   

        self.Investment_Expense_tot = 0          
        self.Investment_Expense_fwa = 0  
        self.Investment_Expense_Surplus = 0
        self.Investment_Expense_Surplus_FI = 0
        self.Investment_Expense_Surplus_alt = 0

        self.Income_before_Tax_LOB = 0
        self.Income_Tax_LOB = 0
        self.Income_after_Tax_LOB = 0

        self.Income_before_Tax_Surplus = 0
        self.Income_Tax_Surplus        = 0
        self.Income_after_Tax_Surplus  = 0        

        self.Income_before_Tax = 0
        self.Income_Tax = 0
        self.Income_after_Tax = 0

class LOC_Account(basic_fin_account):
    
    def __init__(self):
        
        super().__init__()
#        self._Target_Capital_ratio = 1.5 # Kyle: Updated by tarcap input 
        self.Target_Capital = 0
        self.tier2 = 0
        self.tier3 = 0
        self.tier1_eligible = 0
        self.tier2_eligible = 0
        self.tier3_eligible = 0
        self.SFS_limit      = 0
        self.SFS_limit_pct  = 0
        self.SFS_equity_BOP = 0

#%% Vincent
class Stress_Scenarios(object):
#    instances = []
    
    def __init__(self, scen_num):
        self.scen_num = int(scen_num)
        self.scen_Def = {}
#        Stress_Scenarios.instances.append(self)
       
    def set_scen_Def(self, name, value):
        self.scen_Def[name] = value
        
    def get_scen_Def(self,name):
        return self.scen_Def[name]
    

   
#%%
#
## Liability Class
#class LiabAnalytics (object):
#
#    def __init__(self, lobName):
#        self._lobName    = lobName
#        self._LOB_Def    = {}
#        self._cashflow   = {}
#        self._value      = {}
#        self._keyRateDur = {}
#        self._DashBoard  = {}
#
#    def set_LOB_Def(self, name, value):
#        self._LOB_Def[name] = value
#
#    def get_LOB_Def(self,name):
#        return self._LOB_Def[name]
#
#    def set_cashflow(self, name, value):
#        self._cashflow[name] = value
#
#    def get_cashflow(self,name):
#        return self._cashflow[name]
#
#    def set_liab_value(self, name, value):
#        self._value[name] = value
#
#    def get_liab_value(self, name):
#        return self._value[name]
#
#    def set_DashBoard(self, name, value):
#        self._DashBoard[name] = value
#
#    def get_DashBoard(self, name):
#        return self._DashBoard[name]
#
#
## Asset Class
#class AssetAnalytics (object):
#
#    def __init__(self):
#        self._value      = {}
##        self._DashBoard  = {}
#
#    def set_asset_value(self, name, value):
#        self._value[name] = value
#
#    def get_asset_value(self, name):
#        return self._value[name]
#
##    def set_DashBoard(self, name, value):
##        self._DashBoard[name] = value
##
##    def get_DashBoard(self, name):
##        return self._DashBoard[name]
#
