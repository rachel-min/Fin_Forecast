# -*- coding: utf-8 -*-
"""
Created on Wed May 22 23:05:57 2019

@author: seongpar
"""
import os
import datetime
import copy
import math as math
import pandas as pd
import numpy as np
import Config_BSCR as BSCR_Config
import User_Input_Dic as UI
import Lib_Corp_Model as Corp
import Lib_Market_Akit as IAL_App

# load akit DLL into python
akit_dir = 'C:/AKit v4.1.0/BIN'
os.sys.path.append(akit_dir)
#import IALPython3        as IAL
#import App_daily_portfolio_feed as Asset_App

#valDate        = datetime.datetime(2019, 3, 31)
# =============================================================================
# # load Corp Model Folder DLL into python
# corp_model_dir = 'L:\\DSA Re\\Workspace\\Production\2019_Q2\\BMA Best Estimate\\Main_Run_v003\\Step 2 Python Parallel'
# os.sys.path.append(corp_model_dir)
# =============================================================================

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
        
        Total_cor = BSCR_Config.Total_cor
        
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
       

def BSCR_IR_Risk(FI_MV, FI_Dur, PV_BE, Liab_Dur):
    Liab_dur_scaled = Liab_Dur * PV_BE / FI_MV                                       
    Dur_mismatch    = abs(Liab_dur_scaled - FI_Dur)
    IR_Risk_Charge  = FI_MV * max(1, Dur_mismatch) * 0.02 * 0.5
    
    return IR_Risk_Charge


def BSCR_Mort_Risk(baseLiabAnalytics, numOfLoB, Proj_Year, eval_date, mort_charge_table=BSCR_Config.Mort_Charge):
    print(' Mortality BSCR ...')
    Mort_LOB = ['UL', 'WL', 'ROP']
         
    key2=[0]
    key = sorted(mort_charge_table.keys())
    
    for i in range(len(key) - 1):
        key2.append(key[i])

    Diff = [i - j for i, j in zip(key, key2)]
        
    # Set up Mort_Risk Dictionary        
    Face_Amount    =  {}
    PVBE           =  {}
    BSCR_Mort_Risk =  {}
    Naar           =  {}
        
    for idx in range(1, numOfLoB + 1, 1):  
             
        BSCR_LOB = baseLiabAnalytics[idx].LOB_Def['BSCR LOB']
                
        PVBE[BSCR_LOB]          = {}
        Face_Amount[BSCR_LOB]   = {}
        Naar[BSCR_LOB]          = {}
        PVBE['Total']           = {}
        Face_Amount['Total']    = {}
        Naar['Total']           = {}
        BSCR_Mort_Risk[BSCR_LOB]= {}
                
        for t in range(0, Proj_Year + 1, 1):
                              
            PVBE[BSCR_LOB][t]           = 0  
            Face_Amount[BSCR_LOB][t]    = 0
            Naar[BSCR_LOB][t]           = 0
            PVBE['Total'][t]            = 0  
            Face_Amount['Total'][t]     = 0
            Naar['Total'][t]            = 0  
            BSCR_Mort_Risk[BSCR_LOB][t] = 0
   
    # Sum up PVBE, faceamount and Narr               
    for t in range(0, Proj_Year + 1, 1):
        
        for idx in range(1, numOfLoB + 1, 1): 
            
            try:
                cf_idx = baseLiabAnalytics[idx].cashflow[0]
            except:
                cf_idx = baseLiabAnalytics[idx].cashflow
                
            BSCR_LOB  = baseLiabAnalytics[idx].LOB_Def['BSCR LOB']
            Risk_Type = baseLiabAnalytics[idx].LOB_Def['Risk Type']
                            
            if Risk_Type  == "Mortality":
                
                if t == 0 and cf_idx['Period'][0] != eval_date:
                    Face_Amount['Total'][t] += (cf_idx['Total net face amount'][0] * (cf_idx['Period'][1] - eval_date).days + \
                                                cf_idx['Total net face amount'][1] * (eval_date - cf_idx['Period'][0]).days ) / \
                                               (cf_idx['Period'][1] - cf_idx['Period'][0]).days                
                else:
                    Face_Amount['Total'][t] += cf_idx['Total net face amount'][t]
                                                
                PVBE['Total'][t] += abs(baseLiabAnalytics[idx].EBS_PVBE[t])
                Naar['Total'][t]  = Face_Amount['Total'][t] - PVBE['Total'][t]
                                    
                if BSCR_LOB in Mort_LOB:
                    
                    if t == 0 and cf_idx['Period'][0] != eval_date:
                        Face_Amount[BSCR_LOB][t] += (cf_idx['Total net face amount'][0] * (cf_idx['Period'][1] - eval_date).days + \
                                                     cf_idx['Total net face amount'][1] * (eval_date - cf_idx['Period'][0]).days ) / \
                                                    (cf_idx['Period'][1] - cf_idx['Period'][0]).days
                    else:                           
                        Face_Amount[BSCR_LOB][t] += cf_idx['Total net face amount'][t]

                    PVBE[BSCR_LOB][t] += abs(baseLiabAnalytics[idx].EBS_PVBE[t])
                    Naar[BSCR_LOB][t]  = Face_Amount[BSCR_LOB][t] - PVBE[BSCR_LOB][t]        
         
    # Calculate Mortality BSCR for each LOB
    for each_LOB in Mort_LOB:
        
        BSCR_Mort_Risk[each_LOB] = {}
        
        for t in range(0, Proj_Year + 1, 1):
            BSCR_Mort_Risk[each_LOB][t] = 0
        
            for i in range(len(key)):
            
                if key[i] > Naar[each_LOB][t]:
                
                    BSCR_Mort_Risk[each_LOB][t] += (Naar[each_LOB][t] - key2[i]) * mort_charge_table[key[i]]
                    break
            
                else:
                
                    BSCR_Mort_Risk[each_LOB][t] += Diff[i] * mort_charge_table[key[i]]
        
    # Calculate Mortality BSCR for Aggregate
    BSCR_Mort_Risk['Total'] = {}
        
    for t in range(0, Proj_Year + 1, 1):
        BSCR_Mort_Risk['Total'][t] = 0
     
        for i in range(len(key)):
            
            if key[i] > Naar['Total'][t]:
                
                BSCR_Mort_Risk['Total'][t] += (Naar['Total'][t] - key2[i]) * mort_charge_table[key[i]]
                break
            
            else:
                
                BSCR_Mort_Risk['Total'][t] += Diff[i] * mort_charge_table[key[i]]
    
    return BSCR_Mort_Risk

