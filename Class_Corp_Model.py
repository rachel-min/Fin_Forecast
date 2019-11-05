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

# EBS Acount Entry
class EBS_Dashboard(object):
    def __init__(self, eval_date, actual_estimate, liab_base_date):
        self.eval_date       = eval_date
        self.actual_estimate = actual_estimate
        self.liab_base_date  = liab_base_date
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
        
    def set_sfs(self, SFS_File):
        self.SFS = Corp.set_SFS_BS(self.SFS, SFS_File)
        
    def set_asset_holding(self, workDir, fileName, asset_fileName_T_plus_1, Price_Date, market_factor, output = 1, mappingFile = '.\Mapping.xlsx', ratingMapFile = '.\Rating_Mapping.xlsx'):
        self.asset_holding = Asset_App.daily_portfolio_feed(self.eval_date, self.liab_base_date, workDir, fileName, asset_fileName_T_plus_1, Price_Date, market_factor, output, mappingFile, ratingMapFile)       

    def set_base_cash_flow(self, valDate, CF_Database, CF_TableName, Step1_Database, PVBE_TableName, bindingScen, numOfLoB, Proj_Year, work_dir, freq): ### Vincent 07/02/2019
        self.liability['base'] = Corp.get_liab_cashflow(self.actual_estimate, valDate, CF_Database, CF_TableName, Step1_Database, PVBE_TableName, bindingScen, numOfLoB, Proj_Year, work_dir, freq)
  
    def set_base_liab_value(self, valDate, curveType, curr_GBP, numOfLoB, rating = "BBB", irCurve_USD = 0, irCurve_GBP = 0):
        self.liability['base'] = Corp.Set_Liab_Base(valDate, curveType, curr_GBP, numOfLoB, self.liability['base'], rating, irCurve_USD = irCurve_USD, irCurve_GBP = irCurve_GBP)

    def set_base_liab_summary(self, numOfLoB):
        self.liab_summary['base'] = Corp.summary_liab_analytics(self.liability['base'], numOfLoB)

    def run_dashboard_liab_value(self, valDate, EBS_Calc_Date, curveType, numOfLoB, market_factor, liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term, irCurve_USD = 0, irCurve_GBP = 0, gbp_rate = 0 ):
        self.liability['dashboard'] = Corp.Run_Liab_DashBoard(valDate, EBS_Calc_Date, curveType, numOfLoB, self.liability['base'], market_factor, liab_spread_beta = liab_spread_beta, KRD_Term = KRD_Term,  irCurve_USD = irCurve_USD, irCurve_GBP = irCurve_GBP, gbp_rate = gbp_rate)

    ### Vincent ###
    def run_dashboard_stress_liab_value(self, valDate, EBS_Calc_Date, curveType, numOfLoB, Scen_market_factor, stress_scen, M_Stress_Scen, liab_spread_beta = 0.65):
        self.liability[stress_scen] = Corp.Run_Stress_Liab_DashBoard(valDate, EBS_Calc_Date, curveType, numOfLoB, self.liability['base'], Scen_market_factor, stress_scen, M_Stress_Scen, liab_spread_beta)
    ### --- ###
        
    def set_dashboard_liab_summary(self, numOfLoB):
        self.liab_summary['dashboard'] = Corp.summary_liab_analytics(self.liability['dashboard'], numOfLoB)
        
    def run_dashboard_EBS(self, numOfLoB, market_factor):  ### Vincent 06/28/2019 - LTIC revaluation
        self.EBS = Corp.run_EBS_dashboard(self.liab_base_date, self.eval_date, self.EBS, self.asset_holding, self.liab_summary['dashboard'], numOfLoB, market_factor)
        
    def run_base_EBS(self, EBS_asset_Input, AssetAdjustment):  ### Vincent 07/17/2019 - Step 2 EBS
        self.EBS = Corp.run_EBS_base(self.liab_base_date, self.EBS, self.liab_summary['base'], EBS_asset_Input, AssetAdjustment, self.SFS)
        self.Run_Iteration =+ 1
       
    def set_base_BSCR(self, Step1_Database, BSCRRisk_agg_TableName, BSCRRisk_LR_TableName, BSCRRisk_PC_TableName, Regime):
        self.BSCR_Base = Corp.Set_BSCR_Base(self.BSCR_Base, Step1_Database, BSCRRisk_agg_TableName, BSCRRisk_LR_TableName, BSCRRisk_PC_TableName, Regime)

    def run_BSCR_dashboard(self, Regime):
        if self.actual_estimate == 'Estimate':
            self.BSCR_Dashboard = Corp.run_BSCR_dashboard(self.BSCR_Dashboard, self.BSCR_Base, self.EBS, self.liab_summary['base'], self.liab_summary['dashboard'], self.actual_estimate, Regime)
            
        elif self.actual_estimate == 'Actual': ### Vincent 07/18/2019 - Step 2
            self.BSCR_Dashboard = Corp.run_BSCR_dashboard(self.BSCR_Dashboard, self.BSCR, self.EBS, self.liab_summary['base'], self.liab_summary['base'], self.actual_estimate, Regime)
    
    def print_accounts(self, accountType, lobName):
        # Currently support EBS_Account, BSCR_Analytics, Reins_Settlement, EBS_IS, SFS_Account, SFS_IS, Taxable_Income
        # Lob name can be 1-45, LT, GI or Agg
        acc = getattr(self, accountType)
        return acc[lobName]._summary()
    
    @staticmethod
    def export_LiabAnalytics(work_liab_analytics, outFileName, work_dir, valDate, EBS_Calc_Date):
        Corp.exportLobAnalytics(work_liab_analytics, outFileName, work_dir, valDate, EBS_Calc_Date)
        
    ### Vincent 07/02/2019; revised on 07/08/2019: liability['EBS_reporting'] ==> liability['base'];
    def run_PVBE(self, valDate, numOfLoB, Proj_Year, bindingScen, BMA_curve_dir, Step1_Database, Disc_rate_TableName, base_GBP): 
        self.liability['base'] = Corp.run_EBS_PVBE(self.liability['base'], valDate, numOfLoB, Proj_Year, bindingScen, BMA_curve_dir, Step1_Database, Disc_rate_TableName, base_GBP)
        
    ### Vincent 07/09/2019
    ### Vincent update 07/30/2019
    def run_BSCR(self, numOfLoB, Proj_Year, input_work_dir, EBS_asset_Input, AssetAdjustment, AssetRiskCharge, Regime, PC_method): 
        if self.Run_Iteration == 0:
            self.BSCR['BSCR_Mort']      = Bscr.BSCR_Mort_Risk(self.liability['base'], numOfLoB, Proj_Year)                        # Mortality BSCR
            self.BSCR['BSCR_Long']      = Bscr.BSCR_Long_Risk_Charge(self.liability['base'], numOfLoB, Proj_Year, self.eval_date) # Longevity BSCR
            self.BSCR['BSCR_Morb']      = Bscr.BSCR_Morb_Charge(self.liability['base'], numOfLoB, Proj_Year)                      # Morbidity BSCR
            self.BSCR['BSCR_Other']     = Bscr.BSCR_Other_Charge(self.liability['base'], numOfLoB, Proj_Year)                     # Other BSCR
            self.BSCR['BSCR_Stoploss']  = Bscr.BSCR_Stoploss_Charge(self.liability['base'], numOfLoB, Proj_Year)                  # Stoploss BSCR
            self.BSCR['BSCR_Riders']    = Bscr.BSCR_Riders_Charge(self.liability['base'], numOfLoB, Proj_Year)                    # Riders BSCR
            self.BSCR['BSCR_VA']        = Bscr.BSCR_VA_Charge(self.liability['base'], numOfLoB, Proj_Year)                        # VA BSCR
            self.BSCR['BSCR_LT']        = Bscr.BSCR_LT_Charge(self.BSCR, Proj_Year, Regime)                                       # LT BSCR        
            self.BSCR['BSCR_PC']        = Bscr.BSCR_PC_Res_Charge(self.liability['base'], numOfLoB, Proj_Year, Regime, PC_method) # PC Reserve BSCR        
            self.BSCR['BSCR_FI']        = Bscr.BSCR_FI_Risk_Charge(EBS_asset_Input, AssetAdjustment)                              # Fixed Income Investment Risk BSCR
            self.BSCR['BSCR_ConRisk']   = Bscr.BSCR_Con_Risk_Charge(EBS_asset_Input, AssetAdjustment, input_work_dir, Regime)                      # Concentration Risk
        elif self.Run_Iteration == 1: # Run these BSCR after EBS being generated [EBS DTA is required]
            self.BSCR['BSCR_Ccy']       = Bscr.BSCR_Ccy(EBS_asset_Input,self.liability['base'])                                          # Currency Risk
            self.BSCR['BSCR_IR']     = Bscr.BSCR_IR_Risk_Actual(self.EBS, self.liab_summary['base'])                                     # Interest rate risk
            self.BSCR['BSCR_Eq']     = Bscr.BSCR_Equity_Risk_Charge(self.EBS, EBS_asset_Input, AssetAdjustment, AssetRiskCharge, Regime) # Equity Investment risk BSCR
            self.BSCR['BSCR_Market'] = Bscr.BSCR_Market_Risk_Charge(self.BSCR, Regime)                                                   # Market risk BSCR
                            
    ### Xi 07/12/2019
    def run_RiskMargin(self, valDate, Proj_Year, Regime, BMA_curve_dir):
        self.RM = Corp.run_RM(self.BSCR, valDate, Proj_Year, Regime, BMA_curve_dir)
    
    ### Vincent 07/15/2019    
    def run_TP(self, numOfLoB, Proj_Year):    
        self.liability['base'] = Corp.run_TP(self.liability['base'], self.BSCR, self.RM, numOfLoB, Proj_Year) 
        
