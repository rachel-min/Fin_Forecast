# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 13:18:04 2019

@author: seongpar
"""
import os
import math as math
import numpy as np
import pandas as pd
import Lib_Market_Akit  as IAL_App
import Config_BSCR as BSCR_Config
import Lib_Corp_Model as Corp
import Lib_Corp_Math_Function as Math_Func
import Class_Corp_Model as Corp_Class
import User_Input_Dic as UI
import Config_BSCR as BSCR_Cofig

# load akit DLL into python
akit_dir = 'C:/AKit v4.1.0/BIN'
os.sys.path.append(akit_dir)
import IALPython3        as IAL
#import App_daily_portfolio_feed as Asset_App
# load akit DLL into python


def BSCR_PC_Reserve_Risk_Charge(Liab_LOB, method = "Bespoke", BSCR_PC_group = BSCR_Config.PC_BSCR_Group, BSCR_PC_RSV_Map = BSCR_Config.PC_Reserve_mapping, pc_f = BSCR_Config.Reserve_Risk_Charge, pc_cor = BSCR_Config.PC_Matrix):
    
    BSCR_PC_Risk          = {}
    BSCR_PC_Reserve_Array = []
    BSCR_PC_Risk_Array    = []

    for idx, clsLiab in Liab_LOB.items():
        Risk_Type = clsLiab.LOB_Def['Risk Type']
        
        for each_group in BSCR_PC_group:

            if idx == 1:
                each_reserve_risk = {'PV_BE' : 0 , 'Risk_Factor' : 0, 'Reserve_Risk' : 0}
                BSCR_PC_Risk.update( { each_group : each_reserve_risk } ) 
            
            if Risk_Type == "PC":
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
        
    for t, each_date in enumerate(nested_proj_dates): 
        Nested_Proj_LOB = Corp.Run_Liab_DashBoard(val_date_base, each_date, curveType, numOfLoB, liab_val_base,  market_factor,liab_spread_beta,  KRD_Term,  base_irCurve_USD,  base_irCurve_GBP, gbp_rate)
        PC_Risk_calc    = BSCR_PC_Reserve_Risk_Charge(Nested_Proj_LOB, method = reserve_risk_method)
        
        Reserve_Risk_current.update({ each_date : PC_Risk_calc['BSCR_Current'] })
        Reserve_Risk_new.update({ each_date : PC_Risk_calc['BSCR_New'] })


        if t == 0:
            Reserve_CoC_current.update({ each_date : 0 })
            Reserve_CoC_new.update({ each_date : 0 })

        else:
            prev_date = nested_proj_dates[t-1]
            Reserve_CoC_current.update({ each_date : Reserve_Risk_current[prev_date] * (1 + OpRiskCharge) * coc })
            Reserve_CoC_new.update({ each_date : Reserve_Risk_new[prev_date] * (1 + OpRiskCharge) * coc })

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

def BSCR_Longevity_Risk_Charge(Liab_LOB, proj_t, start_date, eval_date, start_longevity_risk, Longevity_LOB = BSCR_Config.Longevity_LOB, longevity_pay_split = BSCR_Config.longevity_pay_split, longevity_age_split = BSCR_Config.longevity_age_split, longevity_charge = BSCR_Config.Longevity_Charge, longevity_age_average = BSCR_Config.longevity_age_average):
    
    BSCR_Longevity_Risk   = {}

#   Initialize
    BSCR_Longevity_Risk = {}
    for each_group in Longevity_LOB:
        BSCR_Longevity_Risk.update( { each_group : {} } )

        for each_pay_status, each_item in longevity_charge.items():
            BSCR_Longevity_Risk[each_group].update( { each_pay_status : {} } )

            for each_age_group in each_item.keys():
                BSCR_Longevity_Risk[each_group][each_pay_status].update( {each_age_group :{'PV_BE' : 0 , 'Risk_Factor' : 0, 'Longevity_Risk' : 0 } } )
                BSCR_Longevity_Risk[each_group][each_pay_status].update( {'Total' :{'PV_BE' : 0 , 'Risk_Factor' : 0, 'Longevity_Risk' : 0 } } )

    #### Calculaiton by Individual Liability #####
    for idx, clsLiab in Liab_LOB.items():
        each_risk_type  = clsLiab.LOB_Def['Risk Type']
        each_group      = clsLiab.LOB_Def['BSCR LOB']
        
        if each_group in Longevity_LOB and each_risk_type  == "Longevity":
            each_pay_split_t = longevity_pay_split[each_group]
            
            for each_pay_status, each_pay_split in each_pay_split_t.items():
                each_age_split_t = longevity_age_split[each_group][each_pay_status]

                #### Full Calculation when t = 0 #####
                if proj_t == 0:
                    for each_age_group, each_age_split in each_age_split_t.items():
                        each_split_value = each_pay_split * each_age_split
                        each_pvbe        = each_split_value * clsLiab.PV_BE_net
                        each_risk_charge = each_pvbe * longevity_charge[each_pay_status][each_age_group]
                        clsLiab.Longevity_BSCR.update( { each_pay_status : {each_age_group : each_pvbe } } ) 
    
                        BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['PV_BE']          += each_pvbe
                        BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['Longevity_Risk'] += each_risk_charge
                        BSCR_Longevity_Risk[each_group][each_pay_status]['Total']['PV_BE']                 += each_pvbe
                        BSCR_Longevity_Risk[each_group][each_pay_status]['Total']['Longevity_Risk']        += each_risk_charge
            
                #### PVBE calculation only when t > 0 #####
                else:
                    each_split_value = each_pay_split
                    each_pvbe        = each_split_value * clsLiab.PV_BE_net
                    BSCR_Longevity_Risk[each_group][each_pay_status]['Total']['PV_BE'] += each_pvbe
                        
    ### Aggregation - Initialization ####
    BSCR_Longevity_Risk.update( { 'Total' : {} } )
    pvbe_tot = 0
    risk_tot = 0
    for each_pay_status, each_item in longevity_charge.items():
        BSCR_Longevity_Risk['Total'].update( { each_pay_status : {} } )

        for each_age_group in each_item.keys():
            BSCR_Longevity_Risk['Total'][each_pay_status].update( {each_age_group :{'PV_BE' : 0 , 'Risk_Factor' : 0, 'Longevity_Risk' : 0 } } )
            BSCR_Longevity_Risk['Total'][each_pay_status].update( {'Total' :{'PV_BE' : 0 , 'Risk_Factor' : 0, 'Longevity_Risk' : 0 } } )            

    ### Aggregation - LOB / Total Calculation ####
    #### Approximation of longevity risk charge when t > 0 #####
    if proj_t == 0:
        for each_group in Longevity_LOB:
            for each_pay_status, each_item in longevity_charge.items():
                for each_age_group in each_item.keys():
                    #### Average Risk Charge by LOB, Pay Status and Age Group
                    if BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['PV_BE'] < 0.0001:
                        BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['Risk_Factor'] = 0
            
                    else:
                        BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['Risk_Factor'] = BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['Longevity_Risk'] / BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['PV_BE']
                    
                    BSCR_Longevity_Risk['Total'][each_pay_status][each_age_group]['PV_BE']          += BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['PV_BE']
                    BSCR_Longevity_Risk['Total'][each_pay_status][each_age_group]['Longevity_Risk'] += BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['Longevity_Risk']
                    BSCR_Longevity_Risk['Total'][each_pay_status]['Total']['PV_BE']                 += BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['PV_BE']
                    BSCR_Longevity_Risk['Total'][each_pay_status]['Total']['Longevity_Risk']        += BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['Longevity_Risk']
                    
                    pvbe_tot += BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['PV_BE']
                    risk_tot += BSCR_Longevity_Risk[each_group][each_pay_status][each_age_group]['Longevity_Risk']
    
                #### Average Risk Charge by LOB and Pay Status
                if BSCR_Longevity_Risk[each_group][each_pay_status]['Total']['PV_BE'] < 0.0001:
                    BSCR_Longevity_Risk[each_group][each_pay_status]['Total']['Risk_Factor'] = 0
        
                else:
                    BSCR_Longevity_Risk[each_group][each_pay_status]['Total']['Risk_Factor'] = BSCR_Longevity_Risk[each_group][each_pay_status]['Total']['Longevity_Risk'] / BSCR_Longevity_Risk[each_group][each_pay_status]['Total']['PV_BE']

        for each_pay_status, each_item in longevity_charge.items():
            for each_age_group in each_item.keys():
                #### Average Risk Charge by Pay Status and Age Group
                if BSCR_Longevity_Risk['Total'][each_pay_status][each_age_group]['PV_BE'] < 0.0001:
                    BSCR_Longevity_Risk['Total'][each_pay_status][each_age_group]['Risk_Factor'] = 0
            
                else:
                    BSCR_Longevity_Risk['Total'][each_pay_status][each_age_group]['Risk_Factor'] = BSCR_Longevity_Risk['Total'][each_pay_status][each_age_group]['Longevity_Risk'] / BSCR_Longevity_Risk['Total'][each_pay_status][each_age_group]['PV_BE']
    
            #### Average Risk Charge by Pay Status
            if BSCR_Longevity_Risk['Total'][each_pay_status]['Total']['PV_BE'] < 0.0001:
                BSCR_Longevity_Risk['Total'][each_pay_status]['Total']['Risk_Factor'] = 0
    
            else:
                BSCR_Longevity_Risk['Total'][each_pay_status]['Total']['Risk_Factor'] = BSCR_Longevity_Risk['Total'][each_pay_status]['Total']['Longevity_Risk'] / BSCR_Longevity_Risk['Total'][each_pay_status]['Total']['PV_BE']

    #### Approximation of longevity risk charge when t > 0 #####
    else:
        for each_group in Longevity_LOB :
            for each_pay_status, each_pay_split in each_pay_split_t.items():
                each_risk_charge = BSCR_Longevity_Risk_Factor(start_date, eval_date, longevity_age_average[each_group][each_pay_status], start_longevity_risk[each_group][each_pay_status]['Total']['Risk_Factor'], longevity_age_average['Ultimate'][each_pay_status], longevity_charge['Ultimate'][each_pay_status])
                BSCR_Longevity_Risk[each_group][each_pay_status]['Total']['Longevity_Risk'] = each_risk_charge * BSCR_Longevity_Risk[each_group][each_pay_status]['Total']['PV_BE']
                BSCR_Longevity_Risk[each_group][each_pay_status]['Total']['Risk_Factor']    = each_risk_charge

                pvbe_tot += BSCR_Longevity_Risk[each_group][each_pay_status]['Total']['PV_BE']
                risk_tot += BSCR_Longevity_Risk[each_group][each_pay_status]['Total']['Longevity_Risk']

    #### Average Risk Charge in Aggregate
    if pvbe_tot < 0.0001:
        avg_risk_charge = 0

    else:
        avg_risk_charge = risk_tot / pvbe_tot
    
    BSCR_Longevity_Risk['Total'].update({'PV_BE' : pvbe_tot, 'Longevity_Risk' : risk_tot, 'Risk_Factor' : avg_risk_charge })
    
    return BSCR_Longevity_Risk


def BSCR_Longevity_Risk_Factor(start_date, eval_date, start_age, start_factor, ultimate_age, ultimate_factor):

    grade_year       = eval_date.year - start_date.year # IAL.Date.yearFrac("ACT/365",  start_date, eval_date)
    d_risk_factor    = ultimate_factor - start_factor
    d_risk_age       = ultimate_age - start_age 
    risk_factor_calc = min(ultimate_factor, start_factor + grade_year * d_risk_factor / d_risk_age)
    
    return risk_factor_calc

def BSCR_Morbidity_Risk_Charge(Liab_LOB, proj_t, BSCR_Morbidity_group = BSCR_Config.Morbidity_LOB, morb_f = BSCR_Config.Morb_Charge, Morbidity_Split = BSCR_Config.Morbidity_split):

#   Initialize
    BSCR_Morbidity_Risk = {}
    for each_group in BSCR_Morbidity_group:
        BSCR_Morbidity_Risk.update( { each_group : {'PV_BE' : 0 , 'Premium' : 0, 'Morbidity_Risk' : 0, 'PV_BE_Inpay' : 0, 'Premium_Active' : 0 } } ) 

#   Loop for all LOBs 
    for idx, clsLiab in Liab_LOB.items():
   
        each_risk_type  = clsLiab.LOB_Def['Risk Type']
        each_group      = clsLiab.LOB_Def['BSCR LOB']

        if each_risk_type  == 'Morbidity & Disability':        
            temp_premium_sum = clsLiab.cashflow.loc[clsLiab.cashflow["RowNo"] == proj_t + 2, ['Total premium']].sum()
            each_premium     = temp_premium_sum['Total premium']
            BSCR_Morbidity_Risk[each_group]['PV_BE']       += clsLiab.PV_BE_net
            BSCR_Morbidity_Risk[each_group]['Premium']     += each_premium
            BSCR_Morbidity_Risk[each_group]['PV_BE_Inpay']    = BSCR_Morbidity_Risk[each_group]['PV_BE'] * Morbidity_Split[each_group]['inpayment']
            BSCR_Morbidity_Risk[each_group]['Premium_Active'] = BSCR_Morbidity_Risk[each_group]['Premium'] * Morbidity_Split[each_group]['active']

    ### Aggregation ####
    BSCR_Morbidity_Risk.update( { 'Total' : {'PV_BE' : 0 , 'Premium' : 0, 'Morbidity_Risk' : 0, 'PV_BE_Inpay' : 0, 'Premium_Active' : 0 } } ) 
    for each_group in BSCR_Morbidity_group:
        if each_group == 'LTC':                                       
            BSCR_Morbidity_Risk[each_group]['Morbidity_Risk'] \
            = BSCR_Morbidity_Risk[each_group]['PV_BE_Inpay'] * morb_f["Disability income: claims in payment Waiver of premium and long-term care"] \
            + BSCR_Morbidity_Risk[each_group]['Premium_Active'] * morb_f["Disability Income: Active Lives, Prem guar ≤ 1 Yr; Benefit Period > 2 Years"] 
            
        else: #### AH or PC                
            BSCR_Morbidity_Risk[each_group]['Morbidity_Risk'] \
            = BSCR_Morbidity_Risk[each_group]['PV_BE_Inpay'] * morb_f["Disability income: claims in payment Other accident and sickness"] \
            + BSCR_Morbidity_Risk[each_group]['Premium_Active'] * morb_f["Disability Income: Active lives, Other Accident and Sickness"]

        BSCR_Morbidity_Risk['Total']['PV_BE']           += BSCR_Morbidity_Risk[each_group]['PV_BE']
        BSCR_Morbidity_Risk['Total']['Premium']         += BSCR_Morbidity_Risk[each_group]['Premium']
        BSCR_Morbidity_Risk['Total']['PV_BE_Inpay']     += BSCR_Morbidity_Risk[each_group]['PV_BE_Inpay']
        BSCR_Morbidity_Risk['Total']['Premium_Active']  += BSCR_Morbidity_Risk[each_group]['Premium_Active']
        BSCR_Morbidity_Risk['Total']['Morbidity_Risk']  += BSCR_Morbidity_Risk[each_group]['Morbidity_Risk']

    return BSCR_Morbidity_Risk


def BSCR_Other_Ins_Risk_Charge(Liab_LOB, BSCR_Other_Ins_group = BSCR_Config.Other_Ins_Risk_LOB, other_f = BSCR_Config.Other_Charge, Morbidity_Split = BSCR_Config.Morbidity_split):

#   Initialize
    BSCR_Other_Ins_Risk = {}
    for each_group in BSCR_Other_Ins_group:
        BSCR_Other_Ins_Risk.update( { each_group : {'PV_BE' : 0, 'Other_Ins_Risk' : 0 } } ) 

#   Loop for all LOBs 
    for idx, clsLiab in Liab_LOB.items():
        each_risk_type  = clsLiab.LOB_Def['Risk Type']
        each_group      = clsLiab.LOB_Def['BSCR LOB']

        if each_group in BSCR_Other_Ins_group:
            if each_group != 'PC' or (each_group == "PC" and each_risk_type  == 'Morbidity & Disability'):
                BSCR_Other_Ins_Risk[each_group]['PV_BE'] += clsLiab.PV_BE_net

    ### Aggregation ####
    BSCR_Other_Ins_Risk.update( { 'Total' : {'PV_BE' : 0 , 'Other_Ins_Risk' : 0 } } ) 
    for each_group in BSCR_Other_Ins_group:

        if each_group in ['UL','WL','ROP']:
            BSCR_Other_Ins_Risk[each_group]['Other_Ins_Risk'] = BSCR_Other_Ins_Risk[each_group]['PV_BE'] * other_f["Mortality (term insurance, whole life, universal life)"]

        elif each_group in ['SS','TFA','SPIA','ALBA']:
            BSCR_Other_Ins_Risk[each_group]['Other_Ins_Risk'] = BSCR_Other_Ins_Risk[each_group]['PV_BE'] * other_f["Longevity (immediate pay-out annuities, contingent annuities, pension pay-outs)"]
        
        elif each_group == 'LTC':                                       
            BSCR_Other_Ins_Risk[each_group]['Other_Ins_Risk'] \
            = BSCR_Other_Ins_Risk[each_group]['PV_BE']  \
            *( other_f["Disability Income: active lives - including waiver of premium and long-term care"] * Morbidity_Split[each_group]['active'] \
              + other_f["Disability Income: claims in payment - including waiver of premium and long-term care"] * Morbidity_Split[each_group]['inpayment'] )

        else: #### AH or PC                
            BSCR_Other_Ins_Risk[each_group]['Other_Ins_Risk'] \
            = BSCR_Other_Ins_Risk[each_group]['PV_BE']  \
             * (  other_f["Critical Illness (including accelerated critical illness products)"] * Morbidity_Split[each_group]['critical'] \
                + other_f["Disability Income: active lives - other accident and sickness"] * Morbidity_Split[each_group]['active']        \
                + other_f["Disability Income: claims in payment - other accident and sickness"] * Morbidity_Split[each_group]['inpayment'] )

        BSCR_Other_Ins_Risk['Total']['PV_BE']           += BSCR_Other_Ins_Risk[each_group]['PV_BE']
        BSCR_Other_Ins_Risk['Total']['Other_Ins_Risk']  += BSCR_Other_Ins_Risk[each_group]['Other_Ins_Risk']

    return BSCR_Other_Ins_Risk

def BSCR_Stoploss_Risk_Charge(Liab_LOB):
    
    BSCR_StopLoss_Risk = {'Total' : {'StopLoss_Risk' : 0}}
    
    return BSCR_StopLoss_Risk

def BSCR_Riders_Risk_Charge(Liab_LOB):
    
    BSCR_Riders_Risk = {'Total' : {'Riders_Risk' : 0}}
    
    return BSCR_Riders_Risk

def BSCR_VA_Risk_Charge(Liab_LOB):
    
    BSCR_VA_Risk = {'Total' : {'VA_Risk' : 0}}
    
    return BSCR_VA_Risk

def BSCR_LT_Ins_Risk_Aggregate( BSCR_Analytics, lt_cor = BSCR_Config.LT_Matrix ):

    LT_Mort     = BSCR_Analytics.Mortality_Risk
    LT_Stoploss = BSCR_Analytics.StopLoss_Risk
    LT_Riders   = BSCR_Analytics.Riders_Risk
    LT_Morb     = BSCR_Analytics.Morbidity_Risk
    LT_Long     = BSCR_Analytics.Longevity_Risk
    LT_VA       = BSCR_Analytics.VA_Guarantee_Risk
    LT_Other    = BSCR_Analytics.OtherInsurance_Risk

    BSCR_LT_Risk_Array = [LT_Mort,LT_Stoploss,LT_Riders,LT_Morb, LT_Long, LT_VA, LT_Other ]

    BSCR_Current = np.sqrt( (LT_Mort + LT_Stoploss + LT_Riders) ** 2 + LT_Morb ** 2 + LT_Long ** 2 + LT_VA ** 2 + LT_Other ** 2 - 0.5 * ( (LT_Mort + LT_Stoploss + LT_Riders) * LT_Long ) )

    BSCR_New_M   = (np.array(BSCR_LT_Risk_Array).dot(lt_cor)).dot(np.array(BSCR_LT_Risk_Array).transpose())
    BSCR_New     = math.sqrt(BSCR_New_M)
    
    BSCR_LT_Risk_Results = { 'BSCR_Current' : BSCR_Current, 'BSCR_New' : BSCR_New }
    
    return BSCR_LT_Risk_Results
    
def BSCR_LT_Ins_Risk_Forecast_RM(proj_date, val_date_base, nested_proj_dates, liab_val_base, liab_summary_base, curveType, numOfLoB, gbp_rate, base_irCurve_USD = 0, base_irCurve_GBP = 0, market_factor = [], liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term, OpRiskCharge = BSCR_Config.BSCR_Charge['OpRiskCharge'], coc = BSCR_Config.RM_Cost_of_Capital):

    LT_Ins_Risk_current     = {}
    LT_Ins_Risk_new         = {}
    LT_Ins_Risk_CoC_current = {}
    LT_Ins_Risk_CoC_new     = {}    
    Start_BSCR              = { 'LT_Longevity_Risk' : {}}
        
    for t, each_date in enumerate(nested_proj_dates): 
        Nested_Proj_LOB = Corp.Run_Liab_DashBoard(val_date_base, each_date, curveType, numOfLoB, liab_val_base,  market_factor,liab_spread_beta,  KRD_Term,  base_irCurve_USD,  base_irCurve_GBP, gbp_rate)


        each_BSCR = Corp_Class.BSCR_Analytics("Agg")

#        PC_Risk_calc    = BSCR_PC_Reserve_Risk_Charge(Nested_Proj_LOB, method = reserve_risk_method)
        ##  LT Mortality Risk
        LT_Mort_calc      = BSCR_Mortality_Risk_Charge(Nested_Proj_LOB, t)
        LT_Longevity_calc = BSCR_Longevity_Risk_Charge(Nested_Proj_LOB, t, nested_proj_dates[0], each_date, Start_BSCR['LT_Longevity_Risk'])
        
        if t == 0:
            Start_BSCR['LT_Longevity_Risk'] = LT_Longevity_calc
        
        LT_Morbidity_calc = BSCR_Morbidity_Risk_Charge(Nested_Proj_LOB, t)
        LT_Other_Ins_calc = BSCR_Other_Ins_Risk_Charge(Nested_Proj_LOB)
        LT_Stop_Loss_calc = BSCR_Stoploss_Risk_Charge(Nested_Proj_LOB)
        LT_Riders_calc    = BSCR_Riders_Risk_Charge(Nested_Proj_LOB)
        LT_VA_calc        = BSCR_VA_Risk_Charge(Nested_Proj_LOB)
  
        each_BSCR.Mortality_Risk      = LT_Mort_calc['Total']['Mort_Risk']
        each_BSCR.StopLoss_Risk       = LT_Stop_Loss_calc['Total']['StopLoss_Risk']
        each_BSCR.Riders_Risk         = LT_Riders_calc['Total']['Riders_Risk']
        each_BSCR.Morbidity_Risk      = LT_Morbidity_calc['Total']['Morbidity_Risk']
        each_BSCR.Longevity_Risk      = LT_Longevity_calc['Total']['Longevity_Risk']
        each_BSCR.VA_Guarantee_Risk   = LT_VA_calc['Total']['VA_Risk']
        each_BSCR.OtherInsurance_Risk = LT_Other_Ins_calc['Total']['Other_Ins_Risk']

        LT_Agg_calc = BSCR_LT_Ins_Risk_Aggregate(each_BSCR)
        LT_Ins_Risk_current.update({ each_date : LT_Agg_calc['BSCR_Current'] })
        LT_Ins_Risk_new.update({ each_date : LT_Agg_calc['BSCR_New'] })

        if t == 0:
            LT_Ins_Risk_CoC_current.update({ each_date : 0 })
            LT_Ins_Risk_CoC_new.update({ each_date : 0 })

        else:
            prev_date = nested_proj_dates[t-1]
            LT_Ins_Risk_CoC_current.update({ each_date : LT_Ins_Risk_current[prev_date] * (1 + OpRiskCharge) * coc })
            LT_Ins_Risk_CoC_new.update({ each_date : LT_Ins_Risk_new[prev_date] * (1 + OpRiskCharge) * coc })

    BSCR_LT_Risk_Forecast_RM = { 'BSCR_Current' : LT_Ins_Risk_current, 'BSCR_New' : LT_Ins_Risk_new , 'LT_CoC_Current': LT_Ins_Risk_CoC_current  , 'LT_CoC_New': LT_Ins_Risk_CoC_new}
       
    return BSCR_LT_Risk_Forecast_RM

def BSCR_FI_Risk_Charge(portInput, AssetAdjustment):
    
    BSCR_FI_Risk = {}     
    
    # Existing Asset Charge        
    BSCR_Asset_Risk_Charge = portInput.groupby(['FIIndicator','Fort Re Corp Segment'])['AssetCharge_Current'].sum()  
    
    BSCR_FI_EA_Risk_Charge_Agg = BSCR_Asset_Risk_Charge.loc[([1])].sum()
    BSCR_FI_EA_Risk_Charge_LT  = BSCR_Asset_Risk_Charge.loc[([1],['ALBA','Long Term Surplus','ModCo'])].sum()
    BSCR_FI_EA_Risk_Charge_GI  = BSCR_Asset_Risk_Charge.loc[([1],['LPT','General Surplus'])].sum()
    
    # Adjustment Asset Charge    
    BSCR_AssetAdjustment_Risk_Charge = AssetAdjustment.groupby(['FIIndicator','Fort Re Corp Segment'])['AssetCharge_Current'].sum()
    
    BSCR_FI_AA_Risk_Charge_Agg = BSCR_AssetAdjustment_Risk_Charge.loc[([1])].sum()
    BSCR_FI_AA_Risk_Charge_LT = BSCR_AssetAdjustment_Risk_Charge.loc[([1],['ALBA','Long Term Surplus','ModCo'])].sum()    
    BSCR_FI_AA_Risk_Charge_GI = BSCR_AssetAdjustment_Risk_Charge.loc[([1],['LPT','General Surplus'])].sum()
        
    BSCR_FI_Risk['Agg'] = BSCR_FI_EA_Risk_Charge_Agg + BSCR_FI_AA_Risk_Charge_Agg
    BSCR_FI_Risk['LT']  = BSCR_FI_EA_Risk_Charge_LT + BSCR_FI_AA_Risk_Charge_LT  
    BSCR_FI_Risk['GI']  = BSCR_FI_EA_Risk_Charge_GI + BSCR_FI_AA_Risk_Charge_GI
        
    return BSCR_FI_Risk

def BSCR_Equity_Risk_Charge(EBS, portInput, AssetAdjustment, regime = "Current"):
        
    BSCR_Eq_Risk = {}   
    
    AssetRiskCharge = pd.DataFrame(BSCR_Config.BSCR_Asset_Risk_Charge_v1).transpose()
    AssetRiskCharge['BMA_Category'] = AssetRiskCharge.index
    
    if regime =="Current":      
        # Existing Asset Charge  
        BSCR_Asset_Risk_Charge = portInput.groupby(['FIIndicator','Fort Re Corp Segment'])['AssetCharge_Current'].sum()  
        BSCR_Equity_EA_Risk_Charge_Agg = BSCR_Asset_Risk_Charge.loc[([0])].sum() 
        BSCR_Equity_EA_Risk_Charge_LT = BSCR_Asset_Risk_Charge.loc[([0],['ALBA','Long Term Surplus','ModCo'])].sum()
        BSCR_Equity_EA_Risk_Charge_GI = BSCR_Asset_Risk_Charge.loc[([0],['LPT','General Surplus'])].sum()     
    
        # Adjustment Asset Charge    
        BSCR_AssetAdjustment_Risk_Charge = AssetAdjustment.groupby(['FIIndicator','Fort Re Corp Segment'])['AssetCharge_Current'].sum()
    
        BSCR_Equity_AA_Risk_Charge_Agg = BSCR_AssetAdjustment_Risk_Charge.loc[([0])].sum() + EBS['Agg'].DTA_DTL * AssetRiskCharge[AssetRiskCharge['BMA_Category']=='DTA']['Risk_Charge'].iloc[0]
        BSCR_Equity_AA_Risk_Charge_LT = BSCR_AssetAdjustment_Risk_Charge.loc[([0],['ALBA','Long Term Surplus','ModCo'])].sum() + EBS['LT'].DTA_DTL*AssetRiskCharge[AssetRiskCharge['BMA_Category']=='DTA']['Risk_Charge'].iloc[0]
        BSCR_Equity_AA_Risk_Charge_GI = BSCR_AssetAdjustment_Risk_Charge.loc[([0],['LPT','General Surplus'])].sum() + EBS['GI'].DTA_DTL*AssetRiskCharge[AssetRiskCharge['BMA_Category']=='DTA']['Risk_Charge'].iloc[0]
    
        BSCR_Eq_Risk['Agg'] = BSCR_Equity_EA_Risk_Charge_Agg+BSCR_Equity_AA_Risk_Charge_Agg
        BSCR_Eq_Risk['LT'] = BSCR_Equity_EA_Risk_Charge_LT+BSCR_Equity_AA_Risk_Charge_LT
        BSCR_Eq_Risk['GI'] = BSCR_Equity_EA_Risk_Charge_GI+BSCR_Equity_AA_Risk_Charge_GI
    
    elif regime =="Future":
        
        for bu in ['Agg', 'LT', 'GI']:
             
         Equity = portInput.groupby(['FIIndicator', 'Fort Re Corp Segment'])['AssetCharge_Future'].sum()
         Equity_AA = AssetAdjustment.groupby(['FIIndicator','Fort Re Corp Segment'])['AssetCharge_Future'].sum()
#         Equity_AA = AssetAdjustment.groupby(['BMA_Catory', 'Fort Re Corp Segment'])['MV_USD_GAAP'].sum()
         type_1 = {'Agg': Equity.loc[([0], ['ALBA', 'ModCo', 'LPT'])].sum() + Equity_AA.loc[([0], ['ALBA', 'ModCo', 'LPT'])].sum(),
                    'LT': Equity.loc[([0], ['ALBA', 'ModCo'])].sum() + Equity_AA.loc[([0], ['ALBA', 'ModCo'])].sum(),
                    'GI': Equity.loc[([0], ['LPT'])].sum() + Equity_AA.loc[([0], ['LPT'])].sum()}
         type_2 = {'Agg': Equity.loc[([0], ['Long Term Surplus', 'General Surplus'])].sum() + Equity_AA.loc[([0], ['Long Term Surplus', 'General Surplus'])].sum(),
                    'LT': Equity.loc[([0], ['Long Term Surplus'])].sum() + Equity_AA.loc[([0], ['Long Term Surplus'])].sum(),
                    'GI': Equity.loc[([0], ['General Surplus'])].sum() + Equity_AA.loc[([0], ['General Surplus'])].sum()}
        
#        for bu in ['Agg', 'LT', 'PC']:
            
         charge = pd.Series([type_1[bu], type_2[bu],  0,  0])
         BSCR_Eq_Risk[bu] = math.sqrt(np.dot(np.dot(charge, BSCR_Config.Equity_cor), charge.transpose()))
                           
    return BSCR_Eq_Risk

def BSCR_IR_Risk(FI_MV, FI_Dur, PV_BE, Liab_Dur):
    if FI_MV == 0:
        return np.nan
    Liab_dur_scaled = Liab_Dur * PV_BE / FI_MV                                       
    Dur_mismatch    = abs(Liab_dur_scaled - FI_Dur)
    IR_Risk_Charge  = FI_MV * max(1, Dur_mismatch) * 0.02 * 0.5
    
    return IR_Risk_Charge

def BSCR_IR_Risk_Actual(EBS, LiabSummary):
    
    BSCR_IR_Risk_Charge = {'Agg': {}, 'LT': {}, 'GI': {}}
    
    # FI duration    
    Actual_FI_Dur_MV_LT = EBS['LT'].FWA_MV_FI + EBS['LT'].Fixed_Inv_Surplus + EBS['LT'].Cash + EBS['LT'].Other_Assets + (EBS['LT'].FWA_Acc_Int - EBS['LT'].Acc_Int_Liab) # include ALBA accrued interest
    Actual_FI_Dur_MV_PC = EBS['GI'].FWA_MV_FI + EBS['GI'].Fixed_Inv_Surplus + EBS['GI'].Cash + EBS['GI'].Other_Assets
    Actual_FI_Dur_MV_Agg = Actual_FI_Dur_MV_LT + Actual_FI_Dur_MV_PC
    
    Actual_FI_Dur_LT = EBS['LT'].FI_Dur
    Actual_FI_Dur_PC = EBS['GI'].FI_Dur
    Actual_FI_Dur = EBS['Agg'].FI_Dur
    
    # Liability duration   
    Actual_Liab_Dur_Agg = LiabSummary['Agg']['duration']
    Actual_PV_BE_Agg = LiabSummary['Agg']['PV_BE']-UI.ALBA_adj
    
    Actual_Liab_Dur_LT = LiabSummary['LT']['duration']
    Actual_PV_BE_LT = LiabSummary['LT']['PV_BE']-UI.ALBA_adj
    
    Actual_Liab_Dur_PC = LiabSummary['GI']['duration']
    Actual_PV_BE_PC = LiabSummary['GI']['PV_BE']
    
    # Interest risk calculation   
    BSCR_IR_Risk_Charge['Agg']  = BSCR_IR_Risk(Actual_FI_Dur_MV_Agg, Actual_FI_Dur, Actual_PV_BE_Agg, Actual_Liab_Dur_Agg)
    BSCR_IR_Risk_Charge['LT']   = BSCR_IR_Risk(Actual_FI_Dur_MV_LT, Actual_FI_Dur_LT, Actual_PV_BE_LT, Actual_Liab_Dur_LT)
    BSCR_IR_Risk_Charge['GI']   = BSCR_IR_Risk(Actual_FI_Dur_MV_PC, Actual_FI_Dur_PC, Actual_PV_BE_PC, Actual_Liab_Dur_PC)
    
    return BSCR_IR_Risk_Charge

def BSCR_Ccy(portInput,baseLiabAnalytics):
    BSCR_Ccy = {}
    MVA = portInput.groupby('Fort Re Corp Segment')['Market Value with Accrued Int USD GAAP'].sum()
    MVA_alba = MVA.loc['ALBA'].sum()
    alba_tp = -baseLiabAnalytics[34].Technical_Provision
    if alba_tp*1.05 > MVA_alba:
        BSCR_Ccy_risk = (alba_tp*1.05 - MVA_alba)*0.25
    else:
        BSCR_Ccy_risk = 0
    
    BSCR_Ccy = {"Agg": BSCR_Ccy_risk, "LT": BSCR_Ccy_risk, "GI": 0}  
        
    return BSCR_Ccy

def BSCR_Con_Risk_Charge(base_date, eval_date, portInput, workDir, regime, AssetAdjustment): 
    
    BSCR_Con_Risk = {}
    
    portInput = portInput[(portInput['Issuer Name'] != 'SOURCE UNDEFINED') & (portInput['Issuer Name'] != 'AIGGRE U.S. Real Estate Fund I LP') & (portInput['Issuer Name'] != 'AIGGRE U.S. Real Estate Fund II LP')]
    portInputAgg = portInput.groupby(['Issuer LE ID', 'Issuer Name'])['MV_USD_GAAP'].sum()
    
    portInputAccount = portInput.groupby(['Issuer LE ID', 'Issuer Name', 'Fort Re Corp Segment'])['MV_USD_GAAP'].sum()    
    portInputAccount = portInputAccount.reset_index()
    
    LTList = ['Long Term Surplus', 'ModCo', 'ALBA']
    GIList = ['LPT', 'General Surplus']
    
    portInputLT = portInputAccount[portInputAccount['Fort Re Corp Segment'].isin(LTList)]
    portInputGI = portInputAccount[portInputAccount['Fort Re Corp Segment'].isin(GIList)]
    
    portInputLT = portInputLT.groupby(['Issuer LE ID','Issuer Name'])['MV_USD_GAAP'].sum()
    portInputGI = portInputGI.groupby(['Issuer LE ID','Issuer Name'])['MV_USD_GAAP'].sum()
    
    Conrisk_top_10_Agg = portInputAgg.to_frame().nlargest(10, 'MV_USD_GAAP')       
    Conrisk_top_10_LT = portInputLT.to_frame().nlargest(10, 'MV_USD_GAAP')
    Conrisk_top_10_GI = portInputGI.to_frame().nlargest(10, 'MV_USD_GAAP')
    
#    Conrisk_output_Agg = Conrisk_top_20_Agg.sort_values(by = ['MV_USD_GAAP']).reset_index()
#    Conrisk_output_LT = Conrisk_top_20_LT.sort_values(by = ['MV_USD_GAAP']).reset_index()
#    Conrisk_output_GI = Conrisk_top_20_GI.sort_values(by = ['MV_USD_GAAP']).reset_index()    
    
    if not isinstance(AssetAdjustment, pd.DataFrame):
        excel_file_Agg_name = r'.\Concentration risk top 10_Agg_' + eval_date.strftime('%Y%m%d') + '.xlsx'
        excel_file_LT_name = r'.\Concentration risk top 10_LT_' + eval_date.strftime('%Y%m%d') + '.xlsx'
        excel_file_GI_name = r'.\Concentration risk top 10_GI_' + eval_date.strftime('%Y%m%d') + '.xlsx'
#        Conrisk_file_current = r'.\Concentration risk top 10_Current_' + eval_date.strftime('%Y%m%d') + '.xlsx'
#        Conrisk_file_future = r'.\Concentration risk top 10_Future_' + eval_date.strftime('%Y%m%d') + '.xlsx'
    else:
        excel_file_Agg_name = r'.\Concentration risk top 10_Agg.xlsx'
        excel_file_LT_name = r'.\Concentration risk top 10_LT.xlsx'
        excel_file_GI_name = r'.\Concentration risk top 10_GI.xlsx'
#        Conrisk_file_current = r'.\Concentration risk top 10_Current.xlsx'
#        Conrisk_file_future = r'.\Concentration risk top 10_Future.xlsx'
    
    currDir = os.getcwd()
    os.chdir(workDir)
    
    Conrisk_top_10_Agg.to_excel(excel_file_Agg_name, sheet_name = 'Agg', header = True, index = True)
    Conrisk_top_10_LT.to_excel(excel_file_LT_name, sheet_name = 'LT', header = True, index = True)
    Conrisk_top_10_GI.to_excel(excel_file_GI_name, sheet_name = 'GI', header = True, index = True)
    
#    ### Action required: update top-10 issuers ###
#    input("Please update the Top 10 issuers in " + workDir + " for both Current OR Future (LOC) regimes" + " \nOnce finished,\nPress Enter to continue ...")         
#    print('\n')

    if regime =="Current":
        Conrisk_Agg_current = pd.read_excel(excel_file_Agg_name, sheetname = 'Agg')
        Conrisk_LT_current = pd.read_excel(excel_file_LT_name, sheetname = 'LT') 
        Conrisk_GI_current = pd.read_excel(excel_file_GI_name, sheetname = 'GI')
            
        AggTop10_current = Conrisk_Agg_current['Issuer Name']
        LTTop10_current = Conrisk_LT_current['Issuer Name']
        GITop10_current = Conrisk_GI_current['Issuer Name']
    
        Conrisk_Calc = portInput.groupby(['Issuer Name','Fort Re Corp Segment'])['AssetCharge_Current'].sum()
        
        BSCR_Con_Risk['Agg'] = Conrisk_Calc.loc[(AggTop10_current)].sum()
        BSCR_Con_Risk['LT'] = Conrisk_Calc.loc[(LTTop10_current,LTList),].sum()
        BSCR_Con_Risk['GI'] = Conrisk_Calc.loc[(GITop10_current,GIList),].sum()
        
    elif regime =="Future":
        Conrisk_Agg_future = pd.read_excel(excel_file_Agg_name, sheetname = 'Agg')
        Conrisk_LT_future = pd.read_excel(excel_file_LT_name, sheetname = 'LT') 
        Conrisk_GI_future = pd.read_excel(excel_file_GI_name, sheetname = 'GI')
            
        AggTop10_future = Conrisk_Agg_future['Issuer Name']
        LTTop10_future = Conrisk_LT_future['Issuer Name']
        GITop10_future = Conrisk_GI_future['Issuer Name']
        
        Conrisk_Calc = portInput.groupby(['Issuer Name','Fort Re Corp Segment'])['AssetCharge_Future'].sum()
        
        if not isinstance(AssetAdjustment, pd.DataFrame):
            BSCR_Con_Risk['Agg'] = Conrisk_Calc.loc[(AggTop10_future)].sum() + 400000000 * 0.2
            BSCR_Con_Risk['LT'] = Conrisk_Calc.loc[(LTTop10_future,LTList),].sum()
            BSCR_Con_Risk['GI'] = Conrisk_Calc.loc[(GITop10_future,GIList),].sum() + UI.EBS_Inputs[base_date]['GI']['LOC'] * 0.2
        else:
            BSCR_Con_Risk['Agg'] = Conrisk_Calc.loc[(AggTop10_future)].sum() + 400000000 * 0.2
            BSCR_Con_Risk['LT'] = Conrisk_Calc.loc[(LTTop10_future,LTList),].sum()
            BSCR_Con_Risk['GI'] = Conrisk_Calc.loc[(GITop10_future,GIList),].sum() + AssetAdjustment[AssetAdjustment['BMA_Category'] == 'LOC']['MV_USD_GAAP'].values[0] * 0.2
    
    os.chdir(currDir)        
    return BSCR_Con_Risk

def BSCR_Market_Risk_Charge(BSCR, Regime):
    
    BSCR_Market_Risk_Charge = {'Agg': {}, 'LT': {}, 'GI': {}}
    
    accounts = ['LT', 'GI', 'Agg']
    
    for each_account in accounts:
        FI  = BSCR['FI_Risk'][each_account]
        EQ  = BSCR['Equity_Risk'][each_account]
        IR  = BSCR['Interest_Risk'][each_account]
        CUR = BSCR['Currency_Risk'][each_account]
        CON = BSCR['Concentration_Risk'][each_account]
        
        if Regime == "Current":
            Market_cor = BSCR_Config.Market_cor_Current
            
        elif Regime == "Future":
            Market_cor = BSCR_Config.Market_cor_Future        
            
        Market_RC = pd.DataFrame(data = [FI, EQ, IR, CUR,CON],index = ['Fixed_income', 'Equity', 'Interest_rate','Currency','Concentration'])
        Market_RC_trans = Market_RC.transpose()
    
        BSCR_Market_Risk_Charge[each_account] = np.sqrt(Market_RC_trans @ Market_cor @ Market_RC).values[0][0]
    
    return BSCR_Market_Risk_Charge

def BSCR_TaxCredit(BSCR_Components, EBS, LiabSummary, regime):
   
    if regime =="Current":         
        Tax_Credit = 0
        
    elif regime =="Future":
        Tax_Credit = min(UI.tax_rate * BSCR_Components.BSCR_Bef_Tax_Adj, 0.2 * BSCR_Components.BSCR_Bef_Tax_Adj, sum([EBS.DTA_DTL, BSCR_Components.tax_sharing, UI.tax_rate * LiabSummary['Risk_Margin']]))
            
    return Tax_Credit

def BSCR_Aggregate(BSCR_Components, Regime, OpRiskCharge):
    
    BSCR_result = {}
    
    if Regime == 'Current':
        
        BSCR_result['BSCR_agg'] = math.sqrt((BSCR_Components.FI_Risk**2+BSCR_Components.Equity_Risk**2+BSCR_Components.IR_Risk**2+BSCR_Components.Currency_Risk**2+BSCR_Components.Concentration_Risk**2+BSCR_Components.Premium_Risk**2+BSCR_Components.Cat_Risk**2
                                +(BSCR_Components.Mortality_Risk+BSCR_Components.StopLoss_Risk+BSCR_Components.Riders_Risk)**2+BSCR_Components.Morbidity_Risk**2+BSCR_Components.Longevity_Risk**2+BSCR_Components.VA_Guarantee_Risk**2+BSCR_Components.OtherInsurance_Risk**2
                                +(BSCR_Components.Reserve_Risk+BSCR_Components.Net_Credit_Risk/2)**2+(BSCR_Components.Net_Credit_Risk/2)**2-0.5*((BSCR_Components.Mortality_Risk+BSCR_Components.StopLoss_Risk+BSCR_Components.Riders_Risk)*BSCR_Components.Longevity_Risk)))    
        
        BSCR_result['BSCR_Net_Market_Risk']  = BSCR_Components.FI_Risk + BSCR_Components.Equity_Risk + BSCR_Components.IR_Risk + BSCR_Components.Currency_Risk + BSCR_Components.Concentration_Risk
        BSCR_result['Net_LT_Insurance_Risk'] = BSCR_Components.Mortality_Risk + BSCR_Components.StopLoss_Risk + BSCR_Components.Riders_Risk + BSCR_Components.Morbidity_Risk + BSCR_Components.Longevity_Risk + BSCR_Components.VA_Guarantee_Risk + BSCR_Components.OtherInsurance_Risk
    
    elif Regime == 'Future':
        Market  = BSCR_Components.Market_Risk
        Credit  = 0
        PC      = BSCR_Components.Reserve_Risk
        LT      = BSCR_Components.LT_Risk
                           
        Agg_BSCR = pd.DataFrame(data = [Market, Credit, PC, LT], index = ['Market_Risk', 'Credit_Risk', 'PC_Risk','LT_Risk'])        
        Agg_BSCR_trans = Agg_BSCR.transpose()
        
        Total_cor = BSCR_Cofig.Total_cor
        
        BSCR_result['BSCR_agg'] = np.sqrt(Agg_BSCR_trans @ Total_cor @ Agg_BSCR).values[0][0]
        
        BSCR_result['BSCR_Net_Market_Risk']  = BSCR_Components.Market_Risk
        BSCR_result['Net_LT_Insurance_Risk'] = BSCR_Components.LT_Risk
    
        
    BSCR_result['BSCR_sum'] = BSCR_Components.FI_Risk + BSCR_Components.Equity_Risk + BSCR_Components.IR_Risk + BSCR_Components.Currency_Risk + BSCR_Components.Concentration_Risk + BSCR_Components.Net_Credit_Risk + BSCR_Components.Premium_Risk + BSCR_Components.Reserve_Risk + BSCR_Components.Cat_Risk + BSCR_Components.Mortality_Risk \
               + BSCR_Components.StopLoss_Risk + BSCR_Components.Riders_Risk + BSCR_Components.Morbidity_Risk + BSCR_Components.Longevity_Risk + BSCR_Components.VA_Guarantee_Risk + BSCR_Components.OtherInsurance_Risk
    BSCR_result['Net_Credit_Risk']       = BSCR_Components.Net_Credit_Risk
    BSCR_result['Net_PC_Insurance_Risk'] = BSCR_Components.Premium_Risk + BSCR_Components.Reserve_Risk + BSCR_Components.Cat_Risk
    
    BSCR_result['OpRisk_Chage_pct']      = OpRiskCharge
    BSCR_result['OpRisk_Chage']          = BSCR_result['BSCR_agg'] * OpRiskCharge
    BSCR_result['BSCR_Bef_Tax_Adj']      = BSCR_result['BSCR_agg'] + BSCR_result['OpRisk_Chage']

    return BSCR_result

def proj_BSCR_asset_risk_charge(BMA_alloc, BMA_asset_risk_charge = BSCR_Config.BSCR_Asset_Risk_Charge_v1):
    avg_asset_charge = 0
    for each_BMA_ac, each_alloc in BMA_alloc.items():
        avg_asset_charge += BMA_asset_risk_charge[each_BMA_ac]['Risk_Charge'] * each_alloc
    
    return avg_asset_charge