def BSCR_Long_Risk_factor(BSCR_LOB, valDate, long_age = UI.long_age, long_dis = UI.long_dis, long_c = BSCR_Config.Long_Charge, long_f = UI.long_f):
    
    inpay = []
    
    for key, val in long_c['Inpay'].items():
        
        inpay.append(val)

    deferred = []
    
    for key, val  in long_c['Deferred'].items():
        
        deferred.append(val)
   
    inpay_c = pd.DataFrame(data=inpay).transpose()
    deferred_c = pd.DataFrame(data=deferred).transpose()
    
    inpayment=long_f['inpayment'][BSCR_LOB]
    inpayment_f=pd.DataFrame(data=inpayment)
    
    deferred=long_f['deferred'][BSCR_LOB]
    deferred_f=pd.DataFrame(data=deferred)

    time_zero_inpay = inpay_c.dot(inpayment_f).iat[0,0]
    time_zero_def = deferred_c.dot(deferred_f).iat[0,0]
    
    charge_inpay=[time_zero_inpay]
    charge_def = [time_zero_def]
     
    for i in range(1,100):
        charge_inpay.append(min(long_c['ult_c']['inpay'], (long_c['ult_c']["inpay"]-time_zero_inpay)/(long_age['ult_inpay']-long_age["inpayment"][BSCR_LOB])*(1-int(valDate.strftime('%m'))/12+i-1 + 1*(int(valDate.strftime('%m'))/12==1) )+time_zero_inpay))
        
            
    for i in range(1,100):
        charge_def.append(min(long_c['ult_c']['deferred'], (long_c['ult_c']["deferred"]-time_zero_def)/(long_age['ult_def']-long_age["deferred"][BSCR_LOB])*(1-int(valDate.strftime('%m'))/12+i-1 + 1*(int(valDate.strftime('%m'))/12==1) )+time_zero_def))
               
        
    charge = [i*long_dis[BSCR_LOB]['inpayment']+j*long_dis[BSCR_LOB]['deferred'] for i,j in zip(charge_inpay,charge_def)]
    
    return charge           
    
def BSCR_Long_Risk_Charge(baseLiabAnalytics, numOfLoB, Proj_Year, valDate):
    print(' Longevity BSCR ...')
    
    BSCR_Long_Risk = {}       
    PVBE           = {}    
        
    Long_LOB = ['SS', 'SPIA', 'TFA', 'ALBA']
 
    
    # Set up Long_Risk Dictionary
    for idx in range(1, numOfLoB + 1, 1):
        
        BSCR_LOB = baseLiabAnalytics[idx].LOB_Def['BSCR LOB']

#        if BSCR_LOB in Long_LOB:
            
        PVBE[BSCR_LOB] = {}
        BSCR_Long_Risk[BSCR_LOB] = {}
            
        for t in range(0, Proj_Year + 1, 1):
                              
            PVBE[BSCR_LOB][t] = 0   
            BSCR_Long_Risk[BSCR_LOB][t] = 0

    # Sum up PVBE    
    for t in range(0, Proj_Year + 1, 1):
        
        for idx in range(1, numOfLoB + 1, 1):
            
            BSCR_LOB  = baseLiabAnalytics[idx].LOB_Def['BSCR LOB']
            Risk_Type = baseLiabAnalytics[idx].LOB_Def['Risk Type']
            
            if BSCR_LOB in Long_LOB:                                
                
                if Risk_Type == 'Longevity': 
                         
                    PVBE[BSCR_LOB][t] += abs(baseLiabAnalytics[idx].EBS_PVBE[t])
    
    # Calculate Longevity BSCR                                               
    for each_LOB in Long_LOB:
        
        long_f = BSCR_Long_Risk_factor(each_LOB, valDate)  
        BSCR_Long_Risk[each_LOB] = {}    
        
        for t in range(0, Proj_Year + 1, 1):    

            BSCR_Long_Risk[each_LOB][t] = PVBE[each_LOB][t] * long_f[t]
    
    # Sum up Longevity BSCR
    BSCR_Long_Risk['Total']  = {}           
    for t in range(0, Proj_Year + 1, 1):
        BSCR_Long_Risk['Total'][t] = 0
        
        for each_LOB in Long_LOB:        
            BSCR_Long_Risk['Total'][t] += BSCR_Long_Risk[each_LOB][t]
    
    return BSCR_Long_Risk


def BSCR_Morb_Charge(baseLiabAnalytics, numOfLoB, Proj_Year, morb_f = BSCR_Config.Morb_Charge, morb_d = UI.morbidity):
    print(' Morbidity BSCR ...')
    
    BSCR_Morb_Risk = {} 
    PVBE           = {}  
    Premium        = {}
    
    Morb_LOB = ['AH', 'LTC', 'PC'] # NUFIC's BSCR_LOB is PC
    
    # Set up Morb_Risk Dictionary
    for idx in range(1, numOfLoB + 1, 1):        
        Risk_Type = baseLiabAnalytics[idx].LOB_Def['Risk Type']
        BSCR_LOB  = baseLiabAnalytics[idx].LOB_Def['BSCR LOB']
        BSCR_Morb_Risk[BSCR_LOB] = {}
        
        if Risk_Type == 'Morbidity & Disability':
            if BSCR_LOB in Morb_LOB:            
                PVBE[BSCR_LOB]    = {}
                Premium[BSCR_LOB] = {}
                
                for t in range(0, Proj_Year + 1, 1):                              
                    PVBE[BSCR_LOB][t]    = 0 
                    Premium[BSCR_LOB][t] = 0
                    
    # Sum up PVBE               
    for t in range(0, Proj_Year + 1, 1):        
        for idx in range(1, numOfLoB + 1, 1):
            Risk_Type = baseLiabAnalytics[idx].LOB_Def['Risk Type']
            BSCR_LOB  = baseLiabAnalytics[idx].LOB_Def['BSCR LOB']
            BSCR_Morb_Risk[BSCR_LOB][t] = 0
            
            if Risk_Type == 'Morbidity & Disability':            
                if BSCR_LOB in Morb_LOB:                
                    PVBE[BSCR_LOB][t] += abs(baseLiabAnalytics[idx].EBS_PVBE[t])
                    
                    if t != 0:
                        try:
                            Premium[BSCR_LOB][t - 1] += baseLiabAnalytics[idx].cashflow[0]['Total premium'][t]
                        except:
                            Premium[BSCR_LOB][t - 1] += baseLiabAnalytics[idx].cashflow['Total premium'][t]

    for t in range(0, Proj_Year + 1, 1): 
        PVBE['AH'][t]    += PVBE['PC'][t]
        Premium['AH'][t] += Premium['PC'][t]
                     
    # Calculate Morbidity BSCR                                               
    for each_LOB in ['AH', 'LTC']:
        BSCR_Morb_Risk[each_LOB] = {}    
        
        
        for t in range(0, Proj_Year + 1, 1):    
            if each_LOB == 'LTC':                                       
                BSCR_Morb_Risk[each_LOB][t] = PVBE[each_LOB][t] * morb_f["Disability income: claims in payment Waiver of premium and long-term care"] * morb_d['LTC']['inpayment'] \
                                            + Premium[each_LOB][t] * morb_f["Disability Income: Active Lives, Prem guar ≤ 1 Yr; Benefit Period > 2 Years"]
                
            elif each_LOB == 'AH':                
                BSCR_Morb_Risk[each_LOB][t] = PVBE[each_LOB][t] * morb_f["Disability income: claims in payment Other accident and sickness"] * morb_d['AH']['inpayment'] \
                                            + Premium[each_LOB][t] * morb_f["Disability Income: Active lives, Other Accident and Sickness"]
    # Sum up Morbidity BSCR
    BSCR_Morb_Risk['Total']  = {}           
    for t in range(0, Proj_Year + 1, 1):             
            BSCR_Morb_Risk['Total'][t] = BSCR_Morb_Risk['AH'][t] + BSCR_Morb_Risk['LTC'][t]
       
    return BSCR_Morb_Risk          