# EBS Acount Entry
class EBS_Account(basic_fin_account):

    def __init__(self, AccountName):
        self.AccountName = AccountName
        self.cash = 0
        self.net_settlement_receivable = 0
        self.fixed_inv_surplus = 0
        self.fixed_inv_surplus_bef_div = 0
        self.alts_inv_surplus = 0
        self.fwa_tot = 0
        self.fwa_BV = 0
        self.fwa_MV = 0
        self.fwa_MV_FI = 0
        self.fwa_MV_alts = 0
        self.fwa_acc_int = 0
        self.fwa_policy_loan = 0
        self.FI_Dur = 0
        self.STAT_security_adj = 0
        self.GAAP_derivative_adj = 0
        self.GAAP_GRE_FMV_adj = 0
        self.DTA_DTL = 0
        self.LOC = 0
        self.LTIC = 0
        self.Other_Assets = 0
        self.other_assets_adj = 0 ### Vincent update 05/27/2019
        self.other_liab = 0 ### Vincent update 05/27/2019
        self.surplus_asset_acc_int = 0
        self.total_assets = 0
        self.total_assets_excl_LOCs = 0
        self.total_invested_assets = 0
        self.PV_BE = 0
        self.risk_margin = 0
        self.technical_provision = 0
        self.current_tax_payble = 0
        self.net_settlement_payble = 0
        self.amount_due_other = 0
        self.acc_int_liab = 0
        self.total_liabilities = 0
        self.capital_surplus = 0
        self.tot_liab_econ_capital_surplus = 0
        self.Derivative_IR01 = 0
        self.Derivative_Dur  = 0     
        self.ALBA_Adjustment = 0
        self.GOE_provision = 0
        self.target_capital = 0

