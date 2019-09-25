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

            #            // Create LOB lebel forecasting object
            fin_proj[t]['Forecast'].Reins.update( { idx : Corpclass.Reins_Settlement(each_LOB_key) } )      
            fin_proj[t]['Forecast'].EBS.update( { idx : Corpclass.EBS_Account(each_LOB_key) } )      
            fin_proj[t]['Forecast'].EBS_IS.update( { idx : Corpclass.EBS_IS(each_LOB_key) } )                  

            cf_idx    = proj_cash_flows[idx].cashflow

            #           Reinsurance Items
            each_prem       = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Total premium'].sum()
            each_ncf        = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Total net cashflow'].sum()
            each_goe        = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'GOE'].sum()
            each_agg_cf     = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'aggregate cf'].sum()
            each_face       = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Total net face amount'].sum()
            each_death      = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Net benefits - death'].sum()
            each_maturity   = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Net benefits - maturity'].sum()
            each_annuity    = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Net benefits - annuity'].sum()
            each_ah_ben     = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Net - AH benefits'].sum()
            each_gi_claim   = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Net benefits - P&C claims'].sum()
            each_surrender  = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Net benefits - surrender'].sum()
            each_commission = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Total commission'].sum()
            each_maint_exp  = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Maintenance expenses'].sum()
            each_prem_tax   = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Net premium tax'].sum()
            each_cash_div   = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Net cash dividends'].sum()
            each_stat_rsv   = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Total Stat Res - Net Res'].sum()
            each_tot_rsv    = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Total Tax Res - Net Res'].sum()
            each_upr        = cf_idx.loc[cf_idx['RowNo'] == t + 1,  'UPR'].sum()
            each_bva        = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'BV asset backing liab'].sum()
            each_mva        = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'MV asset backing liab'].sum()
            each_nii        = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Net investment Income'].sum()
            each_cft_rsv    = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'CFT reserve'].sum()
            each_imr        = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Interest maintenance reserve (NAIC)'].sum()
            each_acc_int    = cf_idx.loc[cf_idx['RowNo'] == t + 1, 'Accrued Income'].sum()
            
            #           EBS Items
            each_pv_be = fin_proj[t]['Forecast'].liability['dashboard'][idx].PV_BE
            each_rm    = fin_proj[t]['Forecast'].liability['dashboard'][idx].risk_margin
            each_tp    = fin_proj[t]['Forecast'].liability['dashboard'][idx].technical_provision
            
            fin_proj[t]['Forecast'].Reins[idx].Premiums     = each_prem
            fin_proj[t]['Forecast'].Reins[idx].Death_claims = each_death

            #           Income Statement Items            
            fin_proj[t]['Forecast'].EBS[idx].PV_BE = each_pv_be    
            fin_proj[t]['Forecast'].EBS[idx].risk_margin = each_rm    
            fin_proj[t]['Forecast'].EBS[idx].technical_provision = each_tp    

            #           Income Statement Items            
            if t == 0:
                each_pvbe_change = 0
                each_rm_change   = 0
                each_tp_change   = 0
            ####################### more columns to be added ####################zzzzzzzzzzzzzzzzzzzzzzzz                
            else:
                each_pvbe_change = fin_proj[t]['Forecast'].EBS[idx].PV_BE - fin_proj[t-1]['Forecast'].EBS[idx].PV_BE
                each_rm_change = fin_proj[t]['Forecast'].EBS[idx].risk_margin - fin_proj[t-1]['Forecast'].EBS[idx].risk_margin
                each_tp_change = fin_proj[t]['Forecast'].EBS[idx].technical_provision - fin_proj[t-1]['Forecast'].EBS[idx].technical_provision
            ####################### more columns to be added zzzzzzzzzzzzzzzzzzzzzzzz                
            
            fin_proj[t]['Forecast'].EBS_IS[idx].Premiums     = each_prem    
            fin_proj[t]['Forecast'].EBS_IS[idx].Death_claims = each_death    
            fin_proj[t]['Forecast'].EBS_IS[idx].Chng_PVBE    = each_pvbe_change    
            fin_proj[t]['Forecast'].EBS_IS[idx].Chng_RM      = each_rm_change    
            fin_proj[t]['Forecast'].EBS_IS[idx].Chng_TP      = each_tp_change    

            ################## Aggregation
            clsLiab    = proj_cash_flows[idx]
            each_lob   = clsLiab.get_LOB_Def('Agg LOB')        
            
            if each_lob == "LR":
                fin_proj[t]['Forecast'].Reins['LT'].Premiums += each_prem
                
                fin_proj[t]['Forecast'].EBS['LT'].PV_BE += each_pv_be
                fin_proj[t]['Forecast'].EBS['LT'].risk_margin += each_rm   
                fin_proj[t]['Forecast'].EBS['LT'].technical_provision += each_tp   
                
                fin_proj[t]['Forecast'].EBS_IS['LT'].Premiums += each_prem     
                fin_proj[t]['Forecast'].EBS_IS['LT'].Chng_PVBE += each_pvbe_change    
                fin_proj[t]['Forecast'].EBS_IS['LT'].Chng_RM += each_rm_change    
                fin_proj[t]['Forecast'].EBS_IS['LT'].Chng_TP += each_tp_change    
    
            else:
                fin_proj[t]['Forecast'].Reins['GI'].Premiums += each_prem

                fin_proj[t]['Forecast'].EBS['GI'].PV_BE += each_pv_be
                fin_proj[t]['Forecast'].EBS['GI'].risk_margin += each_rm   
                fin_proj[t]['Forecast'].EBS['GI'].technical_provision += each_tp   
                
                fin_proj[t]['Forecast'].EBS_IS['GI'].Premiums += each_prem                                
                fin_proj[t]['Forecast'].EBS_IS['GI'].Chng_PVBE += each_pvbe_change   
                fin_proj[t]['Forecast'].EBS_IS['GI'].Chng_RM += each_rm_change    
                fin_proj[t]['Forecast'].EBS_IS['GI'].Chng_TP += each_tp_change    

            fin_proj[t]['Forecast'].Reins['Agg'].Premiums          += each_prem
            fin_proj[t]['Forecast'].EBS['Agg'].PV_BE               += each_pv_be      
            fin_proj[t]['Forecast'].EBS['Agg'].risk_margin         += each_rm   
            fin_proj[t]['Forecast'].EBS['Agg'].technical_provision += each_tp   
            fin_proj[t]['Forecast'].EBS_IS['Agg'].Premiums  += each_prem
            fin_proj[t]['Forecast'].EBS_IS['Agg'].Chng_PVBE += each_pvbe_change 
            fin_proj[t]['Forecast'].EBS_IS['Agg'].Chng_RM   += each_rm_change    
            fin_proj[t]['Forecast'].EBS_IS['Agg'].Chng_TP   += each_tp_change    
            