# Xi 7/2/2019; Vincent update on 07/11/2019       
def BSCR_Other_Charge(baseLiabAnalytics, numOfLoB, Proj_Year, other_f = BSCR_Config.Other_Charge):
    print(' Other BSCR ...')    
    
    BSCR_Other_Risk = {}       
    PVBE            = {} 
    
    # Set up Other_Risk Dictionary
    for idx in range(1, numOfLoB + 1, 1):        
        BSCR_LOB       = baseLiabAnalytics[idx].LOB_Def['BSCR LOB']                                
        PVBE[BSCR_LOB] = {}  
        BSCR_Other_Risk[BSCR_LOB] = {}
        
        for t in range(0, Proj_Year + 1, 1):                              
            PVBE[BSCR_LOB][t] = 0 
            BSCR_Other_Risk[BSCR_LOB][t] = 0
            
    # Sum up PVBE               
    for t in range(0, Proj_Year + 1, 1):        
        for idx in range(1, numOfLoB + 1, 1):
            BSCR_LOB  = baseLiabAnalytics[idx].LOB_Def['BSCR LOB']                                   
            
            if baseLiabAnalytics[idx].LOB_Def['Agg LOB'] == 'LR': # NUFIC's BSCR_LOB is PC
                try: 
                    PVBE[BSCR_LOB][t] += abs(baseLiabAnalytics[idx].EBS_PVBE[t])
                except:
                    PVBE[BSCR_LOB][t] += 0
        PVBE['AH'][t] += PVBE['PC'][t]                
          
    # Calculate Other BSCR                                               
    for each_LOB in ['UL','WL','ROP', 'AH', 'LTC', 'SS','TFA','SPIA','ALBA']:
        BSCR_Other_Risk[each_LOB] = {}
        
        for t in range(0, Proj_Year + 1, 1):
            if each_LOB in ['UL','WL','ROP']:
                BSCR_Other_Risk[each_LOB][t] = PVBE[each_LOB][t] * other_f["Mortality (term insurance, whole life, universal life)"]
                
            elif each_LOB in ['SS','TFA','SPIA','ALBA']:
                BSCR_Other_Risk[each_LOB][t] = PVBE[each_LOB][t] * other_f["Longevity (immediate pay-out annuities, contingent annuities, pension pay-outs)"]
            
            elif each_LOB =='AH':
                BSCR_Other_Risk[each_LOB][t] = PVBE[each_LOB][t] * \
                                              (other_f["Critical Illness (including accelerated critical illness products)"] * UI.morbidity['AH']['critical'] \
                                             + other_f["Disability Income: active lives - other accident and sickness"] * UI.morbidity['AH']['active']        \
                                             + other_f["Disability Income: claims in payment - other accident and sickness"] * (1 - UI.morbidity['AH']['critical'] - UI.morbidity['AH']['active']) )
            elif each_LOB =='LTC':
                BSCR_Other_Risk[each_LOB][t] = PVBE[each_LOB][t] * \
                                              (other_f["Disability Income: active lives - including waiver of premium and long-term care"] * UI.morbidity['LTC']['active'] \
                                             + other_f["Disability Income: claims in payment - including waiver of premium and long-term care"] * (1 - UI.morbidity['LTC']['active']) )
   
    # Sum up Other BSCR
    BSCR_Other_Risk['Life']    = {} 
    BSCR_Other_Risk['Annuity'] = {} 
    BSCR_Other_Risk['Total']   = {} 
          
    for t in range(0, Proj_Year + 1, 1):             
        BSCR_Other_Risk['Life'][t]    = BSCR_Other_Risk['UL'][t] + BSCR_Other_Risk['WL'][t] + BSCR_Other_Risk['AH'][t] + BSCR_Other_Risk['LTC'][t] + BSCR_Other_Risk['ROP'][t]
        BSCR_Other_Risk['Annuity'][t] = BSCR_Other_Risk['SS'][t] + BSCR_Other_Risk['SPIA'][t] + BSCR_Other_Risk['TFA'][t] + BSCR_Other_Risk['ALBA'][t]   
        BSCR_Other_Risk['Total'][t]   = BSCR_Other_Risk['Life'][t] + BSCR_Other_Risk['Annuity'][t]
        
    return BSCR_Other_Risk

# as a placeholder
def BSCR_Stoploss_Charge(baseLiabAnalytics, numOfLoB, Proj_Year):
    
    BSCR_Stoploss = {}
    BSCR_Stoploss['Total'] = {}
    
    for idx in range(1, numOfLoB + 1, 1): 
        BSCR_LOB       = baseLiabAnalytics[idx].LOB_Def['BSCR LOB'] 
        BSCR_Stoploss[BSCR_LOB] = {}
        
        for t in range(0, Proj_Year + 1, 1): 
            BSCR_Stoploss[BSCR_LOB][t] = 0
            BSCR_Stoploss['Total'][t] = 0
    
    return BSCR_Stoploss
        
# as a placeholder
def BSCR_Riders_Charge(baseLiabAnalytics, numOfLoB, Proj_Year):
    
    BSCR_Riders = {}
    BSCR_Riders['Total'] = {}
    
    for idx in range(1, numOfLoB + 1, 1): 
        BSCR_LOB       = baseLiabAnalytics[idx].LOB_Def['BSCR LOB'] 
        BSCR_Riders[BSCR_LOB] = {}
        
        for t in range(0, Proj_Year + 1, 1): 
            BSCR_Riders[BSCR_LOB][t] = 0
            BSCR_Riders['Total'][t] = 0
    
    return BSCR_Riders    

# as a placeholder
def BSCR_VA_Charge(baseLiabAnalytics, numOfLoB, Proj_Year):
    
    BSCR_VA = {}
    BSCR_VA['Total'] = {}
    
    for idx in range(1, numOfLoB + 1, 1): 
        BSCR_LOB       = baseLiabAnalytics[idx].LOB_Def['BSCR LOB'] 
        BSCR_VA[BSCR_LOB] = {}
        
        for t in range(0, Proj_Year + 1, 1): 
            BSCR_VA[BSCR_LOB][t] = 0
            BSCR_VA['Total'][t] = 0
    
    return BSCR_VA  


