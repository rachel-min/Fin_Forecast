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

def load_excel_input(fin_proj, attr_name, file_name, work_dir, index_col = None):
    curr_dir = os.getcwd()
    os.chdir(work_dir)
    inputs = pd.read_excel(file_name, index_col = index_col)
    os.chdir(curr_dir)
    for t in fin_proj.keys():
        setattr(fin_proj[t]['Forecast'], attr_name, inputs)
    print(attr_name, 'information loaded.')
    
### (Kyle) This will be removed in the future
def load_control_input(fin_proj, file_name, work_dir, index_col = None):
    curr_dir = os.getcwd()
    os.chdir(work_dir)
    inputs = pd.read_excel(file_name, index_col = index_col)
    os.chdir(curr_dir)
    for t in fin_proj.keys():
        setattr(fin_proj[t]['Forecast'], '_control_input', inputs.iloc[:,0])
    print('Control information loaded.')


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
        
def run_fin_forecast(fin_proj, proj_t, numOfLoB, proj_cash_flows, Asset_holding, Asset_adjustment, run_control):
     
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
            run_Tax_forecast(items, fin_proj, t, idx)   ### Tax forecast will be added later
            
            ### Aggregation
            clsLiab    = proj_cash_flows[idx]
            each_lob   = clsLiab.get_LOB_Def('Agg LOB')
            
            if each_lob == "LR":                
                run_aggregation_forecast(fin_proj, t, idx, 'LT')
                
            else: 
                run_aggregation_forecast(fin_proj, t, idx, 'GI')
                
            #           Aggregate Account
            run_aggregation_forecast(fin_proj, t, idx, 'Agg')
            
        fin_proj[t]['Forecast'].Agg_items = {}
        fin_proj[t]['Forecast'].Agg_items['Agg'] = roll_fwd_items(fin_proj, t, 'Agg')
        fin_proj[t]['Forecast'].Agg_items['LT'] = roll_fwd_items(fin_proj, t, 'LT', surplus_split = fin_proj[t]['Forecast'].surplus_split.loc[t, 'Surplus Life'])
        fin_proj[t]['Forecast'].Agg_items['GI'] = roll_fwd_items(fin_proj, t, 'GI', surplus_split = fin_proj[t]['Forecast'].surplus_split.loc[t, 'Surplus P&C'])

        #####   BSCR Calculations ##################
        run_BSCR_forecast(fin_proj, t, Asset_holding, Asset_adjustment)
        run_LOC_forecast(fin_proj, t)
        run_EBS_Corp_forecast(fin_proj, t, 'Agg', run_control)
        run_SFS_Corp_forecast(fin_proj, t, 'Agg')
        

