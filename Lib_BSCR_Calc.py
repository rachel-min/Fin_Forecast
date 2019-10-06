# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 13:18:04 2019

@author: seongpar
"""
import os
import math as math
import numpy as np
import Lib_Market_Akit  as IAL_App
import Config_BSCR as BSCR_Config
import Lib_Corp_Model as Corp
import Lib_Corp_Math_Function as Math_Func

# load akit DLL into python
akit_dir = 'C:/AKit v4.1.0/BIN'
os.sys.path.append(akit_dir)
#import IALPython3        as IAL
#import App_daily_portfolio_feed as Asset_App

def BSCR_PC_Reserve_Risk_Charge(Liab_LOB, method = "Bespoke", BSCR_PC_group = BSCR_Config.PC_BSCR_Group, BSCR_PC_RSV_Map = BSCR_Config.PC_Reserve_mapping, pc_f = BSCR_Config.Reserve_Risk_Charge, pc_cor = BSCR_Config.PC_Matrix):
    
    BSCR_PC_Risk          = {}
    BSCR_PC_Reserve_Array = []
    BSCR_PC_Risk_Array    = []

    for idx, clsLiab in Liab_LOB.items():
        BSCR_LOB = clsLiab.LOB_Def['Agg LOB']
        
        for each_group in BSCR_PC_group:

            if idx == 1:
                each_reserve_risk = {'PV_BE' : 0 , 'Risk_Factor' : 0, 'Reserve_Risk' : 0}
                BSCR_PC_Risk.update( { each_group : each_reserve_risk } ) 
            
            if BSCR_LOB == "PC":
                reserve_split = BSCR_PC_RSV_Map[idx][each_group]
                temp_reserve = clsLiab.PV_BE_net * reserve_split
                temp_risk_factor = pc_f[method][each_group]
                temp_risk_charge = temp_reserve * temp_risk_factor
                
                BSCR_PC_Risk[each_group]['PV_BE']        += temp_reserve
                BSCR_PC_Risk[each_group]['Risk_Factor']   = temp_risk_factor
                BSCR_PC_Risk[each_group]['Reserve_Risk'] += temp_risk_charge
                clsLiab.PC_PVBE_BSCR.update( { each_group : temp_reserve } ) 

            else:
                clsLiab.PC_PVBE_BSCR.update( { each_group : 0 } )

    for each_group in BSCR_PC_group:
        BSCR_PC_Reserve_Array.append(BSCR_PC_Risk[each_group]['PV_BE'])
        BSCR_PC_Risk_Array.append(BSCR_PC_Risk[each_group]['Reserve_Risk'])

    max_reserve = max(BSCR_PC_Reserve_Array)
    sum_reserve = sum(BSCR_PC_Reserve_Array)
    sum_risk    = sum(BSCR_PC_Risk_Array)

    if sum_reserve < 0.0001:
        BSCR_Current = 0
    else:
        BSCR_Current = (0.4 * max_reserve / sum_reserve + 0.6) * sum_risk        
        
    BSCR_New_M   = (np.array(BSCR_PC_Risk_Array).dot(pc_cor)).dot(np.array(BSCR_PC_Risk_Array).transpose())
    BSCR_New     = math.sqrt(BSCR_New_M)
    
    BSCR_PC_Risk_Results = { 
                                'BSCR_PC_Risk_Group' : BSCR_PC_Risk,
                                'max_reserve'        : max_reserve,
                                'sum_reserve'        : sum_reserve,
                                'sum_risk'           : sum_risk,
                                'BSCR_Current'       : BSCR_Current,
                                'BSCR_New'           : BSCR_New
                            }
       
    return BSCR_PC_Risk_Results      

def BSCR_PC_Risk_Forecast_RM( reserve_risk_method, proj_date, val_date_base, nested_proj_dates, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = 0, base_irCurve_GBP = 0, market_factor = [], liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term, OpRiskCharge = BSCR_Config.BSCR_Charge['OpRiskCharge'], coc = BSCR_Config.RM_Cost_of_Capital):

    Reserve_Risk_current = {}
    Reserve_Risk_new     = {}
    Reserve_CoC_current = {}
    Reserve_CoC_new     = {}    
        
    for each_date in nested_proj_dates:
        Nested_Proj_LOB = Corp.Run_Liab_DashBoard(val_date_base, each_date, curveType, numOfLoB, liab_val_base,  market_factor,liab_spread_beta,  KRD_Term,  base_irCurve_USD,  base_irCurve_GBP, gbp_rate)
        PC_Risk_calc    = BSCR_PC_Reserve_Risk_Charge(Nested_Proj_LOB, method = reserve_risk_method)
        
        Reserve_Risk_current.update({ each_date : PC_Risk_calc['BSCR_Current'] })
        Reserve_Risk_new.update({ each_date : PC_Risk_calc['BSCR_New'] })

        Reserve_CoC_current.update({ each_date : PC_Risk_calc['BSCR_Current'] * (1 + OpRiskCharge) * coc })
        Reserve_CoC_new.update({ each_date : PC_Risk_calc['BSCR_New'] * (1 + OpRiskCharge) * coc })


    BSCR_PC_Risk_Forecast_RM = { 'BSCR_Current' : Reserve_Risk_current, 'BSCR_New' : Reserve_Risk_new , 'PC_CoC_Current': Reserve_CoC_current  , 'PC_CoC_New': Reserve_CoC_new}
       
    return BSCR_PC_Risk_Forecast_RM

def BSCR_Mortality_Risk_Charge(Liab_LOB, proj_t, BSCR_Mort_group = BSCR_Config.BSCR_Mort_LOB, mort_charge_table=BSCR_Config.Mort_Charge):

#   Initialize
    BSCR_Mort_Risk = {}
    for each_group in BSCR_Mort_group:
        BSCR_Mort_Risk.update( { each_group : {'PV_BE' : 0 , 'Risk_Factor' : 0, 'Mort_Risk' : 0, 'Face_Amount' : 0, 'NAAR' : 0} } ) 

#   Loop for all LOBs zzzzzzzzzzzzzzzzzzz why need to summarize by mortality group????? zzzzzzzzzzzz
    for idx, clsLiab in Liab_LOB.items():
   
        each_risk_type  = clsLiab.LOB_Def['Risk Type']
        each_group      = clsLiab.LOB_Def['BSCR LOB']

        if each_risk_type  == "Mortality":        
            temp_face_amount_sum = clsLiab.cashflow.loc[clsLiab.cashflow["RowNo"] == proj_t + 1, ['Total net face amount']].sum()
            each_face_amount     = temp_face_amount_sum['Total net face amount']
            each_naar            = each_face_amount - clsLiab.PV_BE_net
            clsLiab.Face_Amount  = each_face_amount
            clsLiab.NAAR         = each_naar
            BSCR_Mort_Risk[each_group]['PV_BE']       += clsLiab.PV_BE_net
            BSCR_Mort_Risk[each_group]['Face_Amount'] += each_face_amount
            BSCR_Mort_Risk[each_group]['NAAR']        += each_naar

    ### Aggregation ####
    BSCR_Mort_Risk.update( { 'Total' : {'PV_BE' : 0 , 'Risk_Factor' : 0, 'Mort_Risk' : 0, 'Face_Amount' : 0, 'NAAR' : 0} } ) 
    for each_group in BSCR_Mort_group:
        BSCR_Mort_Risk['Total']['PV_BE']        += BSCR_Mort_Risk[each_group]['PV_BE']
        BSCR_Mort_Risk['Total']['Face_Amount']  += BSCR_Mort_Risk[each_group]['Face_Amount']
        BSCR_Mort_Risk['Total']['NAAR']         += BSCR_Mort_Risk[each_group]['NAAR']

    ### Mortality Risk Calculation ####
    BSCR_Mort_Risk['Total']['Mort_Risk'] = Math_Func.Step_Range_Factor(max(0, BSCR_Mort_Risk['Total']['NAAR']), mort_charge_table)

    if BSCR_Mort_Risk['Total']['NAAR'] < 0.0001:
        BSCR_Mort_Risk['Total']['Mort_Risk_Factor'] = 0

    else:
        BSCR_Mort_Risk['Total']['Mort_Risk_Factor'] = BSCR_Mort_Risk['Total']['Mort_Risk'] / BSCR_Mort_Risk['Total']['NAAR']
   
    return BSCR_Mort_Risk

def BSCR_Longevity_Risk_Charge(Liab_LOB, proj_t, Longevity_LOB = BSCR_Config.Longevity_LOB, longevity_pay_split = BSCR_Config.longevity_pay_split, longevity_age_split = BSCR_Config.longevity_age_split, longevity_charge = BSCR_Config.Longevity_Charge, longevity_age_average = BSCR_Config.longevity_age_average):
    
    BSCR_Longevity_Risk   = {}

#   Initialize
    BSCR_Longevity_Risk = {}
    for each_group in Longevity_LOB:
        BSCR_Longevity_Risk.update( { each_group : {} } )

        for each_pay_status, each_item in longevity_charge.items():
            BSCR_Longevity_Risk[each_group].update( { each_pay_status : {} } )

            for each_age_group in each_item.keys():
                BSCR_Longevity_Risk[each_group][each_pay_status].update( {each_age_group :{'PV_BE' : 0 , 'Risk_Factor' : 0, 'Longevity_Risk' : 0 } } )

    for idx, clsLiab in Liab_LOB.items():

        each_risk_type  = clsLiab.LOB_Def['Risk Type']
        each_group      = clsLiab.LOB_Def['BSCR LOB']
        
        if each_group in Longevity_LOB and each_risk_type  == "Longevity":
            
            each_pay_split_t = longevity_pay_split[each_group]
            
            for each_pay_status, each_pay_split in each_pay_split_t.items():
                each_age_split_t = longevity_age_split[each_group][each_pay_status]
                
                for each_age_group, each_age_split in each_age_split_t.items():
                    each_split_value = each_pay_split * each_age_split
                    each_pvbe        = each_split_value * clsLiab.PV_BE_net
                    each_risk_charge = each_pvbe * longevity_charge[each_pay_status][each_age_group]
                    clsLiab.Longevity_BSCR.update( { each_pay_status : {each_age_group : each_pvbe } } ) 

                    BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['PV_BE']          += each_pvbe
                    BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['Longevity_Risk'] += each_risk_charge

    ### Aggregation ####
    BSCR_Longevity_Risk.update( { 'Total' : {} } )
    pvbe_tot = 0
    risk_tot = 0
    for each_pay_status, each_item in longevity_charge.items():
        BSCR_Longevity_Risk['Total'].update( { each_pay_status : {} } )

        for each_age_group in each_item.keys():
            BSCR_Longevity_Risk['Total'][each_pay_status].update( {each_age_group :{'PV_BE' : 0 , 'Risk_Factor' : 0, 'Longevity_Risk' : 0 } } )

    for each_group in Longevity_LOB:
        for each_pay_status, each_item in longevity_charge.items():
            for each_age_group in each_item.keys():
                
                if BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['PV_BE'] < 0.0001:
                    BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['Risk_Factor'] = 0
        
                else:
                    BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['Risk_Factor'] = BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['Longevity_Risk'] / BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['PV_BE']
                
                BSCR_Longevity_Risk['Total'][each_pay_status][each_age_group]['PV_BE']          += BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['PV_BE']
                BSCR_Longevity_Risk['Total'][each_pay_status][each_age_group]['Longevity_Risk'] += BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['Longevity_Risk']
                
                pvbe_tot += BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['PV_BE']
                risk_tot += BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['Longevity_Risk']

    ### Mortality Risk Calculation ####
    if BSCR_Longevity_Risk['Total'][each_pay_status][each_age_group]['PV_BE'] < 0.0001:
        BSCR_Longevity_Risk['Total'][each_pay_status][each_age_group]['Risk_Factor'] = 0

    else:
        BSCR_Longevity_Risk['Total'][each_pay_status][each_age_group]['Risk_Factor'] = BSCR_Longevity_Risk['Total'][each_pay_status][each_age_group]['Longevity_Risk'] / BSCR_Longevity_Risk['Total'][each_pay_status][each_age_group]['PV_BE']
   
    BSCR_Longevity_Risk['Total'].update({'PV_BE' : pvbe_tot, 'Longevity_Risk' : risk_tot})
    
    return BSCR_Longevity_Risk