# Vincent - 07/12/2019
def BSCR_LT_Charge(BSCR, Proj_Year, Regime, LT_cor = BSCR_Config.LT_cor):
    print(' Long-Term BSCR ...')
    
    LT_Mort = {}
    for t in range(0, Proj_Year + 1, 1):
        LT_Mort[t] = 0
        
        for key, value in BSCR.items():       
            if 'Total' in value.keys() and key in ['BSCR_Mort', 'BSCR_Stoploss', 'BSCR_Riders']: 
                # Adding value of sharpness to sum 
                try:
                    LT_Mort[t] += value['Total'][t] 
                except:
                    LT_Mort[t] += 0
                    
    LT_Mort = pd.DataFrame(data = LT_Mort.items(), columns = ['Year', 'Mort']).loc[:,'Mort']
    
    LT_Mort = pd.DataFrame(data = BSCR['BSCR_Mort']['Total'].items(), columns = ['Year', 'Mort']).loc[:,'Mort']
    LT_Stoploss = pd.DataFrame(data = BSCR['BSCR_Stoploss']['Total'].items(), columns = ['Year', 'Stoploss']).loc[:,'Stoploss']
    LT_Riders = pd.DataFrame(data = BSCR['BSCR_Riders']['Total'].items(), columns = ['Year', 'Riders']).loc[:,'Riders']
    LT_Morb = pd.DataFrame(data = BSCR['BSCR_Morb']['Total'].items(), columns = ['Year', 'Morb']).loc[:,'Morb']
    LT_Long = pd.DataFrame(data = BSCR['BSCR_Long']['Total'].items(), columns = ['Year', 'Long']).loc[:,'Long']
    LT_VA   = pd.DataFrame(data = BSCR['BSCR_VA']['Total'].items(), columns = ['Year', 'VA']).loc[:,'VA']
    LT_Other= pd.DataFrame(data = BSCR['BSCR_Other']['Total'].items(), columns = ['Year', 'Other']).loc[:,'Other']
    
    if  Regime == "Current":    # Concentration
        BSCR_LT_Risk = np.sqrt( (LT_Mort + LT_Stoploss + LT_Riders) ** 2 + LT_Morb ** 2 + LT_Long ** 2 + LT_VA ** 2 + LT_Other ** 2 - 0.5 * ( (LT_Mort + LT_Stoploss + LT_Riders) * LT_Long ) )
     
    elif Regime == "Future":     # Correlation
        new_LT_RC = pd.concat([LT_Mort, LT_Stoploss, LT_Riders, LT_Morb, LT_Long, LT_VA, LT_Other], axis=1)             
        new_LT_RC_trans = new_LT_RC.transpose()
       
        new_LT_RC_array = np.array(new_LT_RC)
        new_LT_RC_trans_array = np.array(new_LT_RC_trans)

        BSCR_LT_Risk_before_diag = np.sqrt(new_LT_RC_array @ LT_cor @ new_LT_RC_trans_array) 
        BSCR_LT_Risk = [BSCR_LT_Risk_before_diag[i][i] for i in range(len(BSCR_LT_Risk_before_diag[0]))]
        BSCR_LT_Risk = pd.Series(BSCR_LT_Risk)
    
    return BSCR_LT_Risk

# Vincent update on 07/12/2019  
def BSCR_PC_Res_Charge(baseLiabAnalytics, numOfLoB, Proj_Year, regime = "Current", method = "Bespoke", pc_f = BSCR_Config.Reserve_Risk_Charge, pc_m = UI.PC_mapping, pc_cor = BSCR_Config.pc_cor):
    print(' PC Reserve BSCR ...')
    
    BSCR_PC_Risk = {}
    Risk_charge  = {}
    PVBE         = {}
    PC_BLOB      = ['Property', 'Personal_Accident', 'US_Casualty', 'US_Casualty_NP', 'US_Specialty', 'US_Specialty_NP']
    
    # Set up PC_Risk Dictionary
    for idx in range(1, numOfLoB + 1, 1):  
        BSCR_LOB       = baseLiabAnalytics[idx].LOB_Def['BSCR LOB']      
        
        BSCR_PC_Risk[BSCR_LOB] = {}
        
        if BSCR_LOB != "PC":
            
            for t in range(0, Proj_Year + 1, 1):
            
                BSCR_PC_Risk[BSCR_LOB][t] = 0
                                      
        if baseLiabAnalytics[idx].LOB_Def['Agg LOB'] == 'PC': 
            PVBE[idx] = {}        
        
            for t in range(0, Proj_Year + 1, 1):                              
                PVBE[idx][t] = 0 
            
    # Sum up BLOB PVBE               
    for t in range(0, Proj_Year + 1, 1):
        for idx in range(1, numOfLoB + 1, 1):                                             
            if baseLiabAnalytics[idx].LOB_Def['Agg LOB'] == 'PC':            
                try: 
                    PVBE[idx][t] += abs(baseLiabAnalytics[idx].EBS_PVBE[t])
                except:
                    PVBE[idx][t] += 0
           
    mapping  = pd.DataFrame(data = pc_m)
    LOB_PVBE = pd.DataFrame(data = PVBE)

    mapping_array  = np.array(mapping)
    LOB_PVBE_array = np.array(LOB_PVBE)
    
    BLOB_PVBE = LOB_PVBE_array @ mapping_array    
    BLOB_PVBE = pd.DataFrame(BLOB_PVBE, columns = mapping.columns)
 
    # Calculate PC BSCR   
    for each_BLOB in PC_BLOB:
        Risk_charge[each_BLOB] = BLOB_PVBE.loc[:, each_BLOB] * pc_f[method][each_BLOB]        
        
    new_PC_RC = [v for each_BLOB, v in Risk_charge.items()]
    
    if regime  == "Current":    # Concentration
        BSCR_PC = (0.4 * BLOB_PVBE.max(axis = 1) / BLOB_PVBE.sum(axis = 1) + 0.6) * sum(new_PC_RC)
        BSCR_PC = BSCR_PC.fillna(0).replace(-np.inf, 0)
        
    elif regime == "Future":     # Correlation
       new_PC_RC = pd.DataFrame(data = new_PC_RC)
       new_PC_RC_trans = pd.DataFrame(data = new_PC_RC).transpose()
       
       BSCR_PC_Risk_before_diag = np.sqrt(new_PC_RC_trans @ pc_cor @ new_PC_RC)       
       BSCR_PC = [BSCR_PC_Risk_before_diag[i][i] for i in range(len(BSCR_PC_Risk_before_diag[0]))]
       BSCR_PC = pd.Series(BSCR_PC).replace(-np.inf, 0)
       
    BSCR_PC_Risk['PC'] = BSCR_PC.to_dict()
       
    return BSCR_PC_Risk      
    