def run_reins_settlement_forecast(items, fin_proj, t, idx): #### Reinsurance Settlement Class

    # Balances
    # Add special condition t = 0 ################### Kyle Modified on 9/29/2019
    if t == 0:
        fin_proj[t]['Forecast'].Reins[idx].Net_STAT_reserve_EOP = items.each_scaled_stat_rsv
        fin_proj[t]['Forecast'].Reins[idx].Net_STAT_reserve_BOP = items.each_scaled_stat_rsv
        fin_proj[t]['Forecast'].Reins[idx].CFT_reserve_EOP      = items.each_cft_rsv
        fin_proj[t]['Forecast'].Reins[idx].CFT_reserve_BOP      = items.each_cft_rsv
        fin_proj[t]['Forecast'].Reins[idx].UPR_EOP              = items.each_upr
        fin_proj[t]['Forecast'].Reins[idx].UPR_BOP              = items.each_upr
        fin_proj[t]['Forecast'].Reins[idx].IMR_EOP              = items.each_imr
        fin_proj[t]['Forecast'].Reins[idx].IMR_BOP              = items.each_imr
        fin_proj[t]['Forecast'].Reins[idx].PL_balance_EOP       = 0 ##Policy Loan Balance need to be pulled in##
        fin_proj[t]['Forecast'].Reins[idx].PL_balance_BOP       = 0 ##Policy Loan Balance need to be pulled in##
        fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP = items.each_scaled_total_stat_rsv
        fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_BOP = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP
        fin_proj[t]['Forecast'].Reins[idx].Total_MV_EOP         = items.each_scaled_mva
        fin_proj[t]['Forecast'].Reins[idx].Total_MV_BOP         = fin_proj[t]['Forecast'].Reins[idx].Total_MV_EOP
        
    else:
        fin_proj[t]['Forecast'].Reins[idx].Net_STAT_reserve_EOP = items.each_scaled_stat_rsv
        fin_proj[t]['Forecast'].Reins[idx].Net_STAT_reserve_BOP = fin_proj[t-1]['Forecast'].Reins[idx].Net_STAT_reserve_EOP
        fin_proj[t]['Forecast'].Reins[idx].CFT_reserve_EOP      = items.each_cft_rsv
        fin_proj[t]['Forecast'].Reins[idx].CFT_reserve_BOP      = fin_proj[t-1]['Forecast'].Reins[idx].CFT_reserve_EOP
        fin_proj[t]['Forecast'].Reins[idx].UPR_EOP              = items.each_upr
        fin_proj[t]['Forecast'].Reins[idx].UPR_BOP              = fin_proj[t-1]['Forecast'].Reins[idx].UPR_EOP
        fin_proj[t]['Forecast'].Reins[idx].IMR_EOP              = items.each_imr
        fin_proj[t]['Forecast'].Reins[idx].IMR_BOP              = fin_proj[t-1]['Forecast'].Reins[idx].IMR_EOP
        fin_proj[t]['Forecast'].Reins[idx].PL_balance_EOP       = 0 ##Policy Loan Balance need to be pulled in##
        fin_proj[t]['Forecast'].Reins[idx].PL_balance_BOP       = fin_proj[t-1]['Forecast'].Reins[idx].PL_balance_EOP ##Policy Loan Balance need to be pulled in##
        fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP = items.each_scaled_total_stat_rsv
        fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_BOP = fin_proj[t-1]['Forecast'].Reins[idx].Total_STAT_reserve_EOP
        fin_proj[t]['Forecast'].Reins[idx].Total_MV_EOP         = items.each_scaled_mva
        fin_proj[t]['Forecast'].Reins[idx].Total_MV_BOP         = fin_proj[t-1]['Forecast'].Reins[idx].Total_MV_EOP
        
    ## Added for Validation but need to be removed from Q2 2019    #####################
    if idx in [35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45] and t != 0:
        fin_proj[t]['Forecast'].Reins[idx].Investment_expense   = (fin_proj[t]['Forecast'].Reins[idx].Total_MV_BOP + fin_proj[t]['Forecast'].Reins[idx].Total_MV_EOP) * 0.5 * (0 - 0.0015)
    else:
        fin_proj[t]['Forecast'].Reins[idx].Investment_expense   = 0

    # Revenues                        
    fin_proj[t]['Forecast'].Reins[idx].Premiums            = items.each_prem
    fin_proj[t]['Forecast'].Reins[idx].PL_interest         = 0.05 * ((fin_proj[t]['Forecast'].Reins[idx].PL_balance_BOP + fin_proj[t]['Forecast'].Reins[idx].PL_balance_EOP) / 2) 
    ##PL_interest: 5% PL interest could be coded as flexible input; need to divide by 4 if quarterly##
    fin_proj[t]['Forecast'].Reins[idx].Chng_IMR            = fin_proj[t]['Forecast'].Reins[idx].IMR_EOP - fin_proj[t]['Forecast'].Reins[idx].IMR_BOP
    fin_proj[t]['Forecast'].Reins[idx].Impairment_reversal = 0
    fin_proj[t]['Forecast'].Reins[idx].NII_ABR_USSTAT      = items.each_scaled_nii_abr + fin_proj[t]['Forecast'].Reins[idx].Chng_IMR - fin_proj[t]['Forecast'].Reins[idx].PL_interest - fin_proj[t]['Forecast'].Reins[idx].Investment_expense

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
    

def run_EBS_forecast(items, fin_proj, t, idx, iter = 0):  # EBS Items    
    
    if iter == 1:
        # Balance sheet: Assets
        #######################SURPLUS ITEMS TO BE CALCULATED AT OVERALL LEVEL zzzzzzzzzzzzzzzz
        fin_proj[t]['Forecast'].EBS[idx].fixed_inv_surplus = 0
        fin_proj[t]['Forecast'].EBS[idx].alts_inv_surplus = 0
        fin_proj[t]['Forecast'].EBS[idx].total_invested_assets = fin_proj[t]['Forecast'].EBS[idx].fixed_inv_surplus + fin_proj[t]['Forecast'].EBS[idx].alts_inv_surplus
    
    elif iter == 0:
        # Balance sheet: Assets
        #######################Time zero need to tie with actuals; may need scaling zzzzzzzzzzzzzzzz
        fin_proj[t]['Forecast'].EBS[idx].fwa_MV = items.each_scaled_mva #Equal to scaled MVA
        fin_proj[t]['Forecast'].EBS[idx].fwa_BV = items.each_scaled_bva #Equal to scaled BVA
        fin_proj[t]['Forecast'].EBS[idx].LTIC = items.ltic_agg * items.each_pvbe_ratio 
        fin_proj[t]['Forecast'].EBS[idx].LOC = 0
        fin_proj[t]['Forecast'].EBS[idx].DTA_DTL = 0
        fin_proj[t]['Forecast'].EBS[idx].Other_Assets = fin_proj[t]['Forecast'].EBS[idx].fwa_MV + fin_proj[t]['Forecast'].EBS[idx].LTIC + \
                                                        fin_proj[t]['Forecast'].EBS[idx].LOC + fin_proj[t]['Forecast'].EBS[idx].DTA_DTL
        
        fin_proj[t]['Forecast'].EBS[idx].total_assets = fin_proj[t]['Forecast'].EBS[idx].total_invested_assets + fin_proj[t]['Forecast'].EBS[idx].Other_Assets
        
        # Balance sheet: Liabilities    
        fin_proj[t]['Forecast'].EBS[idx].PV_BE = items.each_pv_be    
        fin_proj[t]['Forecast'].EBS[idx].risk_margin = items.each_rm    
        fin_proj[t]['Forecast'].EBS[idx].technical_provision = items.each_tp    
        fin_proj[t]['Forecast'].EBS[idx].other_liab = items.each_scaled_acc_int
        fin_proj[t]['Forecast'].EBS[idx].total_liabilities = fin_proj[t]['Forecast'].EBS[idx].technical_provision + fin_proj[t]['Forecast'].EBS[idx].other_liab
        fin_proj[t]['Forecast'].EBS[idx].GOE_provision = items.each_GOE_provision
        
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
        fin_proj[t]['Forecast'].EBS_IS[idx].GOE_F           = items.each_goe_f
        fin_proj[t]['Forecast'].EBS_IS[idx].Operating_expense = items.each_maint_exp + items.each_goe_f

        # Net investment income
        ####################### EMBEDDED DERIVATIVE ADJUSTMENT NEED TO BE INCORPORATED zzzzzzzzzzzzzzzzzzzzzzzz
        fin_proj[t]['Forecast'].EBS_IS[idx].NII_ABR_GAAP = items.each_scaled_nii_abr + fin_proj[t]['Forecast'].Reins[idx].Chng_IMR 
        
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
            fin_proj[t]['Forecast'].EBS_IS[idx].Other_income      = fin_proj[t-1]['Forecast'].EBS[idx].other_liab - items.each_scaled_acc_int
            fin_proj[t]['Forecast'].EBS_IS[idx].RCGL_ED           = fin_proj[t]['Forecast'].EBS_IS[idx].URCGL - fin_proj[t-1]['Forecast'].EBS_IS[idx].URCGL
    
        # Net income
        fin_proj[t]['Forecast'].EBS_IS[idx].Income_before_tax = fin_proj[t]['Forecast'].EBS_IS[idx].Net_underwriting_profit + fin_proj[t]['Forecast'].EBS_IS[idx].Operating_expense + \
                                                                fin_proj[t]['Forecast'].EBS_IS[idx].Total_NII + fin_proj[t]['Forecast'].EBS_IS[idx].Other_income + \
                                                                fin_proj[t]['Forecast'].EBS_IS[idx].RCGL_ED + fin_proj[t]['Forecast'].EBS_IS[idx].LOC_cost
        fin_proj[t]['Forecast'].EBS_IS[idx].Income_tax        = -0.21 * fin_proj[t]['Forecast'].EBS_IS[idx].Income_before_tax
        fin_proj[t]['Forecast'].EBS_IS[idx].Income_after_tax  = fin_proj[t]['Forecast'].EBS_IS[idx].Income_before_tax - fin_proj[t]['Forecast'].EBS_IS[idx].Income_tax 

