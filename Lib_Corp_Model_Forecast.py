# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 11:20:18 2019

@author: seongpar
"""
import os
import Lib_Market_Akit  as IAL_App
import Class_Corp_Model as Corpclass
import Lib_BSCR_Calc   as BSCR_Calc
import pandas as pd
import datetime as dt

akit_dir = 'C:/AKit v4.1.0/BIN'
os.sys.path.append(akit_dir)
import IALPython3        as IAL

def run_TP_forecast(fin_proj, proj_t, valDate, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = 0, base_irCurve_GBP = 0, market_factor = [], liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term, cf_proj_end_date = dt.datetime(2200, 12, 31), cash_flow_freq = 'A', recast_risk_margin = 'N'):
                    
    #   This should go to an economic scenario generator module - an illustration with the base case only
    if base_irCurve_USD == 0:
        base_irCurve_USD = IAL_App.createAkitZeroCurve(valDate, curveType, "USD")
    
    if base_irCurve_GBP == 0:
        base_irCurve_GBP = IAL_App.load_BMA_Std_Curves(valDate,"GBP",valDate)
        
    for t in range(0, proj_t, 1):
        
        each_date = fin_proj[t]['date']
        #       use the same base line cash flow information for all projections
        fin_proj[t]['Forecast'].liability['base']    = liab_val_base
        fin_proj[t]['Forecast'].liab_summary['base'] = liab_summary_base
            
        #       Projections
        fin_proj[t]['Forecast'].run_dashboard_liab_value(valDate, each_date, curveType, numOfLoB, market_factor ,liab_spread_beta, KRD_Term, base_irCurve_USD, base_irCurve_GBP, gbp_rate)
        fin_proj[t]['Forecast'].set_dashboard_liab_summary(numOfLoB) 

        #  Risk Margin Projection ZZZZZZZZZZZZ risk free curve needs to be fed in
        run_RM_forecast(fin_proj, t, recast_risk_margin, each_date, cf_proj_end_date, cash_flow_freq, valDate, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = base_irCurve_USD, rf_curve = base_irCurve_USD, base_irCurve_GBP = base_irCurve_GBP, market_factor = market_factor, liab_spread_beta = liab_spread_beta, KRD_Term = KRD_Term)
        
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
            fin_proj[t]['Forecast'].Tax_IS.update( { idx : Corpclass.Taxable_Income(each_LOB_key) } )        ### SWP 9/29/2019                                  

            cf_idx    = proj_cash_flows[idx].cashflow

            items = input_items(cf_idx, fin_proj, t, idx)
            
            ### Run by indivdual functions
            run_reins_settlement_forecast(items, fin_proj, t, idx)
            run_EBS_forecast(items, fin_proj, t, idx)
            run_SFS_forecast(items, fin_proj, t, idx)
            run_Tax_forecast(fin_proj, t, idx)   ### Tax forecast will be added later
            
            ### Aggregation
            clsLiab    = proj_cash_flows[idx]
            each_lob   = clsLiab.get_LOB_Def('Agg LOB')
            
            if each_lob == "LR":                
                run_aggregation_forecast(fin_proj, t, idx, 'LT')
                
            else: 
                run_aggregation_forecast(fin_proj, t, idx, 'GI')
                
#            Aggregate Account
            run_aggregation_forecast(fin_proj, t, idx, 'Agg')
            
#####   BSCR Calculations ##################
        run_BSCR_forecast(fin_proj, t)

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
        fin_proj[t]['Forecast'].Reins[idx].PL_balance_EOP       = 0 ##Policy Loan Balance need to be pulled in##
        fin_proj[t]['Forecast'].Reins[idx].PL_balance_BOP       = 0 ##Policy Loan Balance need to be pulled in##
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
        fin_proj[t]['Forecast'].Reins[idx].PL_balance_EOP       = 0 ##Policy Loan Balance need to be pulled in##
        fin_proj[t]['Forecast'].Reins[idx].PL_balance_BOP       = fin_proj[t-1]['Forecast'].Reins[idx].PL_balance_EOP ##Policy Loan Balance need to be pulled in##
        fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP = items.each_stat_rsv + items.each_cft_rsv + items.each_upr + items.each_imr
        fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_BOP = fin_proj[t-1]['Forecast'].Reins[idx].Total_STAT_reserve_EOP

    # Revenues                        
    fin_proj[t]['Forecast'].Reins[idx].Premiums            = items.each_prem
    fin_proj[t]['Forecast'].Reins[idx].PL_interest         = 0.05 * ((fin_proj[t]['Forecast'].Reins[idx].PL_balance_BOP + fin_proj[t]['Forecast'].Reins[idx].PL_balance_EOP) / 2) 
    ##PL_interest: 5% PL interest could be coded as flexible input; need to divide by 4 if quarterly##
    fin_proj[t]['Forecast'].Reins[idx].Chng_IMR            = fin_proj[t]['Forecast'].Reins[idx].IMR_EOP - fin_proj[t]['Forecast'].Reins[idx].IMR_BOP
    fin_proj[t]['Forecast'].Reins[idx].Impairment_reversal = 0
    fin_proj[t]['Forecast'].Reins[idx].Investment_expense  = 0 
    ##Investment_expense: could be estimated as 15bps of asset MV or could be pulled in from AXIS output##
    fin_proj[t]['Forecast'].Reins[idx].NII_ABR_USSTAT      = items.each_nii_abr + fin_proj[t]['Forecast'].Reins[idx].Chng_IMR - fin_proj[t]['Forecast'].Reins[idx].PL_interest - fin_proj[t]['Forecast'].Reins[idx].Investment_expense

    # Policyholder Benefits and Expenses    
    fin_proj[t]['Forecast'].Reins[idx].Death_claims      = items.each_death
    fin_proj[t]['Forecast'].Reins[idx].Maturities        = items.each_maturity
    fin_proj[t]['Forecast'].Reins[idx].Surrender         = items.each_surrender
    fin_proj[t]['Forecast'].Reins[idx].Dividends         = items.each_cash_div
    fin_proj[t]['Forecast'].Reins[idx].Annuity_claims    = items.each_annuity
    fin_proj[t]['Forecast'].Reins[idx].AH_claims         = items.each_ah_ben
    fin_proj[t]['Forecast'].Reins[idx].PC_claims         = items.each_gi_claim
    fin_proj[t]['Forecast'].Reins[idx].Reins_gain        = 0
    fin_proj[t]['Forecast'].Reins[idx].Reins_liab        = items.each_death + items.each_maturity + items.each_surrender + items.each_cash_div + items.each_annuity + items.each_ah_ben + items.each_gi_claim + fin_proj[t]['Forecast'].Reins[idx].Reins_gain
    fin_proj[t]['Forecast'].Reins[idx].Commissions       = items.each_commission
    fin_proj[t]['Forecast'].Reins[idx].Maint_expense     = items.each_maint_exp
    fin_proj[t]['Forecast'].Reins[idx].Premium_tax       = items.each_prem_tax
    fin_proj[t]['Forecast'].Reins[idx].Agg_expense       = items.each_commission + items.each_maint_exp + items.each_prem_tax
    fin_proj[t]['Forecast'].Reins[idx].Guaranty_assess   = 0
    fin_proj[t]['Forecast'].Reins[idx].Surplus_particip  = 0
    fin_proj[t]['Forecast'].Reins[idx].Extra_oblig       = 0
            
    # Settlement calculated fields
    fin_proj[t]['Forecast'].Reins[idx].Amount_toReins      = fin_proj[t]['Forecast'].Reins[idx].PL_interest + fin_proj[t]['Forecast'].Reins[idx].Premiums + fin_proj[t]['Forecast'].Reins[idx].Impairment_reversal
    fin_proj[t]['Forecast'].Reins[idx].Amount_toCeding     = 0 - (fin_proj[t]['Forecast'].Reins[idx].Extra_oblig + fin_proj[t]['Forecast'].Reins[idx].Reins_liab + fin_proj[t]['Forecast'].Reins[idx].Agg_expense +fin_proj[t]['Forecast'].Reins[idx].Investment_expense + fin_proj[t]['Forecast'].Reins[idx].Guaranty_assess + fin_proj[t]['Forecast'].Reins[idx].Surplus_particip) 
    fin_proj[t]['Forecast'].Reins[idx].Chng_PL             = fin_proj[t]['Forecast'].Reins[idx].PL_balance_EOP - fin_proj[t]['Forecast'].Reins[idx].PL_balance_BOP
    fin_proj[t]['Forecast'].Reins[idx].Net_cash_settlement = fin_proj[t]['Forecast'].Reins[idx].Amount_toCeding - fin_proj[t]['Forecast'].Reins[idx].Amount_toReins + fin_proj[t]['Forecast'].Reins[idx].Chng_PL
    fin_proj[t]['Forecast'].Reins[idx].Total_STAT_BVA_BOP  = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_BOP
    fin_proj[t]['Forecast'].Reins[idx].Total_STAT_BVA_EOP  = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_BVA_BOP +  fin_proj[t]['Forecast'].Reins[idx].NII_ABR_USSTAT + fin_proj[t]['Forecast'].Reins[idx].Chng_PL
    fin_proj[t]['Forecast'].Reins[idx].Withdrawal_byReins  = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_BVA_EOP - fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP
    fin_proj[t]['Forecast'].Reins[idx].Net_payment_toReins = fin_proj[t]['Forecast'].Reins[idx].Withdrawal_byReins - fin_proj[t]['Forecast'].Reins[idx].Net_cash_settlement
    

def run_EBS_forecast(items, fin_proj, t, idx):  # EBS Items    
    
    # Balance sheet: Assets
    #######################SURPLUS ITEMS TO BE CALCULATED AT OVERALL LEVEL zzzzzzzzzzzzzzzz
    fin_proj[t]['Forecast'].EBS[idx].fixed_inv_surplus = 0
    fin_proj[t]['Forecast'].EBS[idx].alts_inv_surplus = 0
    fin_proj[t]['Forecast'].EBS[idx].total_invested_assets = fin_proj[t]['Forecast'].EBS[idx].fixed_inv_surplus + fin_proj[t]['Forecast'].EBS[idx].alts_inv_surplus
    #######################Time zero need to tie with actuals; may need scaling zzzzzzzzzzzzzzzz
    fin_proj[t]['Forecast'].EBS[idx].fwa_MV = items.each_mva #Equal to AXIS MVA
    fin_proj[t]['Forecast'].EBS[idx].fwa_BV = items.each_bva #Equal to AXIS BVA
    fin_proj[t]['Forecast'].EBS[idx].LTIC = 0
    fin_proj[t]['Forecast'].EBS[idx].LOC = 0
    fin_proj[t]['Forecast'].EBS[idx].DTA_DTL = 0
    fin_proj[t]['Forecast'].EBS[idx].Other_Assets = fin_proj[t]['Forecast'].EBS[idx].fwa_MV + fin_proj[t]['Forecast'].EBS[idx].LTIC + \
                                                     fin_proj[t]['Forecast'].EBS[idx].LOC + fin_proj[t]['Forecast'].EBS[idx].DTA_DTL
    
    fin_proj[t]['Forecast'].EBS[idx].total_assets = fin_proj[t]['Forecast'].EBS[idx].total_invested_assets + fin_proj[t]['Forecast'].EBS[idx].Other_Assets
    
    # Balance sheet: Liabilities    
    fin_proj[t]['Forecast'].EBS[idx].PV_BE = items.each_pv_be    
    fin_proj[t]['Forecast'].EBS[idx].risk_margin = items.each_rm    
    fin_proj[t]['Forecast'].EBS[idx].technical_provision = items.each_tp    
    fin_proj[t]['Forecast'].EBS[idx].other_liab = items.each_acc_int
    fin_proj[t]['Forecast'].EBS[idx].total_liabilities = fin_proj[t]['Forecast'].EBS[idx].technical_provision + fin_proj[t]['Forecast'].EBS[idx].other_liab
    
    fin_proj[t]['Forecast'].EBS[idx].capital_surplus = fin_proj[t]['Forecast'].EBS[idx].total_assets - fin_proj[t]['Forecast'].EBS[idx].total_liabilities
    fin_proj[t]['Forecast'].EBS[idx].tot_liab_econ_capital_surplus = fin_proj[t]['Forecast'].EBS[idx].total_liabilities + fin_proj[t]['Forecast'].EBS[idx].capital_surplus

    # Underwriting revenues
    fin_proj[t]['Forecast'].EBS_IS[idx].Premiums     = items.each_prem    
    fin_proj[t]['Forecast'].EBS_IS[idx].Total_income = items.each_prem
    
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
    fin_proj[t]['Forecast'].EBS_IS[idx].Total_disbursement = items.each_gi_claim + items.each_death + items.each_cash_div + items.each_surrender + items.each_maturity + \
                                                             items.each_annuity + items.each_ah_ben + items.each_commission + items.each_prem_tax + \
                                                             items.each_tp_change
    
    fin_proj[t]['Forecast'].EBS_IS[idx].Net_underwriting_profit    = fin_proj[t]['Forecast'].EBS_IS[idx].Total_income + \
                                                                     fin_proj[t]['Forecast'].EBS_IS[idx].Total_disbursement
    
    # Combined operating expenses
    fin_proj[t]['Forecast'].EBS_IS[idx].Maint_expense = items.each_maint_exp    
    fin_proj[t]['Forecast'].EBS_IS[idx].GOE           = items.each_goe
    fin_proj[t]['Forecast'].EBS_IS[idx].Operating_expense = items.each_maint_exp + items.each_goe

    # Net investment income
     ####################### EMBEDDED DERIVATIVE ADJUSTMENT NEED TO BE INCORPORATED zzzzzzzzzzzzzzzzzzzzzzzz
    fin_proj[t]['Forecast'].EBS_IS[idx].NII_ABR_GAAP = items.each_nii_abr + fin_proj[t]['Forecast'].Reins[idx].Chng_IMR 
       
    ####################### SURPLUS ITEMS TO BE CALCULATED AT OVERALL LEVEL zzzzzzzzzzzzzzzzzzzzzzzz 
    fin_proj[t]['Forecast'].EBS_IS[idx].NII_surplus                = 0
    fin_proj[t]['Forecast'].EBS_IS[idx].Investment_expense_surplus = 0
    fin_proj[t]['Forecast'].EBS_IS[idx].LOC_cost                   = 0
    
    fin_proj[t]['Forecast'].EBS_IS[idx].Total_NII         = fin_proj[t]['Forecast'].EBS_IS[idx].NII_ABR_GAAP + fin_proj[t]['Forecast'].EBS_IS[idx].NII_surplus + fin_proj[t]['Forecast'].EBS_IS[idx].Investment_expense_surplus
    
    fin_proj[t]['Forecast'].EBS_IS[idx].URCGL             = fin_proj[t]['Forecast'].EBS[idx].fwa_MV - fin_proj[t]['Forecast'].EBS[idx].fwa_BV
    
    # Other income refers to change in other liabilities (i.e. accrued interest)
    if t==0:
        fin_proj[t]['Forecast'].EBS_IS[idx].Other_income = 0
        fin_proj[t]['Forecast'].EBS_IS[idx].RCGL_ED = 0
    else:
        fin_proj[t]['Forecast'].EBS_IS[idx].Other_income      = fin_proj[t-1]['Forecast'].EBS[idx].other_liab - items.each_acc_int
        fin_proj[t]['Forecast'].EBS_IS[idx].RCGL_ED           = fin_proj[t]['Forecast'].EBS_IS[idx].URCGL - fin_proj[t-1]['Forecast'].EBS_IS[idx].URCGL
 
    # Net income
    fin_proj[t]['Forecast'].EBS_IS[idx].Income_before_tax = fin_proj[t]['Forecast'].EBS_IS[idx].Net_underwriting_profit + fin_proj[t]['Forecast'].EBS_IS[idx].Operating_expense + \
                                                            fin_proj[t]['Forecast'].EBS_IS[idx].Total_NII + fin_proj[t]['Forecast'].EBS_IS[idx].Other_income + \
                                                            fin_proj[t]['Forecast'].EBS_IS[idx].RCGL_ED + fin_proj[t]['Forecast'].EBS_IS[idx].LOC_cost
    fin_proj[t]['Forecast'].EBS_IS[idx].Income_tax        = -0.21 * fin_proj[t]['Forecast'].EBS_IS[idx].Income_before_tax
    fin_proj[t]['Forecast'].EBS_IS[idx].Income_after_tax  = fin_proj[t]['Forecast'].EBS_IS[idx].Income_before_tax - fin_proj[t]['Forecast'].EBS_IS[idx].Income_tax 


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
            

def run_Tax_forecast(fin_proj, t, idx): #### Reinsurance Settlement Class
    fin_proj[t]['Forecast'].Tax_IS[idx].Death_claims = fin_proj[t]['Forecast'].Reins[idx].Death_claims


def run_aggregation_forecast(fin_proj, t, idx, agg_level):    
    run_aggregation_Reins_forecast(fin_proj, t, idx, agg_level)
    run_aggregation_EBS_forecast(fin_proj, t, idx, agg_level)
    run_aggregation_SFS_forecast(fin_proj, t, idx, agg_level)
    run_aggregation_Tax_forecast(fin_proj, t, idx, agg_level)


def run_aggregation_Reins_forecast(fin_proj, t, idx, agg_level):    
    fin_proj[t]['Forecast'].Reins[agg_level].Premiums 	                +=	fin_proj[t]['Forecast'].Reins[idx].Premiums 
    fin_proj[t]['Forecast'].Reins[agg_level].NII_ABR_USSTAT 	        +=	fin_proj[t]['Forecast'].Reins[idx].NII_ABR_USSTAT 
    fin_proj[t]['Forecast'].Reins[agg_level].PL_interest	            +=	fin_proj[t]['Forecast'].Reins[idx].PL_interest
    fin_proj[t]['Forecast'].Reins[agg_level].Chng_IMR 	                +=	fin_proj[t]['Forecast'].Reins[idx].Chng_IMR 
    fin_proj[t]['Forecast'].Reins[agg_level].Impairment_reversal 	    +=	fin_proj[t]['Forecast'].Reins[idx].Impairment_reversal 
    fin_proj[t]['Forecast'].Reins[agg_level].Investment_expense 	    +=	fin_proj[t]['Forecast'].Reins[idx].Investment_expense 
            # Expenses		
    fin_proj[t]['Forecast'].Reins[agg_level].Death_claims 	            +=	fin_proj[t]['Forecast'].Reins[idx].Death_claims 
    fin_proj[t]['Forecast'].Reins[agg_level].Maturities 	            +=	fin_proj[t]['Forecast'].Reins[idx].Maturities 
    fin_proj[t]['Forecast'].Reins[agg_level].Surrender 	                +=	fin_proj[t]['Forecast'].Reins[idx].Surrender 
    fin_proj[t]['Forecast'].Reins[agg_level].Dividends 	                +=	fin_proj[t]['Forecast'].Reins[idx].Dividends 
    fin_proj[t]['Forecast'].Reins[agg_level].Annuity_claims 	        +=	fin_proj[t]['Forecast'].Reins[idx].Annuity_claims 
    fin_proj[t]['Forecast'].Reins[agg_level].AH_claims 	                +=	fin_proj[t]['Forecast'].Reins[idx].AH_claims 
    fin_proj[t]['Forecast'].Reins[agg_level].PC_claims 	                +=	fin_proj[t]['Forecast'].Reins[idx].PC_claims 
    fin_proj[t]['Forecast'].Reins[agg_level].Reins_gain 	            +=	fin_proj[t]['Forecast'].Reins[idx].Reins_gain 
    fin_proj[t]['Forecast'].Reins[agg_level].Reins_liab 	            +=	fin_proj[t]['Forecast'].Reins[idx].Reins_liab 
    fin_proj[t]['Forecast'].Reins[agg_level].Commissions 	            +=	fin_proj[t]['Forecast'].Reins[idx].Commissions 
    fin_proj[t]['Forecast'].Reins[agg_level].Maint_expense 	            +=	fin_proj[t]['Forecast'].Reins[idx].Maint_expense 
    fin_proj[t]['Forecast'].Reins[agg_level].Premium_tax 	            +=	fin_proj[t]['Forecast'].Reins[idx].Premium_tax 
    fin_proj[t]['Forecast'].Reins[agg_level].Agg_expense 	            +=	fin_proj[t]['Forecast'].Reins[idx].Agg_expense 
    fin_proj[t]['Forecast'].Reins[agg_level].Guaranty_assess 	        +=	fin_proj[t]['Forecast'].Reins[idx].Guaranty_assess 
    fin_proj[t]['Forecast'].Reins[agg_level].Surplus_particip 	        +=	fin_proj[t]['Forecast'].Reins[idx].Surplus_particip 
    fin_proj[t]['Forecast'].Reins[agg_level].Extra_oblig 	            +=	fin_proj[t]['Forecast'].Reins[idx].Extra_oblig 
            		        
            # Balances		
    fin_proj[t]['Forecast'].Reins[agg_level].Total_STAT_reserve_BOP 	+=	fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_BOP 
    fin_proj[t]['Forecast'].Reins[agg_level].Net_STAT_reserve_BOP 	    +=	fin_proj[t]['Forecast'].Reins[idx].Net_STAT_reserve_BOP 
    fin_proj[t]['Forecast'].Reins[agg_level].CFT_reserve_BOP 	        +=	fin_proj[t]['Forecast'].Reins[idx].CFT_reserve_BOP 
    fin_proj[t]['Forecast'].Reins[agg_level].UPR_BOP 	                +=	fin_proj[t]['Forecast'].Reins[idx].UPR_BOP 
    fin_proj[t]['Forecast'].Reins[agg_level].IMR_BOP 	                +=	fin_proj[t]['Forecast'].Reins[idx].IMR_BOP 
    fin_proj[t]['Forecast'].Reins[agg_level].PL_balance_BOP 	        +=	fin_proj[t]['Forecast'].Reins[idx].PL_balance_BOP 
    fin_proj[t]['Forecast'].Reins[agg_level].Total_STAT_BVA_BOP 	    +=	fin_proj[t]['Forecast'].Reins[idx].Total_STAT_BVA_BOP 
    fin_proj[t]['Forecast'].Reins[agg_level].Total_STAT_reserve_EOP 	+=	fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP 
    fin_proj[t]['Forecast'].Reins[agg_level].Net_STAT_reserve_EOP 	    +=	fin_proj[t]['Forecast'].Reins[idx].Net_STAT_reserve_EOP 
    fin_proj[t]['Forecast'].Reins[agg_level].CFT_reserve_EOP 	        +=	fin_proj[t]['Forecast'].Reins[idx].CFT_reserve_EOP 
    fin_proj[t]['Forecast'].Reins[agg_level].UPR_EOP 	                +=	fin_proj[t]['Forecast'].Reins[idx].UPR_EOP 
    fin_proj[t]['Forecast'].Reins[agg_level].IMR_EOP 	                +=	fin_proj[t]['Forecast'].Reins[idx].IMR_EOP 
    fin_proj[t]['Forecast'].Reins[agg_level].PL_balance_EOP 	        +=	fin_proj[t]['Forecast'].Reins[idx].PL_balance_EOP 
    fin_proj[t]['Forecast'].Reins[agg_level].Total_STAT_BVA_EOP 	    +=	fin_proj[t]['Forecast'].Reins[idx].Total_STAT_BVA_EOP 
            		        
            # Settlement calculated fields		
    fin_proj[t]['Forecast'].Reins[agg_level].Amount_toReins 	        +=	fin_proj[t]['Forecast'].Reins[idx].Amount_toReins 
    fin_proj[t]['Forecast'].Reins[agg_level].Amount_toCeding 	        +=	fin_proj[t]['Forecast'].Reins[idx].Amount_toCeding 
    fin_proj[t]['Forecast'].Reins[agg_level].Chng_PL 	                +=	fin_proj[t]['Forecast'].Reins[idx].Chng_PL 
    fin_proj[t]['Forecast'].Reins[agg_level].Net_cash_settlement 	    +=	fin_proj[t]['Forecast'].Reins[idx].Net_cash_settlement 
    fin_proj[t]['Forecast'].Reins[agg_level].Withdrawal_byReins 	    +=	fin_proj[t]['Forecast'].Reins[idx].Withdrawal_byReins 
    fin_proj[t]['Forecast'].Reins[agg_level].Net_payment_toReins 	    +=	fin_proj[t]['Forecast'].Reins[idx].Net_payment_toReins 
    

def run_aggregation_EBS_forecast(fin_proj, t, idx, agg_level):    
#    Balance Sheet Summary
    fin_proj[t]['Forecast'].EBS[agg_level].cash                          += fin_proj[t]['Forecast'].EBS[idx].cash
    fin_proj[t]['Forecast'].EBS[agg_level].net_settlement_receivable     += fin_proj[t]['Forecast'].EBS[idx].net_settlement_receivable
    fin_proj[t]['Forecast'].EBS[agg_level].fixed_inv_surplus             += fin_proj[t]['Forecast'].EBS[idx].fixed_inv_surplus
    fin_proj[t]['Forecast'].EBS[agg_level].alts_inv_surplus              += fin_proj[t]['Forecast'].EBS[idx].alts_inv_surplus
    fin_proj[t]['Forecast'].EBS[agg_level].fwa_tot                       += fin_proj[t]['Forecast'].EBS[idx].fwa_tot
    fin_proj[t]['Forecast'].EBS[agg_level].fwa_BV                        += fin_proj[t]['Forecast'].EBS[idx].fwa_BV
    fin_proj[t]['Forecast'].EBS[agg_level].fwa_MV                        += fin_proj[t]['Forecast'].EBS[idx].fwa_MV
    fin_proj[t]['Forecast'].EBS[agg_level].fwa_MV_FI                     += fin_proj[t]['Forecast'].EBS[idx].fwa_MV_FI
    fin_proj[t]['Forecast'].EBS[agg_level].FI_Dur                        += fin_proj[t]['Forecast'].EBS[idx].FI_Dur * fin_proj[t]['Forecast'].EBS[idx].fwa_MV_FI ### Will be divided by FI MV in the main model
    fin_proj[t]['Forecast'].EBS[agg_level].fwa_MV_alts                   += fin_proj[t]['Forecast'].EBS[idx].fwa_MV_alts
    fin_proj[t]['Forecast'].EBS[agg_level].fwa_acc_int                   += fin_proj[t]['Forecast'].EBS[idx].fwa_acc_int
    fin_proj[t]['Forecast'].EBS[agg_level].fwa_policy_loan               += fin_proj[t]['Forecast'].EBS[idx].fwa_policy_loan
    fin_proj[t]['Forecast'].EBS[agg_level].STAT_security_adj             += fin_proj[t]['Forecast'].EBS[idx].STAT_security_adj
    fin_proj[t]['Forecast'].EBS[agg_level].GAAP_derivative_adj           += fin_proj[t]['Forecast'].EBS[idx].GAAP_derivative_adj
    fin_proj[t]['Forecast'].EBS[agg_level].GAAP_GRE_FMV_adj              += fin_proj[t]['Forecast'].EBS[idx].GAAP_GRE_FMV_adj
    fin_proj[t]['Forecast'].EBS[agg_level].DTA_DTL                       += fin_proj[t]['Forecast'].EBS[idx].DTA_DTL
    fin_proj[t]['Forecast'].EBS[agg_level].LOC                           += fin_proj[t]['Forecast'].EBS[idx].LOC
    fin_proj[t]['Forecast'].EBS[agg_level].LTIC                          += fin_proj[t]['Forecast'].EBS[idx].LTIC
    fin_proj[t]['Forecast'].EBS[agg_level].Other_Assets                  += fin_proj[t]['Forecast'].EBS[idx].Other_Assets
    fin_proj[t]['Forecast'].EBS[agg_level].other_assets_adj              += fin_proj[t]['Forecast'].EBS[idx].other_assets_adj
    fin_proj[t]['Forecast'].EBS[agg_level].other_liab                    += fin_proj[t]['Forecast'].EBS[idx].other_liab
    fin_proj[t]['Forecast'].EBS[agg_level].surplus_asset_acc_int         += fin_proj[t]['Forecast'].EBS[idx].surplus_asset_acc_int
    fin_proj[t]['Forecast'].EBS[agg_level].total_assets                  += fin_proj[t]['Forecast'].EBS[idx].total_assets
    fin_proj[t]['Forecast'].EBS[agg_level].total_assets_excl_LOCs        += fin_proj[t]['Forecast'].EBS[idx].total_assets_excl_LOCs
    fin_proj[t]['Forecast'].EBS[agg_level].total_invested_assets         += fin_proj[t]['Forecast'].EBS[idx].total_invested_assets
    fin_proj[t]['Forecast'].EBS[agg_level].PV_BE                         += fin_proj[t]['Forecast'].EBS[idx].PV_BE
    fin_proj[t]['Forecast'].EBS[agg_level].risk_margin                   += fin_proj[t]['Forecast'].EBS[idx].risk_margin
    fin_proj[t]['Forecast'].EBS[agg_level].technical_provision           += fin_proj[t]['Forecast'].EBS[idx].technical_provision
    fin_proj[t]['Forecast'].EBS[agg_level].current_tax_payble            += fin_proj[t]['Forecast'].EBS[idx].current_tax_payble
    fin_proj[t]['Forecast'].EBS[agg_level].net_settlement_payble         += fin_proj[t]['Forecast'].EBS[idx].net_settlement_payble
    fin_proj[t]['Forecast'].EBS[agg_level].amount_due_other              += fin_proj[t]['Forecast'].EBS[idx].amount_due_other
    fin_proj[t]['Forecast'].EBS[agg_level].acc_int_liab                  += fin_proj[t]['Forecast'].EBS[idx].acc_int_liab
    fin_proj[t]['Forecast'].EBS[agg_level].total_liabilities             += fin_proj[t]['Forecast'].EBS[idx].total_liabilities
    fin_proj[t]['Forecast'].EBS[agg_level].capital_surplus               += fin_proj[t]['Forecast'].EBS[idx].capital_surplus
    fin_proj[t]['Forecast'].EBS[agg_level].tot_liab_econ_capital_surplus += fin_proj[t]['Forecast'].EBS[idx].tot_liab_econ_capital_surplus
    fin_proj[t]['Forecast'].EBS[agg_level].Derivative_IR01               += fin_proj[t]['Forecast'].EBS[idx].Derivative_IR01
    fin_proj[t]['Forecast'].EBS[agg_level].Derivative_Dur                += fin_proj[t]['Forecast'].EBS[idx].Derivative_Dur     
    fin_proj[t]['Forecast'].EBS[agg_level].ALBA_Adjustment               += fin_proj[t]['Forecast'].EBS[idx].ALBA_Adjustment                

#   Income Statement Summary
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Premiums 	                    +=         fin_proj[t]['Forecast'].EBS_IS[idx].Premiums 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Total_income 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].Total_income 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Death_claims 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].Death_claims 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Maturities 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].Maturities 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Surrender 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].Surrender 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Dividends 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].Dividends 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Annuity_claims 	            +=         fin_proj[t]['Forecast'].EBS_IS[idx].Annuity_claims 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].AH_claims 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].AH_claims 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].PC_claims 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].PC_claims 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Commissions 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].Commissions 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Premium_tax 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].Premium_tax 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Chng_TP 	                    +=         fin_proj[t]['Forecast'].EBS_IS[idx].Chng_TP 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Chng_PVBE 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].Chng_PVBE 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Chng_RM 	                    +=         fin_proj[t]['Forecast'].EBS_IS[idx].Chng_RM
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Total_disbursement 	        +=         fin_proj[t]['Forecast'].EBS_IS[idx].Total_disbursement
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Net_underwriting_profit 	    +=         fin_proj[t]['Forecast'].EBS_IS[idx].Net_underwriting_profit 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Maint_expense 	            +=         fin_proj[t]['Forecast'].EBS_IS[idx].Maint_expense 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].GOE 	                        +=         fin_proj[t]['Forecast'].EBS_IS[idx].GOE
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Operating_expense 	        +=         fin_proj[t]['Forecast'].EBS_IS[idx].Operating_expense
    fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_ABR_GAAP 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].NII_ABR_GAAP 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_surplus 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].NII_surplus 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Investment_expense_surplus 	+=         fin_proj[t]['Forecast'].EBS_IS[idx].Investment_expense_surplus 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Total_NII 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].Total_NII 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Other_income 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].Other_income
    fin_proj[t]['Forecast'].EBS_IS[agg_level].URCGL 	                    +=         fin_proj[t]['Forecast'].EBS_IS[idx].URCGL
    fin_proj[t]['Forecast'].EBS_IS[agg_level].RCGL_ED 	                    +=         fin_proj[t]['Forecast'].EBS_IS[idx].RCGL_ED 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].LOC_cost 	                    +=         fin_proj[t]['Forecast'].EBS_IS[idx].LOC_cost 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_before_tax 	        +=         fin_proj[t]['Forecast'].EBS_IS[idx].Income_before_tax 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_tax 	                +=         fin_proj[t]['Forecast'].EBS_IS[idx].Income_tax 
    fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_after_tax 	            +=         fin_proj[t]['Forecast'].EBS_IS[idx].Income_after_tax 


def run_aggregation_SFS_forecast(fin_proj, t, idx, agg_level):    

    fin_proj[t]['Forecast'].SFS[agg_level].cash                                         	+=	        fin_proj[t]['Forecast'].SFS[idx].cash 
    		        
    fin_proj[t]['Forecast'].SFS[agg_level].short_term_investments                       	+=	        fin_proj[t]['Forecast'].SFS[idx].short_term_investments 
    fin_proj[t]['Forecast'].SFS[agg_level].Bonds_AFS                                    	+=	        fin_proj[t]['Forecast'].SFS[idx].Bonds_AFS 
    fin_proj[t]['Forecast'].SFS[agg_level].Other_invested_assets                        	+=	        fin_proj[t]['Forecast'].SFS[idx].Other_invested_assets 
    fin_proj[t]['Forecast'].SFS[agg_level].Total_investments                            	+=	        fin_proj[t]['Forecast'].SFS[idx].Total_investments 
    		        
    fin_proj[t]['Forecast'].SFS[agg_level].FWA_Host                                     	+=	        fin_proj[t]['Forecast'].SFS[idx].FWA_Host 
    fin_proj[t]['Forecast'].SFS[agg_level].FWA_Embedded_derivative                      	+=	        fin_proj[t]['Forecast'].SFS[idx].FWA_Embedded_derivative 
    fin_proj[t]['Forecast'].SFS[agg_level].Total_funds_withheld_assets                  	+=	        fin_proj[t]['Forecast'].SFS[idx].Total_funds_withheld_assets 
    		        
    fin_proj[t]['Forecast'].SFS[agg_level].Loan_receivable                              	+=	        fin_proj[t]['Forecast'].SFS[idx].Loan_receivable 
    fin_proj[t]['Forecast'].SFS[agg_level].DTA                                          	+=	        fin_proj[t]['Forecast'].SFS[idx].DTA 
    fin_proj[t]['Forecast'].SFS[agg_level].Other_assets                                 	+=	        fin_proj[t]['Forecast'].SFS[idx].Other_assets 
    fin_proj[t]['Forecast'].SFS[agg_level].Total_assets                                 	+=	        fin_proj[t]['Forecast'].SFS[idx].Total_assets 
    		        
    # Liability 		        # Liability 
    fin_proj[t]['Forecast'].SFS[agg_level].Liability_for_unpaid_losses_and_claim_adj_exp 	+=	        fin_proj[t]['Forecast'].SFS[idx].Liability_for_unpaid_losses_and_claim_adj_exp 
    fin_proj[t]['Forecast'].SFS[agg_level].Unearned_premiums 	                            +=	        fin_proj[t]['Forecast'].SFS[idx].Unearned_premiums 
    fin_proj[t]['Forecast'].SFS[agg_level].Future_policyholders_benefits 	                +=	        fin_proj[t]['Forecast'].SFS[idx].Future_policyholders_benefits 
    fin_proj[t]['Forecast'].SFS[agg_level].Policyholder_contract_deposits 	                +=	        fin_proj[t]['Forecast'].SFS[idx].Policyholder_contract_deposits 
    fin_proj[t]['Forecast'].SFS[agg_level].DTL                                          	+=	        fin_proj[t]['Forecast'].SFS[idx].DTL 
    fin_proj[t]['Forecast'].SFS[agg_level].Current_tax_payable                          	+=	        fin_proj[t]['Forecast'].SFS[idx].Current_tax_payable 
    fin_proj[t]['Forecast'].SFS[agg_level].Amounts_due_to_related_parties_settlement    	+=	        fin_proj[t]['Forecast'].SFS[idx].Amounts_due_to_related_parties_settlement 
    fin_proj[t]['Forecast'].SFS[agg_level].Amounts_due_to_related_parties_other         	+=	        fin_proj[t]['Forecast'].SFS[idx].Amounts_due_to_related_parties_other 
    fin_proj[t]['Forecast'].SFS[agg_level].Deferred_gain_on_reinsurance                 	+=	        fin_proj[t]['Forecast'].SFS[idx].Deferred_gain_on_reinsurance 
    fin_proj[t]['Forecast'].SFS[agg_level].Other_liabilities                            	+=	        fin_proj[t]['Forecast'].SFS[idx].Other_liabilities 
    fin_proj[t]['Forecast'].SFS[agg_level].Total_liabilities                            	+=	        fin_proj[t]['Forecast'].SFS[idx].Total_liabilities 
    		        
    # Equity		        # Equity
    fin_proj[t]['Forecast'].SFS[agg_level].Common_stock                                 	+=	        fin_proj[t]['Forecast'].SFS[idx].Common_stock 
    fin_proj[t]['Forecast'].SFS[agg_level].APIC                                         	+=	        fin_proj[t]['Forecast'].SFS[idx].APIC 
    fin_proj[t]['Forecast'].SFS[agg_level].Retained_earnings                            	+=	        fin_proj[t]['Forecast'].SFS[idx].Retained_earnings 
    fin_proj[t]['Forecast'].SFS[agg_level].AOCI                                         	+=	        fin_proj[t]['Forecast'].SFS[idx].AOCI 
    fin_proj[t]['Forecast'].SFS[agg_level].Total_equity                                 	+=	        fin_proj[t]['Forecast'].SFS[idx].Total_equity 
    		        
    fin_proj[t]['Forecast'].SFS[agg_level].Total_liabilities_and_equity                 	+=	        fin_proj[t]['Forecast'].SFS[idx].Total_liabilities_and_equity 
		
    # Underwriting revenues		        # Underwriting revenues
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Premiums                                  	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Premiums 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Decr_unearned_prem                        	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Decr_unearned_prem 
    		        
    # Underwriting expenses		        # Underwriting expenses
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Death_claims                              	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Death_claims 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Maturities                                	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Maturities 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Surrender                                 	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Surrender 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Dividends                                 	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Dividends 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Annuity_claims                                +=	        fin_proj[t]['Forecast'].SFS_IS[idx].Annuity_claims 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].AH_claims                                 	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].AH_claims 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].PC_claims                                 	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].PC_claims 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Commissions                               	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Commissions 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Premium_tax                               	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Premium_tax 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Chng_GAAPRsv                              	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Chng_GAAPRsv 
    		        
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Net_underwriting_profit                   	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Net_underwriting_profit 
    		        
    # Combined operation expenses		        # Combined operation expenses
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Maint_expense                             	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Maint_expense 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].GOE                                       	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].GOE 
    		        
    # Net investment income		        # Net investment income
    fin_proj[t]['Forecast'].SFS_IS[agg_level].NII_ABR_GAAP                              	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].NII_ABR_GAAP 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].NII_surplus                               	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].NII_surplus 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Investment_expense_surplus                	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Investment_expense_surplus 
    		        
    # Other		        # Other
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Amort_deferred_gain                       	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Amort_deferred_gain 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].RCGL_ED                                   	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].RCGL_ED 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].LOC_cost                                  	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].LOC_cost 
    		        
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_before_tax                         	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Income_before_tax 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_tax                                	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Income_tax 
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_after_tax                          	+=	        fin_proj[t]['Forecast'].SFS_IS[idx].Income_after_tax 
    

def run_aggregation_Tax_forecast(fin_proj, t, idx, agg_level):    
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Premiums          	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Premiums 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].NII_ABR_USSTAT    	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].NII_ABR_USSTAT 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].PL_interest	        +=  	    fin_proj[t]['Forecast'].Tax_IS[idx].PL_interest
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Chng_IMR              += 	        fin_proj[t]['Forecast'].Tax_IS[idx].Chng_IMR 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Impairment_reversal 	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Impairment_reversal 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Investment_expense 	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Investment_expense 
    		        
    # Expenses		        # Expenses
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Death_claims      	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Death_claims 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Maturities        	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Maturities 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Surrender         	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Surrender 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Dividends         	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Dividends 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Annuity_claims    	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Annuity_claims 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].AH_claims         	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].AH_claims 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].PC_claims         	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].PC_claims 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Reins_gain        	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Reins_gain 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Reins_liab        	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Reins_liab 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Commissions       	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Commissions 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Maint_expense     	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Maint_expense 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Premium_tax       	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Premium_tax 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Agg_expense       	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Agg_expense 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Guaranty_assess   	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Guaranty_assess 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Surplus_particip  	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Surplus_particip 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Extra_oblig       	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Extra_oblig 
    		        
    # Balances		        # Balances
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Tax_reserve_BOP   	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_BOP 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Tax_reserve_EOP   	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_EOP 
		
    # Settlement calculated fields		        # Settlement calculated fields
    fin_proj[t]['Forecast'].Tax_IS[agg_level].USSTAT_IBT        	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].USSTAT_IBT 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].Tax_exempt_interest 	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_exempt_interest 
    fin_proj[t]['Forecast'].Tax_IS[agg_level].DAC_cap_amort     	+=	        fin_proj[t]['Forecast'].Tax_IS[idx].DAC_cap_amort 
    
    
class input_items:
    
    def __init__(self, cashFlow, fin_proj, t, idx, check = False):
        
        self._cols_input = ['Total premium', 'Total net cashflow', 'GOE', 'aggregate cf', 'Total net face amount', 'Net benefits - death', \
                           'Net benefits - maturity', 'Net benefits - annuity', 'Net - AH benefits', 'Net benefits - P&C claims', \
                           'Net benefits - surrender', 'Total commission', 'Maintenance expenses', 'Net premium tax', 'Net cash dividends', \
                           'Total Stat Res - Net Res', 'Total Tax Res - Net Res', 'UPR', 'BV asset backing liab', 'MV asset backing liab', \
                           'Net investment Income', 'CFT reserve', 'Interest maintenance reserve (NAIC)', 'Accrued Income']
        items = cashFlow.loc[cashFlow['RowNo'] == t + 1, self._cols_input].sum()
        
        ####################### SCALING FUNCTIONALITY NEED TO BE CODED IN zzzzzzzzzzzzzzzzzzzzzzzz
        self.each_prem          = items['Total premium'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_ncf           = items['Total net cashflow'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_goe           = items['GOE'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_agg_cf        = items['aggregate cf'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_face          = items['Total net face amount'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_death         = items['Net benefits - death'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_maturity      = items['Net benefits - maturity'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_annuity       = items['Net benefits - annuity'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_ah_ben        = items['Net - AH benefits'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_gi_claim      = items['Net benefits - P&C claims'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_surrender     = items['Net benefits - surrender'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_commission    = items['Total commission'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_maint_exp     = items['Maintenance expenses'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_prem_tax      = items['Net premium tax'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_cash_div      = items['Net cash dividends'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_stat_rsv      = items['Total Stat Res - Net Res'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_tax_rsv       = items['Total Tax Res - Net Res'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_upr           = items['UPR'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_bva           = items['BV asset backing liab'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_mva           = items['MV asset backing liab'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_nii           = items['Net investment Income'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_cft_rsv       = items['CFT reserve'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_imr           = items['Interest maintenance reserve (NAIC)'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_acc_int       = items['Accrued Income'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self.each_total_stat_rsv = self.each_stat_rsv + self.each_cft_rsv + self.each_imr + self.each_upr
        
        self.each_pv_be = fin_proj[t]['Forecast'].liability['dashboard'][idx].PV_BE + items['aggregate cf'] * fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate ### temporarily subtract aggregate cash flows for each time ZZZZZ need to be refined to reflect the cash flow timing vs. valuation timing
        self.each_rm    = fin_proj[t]['Forecast'].liability['dashboard'][idx].risk_margin
        self.each_tp    = fin_proj[t]['Forecast'].liability['dashboard'][idx].technical_provision

        
        if t == 0:
            self.each_pvbe_change = 0
            self.each_rm_change   = 0
            self.each_tp_change   = 0
        else:
            self.each_pvbe_change = self.each_pv_be - fin_proj[t-1]['Forecast'].liability['dashboard'][idx].PV_BE
            self.each_rm_change   = self.each_rm - fin_proj[t-1]['Forecast'].liability['dashboard'][idx].risk_margin
            self.each_tp_change   = self.each_tp - fin_proj[t-1]['Forecast'].liability['dashboard'][idx].technical_provision
        
        # NII from AXIS is adjusted for any scaling in reserves 
        # Error handling required - self.each_nii_abr = self.each_nii / (items['Total Stat Res - Net Res']+items['CFT reserve']+items['Interest maintenance reserve (NAIC)']+items['UPR']) * self.each_total_stat_rsv April 10/04/2019
        self.each_nii_abr     = self.each_nii
        
        if check:
            print("Inputs initialized")

def run_BSCR_forecast(fin_proj, t):
    Liab_LOB         = fin_proj[t]['Forecast'].liability['dashboard']

    ##  PC Reserve Risk
    PC_Risk_calc     = BSCR_Calc.BSCR_PC_Reserve_Risk_Charge(Liab_LOB, method = "Bespoke")
    PC_Risk_calc_BMA = BSCR_Calc.BSCR_PC_Reserve_Risk_Charge(Liab_LOB, method = "BMA")
    fin_proj[t]['Forecast'].BSCR.update({ 'PC_Risk_calc_bespoke' : PC_Risk_calc})
    fin_proj[t]['Forecast'].BSCR.update({ 'PC_Risk_calc_BMA' : PC_Risk_calc_BMA})

    ##  LT Mortality Risk
    LT_Mort_calc     = BSCR_Calc.BSCR_Mortality_Risk_Charge(Liab_LOB, t)
    fin_proj[t]['Forecast'].BSCR.update({ 'LT_Mortality_Risk' : LT_Mort_calc})    
    
    ##  LT Longevity Risk    
    LT_Longevity_calc = BSCR_Calc.BSCR_Longevity_Risk_Charge(Liab_LOB, t)
    fin_proj[t]['Forecast'].BSCR.update({ 'LT_Longevity_Risk' : LT_Longevity_calc})    

    ##  LT Morbidity Risk    
    LT_Morbidity_calc = BSCR_Calc.BSCR_Morbidity_Risk_Charge(Liab_LOB, t)
    fin_proj[t]['Forecast'].BSCR.update({ 'LT_Morbidity_Risk' : LT_Morbidity_calc})    

    ##  LT Other Insurance Risk    
    LT_Other_Ins_calc = BSCR_Calc.BSCR_Other_Ins_Risk_Charge(Liab_LOB)
    fin_proj[t]['Forecast'].BSCR.update({ 'LT_Other_Ins_Risk' : LT_Other_Ins_calc})    

def run_Ins_Risk_forecast(proj_date, val_date_base, nested_proj_dates, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = 0, base_irCurve_GBP = 0, market_factor = [], liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term):
    PC_risk_forecast = BSCR_Calc.BSCR_PC_Risk_Forecast_RM("Bespoke", proj_date, val_date_base, nested_proj_dates, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = base_irCurve_USD, base_irCurve_GBP = base_irCurve_GBP, market_factor = market_factor, liab_spread_beta = liab_spread_beta, KRD_Term = KRD_Term)
    
    return {'PC_risk_forecast' : PC_risk_forecast}
    
def run_RM_forecast(fin_proj, t, recast_risk_margin, each_date, cf_proj_end_date, cash_flow_freq, valDate, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = 0, rf_curve = 0, base_irCurve_GBP = 0, market_factor = [], liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term):

    # Risk Margin Calculations
    nested_proj_dates = []
    if t == 0:
        nested_proj_dates.extend(list(pd.date_range(each_date, cf_proj_end_date, freq=cash_flow_freq)))
        ins_risk_forecast = run_Ins_Risk_forecast(each_date, valDate, nested_proj_dates, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD, base_irCurve_GBP)
        fin_proj[t]['Forecast'].BSCR.update(ins_risk_forecast)
        
    else:
        if recast_risk_margin == 'N':
            fin_proj[t]['Forecast'].BSCR.update({'PC_risk_forecast': fin_proj[0]['Forecast'].BSCR['PC_risk_forecast']})
        else:
            nested_proj_dates.extend(list(pd.date_range(each_date, cf_proj_end_date, freq=cash_flow_freq)))
            ins_risk_forecast = run_Ins_Risk_forecast(each_date, valDate, nested_proj_dates, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD, base_irCurve_GBP)
            fin_proj[t]['Forecast'].BSCR.update(ins_risk_forecast)

    methods_to_run = ['PC_CoC_Current', 'PC_CoC_New']
    
    for each_method in methods_to_run:
        cf_period        = list(fin_proj[t]['Forecast'].BSCR['PC_risk_forecast'][each_method])
        cf_values        = fin_proj[t]['Forecast'].BSCR['PC_risk_forecast'][each_method].values()
    
        try:
            cf_current       = fin_proj[t]['Forecast'].BSCR['PC_risk_forecast'][each_method][each_date]
        except:
            cf_current       = 0
        
        each_key = 'PC_RM_' + each_method
            
        cfHandle         = IAL.CF.createSimpleCFs(cf_period,cf_values)
        risk_margin_calc = IAL.CF.PVFromCurve(cfHandle, rf_curve, each_date, 0) - cf_current
        
        fin_proj[t]['Forecast'].BSCR.update({each_key : risk_margin_calc})