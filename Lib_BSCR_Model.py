# -*- coding: utf-8 -*-
"""
Created on Wed May 22 23:05:57 2019

@author: seongpar
"""
import os
import math as math
import pandas as pd
import datetime
import numpy as np

import Config_BSCR as BSCR_Cofig
import User_Input_Dic as UI
#import App_daily_portfolio_feed as Asset_App

# load akit DLL into python
akit_dir = 'C:/AKit v4.1.0/BIN'
os.sys.path.append(akit_dir)

#valDate        = datetime.datetime(2019, 3, 31)
# load Corp Model Folder DLL into python
corp_model_dir = 'L:\\DSA Re\\Workspace\\Production\2019_Q2\\BMA Best Estimate\\Main_Run_v003\\Step 2 Python Parallel'
os.sys.path.append(corp_model_dir)

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
       

def BSCR_IR_Risk(FI_MV, FI_Dur, PV_BE, Liab_Dur):
    Liab_dur_scaled = Liab_Dur * PV_BE / FI_MV                                       
    Dur_mismatch    = abs(Liab_dur_scaled - FI_Dur)
    IR_Risk_Charge  = FI_MV * max(1, Dur_mismatch) * 0.02 * 0.5
    
    return IR_Risk_Charge


# Xi 7/2/2019; Vincent update on 07/09/2019; Xi updated on 07/12/2019
def BSCR_Mort_Risk(baseLiabAnalytics, numOfLoB, Proj_Year, mort_charge_table=BSCR_Cofig.Mort_Charge):
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
            
            BSCR_LOB  = baseLiabAnalytics[idx].LOB_Def['BSCR LOB']
            Risk_Type = baseLiabAnalytics[idx].LOB_Def['Risk Type']
            
                
            if Risk_Type  == "Mortality":
                Face_Amount['Total'][t] +=  baseLiabAnalytics[idx].cashflow[0]['Total net face amount'][t]
                PVBE['Total'][t]        += -baseLiabAnalytics[idx].EBS_PVBE[t]
                Naar['Total'][t]        =   Face_Amount['Total'][t] - PVBE['Total'][t]
                                    
                if BSCR_LOB in Mort_LOB:
                                      
                    Face_Amount[BSCR_LOB][t] +=  baseLiabAnalytics[idx].cashflow[0]['Total net face amount'][t]
                    PVBE[BSCR_LOB][t]        += -baseLiabAnalytics[idx].EBS_PVBE[t]
                    Naar[BSCR_LOB][t] = Face_Amount[BSCR_LOB][t] - PVBE[BSCR_LOB][t]        
         
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


# Xi 7/2/2019; Vincent update on 07/10/2019; Vincent update on 07/11/2019
def BSCR_Long_Risk_factor(BSCR_LOB, valDate, long_age = UI.long_age, long_dis = UI.long_dis, long_c = BSCR_Cofig.Long_Charge, long_f = UI.long_f):
    
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
                         
                    PVBE[BSCR_LOB][t] += -baseLiabAnalytics[idx].EBS_PVBE[t]
    
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