def run_EBS_Corp_forecast(fin_proj, t, agg_level, run_control):  # EBS Items calculated at overall level    
    
    # Override risk margin and technical provision based on the recalculated numbers
    if agg_level == 'LT':
        fin_proj[t]['Forecast'].EBS[agg_level].risk_margin = fin_proj[t]['Forecast'].BSCR['LT_RM_LT_CoC_Current']

    elif agg_level == 'GI':
        fin_proj[t]['Forecast'].EBS[agg_level].risk_margin = fin_proj[t]['Forecast'].BSCR['PC_RM_PC_CoC_Current']

    else:
        fin_proj[t]['Forecast'].EBS[agg_level].risk_margin = fin_proj[t]['Forecast'].BSCR['LT_RM_LT_CoC_Current'] + fin_proj[t]['Forecast'].BSCR['PC_RM_PC_CoC_Current']


    fin_proj[t]['Forecast'].EBS[agg_level].technical_provision = fin_proj[t]['Forecast'].EBS[agg_level].PV_BE + fin_proj[t]['Forecast'].EBS[agg_level].risk_margin


    # Income Statement 


    # Balance sheet: Assets
    if t == 0:
        fin_proj[t]['Forecast'].EBS[agg_level].fixed_inv_surplus = fin_proj[t]['Forecast']._control_input.loc['I_SFSLiqSurplus'] + fin_proj[t]['Forecast'].EBS[agg_level].GOE_provision 
        ####Should be set equal to the input I_SFSLiqSurplus from tab "I___Control" PLUS GOE provision
    else:
        fin_proj[t]['Forecast'].EBS[agg_level].fixed_inv_surplus_bef_div \
        = fin_proj[t-1]['Forecast'].EBS[agg_level].fixed_inv_surplus     \
        + fin_proj[t]['Forecast'].EBS_IS[agg_level].NII_surplus_FI       \
        + fin_proj[t]['Forecast'].Reins[agg_level].Net_payment_toReins   \
        + fin_proj[t]['Forecast'].EBS_IS[agg_level].GOE_F                \
        + fin_proj[t]['Forecast'].EBS_IS[agg_level].LOC_cost             \
        + fin_proj[t]['Forecast'].Tax_IS[agg_level].Tax_Paid             \
    
    fin_proj[t]['Forecast'].EBS[agg_level].alts_inv_surplus = 0 ####Load in MLIII information from tab "I_____MLIII"

    #### zzzzzzzzzzzzzzzzzz Dividend Calculation zzzzzzzzzzzzzzzzzzzzzzzzzzzzz#####
    if agg_level == 'agg' and t > 0:
        fin_proj[t]['Forecast'].EBS[agg_level].target_capital = fin_proj[t]['Forecast'].BSCR_Dashboard[agg_level].BSCR_Div * run_control.Target_ECR_Ratio

    fin_proj[t]['Forecast'].EBS[agg_level].total_invested_assets = fin_proj[t]['Forecast'].EBS[agg_level].fixed_inv_surplus + fin_proj[t]['Forecast'].EBS[agg_level].alts_inv_surplus
    
   