# Xi updated 7/16/2019   
def BSCR_FI_Risk_Charge(portInput, AssetAdjustment):
    print(' Fixed Income Investment Risk BSCR ...')
    
    BSCR_FI_Risk = {}     
    
    # Existing Asset Charge        
    BSCR_Asset_Risk_Charge = portInput.groupby(['FIIndicator','Fort Re Corp Segment'])['AssetCharge_Current'].sum()  
    
    BSCR_FI_EA_Risk_Charge_Agg = BSCR_Asset_Risk_Charge.loc[([1])].sum()
    BSCR_FI_EA_Risk_Charge_LT  = BSCR_Asset_Risk_Charge.loc[([1],['ALBA','Long Term Surplus','ModCo'])].sum()
    BSCR_FI_EA_Risk_Charge_GI  = BSCR_Asset_Risk_Charge.loc[([1],['LPT','General Surplus'])].sum()
    
    #Asset exposure
    FI_Asset_Exposure = portInput.groupby(['FIIndicator','Fort Re Corp Segment'])['MV_USD_GAAP'].sum()
    FI_Exposure_Agg   = FI_Asset_Exposure.loc[([1])].sum()
    FI_Exposure_LT    = FI_Asset_Exposure.loc[([1],['ALBA', 'Long Term Surplus', 'ModCo'])].sum()
    FI_Exposure_GI    = FI_Asset_Exposure.loc[([1], ['LPT', 'General Surplus'])].sum()
    
    # Adjustment Asset Charge
    if isinstance(AssetAdjustment, pd.DataFrame):
        BSCR_AssetAdjustment_Risk_Charge = AssetAdjustment.groupby(['FIIndicator','Fort Re Corp Segment'])['AssetCharge_Current'].sum()
        
        BSCR_FI_AA_Risk_Charge_Agg = BSCR_AssetAdjustment_Risk_Charge.loc[([1])].sum()
        BSCR_FI_AA_Risk_Charge_LT = BSCR_AssetAdjustment_Risk_Charge.loc[([1],['ALBA','Long Term Surplus','ModCo'])].sum()    
        BSCR_FI_AA_Risk_Charge_GI = BSCR_AssetAdjustment_Risk_Charge.loc[([1],['LPT','General Surplus'])].sum()
    
    else:        
        BSCR_FI_AA_Risk_Charge_LT = 0
        BSCR_FI_AA_Risk_Charge_GI = AssetAdjustment
        BSCR_FI_AA_Risk_Charge_Agg = BSCR_FI_AA_Risk_Charge_LT + BSCR_FI_AA_Risk_Charge_GI
        
    BSCR_FI_Risk['Agg'] = [BSCR_FI_EA_Risk_Charge_Agg + BSCR_FI_AA_Risk_Charge_Agg, (BSCR_FI_EA_Risk_Charge_Agg + BSCR_FI_AA_Risk_Charge_Agg) / FI_Exposure_Agg]
    BSCR_FI_Risk['LT']  = [BSCR_FI_EA_Risk_Charge_LT + BSCR_FI_AA_Risk_Charge_LT, (BSCR_FI_EA_Risk_Charge_LT + BSCR_FI_AA_Risk_Charge_LT) / FI_Exposure_LT]  
    BSCR_FI_Risk['GI']  = [BSCR_FI_EA_Risk_Charge_GI + BSCR_FI_AA_Risk_Charge_GI, (BSCR_FI_EA_Risk_Charge_GI + BSCR_FI_AA_Risk_Charge_GI) / FI_Exposure_GI]
        
    return BSCR_FI_Risk

# Xi updated 7/16/2019
def BSCR_Equity_Risk_Charge(EBS, portInput, AssetAdjustment, AssetRiskCharge, regime = "Current"):
    print(' Equity BSCR ...')
    
    BSCR_Eq_Risk = {}   
     
    if regime =="Current":      
        # Existing Asset Charge  
        BSCR_Asset_Risk_Charge = portInput.groupby(['FIIndicator','Fort Re Corp Segment'])['AssetCharge_Current'].sum()  
        BSCR_Equity_EA_Risk_Charge_Agg = BSCR_Asset_Risk_Charge.loc[([0])].sum() 
        BSCR_Equity_EA_Risk_Charge_LT = BSCR_Asset_Risk_Charge.loc[([0],['ALBA','Long Term Surplus','ModCo'])].sum()
        BSCR_Equity_EA_Risk_Charge_GI = BSCR_Asset_Risk_Charge.loc[([0],['LPT','General Surplus'])].sum()     
    
        # Adjustment Asset Charge
        if not isinstance(AssetAdjustment, pd.DataFrame):
            BSCR_Equity_AA_Risk_Charge_Agg = EBS['Agg'].DTA_DTL * AssetRiskCharge[AssetRiskCharge['BMA_Category']=='DTA']['Capital_factor_Current'].iloc[0]\
            + EBS['Agg'].LOC*AssetRiskCharge[AssetRiskCharge['BMA_Category']=='LOC']['Capital_factor_Current'].iloc[0]
            BSCR_Equity_AA_Risk_Charge_LT  = EBS['LT'].DTA_DTL*AssetRiskCharge[AssetRiskCharge['BMA_Category']=='DTA']['Capital_factor_Current'].iloc[0]\
            + EBS['LT'].LOC*AssetRiskCharge[AssetRiskCharge['BMA_Category']=='LOC']['Capital_factor_Current'].iloc[0]
            BSCR_Equity_AA_Risk_Charge_GI  = EBS['GI'].DTA_DTL*AssetRiskCharge[AssetRiskCharge['BMA_Category']=='DTA']['Capital_factor_Current'].iloc[0]\
            + EBS['GI'].LOC*AssetRiskCharge[AssetRiskCharge['BMA_Category']=='LOC']['Capital_factor_Current'].iloc[0]
        else:
            BSCR_AssetAdjustment_Risk_Charge = AssetAdjustment.groupby(['FIIndicator','Fort Re Corp Segment'])['AssetCharge_Current'].sum()
    
            BSCR_Equity_AA_Risk_Charge_Agg = BSCR_AssetAdjustment_Risk_Charge.loc[([0])].sum() + EBS['Agg'].DTA_DTL * AssetRiskCharge[AssetRiskCharge['BMA_Category']=='DTA']['Capital_factor_Current'].iloc[0]
            BSCR_Equity_AA_Risk_Charge_LT = BSCR_AssetAdjustment_Risk_Charge.loc[([0],['ALBA','Long Term Surplus','ModCo'])].sum() + EBS['LT'].DTA_DTL*AssetRiskCharge[AssetRiskCharge['BMA_Category']=='DTA']['Capital_factor_Current'].iloc[0]
            BSCR_Equity_AA_Risk_Charge_GI = BSCR_AssetAdjustment_Risk_Charge.loc[([0],['LPT','General Surplus'])].sum() + EBS['GI'].DTA_DTL*AssetRiskCharge[AssetRiskCharge['BMA_Category']=='DTA']['Capital_factor_Current'].iloc[0]
    
    
        BSCR_Eq_Risk['Agg'] = BSCR_Equity_EA_Risk_Charge_Agg+BSCR_Equity_AA_Risk_Charge_Agg
        BSCR_Eq_Risk['LT'] = BSCR_Equity_EA_Risk_Charge_LT+BSCR_Equity_AA_Risk_Charge_LT
        BSCR_Eq_Risk['GI'] = BSCR_Equity_EA_Risk_Charge_GI+BSCR_Equity_AA_Risk_Charge_GI
    
    elif regime =="Future":
        
        for bu in ['Agg', 'LT', 'GI']:
             
            Equity = portInput.groupby(['FIIndicator', 'Fort Re Corp Segment'])['AssetCharge_Future'].sum()
            if not isinstance(AssetAdjustment, pd.DataFrame):
                type_1 = {'Agg': Equity.loc[([0], ['ALBA', 'ModCo', 'LPT'])].sum(),
                    'LT': Equity.loc[([0], ['ALBA', 'ModCo'])].sum(),
                    'GI': Equity.loc[([0], ['LPT'])].sum()}
                type_2 = {'Agg': Equity.loc[([0], ['Long Term Surplus', 'General Surplus'])].sum(),
                    'LT': Equity.loc[([0], ['Long Term Surplus'])].sum(),
                    'GI': Equity.loc[([0], ['General Surplus'])].sum()}
            else:             
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
    
