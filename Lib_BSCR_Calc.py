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
import Class_Corp_Model as Corp_Class

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

    grade_year       = IAL.Date.yearFrac("ACT/365",  start_date, eval_date)
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
            if each_group != 'PC' or (each_group == "PC" and each_risk_type  == 'Other_Ins & Disability'):
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