def run_SFS_forecast(items, fin_proj, t, idx):  # SFS Items    

    # Assets (for aggregation)
    fin_proj[t]['Forecast'].SFS[idx].fwa_MV = items.each_scaled_mva
    fin_proj[t]['Forecast'].SFS[idx].fwa_BV = items.each_scaled_bva
    fin_proj[t]['Forecast'].SFS[idx].unrealized_capital_gain = items.each_scaled_mva - items.each_scaled_bva
    fin_proj[t]['Forecast'].SFS[idx].GAAP_reserves = 0 # Needed to be coded

    if t == 0:
        fin_proj[t]['Forecast'].SFS_IS[idx].UPR_EOP = items.each_upr
        fin_proj[t]['Forecast'].SFS_IS[idx].UPR_BOP = items.each_upr 
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
    fin_proj[t]['Forecast'].SFS_IS[idx].GOE_F = items.each_goe_f    

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
         
def run_SFS_Corp_forecast(fin_proj, t, agg_level):  # SFS Items calculated at overall level    
    
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Total_expenses = fin_proj[t]['Forecast'].SFS_IS[agg_level].PC_claims + \
                                                               fin_proj[t]['Forecast'].SFS_IS['GI'].Commissions + \
                                                               fin_proj[t]['Forecast'].SFS_IS['GI'].Premium_tax + \
                                                               fin_proj[t]['Forecast'].SFS_IS['GI'].Chng_GAAPRsv + \
                                                               0 ### missing term: Net cost of reinsuarance amortization in Excel <C_SFSIS>

    fin_proj[t]['Forecast'].SFS_IS[agg_level].surplus = fin_proj[t]['Forecast'].SFS[agg_level].fwa_MV - fin_proj[t]['Forecast'].SFS_IS[agg_level].UPR_EOP - \
                                                        fin_proj[t]['Forecast'].SFS[agg_level].GAAP_reserves
                                                        ### Excel <C_AggSFS> Surplus in ModCo/LPT
    fin_proj[t]['Forecast'].SFS_IS[agg_level].deferred_gain_reins = 0 # Need code
    fin_proj[t]['Forecast'].SFS_IS[agg_level].ml3_notes = fin_proj[t]['Forecast'].Agg_items[agg_level].illiquid_assets     
    fin_proj[t]['Forecast'].SFS_IS[agg_level].fixed_inc_surplus = 0 # Need code
    fin_proj[t]['Forecast'].SFS_IS[agg_level].LOC = fin_proj[t]['Forecast'].Agg_items[agg_level].LOC
    fin_proj[t]['Forecast'].SFS_IS[agg_level].DTA_DTL = 0 # Need code
    fin_proj[t]['Forecast'].SFS_IS[agg_level].Total_STAT_capital = fin_proj[t]['Forecast'].SFS_IS[agg_level].surplus + \
                                                                    fin_proj[t]['Forecast'].SFS_IS[agg_level].deferred_gain_reins + \
                                                                    fin_proj[t]['Forecast'].SFS_IS[agg_level].ml3_notes + \
                                                                    fin_proj[t]['Forecast'].SFS_IS[agg_level].LOC + \
                                                                    fin_proj[t]['Forecast'].SFS_IS[agg_level].fixed_inc_surplus + \
                                                                    fin_proj[t]['Forecast'].SFS_IS[agg_level].DTA_DTL

    # Populate into Roll fwd item
    if t == 0:
        fin_proj[t]['Forecast'].Agg_items[agg_level] = 0
    else:
        fin_proj[t]['Forecast'].Agg_items[agg_level].stat_cap_sur_constraint = fin_proj[t]['Forecast'].SFS_IS[agg_level].Total_STAT_capital * \
                                                                                fin_proj[t]['Forecast']._control_input.loc['I_DELimit_CapSur'] * \
                                                                                fin_proj[t]['Forecast'].Agg_items[agg_level].surplus_split_ratio