# Liability Class
class LiabAnalyticsUnit (object):

    def __init__(self, lobName):
        self.lobName    = lobName
        self.LOB_Def    = {}
        self.cashflow   = {}
        self.PV_BE      = 0
        self.PV_GOE     = 0 # Kyle update 10/10/2019
        self.PV_BE_30_m = 0
        self.PV_BE_30_p = 0
        self.risk_margin = 0
        self.technical_provision = 0
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
        self.KRD  = {}
        self.EBS_PVBE        = {} ### Vincent update 07/03/2019
        self.EBS_RM         =  {}
        self.EBS_TP         =  {}
        
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
        self.risk_margin = 0
        self.technical_provision = 0
        self.FI_MV = 0
        self.Alts_MV = 0
        self.FI_Dur = 0
        self.Liab_Dur = 0
        self.LOC = 0
        self.DTA = 0
        self.tax_sharing = 0   ## Xi 07/18/2019
        
 
class SFS_Account(basic_fin_account):
    
    def __init__(self, AccountName):
        self.AccountName = AccountName
        # Asset
        self.cash = 0
        
        self.short_term_investments = 0
        self.Bonds_AFS = 0
        self.Other_invested_assets = 0
        self.Total_investments = 0
        
        self.FWA_Host = 0
        self.FWA_Embedded_derivative = 0
        self.Total_funds_withheld_assets = 0
        
        self.Loan_receivable = 0
        self.DTA = 0
        self.Other_assets = 0        
        self.Total_assets = 0
        
        # Liability 
        self.Liability_for_unpaid_losses_and_claim_adj_exp = 0
        self.Unearned_premiums = 0
        self.Future_policyholders_benefits = 0
        self.Policyholder_contract_deposits = 0
        self.DTL = 0
        self.Current_tax_payable = 0
        self.Amounts_due_to_related_parties_settlement = 0
        self.Amounts_due_to_related_parties_other = 0
        self.Deferred_gain_on_reinsurance = 0
        self.Other_liabilities = 0
        self.Total_liabilities = 0
        
        # Equity
        self.Common_stock = 0
        self.APIC = 0
        self.Retained_earnings = 0
        self.AOCI = 0       
        self.Total_equity = 0
        
        self.Total_liabilities_and_equity = 0
        self.fwa_MV = 0
        self.fwa_BV = 0
        self.unrealized_capital_gain = 0
        self.GAAP_reserves = 0