def BSCR_Con_Risk_Charge(base_date, eval_date, portInput_origin, workDir, regime, AssetAdjustment): 
    print(' Concentration Risk ...')
    
    BSCR_Con_Risk = {}
    portInput = copy.deepcopy(portInput_origin)
    
    ### TBD for Dashboard ###
    # portInput['MV_USD_GAAP'] = np.where(((portInput['AIG Asset Class 3'] == 'Cash')|(portInput['AIG Asset Class 3'] == 'Cash Fund')|(portInput['AIG Asset Class 3'] == \
    #          'Short Term Securities')), 0, portInput['MV_USD_GAAP'])
    
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
    
        Conrisk_Calc = portInput.groupby(['Issuer Name','Fort Re Corp Segment'])['ConCharge_Current'].sum()
        
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
        
        Conrisk_Calc = portInput.groupby(['Issuer Name','Fort Re Corp Segment'])['ConCharge_Future'].sum()
        
        if not isinstance(AssetAdjustment, pd.DataFrame):
            BSCR_Con_Risk['Agg'] = Conrisk_Calc.loc[(AggTop10_future)].sum() + 400000000 * 0.2
            BSCR_Con_Risk['LT'] = Conrisk_Calc.loc[(LTTop10_future,LTList),].sum()
            BSCR_Con_Risk['GI'] = Conrisk_Calc.loc[(GITop10_future,GIList),].sum() + UI.EBS_Inputs[base_date]['GI']['LOC'] * 0.2
        else:
            BSCR_Con_Risk['Agg'] = Conrisk_Calc.loc[(AggTop10_future)].sum() + 400000000 * 0.2
            BSCR_Con_Risk['LT'] = Conrisk_Calc.loc[(LTTop10_future,LTList),].sum()
            BSCR_Con_Risk['GI'] = Conrisk_Calc.loc[(GITop10_future,GIList),].sum() + AssetAdjustment[AssetAdjustment['BMA_Category'] == 'LOC']['MV_USD_GAAP'].values[0] * 0.2
            
    return BSCR_Con_Risk

# Xi updated 7/16/2019
def BSCR_IR_Risk_Actual(EBS, LiabSummary):
    print(' Interest rate BSCR ...')
    
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


# Vincent 07/17/2019  
def BSCR_Market_Risk_Charge(BSCR, Regime):
    print(' Aggregate Market Risk BSCR ...')
    
    BSCR_Market_Risk_Charge = {'Agg': {}, 'LT': {}, 'GI': {}}
    
    accounts = ['LT', 'GI', 'Agg']
    
    for each_account in accounts:
        FI  = BSCR['BSCR_FI'][each_account][0]
        EQ  = BSCR['BSCR_Eq'][each_account]
        IR  = BSCR['BSCR_IR'][each_account]
        CUR = BSCR['BSCR_Ccy'][each_account]
        CON = BSCR['BSCR_ConRisk'][each_account]
        
        if Regime == "Current":
            Market_cor = BSCR_Config.Market_cor_Current
            
        elif Regime == "Future":
            Market_cor = BSCR_Config.Market_cor_Future        
            
        Market_RC = pd.DataFrame(data = [FI, EQ, IR, CUR,CON],index = ['Fixed_income', 'Equity', 'Interest_rate','Currency','Concentration'])
        Market_RC_trans = Market_RC.transpose()
    
        BSCR_Market_Risk_Charge[each_account] = np.sqrt(Market_RC_trans @ Market_cor @ Market_RC).values[0][0]
    
    return BSCR_Market_Risk_Charge
    
# Kellie 07/18/2019  
def BSCR_TaxCredit(BSCR_Components, EBS, LiabSummary, regime):
   
    if regime =="Current": 
        
        Tax_Credit = 0
        
    elif regime =="Future":

        Tax_Credit = min(UI.tax_rate * BSCR_Components.BSCR_Bef_Tax_Adj, 0.2 * BSCR_Components.BSCR_Bef_Tax_Adj, sum([EBS.DTA_DTL, BSCR_Components.tax_sharing, UI.tax_rate * LiabSummary['risk_margin']]))
            
    return Tax_Credit

def BSCR_Ccy(portInput,baseLiabAnalytics):
    print(" Currency BSCR")
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

# Vincent 01/02/2020
def BSCR_IR_New_Regime(valDate, instance, Scen, curveType, numOfLoB, market_factor, base_GBP, CF_Database, CF_TableName, Step1_Database, Proj_Year, work_dir, freq, BMA_curve_dir, Disc_rate_TableName, EBS_asset_Input, PVBE_TableName = 'N/A'):
#   1 BEL_Base
    # Get baseline CFs
    instance.liability['BEL_base_scn'] = Corp.get_liab_cashflow('Actual', valDate, CF_Database, CF_TableName, Step1_Database, PVBE_TableName, 0, numOfLoB, Proj_Year, work_dir, freq)        
    
    print('Calculating Baseline PVBE ...') # with baseline CFs and discount rates
    instance.liability['BEL_base_scn'] = Corp.run_EBS_PVBE(instance.liability['BEL_base_scn'], valDate, numOfLoB, Proj_Year, 0, BMA_curve_dir, Step1_Database, Disc_rate_TableName, base_GBP)
    
#   1.1 EBS reporting
    if instance.actual_estimate == 'Actual':        
        instance.liab_summary['BEL_base_scn'] = Corp.summary_liab_analytics(instance.liability['BEL_base_scn'], numOfLoB) 
        
        BEL_Base = instance.liab_summary['BEL_base_scn']['Agg']['PV_BE'] - UI.ALBA_adj
        