def run_Tax_forecast(items, fin_proj, t, idx): #### Taxable Income Calculation (Direct Method) ###
    
    if t == 0:
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_EOP  = items.each_scaled_tax_rsv
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_BOP  = fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_EOP

    else:
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_EOP  = items.each_scaled_tax_rsv
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_BOP  = fin_proj[t-1]['Forecast'].Tax_IS[idx].Tax_reserve_EOP
    
    if idx in [15, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]:
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_basis_EOP    = fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_EOP
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_basis_BOP    = fin_proj[t]['Forecast'].Tax_IS[idx].Tax_reserve_BOP
    else:
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_basis_EOP    = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_EOP
        fin_proj[t]['Forecast'].Tax_IS[idx].Tax_basis_BOP    = fin_proj[t]['Forecast'].Reins[idx].Total_STAT_reserve_BOP     
        
    
    fin_proj[t]['Forecast'].Tax_IS[idx].Premiums             = items.each_prem    
    fin_proj[t]['Forecast'].Tax_IS[idx].Death_claims         = items.each_death    
    fin_proj[t]['Forecast'].Tax_IS[idx].Maturities           = items.each_maturity    
    fin_proj[t]['Forecast'].Tax_IS[idx].Surrender            = items.each_surrender    
    fin_proj[t]['Forecast'].Tax_IS[idx].Dividends            = items.each_cash_div    
    fin_proj[t]['Forecast'].Tax_IS[idx].Annuity_claims       = items.each_annuity    
    fin_proj[t]['Forecast'].Tax_IS[idx].AH_claims            = items.each_ah_ben    
    fin_proj[t]['Forecast'].Tax_IS[idx].PC_claims            = items.each_gi_claim    
    fin_proj[t]['Forecast'].Tax_IS[idx].Commissions          = items.each_commission    
    fin_proj[t]['Forecast'].Tax_IS[idx].Premium_tax          = items.each_prem_tax 
    fin_proj[t]['Forecast'].Tax_IS[idx].Maint_expense        = items.each_maint_exp    
    fin_proj[t]['Forecast'].Tax_IS[idx].GOE_F                = items.each_goe_f    
    fin_proj[t]['Forecast'].Tax_IS[idx].Chng_taxbasis        = fin_proj[t]['Forecast'].Tax_IS[idx].Tax_basis_EOP - fin_proj[t]['Forecast'].Tax_IS[idx].Tax_basis_BOP
    fin_proj[t]['Forecast'].Tax_IS[idx].NII_ABR_USSTAT       = items.each_scaled_nii_abr + fin_proj[t]['Forecast'].Reins[idx].Chng_IMR
    fin_proj[t]['Forecast'].Tax_IS[idx].Investment_expense   = fin_proj[t]['Forecast'].Reins[idx].Investment_expense
    
    fin_proj[t]['Forecast'].Tax_IS[idx].Taxable_income_ABR = fin_proj[t]['Forecast'].Tax_IS[idx].Premiums + fin_proj[t]['Forecast'].Tax_IS[idx].Death_claims + \
                                                             fin_proj[t]['Forecast'].Tax_IS[idx].Maturities + fin_proj[t]['Forecast'].Tax_IS[idx].Surrender + \
                                                             fin_proj[t]['Forecast'].Tax_IS[idx].Dividends + fin_proj[t]['Forecast'].Tax_IS[idx].Annuity_claims + \
                                                             fin_proj[t]['Forecast'].Tax_IS[idx].AH_claims + fin_proj[t]['Forecast'].Tax_IS[idx].PC_claims + \
                                                             fin_proj[t]['Forecast'].Tax_IS[idx].Commissions + fin_proj[t]['Forecast'].Tax_IS[idx].Premium_tax + \
                                                             fin_proj[t]['Forecast'].Tax_IS[idx].Maint_expense + fin_proj[t]['Forecast'].Tax_IS[idx].GOE_F + \
                                                             fin_proj[t]['Forecast'].Tax_IS[idx].NII_ABR_USSTAT - fin_proj[t]['Forecast'].Tax_IS[idx].Chng_taxbasis + \
                                                             fin_proj[t]['Forecast'].Tax_IS[idx].Investment_expense
   
    ## Added for Completeness. Placeholder - Further Enhancement required #####################################  
    fin_proj[t]['Forecast'].Tax_IS[idx].Tax_exempt_interest  = 0
    fin_proj[t]['Forecast'].Tax_IS[idx].DAC_cap_amort        = 0                                  
                                                             
def run_aggregation_forecast(fin_proj, t, idx, agg_level):    
    run_aggregation_Reins_forecast(fin_proj, t, idx, agg_level)
    run_aggregation_EBS_forecast(fin_proj, t, idx, agg_level)
    run_aggregation_SFS_forecast(fin_proj, t, idx, agg_level)
    run_aggregation_Tax_forecast(fin_proj, t, idx, agg_level)


def run_aggregation_Reins_forecast(fin_proj, t, idx, agg_level):    
    
    #### Kyle: this can replace all codes below
    fin_proj[t]['Forecast'].Reins[agg_level]._aggregate(fin_proj[t]['Forecast'].Reins[idx])


def run_aggregation_EBS_forecast(fin_proj, t, idx, agg_level):    
    
    fin_proj[t]['Forecast'].EBS[agg_level]._aggregate(fin_proj[t]['Forecast'].EBS[idx], exceptions = ['FI_Dur'])
    fin_proj[t]['Forecast'].EBS_IS[agg_level]._aggregate(fin_proj[t]['Forecast'].EBS_IS[idx])

    #### 
    fin_proj[t]['Forecast'].EBS[agg_level].FI_Dur += fin_proj[t]['Forecast'].EBS[idx].FI_Dur * fin_proj[t]['Forecast'].EBS[idx].fwa_MV_FI 
    ### Will be divided by FI MV in the main model


def run_aggregation_SFS_forecast(fin_proj, t, idx, agg_level):    
    
    fin_proj[t]['Forecast'].SFS[agg_level]._aggregate(fin_proj[t]['Forecast'].SFS[idx])
    

def run_aggregation_Tax_forecast(fin_proj, t, idx, agg_level):    
    
    fin_proj[t]['Forecast'].Tax_IS[agg_level]._aggregate(fin_proj[t]['Forecast'].Tax_IS[idx])
    
    
