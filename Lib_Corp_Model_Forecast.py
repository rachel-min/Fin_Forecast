# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 11:20:18 2019

@author: seongpar
"""

import Lib_Market_Akit   as IAL_App
import Class_Corp_Model as Corpclass

def run_TP_forecast(fin_proj, proj_t, valDate, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = 0, base_irCurve_GBP = 0, market_factor = [], liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term):
                    
    #   This should go to an economic scenario generator module - an illustration with the base case only
    if base_irCurve_USD != 0:
        base_irCurve_USD = IAL_App.createAkitZeroCurve(valDate, curveType, "USD")
    
    if base_irCurve_GBP != 0:
        base_irCurve_GBP = IAL_App.load_BMA_Std_Curves(valDate,"GBP",valDate)
        
    for t in range(0, proj_t, 1):
        
        each_date = fin_proj[t]['date']
        #       use the same base line cash flow information for all projections
        fin_proj[t]['Forecast'].liability['base']    = liab_val_base
        fin_proj[t]['Forecast'].liab_summary['base'] = liab_summary_base
            
        #       Projections
        fin_proj[t]['Forecast'].run_dashboard_liab_value(valDate, each_date, curveType, numOfLoB, market_factor ,liab_spread_beta, KRD_Term, base_irCurve_USD, base_irCurve_GBP, gbp_rate)
        fin_proj[t]['Forecast'].set_dashboard_liab_summary(numOfLoB) 

        
def run_fin_forecast(fin_proj, proj_t, numOfLoB, proj_cash_flows):
     
    for t in range(0, proj_t, 1):
        
        for idx in range(1, numOfLoB + 1, 1):
            each_LOB_key = 'LOB' + str(idx)

            ### Create LOB lebel forecasting object
            fin_proj[t]['Forecast'].Reins.update( { idx : Corpclass.Reins_Settlement(each_LOB_key) } )      
            fin_proj[t]['Forecast'].EBS.update( { idx : Corpclass.EBS_Account(each_LOB_key) } )      
            fin_proj[t]['Forecast'].EBS_IS.update( { idx : Corpclass.EBS_IS(each_LOB_key) } )                  
            fin_proj[t]['Forecast'].SFS.update( { idx : Corpclass.SFS_Account(each_LOB_key) } )      ### SWP 9/29/2019
            fin_proj[t]['Forecast'].SFS_IS.update( { idx : Corpclass.SFS_IS(each_LOB_key) } )        ### SWP 9/29/2019                      

            cf_idx    = proj_cash_flows[idx].cashflow

            items = input_items(cf_idx, fin_proj, t, idx)
            
            ### Run by indivdual functions
            run_reins_settlement_forecast(items, fin_proj, t, idx)
            run_EBS_forecast(items, fin_proj, t, idx)
            run_SFS_forecast(items, fin_proj, t, idx)
#            run_Tax_forecast(items, fin_proj, t, idx)   ### Tax forecast will be added later
            
            ### Aggregation
            clsLiab    = proj_cash_flows[idx]
            each_lob   = clsLiab.get_LOB_Def('Agg LOB')
            
            if each_lob == "LR":
                run_aggregation_forecast(items, fin_proj, t, idx, 'LT')
            else: 
                run_aggregation_forecast(items, fin_proj, t, idx, 'GI')
            
            run_aggregation_forecast(items, fin_proj, t, idx, 'Agg')
            

def run_reins_settlement_forecast(items, fin_proj, t, idx): #### Reinsurance Settlement Class

    # Balances
    # Add special condition t = 0 ################### Kyle Modified on 9/29/2019
    if t == 0:
        fin_proj[t]['Forecast'].Reins[idx].Net_STAT_reserve_EOP = items.each_stat_rsv
        fin_proj[t]['Forecast'].Reins[idx].Net_STAT_reserve_BOP = items.each_stat_rsv
        fin_proj[t]['Forecast'].Reins[idx].CFT_reserve_EOP      = items.each_cft_rsv
        fin_proj[t]['Forecast'].Reins[idx].CFT_reserve_BOP      = items.each_cft_rsv
        fin_proj[t]['Forecast'].Reins[idx].UPR_EOP              = items.each_upr
        fin_proj[t]['Forecast'].Reins[idx].UPR_BOP              = items.each_upr
        fin_proj[t]['Forecast'].Reins[idx].IMR_EOP              = items.each_imr
        fin_proj[t]['Forecast'].Reins[idx].IMR_BOP              = items.each_imr
        #fin_proj[t]['Forecast'].Reins[idx].PL_balance_EOP = ##Policy Loan Balance need to be pulled in##
        #fin_proj[t]['Forecast'].Reins[idx].PL_balance_BOP = ##Policy Loan Balance need to be pulled in##
        fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP = items.each_stat_rsv + items.each_cft_rsv + items.each_upr + items.each_imr
        fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_BOP = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP
    else:
        fin_proj[t]['Forecast'].Reins[idx].Net_STAT_reserve_EOP = items.each_stat_rsv
        fin_proj[t]['Forecast'].Reins[idx].Net_STAT_reserve_BOP = fin_proj[t-1]['Forecast'].Reins[idx].Net_STAT_reserve_EOP
        fin_proj[t]['Forecast'].Reins[idx].CFT_reserve_EOP      = items.each_cft_rsv
        fin_proj[t]['Forecast'].Reins[idx].CFT_reserve_BOP      = fin_proj[t-1]['Forecast'].Reins[idx].CFT_reserve_EOP
        fin_proj[t]['Forecast'].Reins[idx].UPR_EOP              = items.each_upr
        fin_proj[t]['Forecast'].Reins[idx].UPR_BOP              = fin_proj[t-1]['Forecast'].Reins[idx].UPR_EOP
        fin_proj[t]['Forecast'].Reins[idx].IMR_EOP              = items.each_imr
        fin_proj[t]['Forecast'].Reins[idx].IMR_BOP              = fin_proj[t-1]['Forecast'].Reins[idx].IMR_EOP
        #fin_proj[t]['Forecast'].Reins[idx].PL_balance_EOP = ##Policy Loan Balance need to be pulled in##
        #fin_proj[t]['Forecast'].Reins[idx].PL_balance_BOP = ##Policy Loan Balance need to be pulled in##
        fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP = items.each_stat_rsv + items.each_cft_rsv + items.each_upr + items.each_imr
        fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_BOP = fin_proj[t-1]['Forecast'].Reins[idx].Total_STAT_reserve_EOP

    # Revenues                        
    fin_proj[t]['Forecast'].Reins[idx].Premiums            = items.each_prem
    fin_proj[t]['Forecast'].Reins[idx].NII_ABR_USSTAT      = items.each_nii   
    #fin_proj[t]['Forecast'].Reins[idx].PL_Interest        = 0 #see below
    fin_proj[t]['Forecast'].Reins[idx].Chng_IMR            = fin_proj[t]['Forecast'].Reins[idx].IMR_BOP - fin_proj[t]['Forecast'].Reins[idx].IMR_EOP
    fin_proj[t]['Forecast'].Reins[idx].Impairment_reversal = 0
    #fin_proj[t]['Forecast'].Reins[idx].Investment_expense = 0 

    # Policyholder Benefits and Expenses    
    fin_proj[t]['Forecast'].Reins[idx].Death_claims      = items.each_death
    fin_proj[t]['Forecast'].Reins[idx].Maturities        = items.each_maturity
    fin_proj[t]['Forecast'].Reins[idx].Surrender         = items.each_surrender
    fin_proj[t]['Forecast'].Reins[idx].Dividends         = items.each_cash_div
    fin_proj[t]['Forecast'].Reins[idx].Annuity_claims    = items.each_annuity
    fin_proj[t]['Forecast'].Reins[idx].AH_claims         = items.each_ah_ben
    fin_proj[t]['Forecast'].Reins[idx].PC_claims         = items.each_gi_claim
    fin_proj[t]['Forecast'].Reins[idx].Reins_gain        = 0
    fin_proj[t]['Forecast'].Reins[idx].Commissions       = items.each_commission
    fin_proj[t]['Forecast'].Reins[idx].Maint_expense     = items.each_maint_exp
    fin_proj[t]['Forecast'].Reins[idx].Premium_tax       = items.each_prem_tax
    fin_proj[t]['Forecast'].Reins[idx].Guaranty_assess   = 0
    fin_proj[t]['Forecast'].Reins[idx].Surplus_particip  = 0
    fin_proj[t]['Forecast'].Reins[idx].Extra_oblig       = 0

    ####################### TO BE CALCULATED zzzzzzzzzzzzzzzzzzzzzzzz                
    # Settlement calculated fields
    fin_proj[t]['Forecast'].Reins[idx].Amount_toReins      = 0
    fin_proj[t]['Forecast'].Reins[idx].Amount_toCeding     = 0
    fin_proj[t]['Forecast'].Reins[idx].Net_cash_settlement = 0
    fin_proj[t]['Forecast'].Reins[idx].Withdrawal_byReins  = 0
    fin_proj[t]['Forecast'].Reins[idx].Net_payment_toReins = 0
    

def run_EBS_forecast(items, fin_proj, t, idx):  # EBS Items    
        
    fin_proj[t]['Forecast'].EBS[idx].PV_BE = items.each_pv_be    
    fin_proj[t]['Forecast'].EBS[idx].risk_margin = items.each_rm    
    fin_proj[t]['Forecast'].EBS[idx].technical_provision = items.each_tp    
    fin_proj[t]['Forecast'].EBS[idx].IMR = items.each_imr

    # Underwriting revenues
    fin_proj[t]['Forecast'].EBS_IS[idx].Premiums     = items.each_prem    
    fin_proj[t]['Forecast'].EBS_IS[idx].Decr_unearned_prem = 0
    
    # Underwriting expenses
    fin_proj[t]['Forecast'].EBS_IS[idx].Death_claims   = items.each_death    
    fin_proj[t]['Forecast'].EBS_IS[idx].Maturities     = items.each_maturity    
    fin_proj[t]['Forecast'].EBS_IS[idx].Surrender      = items.each_surrender    
    fin_proj[t]['Forecast'].EBS_IS[idx].Dividends      = items.each_cash_div    
    fin_proj[t]['Forecast'].EBS_IS[idx].Annuity_claims = items.each_annuity    
    fin_proj[t]['Forecast'].EBS_IS[idx].AH_claims      = items.each_ah_ben    
    fin_proj[t]['Forecast'].EBS_IS[idx].PC_claims      = items.each_gi_claim    
    fin_proj[t]['Forecast'].EBS_IS[idx].Commissions    = items.each_commission    
    fin_proj[t]['Forecast'].EBS_IS[idx].Premium_tax    = items.each_prem_tax    
    fin_proj[t]['Forecast'].EBS_IS[idx].Chng_PVBE      = items.each_pvbe_change    
    fin_proj[t]['Forecast'].EBS_IS[idx].Chng_RM        = items.each_rm_change    
    fin_proj[t]['Forecast'].EBS_IS[idx].Chng_TP        = items.each_tp_change    

    # Combined operation expenses
    fin_proj[t]['Forecast'].EBS_IS[idx].Maint_expense = items.each_maint_exp    
    fin_proj[t]['Forecast'].EBS_IS[idx].GOE           = items.each_goe    


    ####################### TO BE CALCULATED zzzzzzzzzzzzzzzzzzzzzzzz                
    
    fin_proj[t]['Forecast'].EBS_IS[idx].total_expense = items.each_death + items.each_cash_div + items.each_surrender + items.each_maturity + \
                                                        items.each_annuity + items.each_ah_ben + items.each_commission + items.each_prem_tax + \
                                                        items.each_tp_change # decrease in reins covered is not included
                                                        
    fin_proj[t]['Forecast'].EBS_IS[idx].total_revenue = items.each_prem 
    
    fin_proj[t]['Forecast'].EBS_IS[idx].Net_underwriting_profit    = fin_proj[t]['Forecast'].EBS_IS[idx].total_revenue + \
                                                                     fin_proj[t]['Forecast'].EBS_IS[idx].total_expense

    # Net investment income
    fin_proj[t]['Forecast'].EBS_IS[idx].NII_ABR_GAAP               = items.each_nii_abr_gaap + items.each_imr_change
    fin_proj[t]['Forecast'].EBS_IS[idx].NII_surplus                = 0
    fin_proj[t]['Forecast'].EBS_IS[idx].Investment_expense_surplus = 0
    
    # Other
    fin_proj[t]['Forecast'].EBS_IS[idx].Other_income      = 0
    fin_proj[t]['Forecast'].EBS_IS[idx].RCGL_ED           = 0
    fin_proj[t]['Forecast'].EBS_IS[idx].LOC_cost          = 0
    
    fin_proj[t]['Forecast'].EBS_IS[idx].Income_before_tax = 0
    fin_proj[t]['Forecast'].EBS_IS[idx].Income_tax        = 0
    fin_proj[t]['Forecast'].EBS_IS[idx].Income_after_tax  = 0


def run_SFS_forecast(items, fin_proj, t, idx):  # SFS Items    

    if t == 0:
        fin_proj[t]['Forecast'].SFS_IS[idx].UPR_EOP = items.each_upr
        fin_proj[t]['Forecast'].SFS_IS[idx].UPR_BOP = items.each_upr ################ Forced to be 0 (Kyle) #################
        #fin_proj[t]['Forecast'].SFS_IS[idx].PL_balance_EOP = ##Policy Loan Balance need to be pulled in##
        #fin_proj[t]['Forecast'].SFS_IS[idx].PL_balance_BOP = ##Policy Loan Balance need to be pulled in##
    else:
        fin_proj[t]['Forecast'].SFS_IS[idx].UPR_EOP = items.each_upr
        fin_proj[t]['Forecast'].SFS_IS[idx].UPR_BOP = fin_proj[t-1]['Forecast'].SFS_IS[idx].UPR_EOP
        #fin_proj[t]['Forecast'].SFS_IS[idx].PL_balance_EOP = ##Policy Loan Balance need to be pulled in##
        #fin_proj[t]['Forecast'].SFS_IS[idx].PL_balance_BOP = ##Policy Loan Balance need to be pulled in##

    # Underwriting revenues
    fin_proj[t]['Forecast'].SFS_IS[idx].Premiums           = items.each_prem    
    fin_proj[t]['Forecast'].SFS_IS[idx].Decr_unearned_prem = fin_proj[t]['Forecast'].SFS_IS[idx].UPR_BOP - fin_proj[t]['Forecast'].SFS_IS[idx].UPR_EOP
    
    # Underwriting expenses
    fin_proj[t]['Forecast'].SFS_IS[idx].Death_claims   = items.each_death    
    fin_proj[t]['Forecast'].SFS_IS[idx].Maturities     = items.each_maturity    
    fin_proj[t]['Forecast'].SFS_IS[idx].Surrender      = items.each_surrender    
    fin_proj[t]['Forecast'].SFS_IS[idx].Dividends      = items.each_cash_div    
    fin_proj[t]['Forecast'].SFS_IS[idx].Annuity_claims = items.each_annuity    
    fin_proj[t]['Forecast'].SFS_IS[idx].AH_claims      = items.each_ah_ben    
    fin_proj[t]['Forecast'].SFS_IS[idx].PC_claims      = items.each_gi_claim    
    fin_proj[t]['Forecast'].SFS_IS[idx].Commissions    = items.each_commission    
    fin_proj[t]['Forecast'].SFS_IS[idx].Premium_tax    = items.each_prem_tax    
    fin_proj[t]['Forecast'].SFS_IS[idx].Chng_GAAPRsv   = 0 ### To be calculated

    # Combined operation expenses
    fin_proj[t]['Forecast'].SFS_IS[idx].Maint_expense = items.each_maint_exp    
    fin_proj[t]['Forecast'].SFS_IS[idx].GOE = items.each_goe    


    ####################### TO BE CALCULATED zzzzzzzzzzzzzzzzzzzzzzzz                
    fin_proj[t]['Forecast'].SFS_IS[idx].Net_underwriting_profit = 0

    # Net investment income
    fin_proj[t]['Forecast'].SFS_IS[idx].NII_ABR_GAAP = 0    
    fin_proj[t]['Forecast'].SFS_IS[idx].NII_surplus = 0
    fin_proj[t]['Forecast'].SFS_IS[idx].Investment_expense_surplus = 0
    
    # Other
    fin_proj[t]['Forecast'].SFS_IS[idx].Amort_deferred_gain = 0
    fin_proj[t]['Forecast'].SFS_IS[idx].RCGL_ED = 0
    fin_proj[t]['Forecast'].SFS_IS[idx].LOC_cost = 0
    
    fin_proj[t]['Forecast'].SFS_IS[idx].Income_before_tax = 0
    fin_proj[t]['Forecast'].SFS_IS[idx].Income_tax = 0
    fin_proj[t]['Forecast'].SFS_IS[idx].Income_after_tax = 0
            
def run_aggregation_forecast(items, fin_proj, t, idx, agg_level):    
    
    fin_proj[t]['Forecast'].Reins[agg_level].Premiums          += items.each_prem
    fin_proj[t]['Forecast'].Reins[agg_level].Death_claims      += items.each_death
    fin_proj[t]['Forecast'].Reins[agg_level].Annuity_claims    += items.each_annuity

    fin_proj[t]['Forecast'].EBS[agg_level].PV_BE               += items.each_pv_be      
    fin_proj[t]['Forecast'].EBS[agg_level].risk_margin         += items.each_rm   
    fin_proj[t]['Forecast'].EBS[agg_level].technical_provision += items.each_tp   
    
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Premiums  += items.each_prem
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Chng_PVBE += items.each_pvbe_change 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Chng_RM   += items.each_rm_change    
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Chng_TP   += items.each_tp_change 
            
    
class input_items:
    
    def __init__(self, cashFlow, fin_proj, t, idx, check = False):
        
        self._cols_input = ['Total premium', 'Total net cashflow', 'GOE', 'aggregate cf', 'Total net face amount', 'Net benefits - death', \
                           'Net benefits - maturity', 'Net benefits - annuity', 'Net - AH benefits', 'Net benefits - P&C claims', \
                           'Net benefits - surrender', 'Total commission', 'Maintenance expenses', 'Net premium tax', 'Net cash dividends', \
                           'Total Stat Res - Net Res', 'Total Tax Res - Net Res', 'UPR', 'BV asset backing liab', 'MV asset backing liab', \
                           'Net investment Income', 'CFT reserve', 'Interest maintenance reserve (NAIC)', 'Accrued Income']
        items = cashFlow.loc[cashFlow['RowNo'] == t + 1, self._cols_input].sum()
        
        self.each_prem       = items['Total premium']
        self.each_ncf        = items['Total net cashflow']
        self.each_goe        = items['GOE']
        self.each_agg_cf     = items['aggregate cf']
        self.each_face       = items['Total net face amount']
        self.each_death      = items['Net benefits - death']
        self.each_maturity   = items['Net benefits - maturity']
        self.each_annuity    = items['Net benefits - annuity']
        self.each_ah_ben     = items['Net - AH benefits']
        self.each_gi_claim   = items['Net benefits - P&C claims']
        self.each_surrender  = items['Net benefits - surrender']
        self.each_commission = items['Total commission']
        self.each_maint_exp  = items['Maintenance expenses']
        self.each_prem_tax   = items['Net premium tax']
        self.each_cash_div   = items['Net cash dividends']
        self.each_stat_rsv   = items['Total Stat Res - Net Res']
        self.each_tax_rsv    = items['Total Tax Res - Net Res']
        self.each_upr        = items[ 'UPR']
        self.each_bva        = items['BV asset backing liab']
        self.each_mva        = items['MV asset backing liab']
        self.each_nii        = items['Net investment Income']
        self.each_cft_rsv    = items['CFT reserve']
        self.each_imr        = items['Interest maintenance reserve (NAIC)']
        self.each_acc_int    = items['Accrued Income']
        
        self.each_pv_be = fin_proj[t]['Forecast'].liability['dashboard'][idx].PV_BE
        self.each_rm    = fin_proj[t]['Forecast'].liability['dashboard'][idx].risk_margin
        self.each_tp    = fin_proj[t]['Forecast'].liability['dashboard'][idx].technical_provision
        
        if t == 0:
            self.each_pvbe_change = 0
            self.each_rm_change   = 0
            self.each_tp_change   = 0
            self.each_imr_change  = 0             
        else:
            self.each_pvbe_change = self.each_pv_be - fin_proj[t-1]['Forecast'].EBS[idx].PV_BE
            self.each_rm_change   = self.each_rm - fin_proj[t-1]['Forecast'].EBS[idx].risk_margin
            self.each_tp_change   = self.each_tp - fin_proj[t-1]['Forecast'].EBS[idx].technical_provision
            self.each_imr_change  = self.each_imr - fin_proj[t-1]['Forecast'].EBS[idx].IMR
        
        self.each_nii_abr_gaap = self.each_nii / (self.each_stat_rsv + self.each_cft_rsv + self.each_imr + self.each_upr) * self.each_stat_rsv
        
        
        if check:
            print("Inputs initialized")