#   1.2 EBS dashboard
    elif instance.actual_estimate == 'Estimate':
        baseLiabAnalytics = copy.deepcopy(instance.liability['BEL_base_scn'])
        
        for idx in range(1, numOfLoB + 1, 1):       
            baseLiabAnalytics[idx].cashflow  = baseLiabAnalytics[idx].cashflow[0]
            baseLiabAnalytics[idx].OAS_alts  = baseLiabAnalytics[idx].OAS          
            baseLiabAnalytics[idx].PV_BE     = - baseLiabAnalytics[idx].PV_BE
            baseLiabAnalytics[idx].PV_BE_sec = baseLiabAnalytics[idx].PV_BE # for dummy oas_alts calculation in [Set_Liab_Base]
            
        # Reset time 0 OAS based on baseline CFs
        instance.liability['BEL_base_scn'] = Corp.Set_Liab_Base(valDate, curveType, base_GBP, numOfLoB, baseLiabAnalytics)    
        
        print('Calculating Baseline Dashboard PVBE ...')
        instance.liability['BEL_dashboard_base_scn']    = Corp.Run_Liab_DashBoard(valDate, instance.eval_date, curveType, numOfLoB, instance.liability['BEL_base_scn'], market_factor)
        instance.liab_summary['BEL_dashboard_base_scn'] = Corp.summary_liab_analytics(instance.liability['BEL_dashboard_base_scn'], numOfLoB)  
         
        BEL_Base = instance.liab_summary['BEL_dashboard_base_scn']['Agg']['PV_BE']  # no need to remove ALBA_adj as ALBA_adj is not included in Run_Liab_DashBoard

#   2 ALM charge before capital credit
#   2.1 Change in Liability
#   2.1.1 EBS reporting ==> market_factor = []
    if instance.actual_estimate == 'Actual':
        
        # Shocked curves for EBS reporting
        shocked_irCurve_USD_up = IAL_App.load_BMA_Std_Curves(valDate, 'USD', valDate, rollforward = "N", rollforward_date = datetime.datetime(2100, 12, 31), IR_shift = Scen['IR_Parallel_Shift_bps'], shock_type = "Up")
        shocked_irCurve_USD_dn = IAL_App.load_BMA_Std_Curves(valDate, 'USD', valDate, rollforward = "N", rollforward_date = datetime.datetime(2100, 12, 31), IR_shift = Scen['IR_Parallel_Shift_bps'], shock_type = "Down")
    
        shocked_irCurve_GBP_up = IAL_App.load_BMA_Std_Curves(valDate, 'GBP', valDate, rollforward = "N", rollforward_date = datetime.datetime(2100, 12, 31), IR_shift = Scen['IR_Parallel_Shift_bps'], shock_type = "Up")
        shocked_irCurve_GBP_dn = IAL_App.load_BMA_Std_Curves(valDate, 'GBP', valDate, rollforward = "N", rollforward_date = datetime.datetime(2100, 12, 31), IR_shift = Scen['IR_Parallel_Shift_bps'], shock_type = "Down")   
            
        baseLiabAnalytics = copy.deepcopy(instance.liability['BEL_base_scn'])
        
        for idx in range(1, numOfLoB + 1, 1):       
            baseLiabAnalytics[idx].cashflow = baseLiabAnalytics[idx].cashflow[0]
            baseLiabAnalytics[idx].OAS_alts = baseLiabAnalytics[idx].OAS
                
        instance.liability['ALM_Up']   = Corp.Run_Liab_DashBoard(valDate, valDate, curveType, numOfLoB, baseLiabAnalytics, market_factor, liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term, irCurve_USD = shocked_irCurve_USD_up, irCurve_GBP = shocked_irCurve_GBP_up, gbp_rate = base_GBP)
        instance.liability['ALM_Down'] = Corp.Run_Liab_DashBoard(valDate, valDate, curveType, numOfLoB, baseLiabAnalytics, market_factor, liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term, irCurve_USD = shocked_irCurve_USD_dn, irCurve_GBP = shocked_irCurve_GBP_dn, gbp_rate = base_GBP)
    
        instance.liab_summary['ALM_Up']   = Corp.summary_liab_analytics(instance.liability['ALM_Up'], numOfLoB)
        instance.liab_summary['ALM_Down'] = Corp.summary_liab_analytics(instance.liability['ALM_Down'], numOfLoB)
                 
#   2.1.2 EBS Dashboard
    elif instance.actual_estimate == 'Estimate':
        
        # Shocked curves for EBS Dashboard:
        shocked_irCurve_USD_up = IAL_App.createAkitZeroCurve(instance.eval_date, curveType, "USD", rating = "BBB", rollforward = "N", rollforward_date = datetime.datetime(2100, 12, 31), IR_shift = Scen['IR_Parallel_Shift_bps'], shock_type = 'Up')
        shocked_irCurve_USD_dn = IAL_App.createAkitZeroCurve(instance.eval_date, curveType, "USD", rating = "BBB", rollforward = "N", rollforward_date = datetime.datetime(2100, 12, 31), IR_shift = Scen['IR_Parallel_Shift_bps'], shock_type = 'Down')
     
        shocked_irCurve_GBP_up = IAL_App.load_BMA_Std_Curves(valDate, 'GBP', instance.eval_date, rollforward = "N", rollforward_date = datetime.datetime(2100, 12, 31), IR_shift = Scen['IR_Parallel_Shift_bps'], shock_type = "Up")
        shocked_irCurve_GBP_dn = IAL_App.load_BMA_Std_Curves(valDate, 'GBP', instance.eval_date, rollforward = "N", rollforward_date = datetime.datetime(2100, 12, 31), IR_shift = Scen['IR_Parallel_Shift_bps'], shock_type = "Down")   

        baseLiabAnalytics = instance.liability['BEL_base_scn']
        
        instance.liability['ALM_Up']   = Corp.Run_Liab_DashBoard(valDate, instance.eval_date, curveType, numOfLoB, baseLiabAnalytics, market_factor, liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term, irCurve_USD = shocked_irCurve_USD_up, irCurve_GBP = shocked_irCurve_GBP_up, gbp_rate = base_GBP)
        instance.liability['ALM_Down'] = Corp.Run_Liab_DashBoard(valDate, instance.eval_date, curveType, numOfLoB, baseLiabAnalytics, market_factor, liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term, irCurve_USD = shocked_irCurve_USD_dn, irCurve_GBP = shocked_irCurve_GBP_dn, gbp_rate = base_GBP)
    
        instance.liab_summary['ALM_Up']   = Corp.summary_liab_analytics(instance.liability['ALM_Up'], numOfLoB)
        instance.liab_summary['ALM_Down'] = Corp.summary_liab_analytics(instance.liability['ALM_Down'], numOfLoB)
    
    # Change in Liability
    Change_in_Liab_Up   = instance.liab_summary['ALM_Up']['Agg']['PV_BE']   - BEL_Base
    Change_in_Liab_Down = instance.liab_summary['ALM_Down']['Agg']['PV_BE'] - BEL_Base

    print('====== ' + instance.actual_estimate + ' =======')
    print('Change_in_Liab_Up: ' + str(Change_in_Liab_Up))
    print('Change_in_Liab_Down: ' + str(Change_in_Liab_Down))
 