class input_items:
    
    def __init__(self, cashFlow, fin_proj, t, idx, check = False):
        
        self._scalar     = fin_proj[t]['Forecast'].scalars.loc[idx]
        #self._loc_input  = fin_proj[t]['Forecast'].loc_input ### Kyle: this item is moved to LOC
        #self._tarcap_input = fin_proj[t]['Forecast'].tarcap_input ### Kyle: this item is moved to LOC
        #self._surplus_split = fin_proj[t]['Forecast'].surplus_split ### Kyle: this item is moved to roll_fwd_items
        self._control_input = fin_proj[t]['Forecast']._control_input
        
        self._ccy_rate   = fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self._cols_input = ['Total premium', 'Total net cashflow', 'GOE','GOE_F', 'aggregate cf', 'Total net face amount', 'Net benefits - death', \
                           'Net benefits - maturity', 'Net benefits - annuity', 'Net - AH benefits', 'Net benefits - P&C claims', \
                           'Net benefits - surrender', 'Total commission', 'Maintenance expenses', 'Net premium tax', 'Net cash dividends', \
                           'Total Stat Res - Net Res', 'Total Tax Res - Net Res', 'UPR', 'BV asset backing liab', 'MV asset backing liab', \
                           'Net investment Income', 'CFT reserve', 'Interest maintenance reserve (NAIC)', 'Accrued Income']
        items = cashFlow.loc[cashFlow['RowNo'] == t + 1, self._cols_input].sum() * self._ccy_rate ### Currency modification will be applied here
        
        self.each_prem          = items['Total premium']
        #self.each_ncf           = items['Total net cashflow']
        self.each_goe           = items['GOE'] / self._ccy_rate # No need for currency changes
        self.each_goe_f         = items['GOE_F'] / self._ccy_rate # No need for currency changes
        self.each_agg_cf        = items['aggregate cf']
        self.each_face          = items['Total net face amount']
        #self.each_death         = items['Net benefits - death']
        self.each_maturity      = items['Net benefits - maturity']
        #self.each_annuity       = items['Net benefits - annuity']
        self.each_ah_ben        = items['Net - AH benefits']
        self.each_gi_claim      = items['Net benefits - P&C claims']
        self.each_surrender     = items['Net benefits - surrender']
        self.each_commission    = items['Total commission']
        #self.each_maint_exp     = items['Maintenance expenses']
        self.each_prem_tax      = items['Net premium tax']
        self.each_cash_div      = items['Net cash dividends']
        self.each_stat_rsv      = items['Total Stat Res - Net Res']
        self.each_tax_rsv       = items['Total Tax Res - Net Res']
        self.each_upr           = items['UPR']
        self.each_bva           = items['BV asset backing liab']
        self.each_mva           = items['MV asset backing liab']
        self.each_nii           = items['Net investment Income']
        self.each_cft_rsv       = items['CFT reserve']
        self.each_imr           = items['Interest maintenance reserve (NAIC)']
        self.each_acc_int       = items['Accrued Income']
        self.each_total_stat_rsv = self.each_stat_rsv + self.each_cft_rsv + self.each_imr + self.each_upr

        ######################## Scaled vector #################################
        ## Rsv scalar is applied on ALBA only for DTA Calc, Liab CFs shouldn't be affected; NO Rsv scalars needed for all other LOBs. (April 10/08/2019) ##
        if idx == 34:
            self.each_scaled_stat_rsv      = items['Total Stat Res - Net Res'] * self._scalar['STAT reserve (%)']
            self.each_scaled_tax_rsv       = items['Total Tax Res - Net Res'] * self._scalar['Tax reserve (%)']
            ## Coded for Validtion Purpose, which should be removed later ####################################    
            self.each_ncf                  = items['Total net cashflow'] * self._scalar['STAT reserve (%)']
            self.each_death                = items['Net benefits - death'] * self._scalar['STAT reserve (%)']
            self.each_annuity              = items['Net benefits - annuity'] * self._scalar['STAT reserve (%)']
            self.each_maint_exp            = items['Maintenance expenses'] * self._scalar['STAT reserve (%)']
            
        else:
            self.each_scaled_stat_rsv      = items['Total Stat Res - Net Res']
            self.each_scaled_tax_rsv       = items['Total Tax Res - Net Res']
            self.each_ncf                  = items['Total net cashflow']
            self.each_death                = items['Net benefits - death']
            self.each_annuity              = items['Net benefits - annuity']
            self.each_maint_exp            = items['Maintenance expenses']     

        self.each_scaled_total_stat_rsv = self.each_scaled_stat_rsv + self.each_cft_rsv + self.each_imr + self.each_upr 
        self.each_scaled_bva            = self.each_scaled_total_stat_rsv * self._scalar['BV of assets (%)']
        self.each_scaled_acc_int       = items['Accrued Income'] * self._scalar['Accrued Int (%)']
        
        if self.each_bva == 0:
            self.each_scaled_mva        = 0
            self.each_scaled_nii_abr    = 0
        else:
            self.each_scaled_mva        = self.each_scaled_bva * self._scalar['MV of assets (%)'] * self.each_mva / self.each_bva
            self.each_scaled_nii_abr    = self.each_nii * self.each_scaled_bva / self.each_total_stat_rsv 
            # NII from AXIS is adjusted for any scaling in BV of Assets
        
        self.each_pv_be = fin_proj[t]['Forecast'].liability['dashboard'][idx].PV_BE + items['aggregate cf'] * self._ccy_rate 
        ### temporarily subtract aggregate cash flows for each time ZZZZZ need to be refined to reflect the cash flow timing vs. valuation timing
        self.each_rm    = fin_proj[t]['Forecast'].liability['dashboard'][idx].risk_margin
        self.each_tp    = fin_proj[t]['Forecast'].liability['dashboard'][idx].technical_provision
        
        # self.each_LTIC  = (self.each_pv_be - pvbe secondary) * LTIC/(LR PVBE - LR PVBE seconddary) ### THIS NEEDS TO BE POPULATED AT LOB LEVEL
        self.each_pv_GOE = fin_proj[t]['Forecast'].liability['dashboard'][idx].PV_GOE
        if self.each_pv_be == 0:
            self.each_GOE_provision = 0
        else:
            self.each_GOE_provision = self.each_pv_GOE * self.each_tp / self.each_pv_be
        
        self.each_pvbe_sec = fin_proj[t]['Forecast'].liability['dashboard'][idx].PV_BE_sec
        
        pvbe_LR = fin_proj[t]['Forecast'].liab_summary['dashboard']['LT']['PV_BE']
        pvbe_sec_LR = fin_proj[t]['Forecast'].liab_summary['dashboard']['LT']['PV_BE_sec']
        self.each_pvbe_ratio = (self.each_pv_be - self.each_pvbe_sec) / (pvbe_LR - pvbe_sec_LR)
        pvbe_Agg = fin_proj[t]['Forecast'].liab_summary['dashboard']['Agg']['PV_BE']
        pvbe_sec_Agg = fin_proj[t]['Forecast'].liab_summary['dashboard']['Agg']['PV_BE_sec']
        pvbe_diff_t0 = fin_proj[0]['Forecast'].liab_summary['dashboard']['Agg']['PV_BE'] - fin_proj[0]['Forecast'].liab_summary['dashboard']['Agg']['PV_BE_sec']
       
        if pvbe_diff_t0 == 0:
            self.ltic_agg = 0
        else:
            self.ltic_agg = (pvbe_Agg - pvbe_sec_Agg) / pvbe_diff_t0 * self._control_input.loc['time0_LTIC']
          
        
        if t == 0:
            self.each_pvbe_change = 0
            self.each_rm_change   = 0
            self.each_tp_change   = 0
        else:
            self.each_pvbe_change = self.each_pv_be - fin_proj[t-1]['Forecast'].liability['dashboard'][idx].PV_BE
            self.each_rm_change   = self.each_rm - fin_proj[t-1]['Forecast'].liability['dashboard'][idx].risk_margin
            self.each_tp_change   = self.each_tp - fin_proj[t-1]['Forecast'].liability['dashboard'][idx].technical_provision
        
        if check:
            print("Inputs initialized")