# Xi 7/2/2019; Vincent update on 07/11/2019
def BSCR_Morb_Charge(baseLiabAnalytics, numOfLoB, Proj_Year, morb_f = BSCR_Cofig.Morb_Charge, morb_d = UI.morbidity):
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
                    PVBE[BSCR_LOB][t]    += -baseLiabAnalytics[idx].EBS_PVBE[t]
                    
                    if t != 0:
                        Premium[BSCR_LOB][t - 1] += baseLiabAnalytics[idx].cashflow[0]['Total premium'][t]                    

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
def BSCR_Other_Charge(baseLiabAnalytics, numOfLoB, Proj_Year, other_f = BSCR_Cofig.Other_Charge):
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
                    PVBE[BSCR_LOB][t] += -baseLiabAnalytics[idx].EBS_PVBE[t]
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
def BSCR_LT_Charge(BSCR, Proj_Year, Regime, LT_cor = BSCR_Cofig.LT_cor):
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
def BSCR_PC_Res_Charge(baseLiabAnalytics, numOfLoB, Proj_Year, regime = "Current", method = "Bespoke", pc_f = BSCR_Cofig.Reserve_Risk_Charge, pc_m = UI.PC_mapping, pc_cor = BSCR_Cofig.pc_cor):
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
                    PVBE[idx][t] += -baseLiabAnalytics[idx].EBS_PVBE[t]
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
    BSCR_AssetAdjustment_Risk_Charge = AssetAdjustment.groupby(['FIIndicator','Fort Re Corp Segment'])['AssetCharge_Current'].sum()
    
    BSCR_FI_AA_Risk_Charge_Agg = BSCR_AssetAdjustment_Risk_Charge.loc[([1])].sum()
    BSCR_FI_AA_Risk_Charge_LT = BSCR_AssetAdjustment_Risk_Charge.loc[([1],['ALBA','Long Term Surplus','ModCo'])].sum()    
    BSCR_FI_AA_Risk_Charge_GI = BSCR_AssetAdjustment_Risk_Charge.loc[([1],['LPT','General Surplus'])].sum()
    
    
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
         BSCR_Eq_Risk[bu] = math.sqrt(np.dot(np.dot(charge, BSCR_Cofig.Equity_cor), charge.transpose()))
                           
    return BSCR_Eq_Risk
    
