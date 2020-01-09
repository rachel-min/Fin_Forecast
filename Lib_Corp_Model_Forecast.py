# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 11:20:18 2019

@author: seongpar
"""
import os
import Lib_Market_Akit  as IAL_App
import Class_Corp_Model as Corpclass
import Lib_BSCR_Calc   as BSCR_Calc
import numpy as np
import pandas as pd
import datetime as dt
#import Lib_Corp_Model as Corp
import Config_BSCR as BSCR_Cofig
import Class_CFO as CFO_class

akit_dir = 'C:/AKit v4.1.0/BIN'
os.sys.path.append(akit_dir)
import IALPython3        as IAL

def run_TP_forecast(fin_proj, proj_t, valDate, liab_val_base, liab_summary_base, input_liab_val_base,
                    base_irCurve_USD = 0, base_irCurve_GBP = 0, 
                    market_factor = [], liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term):
    
    """
    Input variables:
        fin_proj: financial projections module of cfo
        proj_t:   projection time, integer, 0-70
        valDate:  valuation date, datetime
        liab_summary_base:   dict of 45 base LiabAnalyticsUnit
        input_liab_val_base: dict of information for reading base liability data
        base_irCurve_USD:    Akit USD curve
        base_irCurve_GBP:    Akit GBP curve
        market_factor:       SHOULD BE A DICT BUT A LIST IS GIVEN HERE
        liab_spread_beta:    hard-coded float of 0.65
        KRD_Term:            dict of mapping between term and years
    """
    
    curveType          = input_liab_val_base['curve_type']
    numOfLoB           = input_liab_val_base['numOfLoB']
    gbp_rate           = input_liab_val_base['base_GBP']
    cf_proj_end_date   = input_liab_val_base['cf_proj_end_date']
    cash_flow_freq     = input_liab_val_base['cash_flow_freq']
    Recast_Risk_Margin = input_liab_val_base['Recast_Risk_Margin']
    
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
            
        # TP Projections
        fin_proj[t]['Forecast'].run_dashboard_liab_value(valDate, each_date, curveType, numOfLoB, market_factor ,liab_spread_beta, KRD_Term, base_irCurve_USD, base_irCurve_GBP, gbp_rate)

        # GAAP Reserve Projections
        # def Run_Liab_DashBoard_GAAP_Disc(t, current_liab, base_liab, current_date):
        fin_proj[t]['Forecast'].run_liab_dashboard_GAAP_disc(t, each_date)

        # Preliminary summary before updating risk margin
        fin_proj[t]['Forecast'].set_dashboard_liab_summary(numOfLoB)

        #  Risk Margin Projection 
        run_RM_forecast(fin_proj, t, Recast_Risk_Margin, each_date, cf_proj_end_date, cash_flow_freq, valDate, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, 
                        base_irCurve_USD = base_irCurve_USD, 
                        rf_curve         = base_irCurve_USD, 
                        base_irCurve_GBP = base_irCurve_GBP, 
                        market_factor    = market_factor, 
                        liab_spread_beta = liab_spread_beta, 
                        KRD_Term         = KRD_Term)

        #  Override risk margin based on the calculated value
        update_RM_LOB(Liab_LOB        = fin_proj[t]['Forecast'].liability['dashboard'], 
                      pv_be_agg       = fin_proj[t]['Forecast'].liab_summary['dashboard'], 
                      Risk_Margin_agg = fin_proj[t]['Forecast'].BSCR )
        # Final summary after updating risk margin
        fin_proj[t]['Forecast'].set_dashboard_liab_summary(numOfLoB) 


def update_RM_LOB(Liab_LOB, pv_be_agg, Risk_Margin_agg):

    if pv_be_agg['LT']['PV_BE'] < 0.0001:
        LT_rm_ratio = 0
    else:
        LT_rm_ratio = Risk_Margin_agg['LT_RM_LT_CoC_Current'] / pv_be_agg['LT']['PV_BE']

    if pv_be_agg['GI']['PV_BE'] < 0.0001:
        GI_rm_ratio = 0
    else:
        GI_rm_ratio = Risk_Margin_agg['PC_RM_PC_CoC_Current'] / pv_be_agg['GI']['PV_BE']

    for idx, each_liab in Liab_LOB.items():
        #### This needs to be updated with Risk Type to correct NUFIC        
        if each_liab.LOB_Def['Agg LOB'] == 'PC':  
            each_liab.Risk_Margin = each_liab.PV_BE * GI_rm_ratio
        else:
            each_liab.Risk_Margin = each_liab.PV_BE * LT_rm_ratio

        each_liab.Technical_Provision = each_liab.PV_BE + each_liab.Risk_Margin        
        
def run_fin_forecast(fin_proj, proj_t, numOfLoB, proj_cash_flows, Asset_holding, Asset_adjustment, Regime, work_dir, run_control, valDate, curveType = 'Treasury', base_irCurve_USD = 0 ):
    
    """
    Input variables:
        fin_proj:         financial projections module of cfo
        proj_t:           projection time, integer, 0-70
        numOfLoB:         int, 45
        proj_cash_flows:  dict of 45 projection LiabAnalyticsUnit
        Asset_holding:    pandas.dataframe of asset holding at CUSIP level
        Asset_adjustment: pandas.dataframe of asset adjustment mapping table
        Regime:           str, currently only support "current"
        work_dir:         str, directory for reading extra informations
        run_control:      run_control object
        valDate:          valuation date, datetime 
        curveType:        str, ['Treasury']
        base_irCurve_USD: Akit USD curve
    """
    
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

            liab_proj_items = CFO_class.liab_proj_items(cf_idx, fin_proj, run_control, t, idx)
            liab_proj_items._record(['each_pvbe_ratio'], fin_proj[t]['Forecast'])
            
            ### Run by indivdual functions
            run_reins_settlement_forecast(liab_proj_items, fin_proj, t, idx, run_control)
            run_EBS_forecast_LOB(liab_proj_items, fin_proj, t, idx, run_control)
            run_SFS_forecast_LOB(liab_proj_items, fin_proj, t, idx, run_control)
            run_Tax_forecast_LOB(liab_proj_items, fin_proj, t, idx, run_control)   ### Tax forecast will be added later
            
            ### Aggregation
            clsLiab    = proj_cash_flows[idx]
            each_lob   = clsLiab.get_LOB_Def('Agg LOB')
            
            if each_lob == "LR":                
                run_aggregation_forecast(fin_proj, t, idx, 'LT')
            else: 
                run_aggregation_forecast(fin_proj, t, idx, 'GI')
                
            #           Aggregate Account
            run_aggregation_forecast(fin_proj, t, idx, 'Agg')

        if t == 0:
            curr_dir = os.getcwd()
            os.chdir(work_dir)
            fin_proj[t]['Forecast'].set_sfs(run_control.SFS_BS)
            fin_proj[t]['Forecast'].run_base_EBS(Asset_holding, Asset_adjustment)
            os.chdir(curr_dir)
        else:
            #####   Surplus Account Roll-forward ##################
            roll_forward_surplus_assets(fin_proj, t, 'Agg', valDate, run_control, curveType = curveType, base_irCurve_USD = base_irCurve_USD )      

        #####   Target Capital and Dividend Calculations ##################
        run_BSCR_forecast(fin_proj, t, Asset_holding, Asset_adjustment, Regime, work_dir, run_control)
        run_LOC_forecast(fin_proj, t, run_control, agg_level = 'Agg')
        run_dividend_calculation(fin_proj, t, run_control)
        

def run_reins_settlement_forecast(liab_proj_items, fin_proj, t, idx, run_control): #### Reinsurance Settlement Class

    LOB_line = fin_proj[t]['Forecast'].liability['dashboard'][idx].LOB_Def['PC_Life']
    LOB_Name = fin_proj[t]['Forecast'].liability['dashboard'][idx].LOB_Def['LOB Name']
    
    if LOB_line == 'PC' and LOB_Name != 'LR_NUF_AH':
        inv_fee_explicit_cal = 1 
    else:
        inv_fee_explicit_cal = 0        
    
    # Balances
    # Add special condition t = 0 ################### Kyle Modified on 9/29/2019
    if t == 0:
        fin_proj[t]['Forecast'].Reins[idx].Net_STAT_reserve_EOP = liab_proj_items.each_scaled_stat_rsv
        fin_proj[t]['Forecast'].Reins[idx].Net_STAT_reserve_BOP = liab_proj_items.each_scaled_stat_rsv
        fin_proj[t]['Forecast'].Reins[idx].CFT_reserve_EOP      = liab_proj_items.each_cft_rsv
        fin_proj[t]['Forecast'].Reins[idx].CFT_reserve_BOP      = liab_proj_items.each_cft_rsv
        fin_proj[t]['Forecast'].Reins[idx].UPR_EOP              = liab_proj_items.each_upr
        fin_proj[t]['Forecast'].Reins[idx].UPR_BOP              = liab_proj_items.each_upr
        fin_proj[t]['Forecast'].Reins[idx].IMR_EOP              = liab_proj_items.each_imr
        fin_proj[t]['Forecast'].Reins[idx].IMR_BOP              = liab_proj_items.each_imr
        fin_proj[t]['Forecast'].Reins[idx].PL_balance_EOP       = 0 ##Policy Loan Balance need to be pulled in##
        fin_proj[t]['Forecast'].Reins[idx].PL_balance_BOP       = 0 ##Policy Loan Balance need to be pulled in##
        fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP = liab_proj_items.each_scaled_total_stat_rsv
        fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_BOP = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP
        fin_proj[t]['Forecast'].Reins[idx].Total_MV_EOP         = liab_proj_items.each_scaled_mva
        fin_proj[t]['Forecast'].Reins[idx].Total_MV_BOP         = fin_proj[t]['Forecast'].Reins[idx].Total_MV_EOP
        
    else:
        fin_proj[t]['Forecast'].Reins[idx].Net_STAT_reserve_EOP = liab_proj_items.each_scaled_stat_rsv
        fin_proj[t]['Forecast'].Reins[idx].Net_STAT_reserve_BOP = fin_proj[t-1]['Forecast'].Reins[idx].Net_STAT_reserve_EOP
        fin_proj[t]['Forecast'].Reins[idx].CFT_reserve_EOP      = liab_proj_items.each_cft_rsv
        fin_proj[t]['Forecast'].Reins[idx].CFT_reserve_BOP      = fin_proj[t-1]['Forecast'].Reins[idx].CFT_reserve_EOP
        fin_proj[t]['Forecast'].Reins[idx].UPR_EOP              = liab_proj_items.each_upr
        fin_proj[t]['Forecast'].Reins[idx].UPR_BOP              = fin_proj[t-1]['Forecast'].Reins[idx].UPR_EOP
        fin_proj[t]['Forecast'].Reins[idx].IMR_EOP              = liab_proj_items.each_imr
        fin_proj[t]['Forecast'].Reins[idx].IMR_BOP              = fin_proj[t-1]['Forecast'].Reins[idx].IMR_EOP
        fin_proj[t]['Forecast'].Reins[idx].PL_balance_EOP       = 0 ##Policy Loan Balance need to be pulled in##
        fin_proj[t]['Forecast'].Reins[idx].PL_balance_BOP       = fin_proj[t-1]['Forecast'].Reins[idx].PL_balance_EOP ##Policy Loan Balance need to be pulled in##
        fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP = liab_proj_items.each_scaled_total_stat_rsv
        fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_BOP = fin_proj[t-1]['Forecast'].Reins[idx].Total_STAT_reserve_EOP
        fin_proj[t]['Forecast'].Reins[idx].Total_MV_EOP         = liab_proj_items.each_scaled_mva
        fin_proj[t]['Forecast'].Reins[idx].Total_MV_BOP         = fin_proj[t-1]['Forecast'].Reins[idx].Total_MV_EOP
        

    if t > 0 and inv_fee_explicit_cal == 1:
        work_return_period = IAL.Date.yearFrac("ACT/365",  fin_proj[t-1]['date'], fin_proj[t]['date'])

        LPT_inv_fee        = -run_control.inv_mgmt_fee['LPT']
        fin_proj[t]['Forecast'].Reins[idx].Investment_Expense                                                      \
        = (fin_proj[t]['Forecast'].Reins[idx].Total_MV_BOP + fin_proj[t]['Forecast'].Reins[idx].Total_MV_EOP) / 2  \
        * work_return_period * LPT_inv_fee
    else:
        fin_proj[t]['Forecast'].Reins[idx].Investment_Expense   = 0


    if t > 0:
        work_return_period = IAL.Date.yearFrac("ACT/365",  fin_proj[t-1]['date'], fin_proj[t]['date'])
       
        PL_int_rate   = -run_control.proj_schedule[t]['PL_int_rate']
        fin_proj[t]['Forecast'].Reins[idx].PL_interest  \
        = PL_int_rate * work_return_period              \
        * ((fin_proj[t]['Forecast'].Reins[idx].PL_balance_BOP + fin_proj[t]['Forecast'].Reins[idx].PL_balance_EOP) / 2) 
    else:
        fin_proj[t]['Forecast'].Reins[idx].PL_interest = 0
        
    # Revenues                        
    fin_proj[t]['Forecast'].Reins[idx].Premiums            = liab_proj_items.each_prem
    fin_proj[t]['Forecast'].Reins[idx].Chng_IMR            = fin_proj[t]['Forecast'].Reins[idx].IMR_EOP - fin_proj[t]['Forecast'].Reins[idx].IMR_BOP
    fin_proj[t]['Forecast'].Reins[idx].Impairment_reversal = 0
    fin_proj[t]['Forecast'].Reins[idx].NII_ABR_USSTAT      = liab_proj_items.each_scaled_nii_abr + fin_proj[t]['Forecast'].Reins[idx].Chng_IMR + fin_proj[t]['Forecast'].Reins[idx].PL_interest

    # Policyholder Benefits and Expenses    
    fin_proj[t]['Forecast'].Reins[idx].Death_Claims      = liab_proj_items.each_death
    fin_proj[t]['Forecast'].Reins[idx].Maturities        = liab_proj_items.each_maturity
    fin_proj[t]['Forecast'].Reins[idx].Surrender         = liab_proj_items.each_surrender
    fin_proj[t]['Forecast'].Reins[idx].Dividends         = liab_proj_items.each_cash_div
    fin_proj[t]['Forecast'].Reins[idx].Annuity_Claims    = liab_proj_items.each_annuity
    fin_proj[t]['Forecast'].Reins[idx].AH_Claims         = liab_proj_items.each_ah_ben
    fin_proj[t]['Forecast'].Reins[idx].PC_Claims         = liab_proj_items.each_gi_claim
    fin_proj[t]['Forecast'].Reins[idx].Reins_gain        = 0
    fin_proj[t]['Forecast'].Reins[idx].Reins_liab        = liab_proj_items.each_death + liab_proj_items.each_maturity + liab_proj_items.each_surrender + liab_proj_items.each_cash_div + liab_proj_items.each_annuity + liab_proj_items.each_ah_ben + liab_proj_items.each_gi_claim + fin_proj[t]['Forecast'].Reins[idx].Reins_gain
    fin_proj[t]['Forecast'].Reins[idx].Commissions       = liab_proj_items.each_commission
    fin_proj[t]['Forecast'].Reins[idx].Maint_Expense     = liab_proj_items.each_maint_exp
    fin_proj[t]['Forecast'].Reins[idx].Premium_Tax       = liab_proj_items.each_prem_tax
    fin_proj[t]['Forecast'].Reins[idx].Agg_Expense       = liab_proj_items.each_commission + liab_proj_items.each_maint_exp + liab_proj_items.each_prem_tax
    fin_proj[t]['Forecast'].Reins[idx].Guaranty_assess   = 0
    fin_proj[t]['Forecast'].Reins[idx].Surplus_particip  = 0
    fin_proj[t]['Forecast'].Reins[idx].Extra_oblig       = 0
            
    # Settlement calculated fields
    fin_proj[t]['Forecast'].Reins[idx].Amount_toReins      = fin_proj[t]['Forecast'].Reins[idx].PL_interest + fin_proj[t]['Forecast'].Reins[idx].Premiums + fin_proj[t]['Forecast'].Reins[idx].Impairment_reversal
    fin_proj[t]['Forecast'].Reins[idx].Amount_toCeding     = 0 - (fin_proj[t]['Forecast'].Reins[idx].Extra_oblig + fin_proj[t]['Forecast'].Reins[idx].Reins_liab + fin_proj[t]['Forecast'].Reins[idx].Agg_Expense +fin_proj[t]['Forecast'].Reins[idx].Investment_Expense + fin_proj[t]['Forecast'].Reins[idx].Guaranty_assess + fin_proj[t]['Forecast'].Reins[idx].Surplus_particip) 
    fin_proj[t]['Forecast'].Reins[idx].Chng_PL             = fin_proj[t]['Forecast'].Reins[idx].PL_balance_EOP - fin_proj[t]['Forecast'].Reins[idx].PL_balance_BOP
    fin_proj[t]['Forecast'].Reins[idx].Net_cash_settlement = fin_proj[t]['Forecast'].Reins[idx].Amount_toCeding - fin_proj[t]['Forecast'].Reins[idx].Amount_toReins + fin_proj[t]['Forecast'].Reins[idx].Chng_PL
    fin_proj[t]['Forecast'].Reins[idx].Total_STAT_BVA_BOP  = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_BOP
    fin_proj[t]['Forecast'].Reins[idx].Total_STAT_BVA_EOP  = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_BVA_BOP +  fin_proj[t]['Forecast'].Reins[idx].NII_ABR_USSTAT + fin_proj[t]['Forecast'].Reins[idx].Chng_PL
    fin_proj[t]['Forecast'].Reins[idx].Withdrawal_byReins  = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_BVA_EOP - fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP
    fin_proj[t]['Forecast'].Reins[idx].Net_payment_toReins = fin_proj[t]['Forecast'].Reins[idx].Withdrawal_byReins - fin_proj[t]['Forecast'].Reins[idx].Net_cash_settlement
    

def run_EBS_forecast_LOB(liab_proj_items, fin_proj, t, idx, run_control, iter = 0):  # EBS Items    
    
    LOB_line = fin_proj[t]['Forecast'].liability['dashboard'][idx].LOB_Def['PC_Life']
    
    if LOB_line == 'Life':
        ltic_explicit_cal = 1
    else:
        ltic_explicit_cal = 0
    
    # Balance sheet: Assets
    #######################Time zero need to tie with actuals; may need scaling zzzzzzzzzzzzzzzz
    fin_proj[t]['Forecast'].EBS[idx].FWA_MV                  \
    = fin_proj[t]['Forecast'].EBS[idx].Total_Invested_Assets_LOB \
    = liab_proj_items.each_scaled_mva #Equal to scaled MVA
    
    fin_proj[t]['Forecast'].EBS[idx].FWA_BV  = liab_proj_items.each_scaled_bva #Equal to scaled BVA
    fin_proj[t]['Forecast'].EBS[idx].LTIC    = liab_proj_items.ltic_agg * liab_proj_items.each_pvbe_ratio * ltic_explicit_cal
    
    # Balance sheet: Liabilities    
    fin_proj[t]['Forecast'].EBS[idx].PV_BE = liab_proj_items.each_pv_be    
    fin_proj[t]['Forecast'].EBS[idx].Risk_Margin = liab_proj_items.each_rm    
    fin_proj[t]['Forecast'].EBS[idx].Technical_Provision = liab_proj_items.each_tp   
    
    fin_proj[t]['Forecast'].EBS[idx].Acc_Int_Liab \
    = fin_proj[t]['Forecast'].EBS[idx].Other_Liab \
    = liab_proj_items.each_scaled_acc_int
    
    fin_proj[t]['Forecast'].EBS[idx].Total_Liabilities = fin_proj[t]['Forecast'].EBS[idx].Technical_Provision + fin_proj[t]['Forecast'].EBS[idx].Other_Liab
    fin_proj[t]['Forecast'].EBS[idx].GOE_Provision = liab_proj_items.each_GOE_Provision

    # Underwriting revenues
    fin_proj[t]['Forecast'].EBS_IS[idx].Premiums     = liab_proj_items.each_prem    
    fin_proj[t]['Forecast'].EBS_IS[idx].Total_Income = liab_proj_items.each_prem
    
    # Underwriting expenses
    fin_proj[t]['Forecast'].EBS_IS[idx].Death_Claims   = liab_proj_items.each_death    
    fin_proj[t]['Forecast'].EBS_IS[idx].Maturities     = liab_proj_items.each_maturity    
    fin_proj[t]['Forecast'].EBS_IS[idx].Surrender      = liab_proj_items.each_surrender    
    fin_proj[t]['Forecast'].EBS_IS[idx].Dividends      = liab_proj_items.each_cash_div    
    fin_proj[t]['Forecast'].EBS_IS[idx].Annuity_Claims = liab_proj_items.each_annuity    
    fin_proj[t]['Forecast'].EBS_IS[idx].AH_Claims      = liab_proj_items.each_ah_ben    
    fin_proj[t]['Forecast'].EBS_IS[idx].PC_Claims      = liab_proj_items.each_gi_claim    
    fin_proj[t]['Forecast'].EBS_IS[idx].Commissions    = liab_proj_items.each_commission    
    fin_proj[t]['Forecast'].EBS_IS[idx].Premium_Tax    = liab_proj_items.each_prem_tax    

    if t == 0:
        fin_proj[t]['Forecast'].EBS_IS[idx].Chng_PVBE = 0
        fin_proj[t]['Forecast'].EBS_IS[idx].Chng_RM   = 0
        fin_proj[t]['Forecast'].EBS_IS[idx].Chng_TP   = 0
    else:
        fin_proj[t]['Forecast'].EBS_IS[idx].Chng_PVBE = fin_proj[t]['Forecast'].EBS[idx].PV_BE - fin_proj[t-1]['Forecast'].EBS[idx].PV_BE
        fin_proj[t]['Forecast'].EBS_IS[idx].Chng_RM   = fin_proj[t]['Forecast'].EBS[idx].Risk_Margin - fin_proj[t-1]['Forecast'].EBS[idx].Risk_Margin
        fin_proj[t]['Forecast'].EBS_IS[idx].Chng_TP   = fin_proj[t]['Forecast'].EBS[idx].Technical_Provision - fin_proj[t-1]['Forecast'].EBS[idx].Technical_Provision

    fin_proj[t]['Forecast'].EBS_IS[idx].Total_Disbursement \
    = fin_proj[t]['Forecast'].EBS_IS[idx].Death_Claims     \
    + fin_proj[t]['Forecast'].EBS_IS[idx].Maturities       \
    + fin_proj[t]['Forecast'].EBS_IS[idx].Surrender        \
    + fin_proj[t]['Forecast'].EBS_IS[idx].Dividends        \
    + fin_proj[t]['Forecast'].EBS_IS[idx].Annuity_Claims   \
    + fin_proj[t]['Forecast'].EBS_IS[idx].AH_Claims        \
    + fin_proj[t]['Forecast'].EBS_IS[idx].PC_Claims        \
    + fin_proj[t]['Forecast'].EBS_IS[idx].Commissions      \
    + fin_proj[t]['Forecast'].EBS_IS[idx].Premium_Tax      \
    - fin_proj[t]['Forecast'].EBS_IS[idx].Chng_TP    

    fin_proj[t]['Forecast'].EBS_IS[idx].Net_underwriting_Profit  = fin_proj[t]['Forecast'].EBS_IS[idx].Total_Income + fin_proj[t]['Forecast'].EBS_IS[idx].Total_Disbursement
    
    # Combined operating expenses
    fin_proj[t]['Forecast'].EBS_IS[idx].Maint_Expense = liab_proj_items.each_maint_exp    
    fin_proj[t]['Forecast'].EBS_IS[idx].GOE_F           = liab_proj_items.each_goe_f
    fin_proj[t]['Forecast'].EBS_IS[idx].Operating_Expense = liab_proj_items.each_maint_exp + liab_proj_items.each_goe_f

    # Net investment income
    ####################### EMBEDDED DERIVATIVE ADJUSTMENT NEED TO BE INCORPORATED zzzzzzzzzzzzzzzzzzzzzzzz
    fin_proj[t]['Forecast'].EBS_IS[idx].NII_ABR_GAAP           = liab_proj_items.each_scaled_nii_abr + fin_proj[t]['Forecast'].Reins[idx].Chng_IMR 
    fin_proj[t]['Forecast'].EBS_IS[idx].URCGL                  = fin_proj[t]['Forecast'].EBS[idx].FWA_MV - fin_proj[t]['Forecast'].EBS[idx].FWA_BV
    fin_proj[t]['Forecast'].EBS_IS[idx].Investment_Expense_fwa = fin_proj[t]['Forecast'].Reins[idx].Investment_Expense        
    
    # Other income refers to change in other liabilities (i.e. accrued interest)
    if t==0:
        fin_proj[t]['Forecast'].EBS_IS[idx].Other_Income = 0
        fin_proj[t]['Forecast'].EBS_IS[idx].RCGL_ED = 0
    else:
        fin_proj[t]['Forecast'].EBS_IS[idx].Other_Income      = fin_proj[t-1]['Forecast'].EBS[idx].Other_Liab - liab_proj_items.each_scaled_acc_int
        fin_proj[t]['Forecast'].EBS_IS[idx].RCGL_ED           = fin_proj[t]['Forecast'].EBS_IS[idx].URCGL - fin_proj[t-1]['Forecast'].EBS_IS[idx].URCGL

    # Net income LOB
    fin_proj[t]['Forecast'].EBS_IS[idx].Income_before_Tax_LOB     \
    = fin_proj[t]['Forecast'].EBS_IS[idx].Net_underwriting_Profit \
    + fin_proj[t]['Forecast'].EBS_IS[idx].Operating_Expense       \
    + fin_proj[t]['Forecast'].EBS_IS[idx].NII_ABR_GAAP            \
    + fin_proj[t]['Forecast'].EBS_IS[idx].Investment_Expense_fwa  \
    + fin_proj[t]['Forecast'].EBS_IS[idx].RCGL_ED                 \
    + fin_proj[t]['Forecast'].EBS_IS[idx].Other_Income 

    fin_proj[t]['Forecast'].EBS_IS[idx].Income_Tax_LOB        = -run_control.proj_schedule[t]['Tax_Rate'] * fin_proj[t]['Forecast'].EBS_IS[idx].Income_before_Tax_LOB
    fin_proj[t]['Forecast'].EBS_IS[idx].Income_after_Tax_LOB  = fin_proj[t]['Forecast'].EBS_IS[idx].Income_before_Tax_LOB + fin_proj[t]['Forecast'].EBS_IS[idx].Income_Tax_LOB 

def run_SFS_forecast_LOB(liab_proj_items, fin_proj, t, idx, run_control):  # SFS Items    

    # Assets (for aggregation)
    fin_proj[t]['Forecast'].SFS[idx].FWA_MV \
    = fin_proj[t]['Forecast'].SFS[idx].Total_Invested_Assets_LOB \
    = liab_proj_items.each_scaled_mva
    
    fin_proj[t]['Forecast'].SFS[idx].FWA_BV                  = liab_proj_items.each_scaled_bva
    fin_proj[t]['Forecast'].SFS[idx].Unrealized_Capital_Gain = liab_proj_items.each_scaled_mva - liab_proj_items.each_scaled_bva

    ###### GAAP Reserve Forecast
    each_GAAP_method = fin_proj[t]['Forecast'].liability['base'][idx].LOB_Def['GAAP_Model']
    run_GAAP_reserve(liab_proj_items, fin_proj, t, idx, each_GAAP_method, run_control.GAAP_Reserve_method)

    if t == 0:
        fin_proj[t]['Forecast'].SFS_IS[idx].UPR_EOP = liab_proj_items.each_upr
        fin_proj[t]['Forecast'].SFS_IS[idx].UPR_BOP = liab_proj_items.each_upr 
        #fin_proj[t]['Forecast'].SFS_IS[idx].PL_balance_EOP = ##Policy Loan Balance need to be pulled in##
        #fin_proj[t]['Forecast'].SFS_IS[idx].PL_balance_BOP = ##Policy Loan Balance need to be pulled in##
    else:
        fin_proj[t]['Forecast'].SFS_IS[idx].UPR_EOP = liab_proj_items.each_upr
        fin_proj[t]['Forecast'].SFS_IS[idx].UPR_BOP = fin_proj[t-1]['Forecast'].SFS_IS[idx].UPR_EOP
        fin_proj[t]['Forecast'].SFS_IS[idx].Chng_GAAPRsv   = fin_proj[t]['Forecast'].SFS[idx].GAAP_Reserve - fin_proj[t-1]['Forecast'].SFS[idx].GAAP_Reserve 
        #fin_proj[t]['Forecast'].SFS_IS[idx].PL_balance_EOP = ##Policy Loan Balance need to be pulled in##
        #fin_proj[t]['Forecast'].SFS_IS[idx].PL_balance_BOP = ##Policy Loan Balance need to be pulled in##

    # Underwriting revenues
    fin_proj[t]['Forecast'].SFS_IS[idx].Premiums           = liab_proj_items.each_prem    
    fin_proj[t]['Forecast'].SFS_IS[idx].Decr_Unearned_Premiums = fin_proj[t]['Forecast'].SFS_IS[idx].UPR_BOP - fin_proj[t]['Forecast'].SFS_IS[idx].UPR_EOP
    fin_proj[t]['Forecast'].SFS_IS[idx].Total_Income       = liab_proj_items.each_prem + fin_proj[t]['Forecast'].SFS_IS[idx].Decr_Unearned_Premiums
    
    # Underwriting expenses
    fin_proj[t]['Forecast'].SFS_IS[idx].Death_Claims   = liab_proj_items.each_death    
    fin_proj[t]['Forecast'].SFS_IS[idx].Maturities     = liab_proj_items.each_maturity    
    fin_proj[t]['Forecast'].SFS_IS[idx].Surrender      = liab_proj_items.each_surrender    
    fin_proj[t]['Forecast'].SFS_IS[idx].Dividends      = liab_proj_items.each_cash_div    
    fin_proj[t]['Forecast'].SFS_IS[idx].Annuity_Claims = liab_proj_items.each_annuity    
    fin_proj[t]['Forecast'].SFS_IS[idx].AH_Claims      = liab_proj_items.each_ah_ben    
    fin_proj[t]['Forecast'].SFS_IS[idx].PC_Claims      = liab_proj_items.each_gi_claim    
    fin_proj[t]['Forecast'].SFS_IS[idx].Commissions    = liab_proj_items.each_commission    
    fin_proj[t]['Forecast'].SFS_IS[idx].Premium_Tax    = liab_proj_items.each_prem_tax    

    fin_proj[t]['Forecast'].SFS_IS[idx].Total_Disbursement \
    = fin_proj[t]['Forecast'].SFS_IS[idx].Death_Claims     \
    + fin_proj[t]['Forecast'].SFS_IS[idx].Maturities       \
    + fin_proj[t]['Forecast'].SFS_IS[idx].Surrender        \
    + fin_proj[t]['Forecast'].SFS_IS[idx].Dividends        \
    + fin_proj[t]['Forecast'].SFS_IS[idx].Annuity_Claims   \
    + fin_proj[t]['Forecast'].SFS_IS[idx].AH_Claims        \
    + fin_proj[t]['Forecast'].SFS_IS[idx].PC_Claims        \
    + fin_proj[t]['Forecast'].SFS_IS[idx].Commissions      \
    + fin_proj[t]['Forecast'].SFS_IS[idx].Premium_Tax      \
    - fin_proj[t]['Forecast'].SFS_IS[idx].Chng_GAAPRsv    

    fin_proj[t]['Forecast'].SFS_IS[idx].Net_underwriting_Profit  \
    = fin_proj[t]['Forecast'].SFS_IS[idx].Total_Income           \
    + fin_proj[t]['Forecast'].SFS_IS[idx].Total_Disbursement

    # Combined operation expenses
    fin_proj[t]['Forecast'].SFS_IS[idx].Maint_Expense  = liab_proj_items.each_maint_exp    
    fin_proj[t]['Forecast'].SFS_IS[idx].GOE_F          = liab_proj_items.each_goe_f    
    fin_proj[t]['Forecast'].SFS_IS[idx].Operating_Expense = liab_proj_items.each_maint_exp + liab_proj_items.each_goe_f

    # Net investment income
    fin_proj[t]['Forecast'].SFS_IS[idx].NII_ABR_GAAP           = liab_proj_items.each_scaled_nii_abr + fin_proj[t]['Forecast'].Reins[idx].Chng_IMR 
    fin_proj[t]['Forecast'].SFS_IS[idx].URCGL                  = fin_proj[t]['Forecast'].SFS[idx].FWA_MV - fin_proj[t]['Forecast'].SFS[idx].FWA_BV
    fin_proj[t]['Forecast'].SFS_IS[idx].Investment_Expense_fwa = fin_proj[t]['Forecast'].Reins[idx].Investment_Expense    

    # Other income refers to change in other liabilities (i.e. accrued interest)
    if t==0:
        fin_proj[t]['Forecast'].SFS_IS[idx].RCGL_ED = 0
        Def_Gain_Liab = run_control.GAAP_Reserve[run_control.GAAP_Reserve['I_LOB_ID'] == idx]['I_Def_Gain_Liab'].iloc[0]
        fin_proj[t]['Forecast'].SFS_IS[idx].Deferred_Gain_on_Reinsurance = fin_proj[t]['Forecast'].SFS[idx].GAAP_Reserve + \
                                                                           fin_proj[t]['Forecast'].SFS_IS[idx].UPR_EOP - \
                                                                           liab_proj_items.each_scaled_mva + \
                                                                           Def_Gain_Liab
        fin_proj[t]['Forecast'].SFS_IS[idx].Other_Income = 0
    else:
        BV_prev    = fin_proj[t-1]['Forecast'].Reins[idx].Total_STAT_reserve_EOP                                  ##BV is the total stat rsv here 
        BV_t       = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP
        average_BV = (BV_prev + BV_t) / 2.0
        total_BV   = fin_proj[t]['Forecast'].liability['dashboard'][idx].cashflow['BV asset backing liab'].sum()
        fin_proj[t]['Forecast'].SFS_IS[idx].Deferred_Gain_on_Reinsurance =  fin_proj[t-1]['Forecast'].SFS_IS[idx].Deferred_Gain_on_Reinsurance - \
                                                                            fin_proj[0]['Forecast'].SFS_IS[idx].Deferred_Gain_on_Reinsurance / total_BV * average_BV
        fin_proj[t]['Forecast'].SFS_IS[idx].Other_Income      = fin_proj[t]['Forecast'].SFS_IS[idx].Deferred_Gain_on_Reinsurance - fin_proj[t-1]['Forecast'].SFS_IS[idx].Deferred_Gain_on_Reinsurance
        fin_proj[t]['Forecast'].SFS_IS[idx].RCGL_ED           = fin_proj[t]['Forecast'].SFS_IS[idx].URCGL - fin_proj[t-1]['Forecast'].SFS_IS[idx].URCGL
    
    # Other
   # fin_proj[t]['Forecast'].SFS_IS[idx].Amort_deferred_gain = 0
    
    
    # Net income LOB
    fin_proj[t]['Forecast'].SFS_IS[idx].Income_before_Tax_LOB     \
    = fin_proj[t]['Forecast'].SFS_IS[idx].Net_underwriting_Profit \
    + fin_proj[t]['Forecast'].SFS_IS[idx].Operating_Expense       \
    + fin_proj[t]['Forecast'].SFS_IS[idx].NII_ABR_GAAP            \
    + fin_proj[t]['Forecast'].SFS_IS[idx].Investment_Expense_fwa  \
    + fin_proj[t]['Forecast'].SFS_IS[idx].RCGL_ED                 \
    + fin_proj[t]['Forecast'].SFS_IS[idx].Other_Income 

    fin_proj[t]['Forecast'].SFS_IS[idx].Income_Tax_LOB        = -run_control.proj_schedule[t]['Tax_Rate'] * fin_proj[t]['Forecast'].SFS_IS[idx].Income_before_Tax_LOB
    fin_proj[t]['Forecast'].SFS_IS[idx].Income_after_Tax_LOB  = fin_proj[t]['Forecast'].SFS_IS[idx].Income_before_Tax_LOB - fin_proj[t]['Forecast'].SFS_IS[idx].Income_Tax_LOB 
         

def run_GAAP_reserve(liab_proj_items, fin_proj, t, idx, each_GAAP_method, overall_GAAP_method):
    if t == 0:
        fin_proj[t]['Forecast'].SFS[idx].GAAP_Reserve            \
        = fin_proj[t]['Forecast'].SFS[idx].GAAP_Reserve_disc     \
        = fin_proj[t]['Forecast'].SFS[idx].GAAP_Reserve_rollfwd  \
        = liab_proj_items.GAAP_Reserve_disc
   
    else:
        Net_CF_t   = liab_proj_items.each_ncf
        GOE_t      = liab_proj_items.each_goe_f

        NII_t      = liab_proj_items.each_scaled_nii_abr + fin_proj[t]['Forecast'].Reins[idx].Chng_IMR            ##GAAP NII includes change in IMR
        BV_prev    = fin_proj[t-1]['Forecast'].Reins[idx].Total_STAT_reserve_EOP                                  ##BV is the total stat rsv here 
        BV_t       = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP
        average_BV = (BV_prev + BV_t) / 2.0
        '''
        GAAP_Margin_t = (liab_proj_items.GAAP_Reserve               \
                        + liab_proj_items.each_ncf.sum()            \
                        + liab_proj_items.each_goe_f.sum()          \
                        + liab_proj_items.each_scaled_nii_abr.sum() \
                        + fin_proj[t]['Forecast'].Reins[idx].Chng_IMR.sum())/liab_proj_items.each_scaled_bva.sum()
        '''
        return_period = IAL.Date.yearFrac("ACT/365",  fin_proj[t-1]['date'], fin_proj[t]['date'])         

        fin_proj[t]['Forecast'].SFS[idx].GAAP_Reserve_disc = liab_proj_items.GAAP_Reserve_disc
        fin_proj[t]['Forecast'].SFS[idx].GAAP_Margin       = liab_proj_items.GAAP_Margin
        fin_proj[t]['Forecast'].SFS[idx].GAAP_IRR          = liab_proj_items.GAAP_IRR

        
        fin_proj[t]['Forecast'].SFS[idx].GAAP_Reserve_rollfwd     \
        = fin_proj[t-1]['Forecast'].SFS[idx].GAAP_Reserve_rollfwd \
        + NII_t  + Net_CF_t + GOE_t - liab_proj_items.GAAP_Margin * average_BV * return_period        

        if each_GAAP_method == 'PC':
            fin_proj[t]['Forecast'].SFS[idx].GAAP_Reserve = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP * fin_proj[0]['Forecast'].SFS[idx].GAAP_Reserve / fin_proj[0]['Forecast'].Reins[idx].Total_STAT_reserve_EOP
        
        elif overall_GAAP_method == 'Product_Level' and each_GAAP_method == 'fixed_discount':
            fin_proj[t]['Forecast'].SFS[idx].GAAP_Reserve = fin_proj[t]['Forecast'].SFS[idx].GAAP_Reserve_disc

        else: #### roll-forward approach
            fin_proj[t]['Forecast'].SFS[idx].GAAP_Reserve =  fin_proj[t]['Forecast'].SFS[idx].GAAP_Reserve_rollfwd
                        
def run_Tax_forecast_LOB(liab_proj_items, fin_proj, t, idx, run_control): #### Taxable Income Calculation (Direct Method) ###

    LOB_line = fin_proj[t]['Forecast'].liability['dashboard'][idx].LOB_Def['PC_Life']
    Port_Name = fin_proj[t]['Forecast'].liability['dashboard'][idx].LOB_Def['Portfolio Name']
    
    if LOB_line == 'PC' or Port_Name == 'ALBA':
        tax_reserve_transfer = 1 
    else:
        tax_reserve_transfer = 0        
    
    if t == 0:
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_EOP  = liab_proj_items.each_scaled_tax_rsv
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_BOP  = fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_EOP

    else:
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_EOP  = liab_proj_items.each_scaled_tax_rsv
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_BOP  = fin_proj[t-1]['Forecast'].Tax_IS[idx].Tax_reserve_EOP
    
    if tax_reserve_transfer == 1:
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_basis_EOP    = fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_EOP
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_basis_BOP    = fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_BOP
    else:
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_basis_EOP    = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_basis_BOP    = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_BOP     
        
    
    fin_proj[t]['Forecast'].Tax_IS[idx].Premiums            = liab_proj_items.each_prem    
    fin_proj[t]['Forecast'].Tax_IS[idx].Total_Income        = liab_proj_items.each_prem


    fin_proj[t]['Forecast'].Tax_IS[idx].Death_Claims           = liab_proj_items.each_death    
    fin_proj[t]['Forecast'].Tax_IS[idx].Maturities             = liab_proj_items.each_maturity    
    fin_proj[t]['Forecast'].Tax_IS[idx].Surrender              = liab_proj_items.each_surrender    
    fin_proj[t]['Forecast'].Tax_IS[idx].Dividends              = liab_proj_items.each_cash_div    
    fin_proj[t]['Forecast'].Tax_IS[idx].Annuity_Claims         = liab_proj_items.each_annuity    
    fin_proj[t]['Forecast'].Tax_IS[idx].AH_Claims              = liab_proj_items.each_ah_ben    
    fin_proj[t]['Forecast'].Tax_IS[idx].PC_Claims              = liab_proj_items.each_gi_claim    
    fin_proj[t]['Forecast'].Tax_IS[idx].Commissions            = liab_proj_items.each_commission    
    fin_proj[t]['Forecast'].Tax_IS[idx].Premium_Tax            = liab_proj_items.each_prem_tax 
    fin_proj[t]['Forecast'].Tax_IS[idx].Chng_Taxbasis          = fin_proj[t]['Forecast'].Tax_IS[idx].Tax_basis_EOP - fin_proj[t]['Forecast'].Tax_IS[idx].Tax_basis_BOP
    fin_proj[t]['Forecast'].Tax_IS[idx].NII_ABR_USSTAT         = liab_proj_items.each_scaled_nii_abr + fin_proj[t]['Forecast'].Reins[idx].Chng_IMR
    fin_proj[t]['Forecast'].Tax_IS[idx].Investment_Expense_fwa = fin_proj[t]['Forecast'].Reins[idx].Investment_Expense

    fin_proj[t]['Forecast'].Tax_IS[idx].Total_Disbursement \
    = fin_proj[t]['Forecast'].Tax_IS[idx].Death_Claims     \
    + fin_proj[t]['Forecast'].Tax_IS[idx].Maturities       \
    + fin_proj[t]['Forecast'].Tax_IS[idx].Surrender        \
    + fin_proj[t]['Forecast'].Tax_IS[idx].Dividends        \
    + fin_proj[t]['Forecast'].Tax_IS[idx].Annuity_Claims   \
    + fin_proj[t]['Forecast'].Tax_IS[idx].AH_Claims        \
    + fin_proj[t]['Forecast'].Tax_IS[idx].PC_Claims        \
    + fin_proj[t]['Forecast'].Tax_IS[idx].Commissions      \
    + fin_proj[t]['Forecast'].Tax_IS[idx].Premium_Tax      \
    - fin_proj[t]['Forecast'].Tax_IS[idx].Chng_Taxbasis    

    ####################### TO BE CALCULATED zzzzzzzzzzzzzzzzzzzzzzzz                
    fin_proj[t]['Forecast'].Tax_IS[idx].Net_underwriting_Profit  \
    = fin_proj[t]['Forecast'].Tax_IS[idx].Total_Income           \
    + fin_proj[t]['Forecast'].Tax_IS[idx].Total_Disbursement

    # Combined operation expenses
    fin_proj[t]['Forecast'].Tax_IS[idx].Maint_Expense  = liab_proj_items.each_maint_exp    
    fin_proj[t]['Forecast'].Tax_IS[idx].GOE_F          = liab_proj_items.each_goe_f    
    fin_proj[t]['Forecast'].Tax_IS[idx].Operating_Expense = liab_proj_items.each_maint_exp + liab_proj_items.each_goe_f
 
    ## Added for Completeness. Placeholder - Further Enhancement required #####################################  
    fin_proj[t]['Forecast'].Tax_IS[idx].Tax_exempt_interest  = 0
    fin_proj[t]['Forecast'].Tax_IS[idx].DAC_cap_amort        = 0                                  

    fin_proj[t]['Forecast'].Tax_IS[idx].Income_before_Tax_LOB     \
    = fin_proj[t]['Forecast'].Tax_IS[idx].Net_underwriting_Profit \
    + fin_proj[t]['Forecast'].Tax_IS[idx].Operating_Expense       \
    + fin_proj[t]['Forecast'].Tax_IS[idx].NII_ABR_USSTAT          \
    + fin_proj[t]['Forecast'].Tax_IS[idx].Investment_Expense_fwa  \
    + fin_proj[t]['Forecast'].Tax_IS[idx].Other_Income 

    fin_proj[t]['Forecast'].Tax_IS[idx].Income_Tax_LOB        \
    = -run_control.proj_schedule[t]['Tax_Rate']               \
    * fin_proj[t]['Forecast'].Tax_IS[idx].Income_before_Tax_LOB
    
    fin_proj[t]['Forecast'].Tax_IS[idx].Income_after_Tax_LOB    \
    = fin_proj[t]['Forecast'].Tax_IS[idx].Income_before_Tax_LOB \
    - fin_proj[t]['Forecast'].Tax_IS[idx].Income_Tax_LOB 

def run_aggregation_forecast(fin_proj, t, idx, agg_level):    

    fin_proj[t]['Forecast'].Reins[agg_level]._aggregate(fin_proj[t]['Forecast'].Reins[idx])
    fin_proj[t]['Forecast'].EBS[agg_level]._aggregate(fin_proj[t]['Forecast'].EBS[idx], exceptions = ['FI_Dur'])
    fin_proj[t]['Forecast'].EBS_IS[agg_level]._aggregate(fin_proj[t]['Forecast'].EBS_IS[idx])
    ### Will be divided by FI MV in the main model
    fin_proj[t]['Forecast'].EBS[agg_level].FI_Dur += fin_proj[t]['Forecast'].EBS[idx].FI_Dur * fin_proj[t]['Forecast'].EBS[idx].FWA_MV_FI 

    fin_proj[t]['Forecast'].SFS[agg_level]._aggregate(fin_proj[t]['Forecast'].SFS[idx])
    fin_proj[t]['Forecast'].SFS_IS[agg_level]._aggregate(fin_proj[t]['Forecast'].SFS_IS[idx])

    fin_proj[t]['Forecast'].Tax_IS[agg_level]._aggregate(fin_proj[t]['Forecast'].Tax_IS[idx])
    
def run_BSCR_forecast(fin_proj, t, Asset_holding, Asset_adjustment, Regime, work_dir, run_control):
    Liab_LOB = fin_proj[t]['Forecast'].liability['dashboard']

    ##  PC Reserve Risk
    PC_Risk_calc     = BSCR_Calc.BSCR_PC_Reserve_Risk_Charge(Liab_LOB, method = "Bespoke")
    PC_Risk_calc_BMA = BSCR_Calc.BSCR_PC_Reserve_Risk_Charge(Liab_LOB, method = "BMA")
    fin_proj[t]['Forecast'].BSCR.update({ 'PC_Risk_calc_bespoke' : PC_Risk_calc})
    fin_proj[t]['Forecast'].BSCR.update({ 'PC_Risk_calc_BMA' : PC_Risk_calc_BMA})

    ##  LT Mortality Risk
    LT_Mort_calc     = BSCR_Calc.BSCR_Mortality_Risk_Charge(Liab_LOB, t)
    fin_proj[t]['Forecast'].BSCR.update({ 'LT_Mortality_Risk' : LT_Mort_calc})    
    
    ##  LT Longevity Risk    
    fin_proj[t]['Forecast'].BSCR.update({ 'LT_Longevity_Risk' : {}})    
    LT_Longevity_calc = BSCR_Calc.BSCR_Longevity_Risk_Charge(Liab_LOB, t, fin_proj[0]['date'], fin_proj[t]['date'], fin_proj[0]['Forecast'].BSCR['LT_Longevity_Risk'])
    fin_proj[t]['Forecast'].BSCR['LT_Longevity_Risk'] = LT_Longevity_calc

    ##  LT Morbidity Risk    
    LT_Morbidity_calc = BSCR_Calc.BSCR_Morbidity_Risk_Charge(Liab_LOB, t)
    fin_proj[t]['Forecast'].BSCR.update({ 'LT_Morbidity_Risk' : LT_Morbidity_calc})    

    ##  LT Other Insurance Risk    
    LT_Other_Ins_calc = BSCR_Calc.BSCR_Other_Ins_Risk_Charge(Liab_LOB)
    fin_proj[t]['Forecast'].BSCR.update({ 'LT_Other_Ins_Risk' : LT_Other_Ins_calc})    

    ##  LT Stop Loss Insurance Risk    
    LT_Stop_Loss_calc = BSCR_Calc.BSCR_Stoploss_Risk_Charge(Liab_LOB)
    fin_proj[t]['Forecast'].BSCR.update({ 'LT_Stop_Loss_Risk' : LT_Stop_Loss_calc})

    ##  LT Risers Insurance Risk    
    LT_Riders_calc = BSCR_Calc.BSCR_Riders_Risk_Charge(Liab_LOB)
    fin_proj[t]['Forecast'].BSCR.update({ 'LT_Riders_Risk' : LT_Riders_calc})

    ##  LT VA Insurance Risk    
    LT_VA_calc = BSCR_Calc.BSCR_VA_Risk_Charge(Liab_LOB)
    fin_proj[t]['Forecast'].BSCR.update({ 'LT_VA_Risk' : LT_VA_calc})

    fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].Reserve_Risk        = fin_proj[t]['Forecast'].BSCR['PC_Risk_calc_bespoke']['BSCR_Current']
    fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].Mortality_Risk      = fin_proj[t]['Forecast'].BSCR['LT_Mortality_Risk']['Total']['Mort_Risk']
    fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].StopLoss_Risk       = fin_proj[t]['Forecast'].BSCR['LT_Stop_Loss_Risk']['Total']['StopLoss_Risk']
    fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].Riders_Risk         = fin_proj[t]['Forecast'].BSCR['LT_Riders_Risk']['Total']['Riders_Risk']
    fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].Morbidity_Risk      = fin_proj[t]['Forecast'].BSCR['LT_Morbidity_Risk']['Total']['Morbidity_Risk']
    fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].Longevity_Risk      = fin_proj[t]['Forecast'].BSCR['LT_Longevity_Risk']['Total']['Longevity_Risk']
    fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].VA_Guarantee_Risk   = fin_proj[t]['Forecast'].BSCR['LT_VA_Risk']['Total']['VA_Risk']
    fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].OtherInsurance_Risk = fin_proj[t]['Forecast'].BSCR['LT_Other_Ins_Risk']['Total']['Other_Ins_Risk']

    fin_proj[t]['Forecast'].BSCR_Dashboard['GI'].Reserve_Risk        = fin_proj[t]['Forecast'].BSCR['PC_Risk_calc_bespoke']['BSCR_Current']
    fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].Mortality_Risk      = fin_proj[t]['Forecast'].BSCR['LT_Mortality_Risk']['Total']['Mort_Risk']
    fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].StopLoss_Risk       = fin_proj[t]['Forecast'].BSCR['LT_Stop_Loss_Risk']['Total']['StopLoss_Risk']
    fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].Riders_Risk         = fin_proj[t]['Forecast'].BSCR['LT_Riders_Risk']['Total']['Riders_Risk']
    fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].Morbidity_Risk      = fin_proj[t]['Forecast'].BSCR['LT_Morbidity_Risk']['Total']['Morbidity_Risk']
    fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].Longevity_Risk      = fin_proj[t]['Forecast'].BSCR['LT_Longevity_Risk']['Total']['Longevity_Risk']
    fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].VA_Guarantee_Risk   = fin_proj[t]['Forecast'].BSCR['LT_VA_Risk']['Total']['VA_Risk']
    fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].OtherInsurance_Risk = fin_proj[t]['Forecast'].BSCR['LT_Other_Ins_Risk']['Total']['Other_Ins_Risk']

    ##  LT Insurance Risk Aggregation
    LT_Agg_calc = BSCR_Calc.BSCR_LT_Ins_Risk_Aggregate(fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'])
    fin_proj[t]['Forecast'].BSCR.update({ 'LT_Agg_Risk' : LT_Agg_calc})

    fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].LT_Risk = fin_proj[t]['Forecast'].BSCR['LT_Agg_Risk']['BSCR_Current']
    fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].LT_Risk  = fin_proj[t]['Forecast'].BSCR['LT_Agg_Risk']['BSCR_Current']
       
    ## Fixed income, Equity, ALM, Currency, Concentration, Market and Total BSCR at time 0
    if t == 0:
        FI_calc = BSCR_Calc.BSCR_FI_Risk_Charge(Asset_holding, Asset_adjustment)
        fin_proj[t]['Forecast'].BSCR.update({ 'FI_Risk' : FI_calc})
        
        #        fin_proj[t]['Forecast'].EBS = Corp.run_EBS_base(fin_proj[t]['date'], fin_proj[t]['Forecast'].EBS, fin_proj[t]['Forecast'].liab_summary['base'], Asset_holding, Asset_adjustment, fin_proj[t]['Forecast'].SFS)        
        #        Out_put_EBS = dict((key, fin_proj[t]['Forecast'].EBS[key]) for key in ('Agg', 'LT', 'GI'))
        #        Corp.export_Dashboard(fin_proj[t]['date'], "Time_0", Out_put_EBS, fin_proj[t]['Forecast'].BSCR_Dashboard, 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\2018Q4', 'Current')
        
        #        ### Mannual DTA Input for the time being to calculate the equity BSCR ###
        #        fin_proj[t]['Forecast'].EBS['Agg'].DTA_DTL = 53424599.0139628
        #        fin_proj[t]['Forecast'].EBS['LT'].DTA_DTL = -48699948.3384355
        #        fin_proj[t]['Forecast'].EBS['GI'].DTA_DTL = 102124547.352397
        #        ### to be deleted once Forecaset EBS BS is built in ###
        
        Equity_calc = BSCR_Calc.BSCR_Equity_Risk_Charge(fin_proj[t]['Forecast'].EBS, Asset_holding, Asset_adjustment)
        fin_proj[t]['Forecast'].BSCR.update({ 'Equity_Risk' : Equity_calc})
        
        IR_calc = BSCR_Calc.BSCR_IR_Risk_Actual(fin_proj[t]['Forecast'].EBS, fin_proj[t]['Forecast'].liab_summary['base'])
        fin_proj[t]['Forecast'].BSCR.update({ 'Interest_Risk' : IR_calc})
                      
        Curr_calc = BSCR_Calc.BSCR_Ccy(Asset_holding, fin_proj[t]['Forecast'].liability['base'])
        fin_proj[t]['Forecast'].BSCR.update({ 'Currency_Risk' : Curr_calc})
        
        Con_calc = BSCR_Calc.BSCR_Con_Risk_Charge(fin_proj[t]['Forecast'].eval_date, fin_proj[t]['Forecast'].eval_date, Asset_holding, work_dir, Regime, Asset_adjustment)
        fin_proj[t]['Forecast'].BSCR.update({ 'Concentration_Risk' : Con_calc})

        Market_calc = BSCR_Calc.BSCR_Market_Risk_Charge(fin_proj[t]['Forecast'].BSCR, Regime)
        fin_proj[t]['Forecast'].BSCR.update({ 'Market_Risk' : Market_calc})
        
        fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].FI_Risk       = fin_proj[t]['Forecast'].BSCR['FI_Risk']['Agg']
        fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].FI_Risk        = fin_proj[t]['Forecast'].BSCR['FI_Risk']['LT']
        fin_proj[t]['Forecast'].BSCR_Dashboard['GI'].FI_Risk        = fin_proj[t]['Forecast'].BSCR['FI_Risk']['GI']
    
        fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].Equity_Risk   = fin_proj[t]['Forecast'].BSCR['Equity_Risk']['Agg']
        fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].Equity_Risk    = fin_proj[t]['Forecast'].BSCR['Equity_Risk']['LT']
        fin_proj[t]['Forecast'].BSCR_Dashboard['GI'].Equity_Risk    = fin_proj[t]['Forecast'].BSCR['Equity_Risk']['GI']
        
        fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].IR_Risk       = fin_proj[t]['Forecast'].BSCR['Interest_Risk']['Agg']
        fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].IR_Risk        = fin_proj[t]['Forecast'].BSCR['Interest_Risk']['LT']
        fin_proj[t]['Forecast'].BSCR_Dashboard['GI'].IR_Risk        = fin_proj[t]['Forecast'].BSCR['Interest_Risk']['GI']
       
        fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].Currency_Risk = fin_proj[t]['Forecast'].BSCR['Currency_Risk']['Agg']
        fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].Currency_Risk  = fin_proj[t]['Forecast'].BSCR['Currency_Risk']['LT']
        fin_proj[t]['Forecast'].BSCR_Dashboard['GI'].Currency_Risk  = fin_proj[t]['Forecast'].BSCR['Currency_Risk']['GI']
        
        fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].Concentration_Risk = fin_proj[t]['Forecast'].BSCR['Concentration_Risk']['Agg']
        fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].Concentration_Risk  = fin_proj[t]['Forecast'].BSCR['Concentration_Risk']['LT']
        fin_proj[t]['Forecast'].BSCR_Dashboard['GI'].Concentration_Risk  = fin_proj[t]['Forecast'].BSCR['Concentration_Risk']['GI']

        fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].Market_Risk   = fin_proj[t]['Forecast'].BSCR['Market_Risk']['Agg']
        fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].Market_Risk    = fin_proj[t]['Forecast'].BSCR['Market_Risk']['LT']
        fin_proj[t]['Forecast'].BSCR_Dashboard['GI'].Market_Risk    = fin_proj[t]['Forecast'].BSCR['Market_Risk']['GI']       
        
        accounts = ['LT', 'GI', 'Agg']
    
        for each_account in accounts:
            Agg_BSCR_calc = BSCR_Calc.BSCR_Aggregate(fin_proj[t]['Forecast'].BSCR_Dashboard[each_account], Regime, OpRiskCharge = BSCR_Cofig.BSCR_Charge['OpRiskCharge'])
            fin_proj[t]['Forecast'].BSCR.update({ 'Agg_BSCR' : Agg_BSCR_calc})
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].BSCR_Bef_Correlation  = Agg_BSCR_calc['BSCR_sum']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].Net_Market_Risk       = Agg_BSCR_calc['BSCR_Net_Market_Risk']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].Net_Credit_Risk       = Agg_BSCR_calc['Net_Credit_Risk']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].Net_PC_Insurance_Risk = Agg_BSCR_calc['Net_PC_Insurance_Risk']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].Net_LT_Insurance_Risk = Agg_BSCR_calc['Net_LT_Insurance_Risk']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].BSCR_Aft_Correlation  = Agg_BSCR_calc['BSCR_agg']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].OpRisk_Chage_pct      = Agg_BSCR_calc['OpRisk_Chage_pct']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].OpRisk_Chage          = Agg_BSCR_calc['OpRisk_Chage']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].BSCR_Bef_Tax_Adj      = Agg_BSCR_calc['BSCR_Bef_Tax_Adj']
            
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].Tax_Credit            = BSCR_Calc.BSCR_TaxCredit(fin_proj[t]['Forecast'].BSCR_Dashboard[each_account], fin_proj[t]['Forecast'].EBS[each_account], fin_proj[t]['Forecast'].liab_summary['base'][each_account], Regime)        
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].BSCR_Aft_Tax_Adj      = fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].BSCR_Bef_Tax_Adj - fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].Tax_Credit 
    
    else:
        ModCo_asset_proj    = run_control.asset_proj_modco_agg
        try:
            work_ModCo_FI_MV    = ModCo_asset_proj.loc[(ModCo_asset_proj['rowNo'] == t) & (ModCo_asset_proj['FI_Alts'] == 'FI'), 'MV'].values[0]
            work_ModCo_Alts_MV  = ModCo_asset_proj.loc[(ModCo_asset_proj['rowNo'] == t) & (ModCo_asset_proj['FI_Alts'] == 'Alts'), 'MV'].values[0]
            
            work_ModCo_dur       = ModCo_asset_proj.loc[(ModCo_asset_proj['rowNo'] == t) & (ModCo_asset_proj['FI_Alts'] == 'FI'), 'Dur'].values[0]
            work_ModCo_FI_charge = ModCo_asset_proj.loc[(ModCo_asset_proj['rowNo'] == t) & (ModCo_asset_proj['FI_Alts'] == 'FI'), 'risk_charge_factor'].values[0]        
            work_ModCo_Alts_charge  = ModCo_asset_proj.loc[(ModCo_asset_proj['rowNo'] == t) & (ModCo_asset_proj['FI_Alts'] == 'Alts'), 'risk_charge_factor'].values[0]        
        except:
            work_ModCo_FI_MV    = 0
            work_ModCo_Alts_MV  = 0
            work_ModCo_dur       = 0
            work_ModCo_FI_charge = 0        
            work_ModCo_Alts_charge  = 0        
        
            
        #### Placeholder for LPT - TBU based on EPA runs
        work_LPT_dur       = run_control.LPT_EPA_Dur.loc[t,'PC Mod Dur']
        work_LPT_FI_charge = 0.02
        work_LPT_Alts_charge  = 0.0

        #### Placeholder for LPT - TBU based on EPA runs
        work_Surplus_dur       = 5.32
        work_Surplus_FI_charge = 0.02
        work_Surplus_Alts_charge  = 0.2

        work_ModCo_total_MV = work_ModCo_FI_MV + work_ModCo_Alts_MV
        if work_ModCo_total_MV == 0:
            ### Kyle: was nan
            fin_proj[t]['Forecast'].EBS['LT'].FWA_MV_FI   = 0
            fin_proj[t]['Forecast'].EBS['LT'].FWA_MV_Alts = 0
        else:
            fin_proj[t]['Forecast'].EBS['LT'].FWA_MV_FI   = fin_proj[t]['Forecast'].EBS['LT'].FWA_MV * work_ModCo_FI_MV / work_ModCo_total_MV
            fin_proj[t]['Forecast'].EBS['LT'].FWA_MV_Alts = fin_proj[t]['Forecast'].EBS['LT'].FWA_MV * work_ModCo_Alts_MV / work_ModCo_total_MV        

        fin_proj[t]['Forecast'].EBS['GI'].FWA_MV_FI   = fin_proj[t]['Forecast'].EBS['GI'].FWA_MV
        fin_proj[t]['Forecast'].EBS['GI'].FWA_MV_Alts = 0

        fin_proj[t]['Forecast'].EBS['Agg'].FWA_MV_FI   = fin_proj[t]['Forecast'].EBS['LT'].FWA_MV_FI   + fin_proj[t]['Forecast'].EBS['GI'].FWA_MV_FI
        fin_proj[t]['Forecast'].EBS['Agg'].FWA_MV_Alts = fin_proj[t]['Forecast'].EBS['LT'].FWA_MV_Alts + fin_proj[t]['Forecast'].EBS['GI'].FWA_MV_Alts

        #### asset risk charge ####
        ModCo_FI_Risk   = fin_proj[t]['Forecast'].EBS['LT'].FWA_MV_FI   * work_ModCo_FI_charge
        ModCo_alts_Risk = fin_proj[t]['Forecast'].EBS['LT'].FWA_MV_Alts * work_ModCo_Alts_charge
        LPT_FI_Risk     = fin_proj[t]['Forecast'].EBS['GI'].FWA_MV_FI   * work_LPT_FI_charge ##### temporary setting #########
        LPT_alts_Risk   = fin_proj[t]['Forecast'].EBS['GI'].FWA_MV_Alts * work_LPT_Alts_charge

        LT_Surplus_FI_risk   = fin_proj[t]['Forecast'].EBS['LT'].Fixed_Inv_Surplus_bef_Div * work_Surplus_FI_charge##### temporary setting #########
        LT_Surplus_alts_risk = fin_proj[t]['Forecast'].EBS['LT'].Alts_Inv_Surplus * work_Surplus_Alts_charge ##### temporary setting #########        
        LT_LOC_DTA_risk      = (fin_proj[t]['Forecast'].EBS['LT'].LOC + fin_proj[t]['Forecast'].EBS['LT'].DTA_DTL)  * work_Surplus_Alts_charge ##### temporary setting #########        

        GI_Surplus_FI_risk   = fin_proj[t]['Forecast'].EBS['GI'].Fixed_Inv_Surplus_bef_Div * work_Surplus_FI_charge ##### temporary setting #########
        GI_Surplus_alts_risk = fin_proj[t]['Forecast'].EBS['GI'].Alts_Inv_Surplus * work_Surplus_Alts_charge ##### temporary setting #########        
        GI_LOC_DTA_risk      = (fin_proj[t]['Forecast'].EBS['GI'].LOC + fin_proj[t]['Forecast'].EBS['GI'].DTA_DTL)  * work_Surplus_Alts_charge ##### temporary setting #########        
        
        Agg_Surplus_FI_risk   = fin_proj[t]['Forecast'].EBS['Agg'].Fixed_Inv_Surplus_bef_Div * work_Surplus_FI_charge ##### temporary setting #########
        Agg_Surplus_alts_risk = fin_proj[t]['Forecast'].EBS['Agg'].Alts_Inv_Surplus * work_Surplus_Alts_charge ##### temporary setting #########        
        Agg_LOC_DTA_risk      = (fin_proj[t]['Forecast'].EBS['Agg'].LOC + fin_proj[t]['Forecast'].EBS['Agg'].DTA_DTL)  * work_Surplus_Alts_charge ##### temporary setting #########        

        fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].FI_Risk  = ModCo_FI_Risk + LT_Surplus_FI_risk
        fin_proj[t]['Forecast'].BSCR_Dashboard['GI'].FI_Risk  = LPT_FI_Risk + GI_Surplus_FI_risk
        fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].FI_Risk = ModCo_FI_Risk + LPT_FI_Risk + Agg_Surplus_FI_risk

        fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].Equity_Risk  = ModCo_alts_Risk + LT_Surplus_alts_risk + LT_LOC_DTA_risk
        fin_proj[t]['Forecast'].BSCR_Dashboard['GI'].Equity_Risk  = LPT_alts_Risk + GI_Surplus_alts_risk + GI_LOC_DTA_risk
        fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].Equity_Risk = ModCo_alts_Risk + LPT_alts_Risk + Agg_Surplus_alts_risk + Agg_LOC_DTA_risk

        #### Concentration Risk charge ####
        fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].Concentration_Risk   \
        = fin_proj[0]['Forecast'].BSCR_Dashboard['Agg'].Concentration_Risk \
        / fin_proj[0]['Forecast'].EBS['Agg'].Total_Invested_Assets         \
        * fin_proj[t]['Forecast'].EBS['Agg'].Total_Invested_Assets_bef_Div
        
        fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].Concentration_Risk   \
        = fin_proj[0]['Forecast'].BSCR_Dashboard['LT'].Concentration_Risk \
        / fin_proj[0]['Forecast'].EBS['LT'].Total_Invested_Assets         \
        * fin_proj[t]['Forecast'].EBS['LT'].Total_Invested_Assets_bef_Div
        
        fin_proj[t]['Forecast'].BSCR_Dashboard['GI'].Concentration_Risk   \
        = fin_proj[0]['Forecast'].BSCR_Dashboard['GI'].Concentration_Risk \
        / fin_proj[0]['Forecast'].EBS['GI'].Total_Invested_Assets         \
        * fin_proj[t]['Forecast'].EBS['GI'].Total_Invested_Assets_bef_Div

        #### ALM risk charge ####
        if fin_proj[t]['Forecast'].EBS['LT'].FWA_MV_FI + fin_proj[t]['Forecast'].EBS['LT'].Fixed_Inv_Surplus_bef_Div < 0.001:
            fin_proj[t]['Forecast'].EBS['LT'].FI_Dur = 0

        else:
            fin_proj[t]['Forecast'].EBS['LT'].FI_Dur \
            = (  fin_proj[t]['Forecast'].EBS['LT'].FWA_MV_FI * work_ModCo_dur   \
               + fin_proj[t]['Forecast'].EBS['LT'].Fixed_Inv_Surplus_bef_Div * work_Surplus_dur) \
              / (fin_proj[t]['Forecast'].EBS['LT'].FWA_MV_FI + fin_proj[t]['Forecast'].EBS['LT'].Fixed_Inv_Surplus_bef_Div )


        if fin_proj[t]['Forecast'].EBS['GI'].FWA_MV_FI + fin_proj[t]['Forecast'].EBS['GI'].Fixed_Inv_Surplus_bef_Div < 0.001:
            fin_proj[t]['Forecast'].EBS['GI'].FI_Dur = 0

        else:
            fin_proj[t]['Forecast'].EBS['GI'].FI_Dur \
            = (  fin_proj[t]['Forecast'].EBS['GI'].FWA_MV_FI * work_LPT_dur   \
               + fin_proj[t]['Forecast'].EBS['GI'].Fixed_Inv_Surplus_bef_Div * work_Surplus_dur ) \
              / (fin_proj[t]['Forecast'].EBS['GI'].FWA_MV_FI + fin_proj[t]['Forecast'].EBS['GI'].Fixed_Inv_Surplus_bef_Div )

        if fin_proj[t]['Forecast'].EBS['Agg'].FWA_MV_FI < 0.001:
            fin_proj[t]['Forecast'].EBS['Agg'].FI_Dur = 0
        else:
            fin_proj[t]['Forecast'].EBS['Agg'].FI_Dur \
            = (  fin_proj[t]['Forecast'].EBS['LT'].FWA_MV_FI                  * work_ModCo_dur     \
               + fin_proj[t]['Forecast'].EBS['GI'].FWA_MV_FI                  * work_LPT_dur       \
               + fin_proj[t]['Forecast'].EBS['Agg'].Fixed_Inv_Surplus_bef_Div * work_Surplus_dur ) \
              / (fin_proj[t]['Forecast'].EBS['Agg'].FWA_MV_FI + fin_proj[t]['Forecast'].EBS['Agg'].Fixed_Inv_Surplus_bef_Div)
        
        #### Populate Forecasting items for BSCR Dashboard ####
        ### Kyle: clean up some warnings
        for agg_lvl in ['LT', 'GI', 'Agg']:
            
            fin_proj[t]['Forecast'].BSCR_Dashboard[agg_lvl].IR_Risk   = BSCR_Calc.BSCR_IR_Risk(
                    fin_proj[t]['Forecast'].EBS[agg_lvl].FWA_MV_FI + fin_proj[t]['Forecast'].EBS[agg_lvl].Fixed_Inv_Surplus_bef_Div, 
                    fin_proj[t]['Forecast'].EBS[agg_lvl].FI_Dur, 
                    fin_proj[t]['Forecast'].liab_summary['dashboard'][agg_lvl]['PV_BE_net'],
                    fin_proj[t]['Forecast'].liab_summary['dashboard'][agg_lvl]['duration'])
            
            fin_proj[t]['Forecast'].BSCR_Dashboard[agg_lvl].DTA       = fin_proj[t]['Forecast'].EBS[agg_lvl].DTA_DTL
            fin_proj[t]['Forecast'].BSCR_Dashboard[agg_lvl].LOC       = fin_proj[t]['Forecast'].EBS[agg_lvl].LOC
            fin_proj[t]['Forecast'].BSCR_Dashboard[agg_lvl].FI_Dur    = fin_proj[t]['Forecast'].EBS[agg_lvl].FI_Dur
            fin_proj[t]['Forecast'].BSCR_Dashboard[agg_lvl].FI_MV     = fin_proj[t]['Forecast'].EBS[agg_lvl].FWA_MV_FI + fin_proj[t]['Forecast'].EBS[agg_lvl].Fixed_Inv_Surplus_bef_Div
            fin_proj[t]['Forecast'].BSCR_Dashboard[agg_lvl].Alts_MV   = fin_proj[t]['Forecast'].EBS[agg_lvl].FWA_MV_Alts + fin_proj[t]['Forecast'].EBS[agg_lvl].Alts_Inv_Surplus
            if fin_proj[t]['Forecast'].BSCR_Dashboard[agg_lvl].FI_MV  == 0:
                fin_proj[t]['Forecast'].BSCR_Dashboard[agg_lvl].Liab_Dur  = np.nan
            else:
                fin_proj[t]['Forecast'].BSCR_Dashboard[agg_lvl].Liab_Dur  = fin_proj[t]['Forecast'].liab_summary['dashboard'][agg_lvl]['duration'] * fin_proj[t]['Forecast'].liab_summary['dashboard'][agg_lvl]['PV_BE_net']/fin_proj[t]['Forecast'].BSCR_Dashboard[agg_lvl].FI_MV       
        
#        accounts = ['LT', 'GI', 'Agg']
        accounts = ['Agg']        
    
        for each_account in accounts:
            Agg_BSCR_calc = BSCR_Calc.BSCR_Aggregate(fin_proj[t]['Forecast'].BSCR_Dashboard[each_account], Regime, OpRiskCharge = BSCR_Cofig.BSCR_Charge['OpRiskCharge'])
            fin_proj[t]['Forecast'].BSCR.update({ 'Agg_BSCR' : Agg_BSCR_calc})
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].BSCR_Bef_Correlation  = Agg_BSCR_calc['BSCR_sum']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].Net_Market_Risk       = Agg_BSCR_calc['BSCR_Net_Market_Risk']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].Net_Credit_Risk       = Agg_BSCR_calc['Net_Credit_Risk']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].Net_PC_Insurance_Risk = Agg_BSCR_calc['Net_PC_Insurance_Risk']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].Net_LT_Insurance_Risk = Agg_BSCR_calc['Net_LT_Insurance_Risk']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].BSCR_Aft_Correlation  = Agg_BSCR_calc['BSCR_agg']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].OpRisk_Chage_pct      = Agg_BSCR_calc['OpRisk_Chage_pct']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].OpRisk_Chage          = Agg_BSCR_calc['OpRisk_Chage']
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].BSCR_Bef_Tax_Adj      = Agg_BSCR_calc['BSCR_Bef_Tax_Adj']
            
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].Tax_Credit            = BSCR_Calc.BSCR_TaxCredit(fin_proj[t]['Forecast'].BSCR_Dashboard[each_account], fin_proj[t]['Forecast'].EBS[each_account], fin_proj[t]['Forecast'].liab_summary['base'][each_account], Regime)        
            fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].BSCR_Aft_Tax_Adj      = fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].BSCR_Bef_Tax_Adj - fin_proj[t]['Forecast'].BSCR_Dashboard[each_account].Tax_Credit 


def run_Ins_Risk_forecast(proj_date, val_date_base, nested_proj_dates, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = 0, base_irCurve_GBP = 0, market_factor = [], liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term):
    PC_risk_forecast = BSCR_Calc.BSCR_PC_Risk_Forecast_RM("Bespoke", proj_date, val_date_base, nested_proj_dates, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = base_irCurve_USD, base_irCurve_GBP = base_irCurve_GBP, market_factor = market_factor, liab_spread_beta = liab_spread_beta, KRD_Term = KRD_Term)
    LT_risk_forecast = BSCR_Calc.BSCR_LT_Ins_Risk_Forecast_RM(proj_date, val_date_base, nested_proj_dates, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = base_irCurve_USD, base_irCurve_GBP = base_irCurve_GBP, market_factor = market_factor, liab_spread_beta = liab_spread_beta, KRD_Term = KRD_Term)
    
    return {'PC_risk_forecast' : PC_risk_forecast, 'LT_risk_forecast': LT_risk_forecast}

def run_RM_forecast(fin_proj, t, Recast_Risk_Margin, each_date, cf_proj_end_date, cash_flow_freq, valDate, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = 0, rf_curve = 0, base_irCurve_GBP = 0, market_factor = [], liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term):

    # Risk Margin Calculations
    nested_proj_dates = []
    if t == 0:
        nested_proj_dates.extend(list(pd.date_range(each_date, cf_proj_end_date, freq=cash_flow_freq)))
        ins_risk_forecast = run_Ins_Risk_forecast(each_date, valDate, nested_proj_dates, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD, base_irCurve_GBP)
        fin_proj[t]['Forecast'].BSCR.update(ins_risk_forecast)
        
    else:
        if Recast_Risk_Margin == 'N':
            fin_proj[t]['Forecast'].BSCR.update({'PC_risk_forecast': fin_proj[0]['Forecast'].BSCR['PC_risk_forecast']})
            fin_proj[t]['Forecast'].BSCR.update({'LT_risk_forecast': fin_proj[0]['Forecast'].BSCR['LT_risk_forecast']})            
        else:
            nested_proj_dates.extend(list(pd.date_range(each_date, cf_proj_end_date, freq=cash_flow_freq)))
            ins_risk_forecast = run_Ins_Risk_forecast(each_date, valDate, nested_proj_dates, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD, base_irCurve_GBP)
            fin_proj[t]['Forecast'].BSCR.update(ins_risk_forecast)

    ########### PC Risk Margin #############
    PC_methods_to_run = ['PC_CoC_Current', 'PC_CoC_New']
    for each_method in PC_methods_to_run:
        cf_period        = list(fin_proj[t]['Forecast'].BSCR['PC_risk_forecast'][each_method])
        cf_values        = fin_proj[t]['Forecast'].BSCR['PC_risk_forecast'][each_method].values()
        try:
            cf_current   = fin_proj[t]['Forecast'].BSCR['PC_risk_forecast'][each_method][dt.datetime.fromordinal(each_date.toordinal())]
        except:
            cf_current   = 0
        
        each_key = 'PC_RM_' + each_method
            
        cfHandle         = IAL.CF.createSimpleCFs(cf_period,cf_values)
        Risk_Margin_calc = IAL.CF.PVFromCurve(cfHandle, rf_curve, each_date, 0) - cf_current

        fin_proj[t]['Forecast'].BSCR.update({each_key : Risk_Margin_calc})

    ########### LT Risk Margin #############
    LT_methods_to_run = ['LT_CoC_Current', 'LT_CoC_New']
    for each_method in LT_methods_to_run:
        cf_period        = list(fin_proj[t]['Forecast'].BSCR['LT_risk_forecast'][each_method])
        cf_values        = fin_proj[t]['Forecast'].BSCR['LT_risk_forecast'][each_method].values()
    
        try:
            cf_current   = fin_proj[t]['Forecast'].BSCR['LT_risk_forecast'][each_method][dt.datetime.fromordinal(each_date.toordinal())]
        except:
            cf_current   = 0
        
        each_key = 'LT_RM_' + each_method
            
        cfHandle         = IAL.CF.createSimpleCFs(cf_period,cf_values)
        Risk_Margin_calc = IAL.CF.PVFromCurve(cfHandle, rf_curve, each_date, 0) - cf_current

        fin_proj[t]['Forecast'].BSCR.update({each_key : Risk_Margin_calc})
        
def run_LOC_forecast(fin_proj, t, run_control, agg_level = 'Agg'):

    loc_account = fin_proj[t]['Forecast'].LOC
    if t == 0:
        # Captial Ratio
        loc_account.tier2 = run_control.initial_LOC['Tier2']
        loc_account.tier3 = run_control.initial_LOC['Tier3']
        loc_account.Target_Capital = run_control.surplus_life_0 + run_control.surplus_PC_0
        
    else:
        loc_account.tier2 = fin_proj[t-1]['Forecast'].LOC.tier2_eligible
        loc_account.tier3 = fin_proj[t-1]['Forecast'].LOC.tier3_eligible
        loc_account.Target_Capital = fin_proj[t]['Forecast'].BSCR_Dashboard[agg_level].BSCR_Aft_Tax_Adj * run_control.proj_schedule[t]['Target_ECR_Ratio']
    
    loc_account.tier1_eligible = loc_account.Target_Capital - loc_account.tier2 - loc_account.tier3

    #   self.LOC_BMA_Limit            = {'Tier2':  0.667, 'Tier3_over_Tier1_2' :  0.1765, 'Tier3_over_Tier1' :  0.667 }
    loc_account.tier2_eligible = min(loc_account.tier2, loc_account.tier1_eligible * run_control.LOC_BMA_Limit['Tier2'])
    
    loc_account.tier3_eligible = min(loc_account.tier3, \
                                     (loc_account.tier1_eligible + loc_account.tier2_eligible) * run_control.LOC_BMA_Limit['Tier3_over_Tier1_2'], \
                                     loc_account.tier1_eligible * run_control.LOC_BMA_Limit['Tier3_over_Tier1'] - loc_account.tier2_eligible)

    loc_account.tier2and3_eligible = loc_account.tier2_eligible + loc_account.tier3_eligible 

    if run_control.LOC_SFS_Limit_YN == 'Y' and t > 0:
        loc_account.SFS_equity_BOP     = fin_proj[t-1]['Forecast'].SFS[agg_level].Total_Equity
        loc_account.SFS_limit_pct      = run_control.proj_schedule[t]['LOC_SFS_Limit']
        loc_account.SFS_limit          = loc_account.SFS_equity_BOP * loc_account.SFS_limit_pct
        loc_account.tier2and3_eligible = min(loc_account.tier2and3_eligible, loc_account.SFS_limit) # It should be linked to SFS_Agg 

    if t > 0:
        #### Set LOC account
        fin_proj[t]['Forecast'].EBS[agg_level].LOC    \
        = fin_proj[t]['Forecast'].SFS[agg_level].LOC  \
        = loc_account.tier2and3_eligible

def run_dividend_calculation(fin_proj, t, run_control, agg_level = 'Agg'):

    if t == 0:
        fin_proj[t]['Forecast'].EBS[agg_level].Target_Capital       = fin_proj[t]['Forecast'].BSCR_Dashboard[agg_level].BSCR_Aft_Tax_Adj * run_control.proj_schedule[t]['Target_ECR_Ratio']
        fin_proj[t]['Forecast'].EBS[agg_level].Dividend_Payment     = -(fin_proj[t]['Forecast'].EBS[agg_level].Capital_Surplus - fin_proj[t]['Forecast'].EBS[agg_level].LOC)
        #Kyle: some missing SFS values added here
        fin_proj[t]['Forecast'].SFS[agg_level].Alts_Inv_Surplus    = fin_proj[t]['Forecast'].EBS[agg_level].Alts_Inv_Surplus
        fin_proj[t]['Forecast'].SFS[agg_level].Fixed_Inv_Surplus    = fin_proj[t]['Forecast'].EBS[agg_level].Fixed_Inv_Surplus
        fin_proj[t]['Forecast'].SFS[agg_level].LOC                  = fin_proj[t]['Forecast'].EBS[agg_level].LOC
    else:
        fin_proj[t]['Forecast'].EBS[agg_level].Target_Capital       = fin_proj[t]['Forecast'].BSCR_Dashboard[agg_level].BSCR_Aft_Tax_Adj * run_control.proj_schedule[t]['Target_ECR_Ratio']

        #### dividend capacity 1 ####
        fin_proj[t]['Forecast'].EBS[agg_level].Div_Cap_SFS_CnS      = fin_proj[t-1]['Forecast'].SFS[agg_level].Total_Equity * run_control.Div_Cap_SFS_CnS
        #### dividend capacity 2 ####
        fin_proj[t]['Forecast'].EBS[agg_level].Div_Cap_SFS_Cap      = (fin_proj[t-1]['Forecast'].SFS[agg_level].Common_Stock + fin_proj[t]['Forecast'].SFS[agg_level].APIC) *run_control.Div_Cap_SFS_Cap
        #### dividend capacity 3 ####
        fin_proj[t]['Forecast'].EBS[agg_level].Div_Cap_SFS_Earnings = fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_after_Tax * run_control.proj_schedule[t]['div_earnings_pct']
        #### Dividend Capacity 4 = Excess EBS Capital over Target Capital ###
        fin_proj[t]['Forecast'].EBS[agg_level].Div_Cap_EBS_Excess    \
        = fin_proj[t-1]['Forecast'].EBS[agg_level].Capital_Surplus   \
        + fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_after_Tax \
        - fin_proj[t]['Forecast'].EBS[agg_level].Target_Capital      \
        + fin_proj[t]['Forecast'].EBS[agg_level].LTIC                \
        - fin_proj[t-1]['Forecast'].EBS[agg_level].LTIC              \
        + fin_proj[t]['Forecast'].EBS[agg_level].LOC                 \
        - fin_proj[t-1]['Forecast'].EBS[agg_level].LOC        

        if run_control.proj_schedule[t]['dividend_schedule'] == 'N':
            max_FI_div = fin_proj[t]['Forecast'].EBS[agg_level].Fixed_Inv_Surplus_bef_Div + max(0,fin_proj[t]['Forecast'].EBS[agg_level].Div_Cap_SFS_Earnings)
        else:
            max_FI_div = run_control.proj_schedule[t]['dividend_schedule_amt']

        if run_control.dividend_model == 'Aggregate capital target':
            work_divid_target_amt = fin_proj[t]['Forecast'].EBS[agg_level].Div_Cap_EBS_Excess
#            elif run_control.dividend_model == 'Earnings based':
#                work_divid_target_amt = fin_proj[t]['Forecast'].EBS[agg_level].Div_Cap_SFS_Earnings
        else:
            work_divid_target_amt = fin_proj[t]['Forecast'].EBS[agg_level].Div_Cap_SFS_Earnings

        if fin_proj[t]['Forecast'].EBS[agg_level].Target_Capital < 0.0001:
            final_dividend = min(max_FI_div, work_divid_target_amt)
        else:
            if run_control.div_SFSCapConstraint == 'Y':
                final_dividend = min(max_FI_div, work_divid_target_amt, fin_proj[t]['Forecast'].EBS[agg_level].Div_Cap_SFS_CnS, fin_proj[t]['Forecast'].EBS[agg_level].Div_Cap_SFS_Cap)
            elif run_control.div_LiquidityConstraint == 'Y':
                final_dividend = min(max(0, max_FI_div), work_divid_target_amt)
            else:
                final_dividend = work_divid_target_amt
                
            if run_control.DivFloorSwitch == 'Y':
                final_dividend = max(0, final_dividend)
                
        fin_proj[t]['Forecast'].EBS[agg_level].Dividend_Payment              = final_dividend
        fin_proj[t]['Forecast'].SFS[agg_level].Dividend_Payment              = final_dividend
        fin_proj[t]['Forecast'].EBS[agg_level].Fixed_Inv_Surplus             = fin_proj[t]['Forecast'].EBS[agg_level].Fixed_Inv_Surplus_bef_Div - fin_proj[t]['Forecast'].EBS[agg_level].Dividend_Payment
        fin_proj[t]['Forecast'].SFS[agg_level].Fixed_Inv_Surplus             = fin_proj[t]['Forecast'].EBS[agg_level].Fixed_Inv_Surplus
        fin_proj[t]['Forecast'].EBS[agg_level].Capital_Surplus               = fin_proj[t]['Forecast'].EBS[agg_level].Capital_Surplus_bef_Div - fin_proj[t]['Forecast'].EBS[agg_level].Dividend_Payment
        fin_proj[t]['Forecast'].EBS[agg_level].Total_Assets                  = fin_proj[t]['Forecast'].EBS[agg_level].Total_Assets_bef_Div - fin_proj[t]['Forecast'].EBS[agg_level].Dividend_Payment
        fin_proj[t]['Forecast'].EBS[agg_level].Total_Assets_excl_LOCs        = fin_proj[t]['Forecast'].EBS[agg_level].Total_Assets_excl_LOCs_bef_Div - fin_proj[t]['Forecast'].EBS[agg_level].Dividend_Payment
        fin_proj[t]['Forecast'].EBS[agg_level].Total_Invested_Assets         = fin_proj[t]['Forecast'].EBS[agg_level].Total_Invested_Assets_bef_Div - fin_proj[t]['Forecast'].EBS[agg_level].Dividend_Payment
        fin_proj[t]['Forecast'].EBS[agg_level].Total_Liab_Econ_Capital_Surplus = fin_proj[t]['Forecast'].EBS[agg_level].Total_Liab_Econ_Capital_Surplus_bef_Div - fin_proj[t]['Forecast'].EBS[agg_level].Dividend_Payment

#def run_EBS_Corp_forecast(fin_proj, t, agg_level):  # EBS Items calculated at overall level    
#    
#    # Override risk margin and technical provision based on the recalculated numbers
#    if agg_level == 'LT':
#        fin_proj[t]['Forecast'].EBS[agg_level].Risk_Margin = fin_proj[t]['Forecast'].BSCR['LT_RM_LT_CoC_Current']
#
#    elif agg_level == 'GI':
#        fin_proj[t]['Forecast'].EBS[agg_level].Risk_Margin = fin_proj[t]['Forecast'].BSCR['PC_RM_PC_CoC_Current']
#
#    else:
#        fin_proj[t]['Forecast'].EBS[agg_level].Risk_Margin = fin_proj[t]['Forecast'].BSCR['LT_RM_LT_CoC_Current'] + fin_proj[t]['Forecast'].BSCR['PC_RM_PC_CoC_Current']
#
#
#    fin_proj[t]['Forecast'].EBS[agg_level].Technical_Provision = fin_proj[t]['Forecast'].EBS[agg_level].PV_BE + fin_proj[t]['Forecast'].EBS[agg_level].Risk_Margin
#    fin_proj[t]['Forecast'].EBS[agg_level].Total_Invested_Assets = fin_proj[t]['Forecast'].EBS[agg_level].Fixed_Inv_Surplus + fin_proj[t]['Forecast'].EBS[agg_level].Alts_Inv_Surplus

def roll_forward_surplus_assets(fin_proj, t, agg_level, valDate, run_control, curveType = 'Treasury', base_irCurve_USD = 0 ):
    
    """
    Notice: This function is actually not run at time = 0
    """
    
    
    Coupon_Surplus_Alt = run_control.ML_III_inputs.loc[t, 'Earnings on ML III']    
    MtM_Surplus_Alt    = run_control.ML_III_inputs.loc[t, 'MtM Return']
    Redemp_Surplus_Alt = run_control.ML_III_inputs.loc[t, 'ML III Redemption']
    NII_alt            = Coupon_Surplus_Alt + MtM_Surplus_Alt
    LT_alt_pct         = run_control.ML_III_inputs.loc[t, 'MLIII LR Allocation']
    
    fin_proj[t]['Forecast'].EBS[agg_level].Alts_Inv_Surplus   \
    = fin_proj[t]['Forecast'].SFS[agg_level].Alts_Inv_Surplus \
    = run_control.ML_III_inputs.loc[t, 'ML III MV']

    FI_Surplus_fee     = -run_control.inv_mgmt_fee['Surplus_FI'] 
    Alt_Surplus_fee    = -run_control.inv_mgmt_fee['Surplus_Alt']
    work_LOC_fee       = -run_control.proj_schedule[t]['LOC_fee']      
    
    if t > 0:
        work_return_period = IAL.Date.yearFrac("ACT/365",  fin_proj[t-1]['date'], fin_proj[t]['date'])

        # Fixed Income Surplus

        FI_Surplus_yield  = IAL_App.FI_Yield_Model_Port(curve_base_date = valDate, 
                                                        eval_date = fin_proj[t-1]['date'], 
                                                        model_port = run_control.FI_Surplus_model_port, 
                                                        initial_spread = run_control.initial_spread, 
                                                        ultimate_spread = run_control.ultimate_spread, 
                                                        ultimate_period = run_control.ultimate_period, 
                                                        curveType = curveType, 
                                                        base_irCurve_USD = base_irCurve_USD)
        work_net_yield    = FI_Surplus_yield + FI_Surplus_fee
        work_net_NII      = fin_proj[t-1]['Forecast'].EBS[agg_level].Fixed_Inv_Surplus * ( np.exp( work_net_yield * work_return_period ) -1 )
        work_gross_NII    = work_net_NII * FI_Surplus_yield / work_net_yield
        work_inv_fee      = work_net_NII * FI_Surplus_fee   / work_net_yield

        fin_proj[t]['Forecast'].EBS_IS[agg_level].Yield_Surplus_FI   \
        = fin_proj[t]['Forecast'].SFS_IS[agg_level].Yield_Surplus_FI \
        = fin_proj[t]['Forecast'].Tax_IS[agg_level].Yield_Surplus_FI   \
        = FI_Surplus_yield

        fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_Surplus_FI \
        = fin_proj[t]['Forecast'].SFS_IS[agg_level].NII_Surplus_FI \
        = fin_proj[t]['Forecast'].Tax_IS[agg_level].NII_Surplus_FI \
        = work_gross_NII

        fin_proj[t]['Forecast'].EBS_IS[agg_level].Investment_Expense_Surplus_FI \
        = fin_proj[t]['Forecast'].SFS_IS[agg_level].Investment_Expense_Surplus_FI \
        = fin_proj[t]['Forecast'].Tax_IS[agg_level].Investment_Expense_Surplus_FI \
        = work_inv_fee

        # Alts Surplus return and cash flows
        if agg_level == 'LT':
            fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_Surplus_Alt            \
            = fin_proj[t]['Forecast'].SFS_IS[agg_level].NII_Surplus_Alt          \
            = fin_proj[t]['Forecast'].Tax_IS[agg_level].NII_Surplus_Alt  \
            = NII_alt * LT_alt_pct
            
            fin_proj[t]['Forecast'].EBS_IS[agg_level].Coupon_Surplus_Alt           \
            = fin_proj[t]['Forecast'].SFS_IS[agg_level].Coupon_Surplus_Alt         \
            = fin_proj[t]['Forecast'].Tax_IS[agg_level].Coupon_Surplus_Alt \
            = Coupon_Surplus_Alt * LT_alt_pct
            
            fin_proj[t]['Forecast'].EBS_IS[agg_level].MtM_Surplus_Alt              \
            = fin_proj[t]['Forecast'].SFS_IS[agg_level].MtM_Surplus_Alt            \
            = fin_proj[t]['Forecast'].Tax_IS[agg_level].MtM_Surplus_Alt    \
            = MtM_Surplus_Alt * LT_alt_pct
            
            fin_proj[t]['Forecast'].EBS_IS[agg_level].Redemp_Surplus_Alt           \
            = fin_proj[t]['Forecast'].SFS_IS[agg_level].Redemp_Surplus_Alt         \
            = fin_proj[t]['Forecast'].Tax_IS[agg_level].Redemp_Surplus_Alt \
            = Redemp_Surplus_Alt * LT_alt_pct
    
        elif agg_level == 'GI':
            fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_Surplus_Alt            \
            = fin_proj[t]['Forecast'].SFS_IS[agg_level].NII_Surplus_Alt          \
            = fin_proj[t]['Forecast'].Tax_IS[agg_level].NII_Surplus_Alt  \
            = NII_alt * (1 - LT_alt_pct)
            
            fin_proj[t]['Forecast'].EBS_IS[agg_level].Coupon_Surplus_Alt           \
            = fin_proj[t]['Forecast'].SFS_IS[agg_level].Coupon_Surplus_Alt         \
            = fin_proj[t]['Forecast'].Tax_IS[agg_level].Coupon_Surplus_Alt \
            = Coupon_Surplus_Alt * (1 - LT_alt_pct)
            
            fin_proj[t]['Forecast'].EBS_IS[agg_level].MtM_Surplus_Alt              \
            = fin_proj[t]['Forecast'].SFS_IS[agg_level].MtM_Surplus_Alt            \
            = fin_proj[t]['Forecast'].Tax_IS[agg_level].MtM_Surplus_Alt    \
            = MtM_Surplus_Alt * (1 - LT_alt_pct)
            
            fin_proj[t]['Forecast'].EBS_IS[agg_level].Redemp_Surplus_Alt \
            = fin_proj[t]['Forecast'].SFS_IS[agg_level].Redemp_Surplus_Alt \
            = fin_proj[t]['Forecast'].Tax_IS[agg_level].Redemp_Surplus_Alt \
            = Redemp_Surplus_Alt * (1 - LT_alt_pct)
    
        else:
            fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_Surplus_Alt            \
            = fin_proj[t]['Forecast'].SFS_IS[agg_level].NII_Surplus_Alt          \
            = fin_proj[t]['Forecast'].Tax_IS[agg_level].NII_Surplus_Alt  \
            = NII_alt 
            
            fin_proj[t]['Forecast'].EBS_IS[agg_level].Coupon_Surplus_Alt \
            = fin_proj[t]['Forecast'].SFS_IS[agg_level].Coupon_Surplus_Alt \
            = fin_proj[t]['Forecast'].Tax_IS[agg_level].Coupon_Surplus_Alt \
            = Coupon_Surplus_Alt 
            
            fin_proj[t]['Forecast'].EBS_IS[agg_level].MtM_Surplus_Alt    \
            = fin_proj[t]['Forecast'].SFS_IS[agg_level].MtM_Surplus_Alt    \
            = fin_proj[t]['Forecast'].Tax_IS[agg_level].MtM_Surplus_Alt    \
            = MtM_Surplus_Alt 
            
            fin_proj[t]['Forecast'].EBS_IS[agg_level].Redemp_Surplus_Alt \
            = fin_proj[t]['Forecast'].SFS_IS[agg_level].Redemp_Surplus_Alt \
            = fin_proj[t]['Forecast'].Tax_IS[agg_level].Redemp_Surplus_Alt \
            = Redemp_Surplus_Alt

        # Alts Surplus Inv mgmt fee
        work_inv_fee_alt \
        = Alt_Surplus_fee \
        * (fin_proj[t-1]['Forecast'].EBS[agg_level].Alts_Inv_Surplus + fin_proj[t]['Forecast'].EBS[agg_level].Alts_Inv_Surplus) /2 \
        * work_return_period

        fin_proj[t]['Forecast'].EBS_IS[agg_level].Investment_Expense_Surplus_alt \
        = fin_proj[t]['Forecast'].SFS_IS[agg_level].Investment_Expense_Surplus_alt \
        = fin_proj[t]['Forecast'].Tax_IS[agg_level].Investment_Expense_Surplus_alt \
        = work_inv_fee_alt

        # LOC Cost
        work_LOC_cost = work_return_period * fin_proj[t-1]['Forecast'].EBS[agg_level].LOC * work_LOC_fee

        fin_proj[t]['Forecast'].EBS_IS[agg_level].LOC_cost   \
        = fin_proj[t]['Forecast'].SFS_IS[agg_level].LOC_cost \
        = fin_proj[t]['Forecast'].Tax_IS[agg_level].LOC_cost \
        = work_LOC_cost

    #### Simple Sum Items
    fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_Surplus \
    = fin_proj[t]['Forecast'].SFS_IS[agg_level].NII_Surplus \
    = fin_proj[t]['Forecast'].Tax_IS[agg_level].NII_Surplus \
    = fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_Surplus_Alt + fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_Surplus_FI

    fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_tot \
    = fin_proj[t]['Forecast'].SFS_IS[agg_level].NII_tot \
    = fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_Surplus + fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_ABR_GAAP

    fin_proj[t]['Forecast'].Tax_IS[agg_level].NII_tot \
    = fin_proj[t]['Forecast'].Tax_IS[agg_level].NII_Surplus + fin_proj[t]['Forecast'].Tax_IS[agg_level].NII_ABR_USSTAT

    fin_proj[t]['Forecast'].EBS_IS[agg_level].Investment_Expense_Surplus \
    = fin_proj[t]['Forecast'].SFS_IS[agg_level].Investment_Expense_Surplus \
    = fin_proj[t]['Forecast'].Tax_IS[agg_level].Investment_Expense_Surplus \
    = fin_proj[t]['Forecast'].EBS_IS[agg_level].Investment_Expense_Surplus_FI + fin_proj[t]['Forecast'].EBS_IS[agg_level].Investment_Expense_Surplus_alt

    fin_proj[t]['Forecast'].EBS_IS[agg_level].Investment_Expense_tot       \
    = fin_proj[t]['Forecast'].SFS_IS[agg_level].Investment_Expense_tot     \
    = fin_proj[t]['Forecast'].SFS_IS[agg_level].Investment_Expense_tot     \
    = fin_proj[t]['Forecast'].EBS_IS[agg_level].Investment_Expense_Surplus \
    + fin_proj[t]['Forecast'].EBS_IS[agg_level].Investment_Expense_fwa

    fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_before_Tax_Surplus    \
    = fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_before_Tax_Surplus  \
    = fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_before_Tax_Surplus  \
    = fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_Surplus                \
    + fin_proj[t]['Forecast'].EBS_IS[agg_level].Investment_Expense_Surplus \
    + fin_proj[t]['Forecast'].EBS_IS[agg_level].LOC_cost   

    fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_Tax_Surplus           \
    = fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_Tax_Surplus         \
    = fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_Tax_Surplus         \
    = -run_control.proj_schedule[t]['Tax_Rate'] * fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_before_Tax_Surplus

    fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_after_Tax_Surplus           \
    = fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_after_Tax_Surplus           \
    = fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_after_Tax_Surplus           \
    = fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_before_Tax_Surplus + fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_Tax_Surplus

    fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_before_Tax            \
    = fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_before_Tax_LOB      \
    + fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_before_Tax_Surplus      

    fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_Tax            \
    = fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_Tax_LOB      \
    + fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_Tax_Surplus      

    fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_after_Tax            \
    = fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_after_Tax_LOB      \
    + fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_after_Tax_Surplus      

    fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_before_Tax            \
    = fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_before_Tax_LOB      \
    + fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_before_Tax_Surplus      

    fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_Tax            \
    = fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_Tax_LOB      \
    + fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_Tax_Surplus      

    fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_after_Tax            \
    = fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_after_Tax_LOB      \
    + fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_after_Tax_Surplus      


    fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_before_Tax            \
    = fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_before_Tax_LOB      \
    + fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_before_Tax_Surplus      

    fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_Tax            \
    = fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_Tax_LOB      \
    + fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_Tax_Surplus      

    fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_after_Tax            \
    = fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_after_Tax_LOB      \
    + fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_after_Tax_Surplus      

    # Change in DTA/DTL
    fin_proj[t]['Forecast'].EBS_IS[agg_level].DTA_Change    \
    = fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_Tax  \
    - fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_Tax

    fin_proj[t]['Forecast'].EBS[agg_level].DTA_DTL          \
    = fin_proj[t-1]['Forecast'].EBS[agg_level].DTA_DTL        \
    + fin_proj[t]['Forecast'].EBS_IS[agg_level].DTA_Change

    fin_proj[t]['Forecast'].SFS_IS[agg_level].DTA_Change    \
    = fin_proj[t]['Forecast'].SFS_IS[agg_level].Income_Tax  \
    - fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_Tax

    fin_proj[t]['Forecast'].SFS[agg_level].DTA_DTL          \
    = fin_proj[t-1]['Forecast'].SFS[agg_level].DTA_DTL        \
    + fin_proj[t]['Forecast'].SFS_IS[agg_level].DTA_Change


    # Balance sheet: Assets
    if t == 0:
        ####Kyle: the whole function is skipped at t=0
        ####      the actual result comes from Lib_Corp_Model run_EBS_base
        fin_proj[t]['Forecast'].EBS[agg_level].Fixed_Inv_Surplus   \
        = fin_proj[t]['Forecast'].SFS[agg_level].Fixed_Inv_Surplus \
        = run_control.I_SFSLiqSurplus + fin_proj[t]['Forecast'].EBS[agg_level].GOE_Provision 
        ####Should be set equal to the input I_SFSLiqSurplus from tab "I___Control" PLUS GOE provision
        #### Hard-coded in config
    else:
        fin_proj[t]['Forecast'].EBS[agg_level].Fixed_Inv_Surplus_bef_Div        \
        = fin_proj[t-1]['Forecast'].EBS[agg_level].Fixed_Inv_Surplus            \
        + fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_Surplus_FI              \
        + fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_Surplus_Alt             \
        + fin_proj[t]['Forecast'].EBS_IS[agg_level].Investment_Expense_Surplus  \
        + fin_proj[t]['Forecast'].EBS_IS[agg_level].Redemp_Surplus_Alt          \
        + fin_proj[t]['Forecast'].Reins[agg_level].Net_payment_toReins          \
        + fin_proj[t]['Forecast'].EBS_IS[agg_level].GOE_F                       \
        + fin_proj[t]['Forecast'].EBS_IS[agg_level].LOC_cost                    \
        + fin_proj[t]['Forecast'].Tax_IS[agg_level].Income_Tax
        
        #### Roll LOC based on the previous amount -----> need to check the sequence with BSCR calculation
        fin_proj[t]['Forecast'].EBS[agg_level].LOC      \
        = fin_proj[t]['Forecast'].EBS[agg_level].LOC    \
        = fin_proj[t]['Forecast'].SFS[agg_level].LOC    \
        = fin_proj[t-1]['Forecast'].EBS[agg_level].LOC   
       

    fin_proj[t]['Forecast'].EBS[agg_level].Total_Invested_Assets_bef_Div \
    = fin_proj[t]['Forecast'].EBS[agg_level].Total_Invested_Assets_LOB   \
    + fin_proj[t]['Forecast'].EBS[agg_level].Fixed_Inv_Surplus_bef_Div   \
    + fin_proj[t]['Forecast'].EBS[agg_level].Alts_Inv_Surplus
    

    fin_proj[t]['Forecast'].EBS[agg_level].Other_Assets    \
    = fin_proj[t]['Forecast'].EBS[agg_level].LTIC          \
    + fin_proj[t]['Forecast'].EBS[agg_level].LOC           \
    + fin_proj[t]['Forecast'].EBS[agg_level].DTA_DTL       

    fin_proj[t]['Forecast'].EBS[agg_level].Total_Assets_bef_Div            \
    = fin_proj[t]['Forecast'].EBS[agg_level].Total_Invested_Assets_bef_Div \
    + fin_proj[t]['Forecast'].EBS[agg_level].Other_Assets

    fin_proj[t]['Forecast'].EBS[agg_level].Total_Assets_excl_LOCs_bef_Div \
    = fin_proj[t]['Forecast'].EBS[agg_level].Total_Assets_bef_Div         \
    - fin_proj[t]['Forecast'].EBS[agg_level].LOC

    fin_proj[t]['Forecast'].EBS[agg_level].Capital_Surplus_bef_Div \
    = fin_proj[t]['Forecast'].EBS[agg_level].Total_Assets_bef_Div  \
    - fin_proj[t]['Forecast'].EBS[agg_level].Total_Liabilities
    
    fin_proj[t]['Forecast'].EBS[agg_level].Total_Liab_Econ_Capital_Surplus_bef_Div \
    = fin_proj[t]['Forecast'].EBS[agg_level].Capital_Surplus_bef_Div             \
    + fin_proj[t]['Forecast'].EBS[agg_level].Total_Liabilities