class roll_fwd_items:

    # Aggregated, Life and PC needs to be updated individually
    
    def __init__(self, fin_proj, t, agg_level, surplus_split = 1, check = False):
        
        self.agg_level = agg_level
        if t == 0:
            if agg_level == 'LT':
                self.target_capital = fin_proj[t]['Forecast']._control_input['capital_surplus_life']
            elif agg_level == 'GI':
                self.target_capital = fin_proj[t]['Forecast']._control_input['capital_surplus_pc']
            else:
                self.target_capital = fin_proj[t]['Forecast']._control_input['capital_surplus_life'] + fin_proj[t]['Forecast']._control_input['capital_surplus_pc']
        else:
            self.target_capital = 0 # Updated in BSCR

        self.surplus_split_ratio = surplus_split # LT + GI = Agg = 1

        self.earnings = fin_proj[t]['Forecast'].EBS_IS[agg_level].Income_after_tax
        self.stat_cap_sur_constraint = 0 # Updated in SFS corp forecast
        self.stat_cap_constraint = 0
        self.earnings_based = 0
        self.fund_lv_cap_target = 0
        self.agg_lv_cap_target = 0
        self.dividend = 0
        self.liquid_surplus = 0
        self.LOC = 0 # Updated in LOC
        self.surplus_modco = 0
        self.surplus_lpt = 0
        self.ltic = 0
        self.dta = 0
        self.illiquid_assets = fin_proj[t]['Forecast'].ml3.loc[t, 'ML III MV']
        self.actual_capital = 0 # Updated by self
        self.capital_ratio = 0 # Updated by self
        
    def _cal_actual_capital(self, fin_proj, t):
        self.actual_capital = self.liquid_surplus + self.LOC + self.surplus_modco + self.surplus_lpt + self.ltic + self.dta + self.illiquid_assets
        self.capital_ratio = self.actual_capital / (self.target_capital / fin_proj[t]['Forecast'].LOC._target_capital_ratio)