def BSCR_Con_Risk_Charge(portInput, AssetAdjustment, workDir,regime): 
    print(' Concentration Risk ...')
    
    BSCR_Con_Risk = {}   
    
    portInputAgg = portInput.groupby(['Issuer LE ID', 'Issuer Name'])['MV_USD_GAAP'].sum()
    
    portInputAccount = portInput.groupby(['Issuer LE ID', 'Issuer Name', 'Fort Re Corp Segment'])['MV_USD_GAAP'].sum()    
    portInputAccount = portInputAccount.reset_index()
    
    LTList = ['Long Term Surplus', 'ModCo', 'ALBA']
    GIList = ['LPT', 'General Surplus']
    
    portInputLT = portInputAccount[portInputAccount['Fort Re Corp Segment'].isin(LTList)]
    portInputGI = portInputAccount[portInputAccount['Fort Re Corp Segment'].isin(GIList)]
    
    portInputLT = portInputLT.groupby(['Issuer LE ID','Issuer Name'])['MV_USD_GAAP'].sum()
    portInputGI = portInputGI.groupby(['Issuer LE ID','Issuer Name'])['MV_USD_GAAP'].sum()
    
    Conrisk_top_20_Agg = portInputAgg.to_frame().nlargest(20, 'MV_USD_GAAP')
    Conrisk_top_20_LT = portInputLT.to_frame().nlargest(20, 'MV_USD_GAAP')
    Conrisk_top_20_GI = portInputGI.to_frame().nlargest(20, 'MV_USD_GAAP')
    
    Conrisk_output_Agg = Conrisk_top_20_Agg.sort_values(by = ['MV_USD_GAAP']).reset_index()
    Conrisk_output_LT = Conrisk_top_20_LT.sort_values(by = ['MV_USD_GAAP']).reset_index()
    Conrisk_output_GI = Conrisk_top_20_GI.sort_values(by = ['MV_USD_GAAP']).reset_index()    
    
    excel_file_Agg_name = r'.\Concentration risk top 20_Agg.xlsx'
    excel_file_LT_name = r'.\Concentration risk top 20_LT.xlsx'
    excel_file_GI_name = r'.\Concentration risk top 20_GI.xlsx'
    Conrisk_file_current = r'.\Concentration risk top 10_Current.xlsx'
    Conrisk_file_future = r'.\Concentration risk top 10_Future.xlsx'
    
    os.chdir(workDir)
    
    Conrisk_output_Agg.to_excel(excel_file_Agg_name, header = True, index = False)
    Conrisk_output_LT.to_excel(excel_file_LT_name, header = True, index = False)
    Conrisk_output_GI.to_excel(excel_file_GI_name, header = True, index = False)
    
    ### Action required: update top-10 issuers ###
    input("Please update the Top 10 issuers in " + workDir + " for both Current OR Future (LOC) regimes" + " \nOnce finished,\nPress Enter to continue ...")         
    print('\n')

    if regime =="Current":
        Conrisk_Agg_current = pd.read_excel(Conrisk_file_current, sheetname = 'Agg')
        Conrisk_LT_current = pd.read_excel(Conrisk_file_current, sheetname = 'LT') 
        Conrisk_GI_current = pd.read_excel(Conrisk_file_current, sheetname = 'GI')
            
        AggTop10_current = Conrisk_Agg_current['Issuer Name']
        LTTop10_current = Conrisk_LT_current['Issuer Name']
        GITop10_current = Conrisk_GI_current['Issuer Name']
    
        Conrisk_Calc = portInput.groupby(['Issuer Name','Fort Re Corp Segment'])['AssetCharge_Current'].sum()
        
        BSCR_Con_Risk['Agg'] = Conrisk_Calc.loc[(AggTop10_current)].sum()
        BSCR_Con_Risk['LT'] = Conrisk_Calc.loc[(LTTop10_current,LTList),].sum()
        BSCR_Con_Risk['GI'] = Conrisk_Calc.loc[(GITop10_current,GIList),].sum()
        
    elif regime =="Future":
        Conrisk_Agg_future = pd.read_excel(Conrisk_file_future, sheetname = 'Agg')
        Conrisk_LT_future = pd.read_excel(Conrisk_file_future, sheetname = 'LT') 
        Conrisk_GI_future = pd.read_excel(Conrisk_file_future, sheetname = 'GI')
            
        AggTop10_future = Conrisk_Agg_future['Issuer Name']
        LTTop10_future = Conrisk_LT_future['Issuer Name']
        GITop10_future = Conrisk_GI_future['Issuer Name']
        
        Conrisk_Calc = portInput.groupby(['Issuer Name','Fort Re Corp Segment'])['AssetCharge_Future'].sum()
    
        BSCR_Con_Risk['Agg'] = Conrisk_Calc.loc[(AggTop10_future)].sum() + 400000000 * 0.2
        BSCR_Con_Risk['LT'] = Conrisk_Calc.loc[(LTTop10_future,LTList),].sum()
        BSCR_Con_Risk['GI'] = Conrisk_Calc.loc[(GITop10_future,GIList),].sum() + AssetAdjustment[AssetAdjustment['BMA_Category'] == 'LOC']['MV_USD_GAAP'].values[0] * 0.2
    
    return BSCR_Con_Risk

# Xi updated 7/16/2019
def BSCR_IR_Risk_Actual(EBS, LiabSummary):
    print(' Interest rate BSCR ...')
    
    BSCR_IR_Risk_Charge = {'Agg': {}, 'LT': {}, 'GI': {}}
    
    # FI duration    
    Actual_FI_Dur_MV_LT = EBS['LT'].fwa_MV_FI + EBS['LT'].fixed_inv_surplus + EBS['LT'].cash + EBS['LT'].Other_Assets
    Actual_FI_Dur_MV_PC = EBS['GI'].fwa_MV_FI + EBS['GI'].fixed_inv_surplus + EBS['GI'].cash + EBS['GI'].Other_Assets
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
            Market_cor = BSCR_Cofig.Market_cor_Current
            
        elif Regime == "Future":
            Market_cor = BSCR_Cofig.Market_cor_Future        
            
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
    alba_tp = -baseLiabAnalytics[34].technical_provision
    if alba_tp*1.05 > MVA_alba:
        BSCR_Ccy_risk = (alba_tp*1.05 - MVA_alba)*0.25
    else:
        BSCR_Ccy_risk = 0
    
    BSCR_Ccy = {"Agg": BSCR_Ccy_risk, "LT": BSCR_Ccy_risk, "GI": 0}  
        
    return BSCR_Ccy
    