class Reins_Settlement(basic_fin_account):

    def __init__(self, AccountName):

        self.AccountName = AccountName
        
        # Revenues
        self.Premiums = 0
        self.NII_ABR_USSTAT = 0
        self.PL_interest= 0     ## calculated field
        self.Chng_IMR = 0   ## calculated field
        self.Impairment_reversal = 0
        self.Investment_expense = 0     ## calculated field
        
        # Expenses
        self.Death_claims = 0
        self.Maturities = 0
        self.Surrender = 0
        self.Dividends = 0
        self.Annuity_claims = 0
        self.AH_claims = 0
        self.PC_claims = 0
        self.Reins_gain = 0
        self.Reins_liab = 0
        self.Commissions = 0
        self.Maint_expense = 0
        self.Premium_tax = 0
        self.Agg_expense = 0
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
        
        self.AccountName = AccountName
        
        # Underwriting revenues
        self.Premiums = 0
        self.Total_income = 0
        self.Decr_unearned_prem = 0
        
        # Underwriting expenses
        self.Death_claims = 0
        self.Maturities = 0
        self.Surrender = 0
        self.Dividends = 0
        self.Annuity_claims = 0
        self.AH_claims = 0
        self.PC_claims = 0
        self.Commissions = 0
        self.Premium_tax = 0
        self.Chng_TP = 0
        self.Chng_PVBE = 0
        self.Chng_RM = 0
        self.Total_disbursement = 0
        
        self.Net_underwriting_profit = 0
        
        # Combined operation expenses
        self.Maint_expense = 0
        self.GOE_F = 0
        self.Operating_expense = 0
        
        # Net investment income
        self.NII_ABR_GAAP = 0
        self.NII_surplus = 0
        self.NII_surplus_FI = 0
        self.NII_surplus_Alt = 0        
        self.Investment_expense_surplus = 0
        self.Total_NII = 0
        
        # Other
        self.Other_income = 0
        self.URCGL = 0
        self.RCGL_ED = 0
        self.LOC_cost = 0
        
        self.Income_before_tax = 0
        self.Income_tax = 0
        self.Income_after_tax = 0


class SFS_IS(basic_fin_account):

    def __init__(self, AccountName):
        
        self.AccountName = AccountName
        
        # Underwriting revenues
        self.Premiums = 0
        self.Decr_unearned_prem = 0
        
        # Underwriting expenses
        self.Death_claims = 0
        self.Maturities = 0
        self.Surrender = 0
        self.Dividends = 0
        self.Annuity_claims = 0
        self.AH_claims = 0
        self.PC_claims = 0
        self.Commissions = 0
        self.Premium_tax = 0
        self.Chng_GAAPRsv = 0
        
        self.Net_underwriting_profit = 0
        
        # Combined operation expenses
        self.Maint_expense = 0
        self.GOE_F = 0
        
        # Net investment income
        self.NII_ABR_GAAP = 0
        self.NII_surplus = 0
        self.Investment_expense_surplus = 0
        
        # Other
        self.Amort_deferred_gain = 0
        self.RCGL_ED = 0
        self.LOC_cost = 0
        
        self.Income_before_tax = 0
        self.Income_tax = 0
        self.Income_after_tax = 0    
        
        self.UPR_EOP = 0
        
        
           
class Taxable_Income(basic_fin_account):

    def __init__(self, AccountName):
        
        self.AccountName = AccountName

        # Revenues
        self.Premiums = 0
        self.NII_ABR_USSTAT = 0
        self.Investment_expense = 0     ## calculated field
        
        # Expenses
        self.Death_claims = 0
        self.Maturities = 0
        self.Surrender = 0
        self.Dividends = 0
        self.Annuity_claims = 0
        self.AH_claims = 0
        self.PC_claims = 0
        self.Commissions = 0
        self.Maint_expense = 0
        self.Premium_tax = 0
        self.GOE_F = 0
        self.Chng_taxbasis = 0
        
        # Balances
        self.Tax_reserve_BOP = 0
        self.Tax_reserve_EOP = 0
        self.Tax_basis_BOP = 0
        self.Tax_basis_EOP = 0

        # Settlement calculated fields
        self.Tax_exempt_interest = 0
        self.DAC_cap_amort = 0   
        self.Taxable_income_ABR = 0
        self.Tax_Paid = 0



class LOC_Account(basic_fin_account):
    
    def __init__(self):
        
        self._target_capital_ratio = 1.5 # Kyle: Updated by tarcap input 
        self.target_capital = 0
        self.tier2 = 0
        self.tier3 = 0
        self.tier1_eligible = 0
        self.tier2_eligible = 0
        self.tier3_eligible = 0


class Run_Control(object):
    def __init__(self):
        self.Target_ECR_Ratio = 1.5








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