#   2.2 Change in Asset       
    os.chdir(IAL_App.BMA_curve_dir)
    shock_file = pd.ExcelFile(IAL_App.BMA_ALM_BSCR_shock_file)
    ALM_BSCR_shock = pd.read_excel(shock_file, sheet_name = 'USD')

    base_irCurve_USD = IAL_App.createAkitZeroCurve(instance.eval_date, curveType, "USD")
    
    if instance.actual_estimate == 'Actual':
        base_asset = copy.deepcopy(EBS_asset_Input)   ### should read from BondEdge, temporary solution: Key Rate Dur + Convexity Estimate
    elif instance.actual_estimate == 'Estimate':
        base_asset = copy.deepcopy(instance.asset_holding)
      
    base_asset['Category'] = np.where((base_asset['AIG Asset Class 3'] == "ML-III B-Notes"), "ML III", base_asset['Category'])

    cusip_num = len(base_asset)
    
    for shock_type in ['Up', 'Down']:
        globals()['Change_in_Asset_%s' % shock_type] = 0
        var = globals()['Change_in_Asset_%s' % shock_type]
        
        for idx in range(0, cusip_num, 1):
            cals_cusip = base_asset.iloc[idx]
            
            # Credit spread shock (if there is any)
            if cals_cusip['FIIndicator'] == 1 and cals_cusip['Market Value USD GAAP'] != 0 and cals_cusip['Category'] != 'ML III':                                                
                spread_shock = Scen['Credit_Spread_Shock_bps'] / 10000
                
                each_spread_duration  = cals_cusip['Spread Duration']
                each_spread_convexity = cals_cusip['Spread Convexity']
            
                each_change_in_asset = - cals_cusip['Market Value USD GAAP'] * each_spread_duration * spread_shock \
                                       + cals_cusip['Market Value USD GAAP'] * 1/2 * each_spread_convexity * spread_shock ** 2 * 100
                
                # Asset value will need to be recalculated based on the credit spread shock amount first, then use it to calculate IR up and down based on KRD.                       
                cals_cusip['Market Value USD GAAP'] += each_change_in_asset
                
            # IR shock - KRD
            if cals_cusip['FIIndicator'] == 1 and cals_cusip['Market Value USD GAAP'] != 0 and cals_cusip['Category'] != 'ML III':                                                
                cusip_change_in_asset = 0
                    
                for key, value in IAL_App.KRD_Term.items():        
                    if key[-1] == 'Y':
                        KRD_name = "KRD " + key
                        
                        each_KRD = cals_cusip[KRD_name]                
                        each_shock = Scen['IR_Parallel_Shift_bps']/10000 + ALM_BSCR_shock[ALM_BSCR_shock['Tenor'] == int(key[0:len(key)-1])][shock_type].values[0]            
                        each_change_in_asset = - cals_cusip['Market Value USD GAAP'] * each_KRD * each_shock  
                        
                        cusip_change_in_asset += each_change_in_asset
                                        
                var += cusip_change_in_asset
            
            # IR shock - Convexity
            if cals_cusip['FIIndicator'] == 1 and cals_cusip['Market Value USD GAAP'] != 0 and cals_cusip['Category'] != 'ML III':  
                each_duration  = cals_cusip['Effective Duration (WAMV)']
                each_convexity = cals_cusip['Effective Convexity']
                
                base_rate = base_irCurve_USD.zeroRate( max(1, each_duration) ) 
                
                if shock_type == 'Up':
                    shocked_rate = shocked_irCurve_USD_up.zeroRate(max(1, each_duration))        
                elif shock_type == 'Down':   
                    shocked_rate = shocked_irCurve_USD_dn.zeroRate(max(1, each_duration))
                                
                each_shock = shocked_rate - base_rate
        
                each_change_in_asset = cals_cusip['Market Value USD GAAP'] * 1/2 * each_convexity * each_shock ** 2 * 100

                var += each_change_in_asset
            
        globals()['Change_in_Asset_%s' % shock_type] = var            
        print('Change_in_Asset_' + shock_type)
        print(var)
   
#   2.3 Hedge Effect
#    if instance.actual_estimate == 'Actual':     
#        Hedge_effect_Up   = -377967000 # placeholder
#        Hedge_effect_Down = 1175505000 # placeholder
#        
#    elif instance.actual_estimate == 'Estimate':
    work_dir  = UI.asset_workDir
    fileName  = UI.derivatives_IR01_file
    
    curr_dir = os.getcwd()
    os.chdir(work_dir)
    work_file_name = pd.ExcelFile(fileName)
    work_file      = pd.read_excel(work_file_name)
    os.chdir(curr_dir)
    
    Hedge_effect_Up   = work_file.groupby(['Date'])['200Up'].sum().loc[([instance.eval_date])].sum()
    Hedge_effect_Down = work_file.groupby(['Date'])['200Down'].sum().loc[([instance.eval_date])].sum()
    
    ### to-do: assume 200m under up scenarios and 0 under down for dashboard purpose
    
    print('Hedge_effect_Up: ' + str(Hedge_effect_Up))
    print('Hedge_effect_Down: ' + str(Hedge_effect_Down))
    
#   2.4 ALM Charge before capital credit
    Net_asset_position_Up   = Change_in_Asset_Up + Hedge_effect_Up - Change_in_Liab_Up
    Net_asset_position_Down = Change_in_Asset_Down + Hedge_effect_Down - Change_in_Liab_Down
       
    Capital_charge_bef_credit = abs( min( min(Net_asset_position_Up, Net_asset_position_Down), 0 ) )
    
    print('Net_asset_position_Up: ' + str(Net_asset_position_Up))
    print('Net_asset_position_Down: ' + str(Net_asset_position_Down))
    print('Capital_charge_bef_credit: ' + str(Capital_charge_bef_credit))
            
#   3 Capital Credit        
    if instance.actual_estimate == 'Actual':         
        BEL_Worst = instance.liab_summary['base']['Agg']['PV_BE'] - UI.ALBA_adj
    
    elif instance.actual_estimate == 'Estimate':           
        BEL_Worst = instance.liab_summary['dashboard']['Agg']['PV_BE']
    
    print('BEL_Base: ' + str(BEL_Base))
    print('BEL_Worst: ' + str(BEL_Worst))   

    Capital_credit = min( 0.75*Capital_charge_bef_credit, 0.5*(BEL_Worst - BEL_Base) )
    print('Capital_credit: ' + str(Capital_credit)) 
        
    Capital_charge = Capital_charge_bef_credit - Capital_credit  
    print('Capital_charge: ' + str(Capital_charge))
    
    return Capital_charge