def run_BSCR_forecast(fin_proj, t, Asset_holding, Asset_adjustment):
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
    
    # Populate into roll forward itmes
    if t != 0:
        fin_proj[t]['Forecast'].Agg_items['Agg'].target_capital = fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].BSCR_Aft_Tax_Adj / fin_proj[t]['Forecast'].LOC._target_capital_ratio
        fin_proj[t]['Forecast'].Agg_items['LT'].target_capital = fin_proj[t]['Forecast'].Agg_items['Agg'].target_capital * fin_proj[t]['Forecast'].Agg_items['LT'].surplus_split_ratio
        fin_proj[t]['Forecast'].Agg_items['GI'].target_capital = fin_proj[t]['Forecast'].Agg_items['Agg'].target_capital * fin_proj[t]['Forecast'].Agg_items['GI'].surplus_split_ratio
    
    ## Fixed income and Equity BSCR at time 0
    if t == 0:
        FI_calc = BSCR_Calc.BSCR_FI_Risk_Charge(Asset_holding, Asset_adjustment)
        fin_proj[t]['Forecast'].BSCR.update({ 'FI_Risk' : FI_calc})
    
        Equity_calc = BSCR_Calc.BSCR_Equity_Risk_Charge(fin_proj[t]['Forecast'].EBS, Asset_holding, Asset_adjustment)
        fin_proj[t]['Forecast'].BSCR.update({ 'Equity_Risk' : Equity_calc})
        
        fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].FI_Risk       = fin_proj[t]['Forecast'].BSCR['FI_Risk']['Agg']
        fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].FI_Risk        = fin_proj[t]['Forecast'].BSCR['FI_Risk']['LT']
        fin_proj[t]['Forecast'].BSCR_Dashboard['GI'].FI_Risk        = fin_proj[t]['Forecast'].BSCR['FI_Risk']['GI']
    
        fin_proj[t]['Forecast'].BSCR_Dashboard['Agg'].Equity_Risk   = fin_proj[t]['Forecast'].BSCR['Equity_Risk']['Agg']
        fin_proj[t]['Forecast'].BSCR_Dashboard['LT'].Equity_Risk    = fin_proj[t]['Forecast'].BSCR['Equity_Risk']['LT']
        fin_proj[t]['Forecast'].BSCR_Dashboard['GI'].Equity_Risk    = fin_proj[t]['Forecast'].BSCR['Equity_Risk']['GI']
       
    
def run_Ins_Risk_forecast(proj_date, val_date_base, nested_proj_dates, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = 0, base_irCurve_GBP = 0, market_factor = [], liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term):
    PC_risk_forecast = BSCR_Calc.BSCR_PC_Risk_Forecast_RM("Bespoke", proj_date, val_date_base, nested_proj_dates, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = base_irCurve_USD, base_irCurve_GBP = base_irCurve_GBP, market_factor = market_factor, liab_spread_beta = liab_spread_beta, KRD_Term = KRD_Term)
    LT_risk_forecast = BSCR_Calc.BSCR_LT_Ins_Risk_Forecast_RM(proj_date, val_date_base, nested_proj_dates, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = base_irCurve_USD, base_irCurve_GBP = base_irCurve_GBP, market_factor = market_factor, liab_spread_beta = liab_spread_beta, KRD_Term = KRD_Term)
    
    return {'PC_risk_forecast' : PC_risk_forecast, 'LT_risk_forecast': LT_risk_forecast}

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
        risk_margin_calc = IAL.CF.PVFromCurve(cfHandle, rf_curve, each_date, 0) - cf_current

        fin_proj[t]['Forecast'].BSCR.update({each_key : risk_margin_calc})

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
        risk_margin_calc = IAL.CF.PVFromCurve(cfHandle, rf_curve, each_date, 0) - cf_current

        fin_proj[t]['Forecast'].BSCR.update({each_key : risk_margin_calc})
        
        
def run_LOC_forecast(fin_proj, t):
    
    ############################ To be updated with BSCR aggregate module ###################################################
    ### (Kyle) currently based on BSCR DASHBOARD aggregated results
    ### (Kyle) target capital ratio is now 1.5 by default, can be imported from fin_proj[t]['Forecast'].tarcap_input
    loc_account = fin_proj[t]['Forecast'].LOC
    if t == 0:
        # Captial Ratio
        loc_account.tier2 = fin_proj[t]['Forecast'].loc_input.loc[0, 'LoC amount']
        loc_account.tier3 = fin_proj[t]['Forecast'].loc_input.loc[1, 'LoC amount']
    else:
        loc_account.tier2 = fin_proj[t-1]['Forecast'].LOC.tier2_eligible
        loc_account.tier3 = fin_proj[t-1]['Forecast'].LOC.tier3_eligible

    loc_account.target_capital =  fin_proj[t]['Forecast'].Agg_items['Agg'].target_capital
    loc_account.tier1_eligible = loc_account.target_capital - loc_account.tier2 - loc_account.tier3
    loc_account.tier2_eligible = min(loc_account.tier2, loc_account.tier1_eligible * fin_proj[t]['Forecast']._control_input['tier2_limit'])
    loc_account.tier3_eligible = min(loc_account.tier3, 
                                     (loc_account.tier1_eligible + loc_account.tier2_eligible) * fin_proj[t]['Forecast']._control_input['tier3_limit_1'],
                                     loc_account.tier1_eligible * fin_proj[t]['Forecast']._control_input['tier3_limit_2'] - loc_account.tier2_eligible)
    loc_account.tier2and3_eligible = loc_account.tier2_eligible + loc_account.tier3_eligible # It should be linked to SFS_Agg 
    
    # Populate into roll forward itmes
    fin_proj[t]['Forecast'].Agg_items['Agg'].LOC = loc_account.tier2and3_eligible
    fin_proj[t]['Forecast'].Agg_items['GI'].LOC = loc_account.tier2and3_eligible # Not applicable in Life