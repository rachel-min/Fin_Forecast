# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 19:59:26 2020

@author: kyle
"""

import os
import numpy as np
import pandas as pd
import Lib_Corp_Model as Corp
import Lib_BSCR_Calc  as BSCR_calc
import Config_BSCR    as BSCR_Config

""" Logs
runControl updated on 6/2/2020
Scen_Control updated on 6/2/2020
BSCR_Control updated on 6/2/2020
Rating_Mapping_Control updated on 6/2/2020
"""

def update_runControl(run_control):
    
    '''
    One Run_Control file for each valuation period
    Always has a function update_runControl
    '''
    
    ### Hard-coded inputs from I_Control
    run_control.time0_LTIC = 97633492
    run_control.surplus_life_0 = 1498468068.62392
    run_control.surplus_PC_0 = 1541220172.25324
    run_control.I_SFSLiqSurplus = 1809687680.14178

    run_control.GAAP_Reserve_method     = 'Roll-forward'  #### 'Product_Level" or 'Roll-forward'
    ### Update assumptions as needed #####
    # Load ModCo Asset Projection
    BSCR_mapping = run_control.modco_BSCR_mapping
    BSCR_charge  = BSCR_Config.BSCR_Asset_Risk_Charge_v1
    
    run_control.asset_proj_modco           = Corp.get_asset_category_proj(run_control._val_date, 'alm', freq = run_control._freq)
    run_control.asset_proj_modco['MV_Dur'] = run_control.asset_proj_modco['MV'] * run_control.asset_proj_modco['Dur']
    run_control.asset_proj_modco['FI_Alts'] =  run_control.asset_proj_modco.apply(lambda x: 'Alts' if x['asset_class'] == 'Alts' else 'FI', axis=1)
    run_control.asset_proj_modco['risk_charge_factor'] \
    =  run_control.asset_proj_modco.apply(lambda \
           x: BSCR_calc.proj_BSCR_asset_risk_charge(BSCR_mapping[x['asset_class']], BMA_asset_risk_charge = BSCR_charge), axis=1)
    
    run_control.asset_proj_modco['asset_risk_charge']  = run_control.asset_proj_modco['MV'] * run_control.asset_proj_modco['risk_charge_factor']
    
    run_control.asset_proj_modco_agg                       = run_control.asset_proj_modco.groupby(['val_date', 'rowNo', 'proj_time', 'FI_Alts']).sum().reset_index()    
    run_control.asset_proj_modco_agg['Dur']                = run_control.asset_proj_modco_agg['MV_Dur'] / run_control.asset_proj_modco_agg['MV']
    run_control.asset_proj_modco_agg['risk_charge_factor'] = run_control.asset_proj_modco_agg['asset_risk_charge'] / run_control.asset_proj_modco_agg['MV']
    run_control.asset_proj_modco_agg.fillna(0, inplace=True)
    
    # Dividend Schedule
    run_control.proj_schedule[1]['dividend_schedule']     = 'Y'
    run_control.proj_schedule[1]['dividend_schedule_amt'] = 500000000
    run_control.proj_schedule[2]['dividend_schedule']     = 'Y'
    run_control.proj_schedule[2]['dividend_schedule_amt'] = 1000000000
    run_control.proj_schedule[3]['dividend_schedule']     = 'Y'
    run_control.proj_schedule[3]['dividend_schedule_amt'] = 1000000000
    
    # LOC SFS Limit
    SFS_limit = [ 0.25,
                 0.248285375,
                 0.252029898,
                 0.285955276,
                 0.38330347,
                 0.441096663,
                 0.460419183,
                 0.470052356,
                 0.462474131,
                 0.448079715,
                 0.42905067,
                 0.401161493,
                 0.374517694,
                 0.354974144,
                 0.312988995,
                 0.298355834,
                 0.301492895,
                 0.294050736,
                 0.284305953,
                 0.274386361,
                 0.264800284,
                 0.257449286,
                 0.253203818,
                 0.248658944,
                 0.240894683,
                 0.235788524,
                 0.224783331,
                 0.218340687,
                 0.214482419,
                 0.209553337,
                 0.208785641,
                 0.211190424,
                 0.210920573,
                 0.216687659,
                 0.222172075,
                 0.227580018,
                 0.232088173,
                 0.236832925,
                 0.241751243,
                 0.245726161,
                 0.248599255,
                 0.248058163,
                 0.246790226,
                 0.24740993,
                 0.247595613,
                 0.247582842,
                 0.244536254,
                 0.254065247,
                 0.246678196,
                 0.242226328,
                 0.25,
                 0.242866482,
                 0.244004135,
                 0.301949013,
                 0.244575476,
                 0.244081956,
                 0.243021021,
                 0.250817216,
                 0.252697673,
                 0.200005319,
                 0.200005319,
                 0.200005319,
                 0.200005319,
                 0.200005319,
                 0.200005319,
                 0.200005319,
                 0.200005319,
                 0.200005319,
                 0.200005319,
                 0.200005319,
                 0.200005319,
                 0.200005319,
                 0.200005319,
                 0.200005319,
                 0.200006653,
                 0.200011781,
                 0.2,
                 0.2,
                 0.2,
                 0.2]
    
    for i in range(min(len(run_control._dates), len(SFS_limit))):
        run_control.proj_schedule[i]['LOC_SFS_Limit'] = SFS_limit[i]
    
    # Initial and Ultimate Spread
    run_control.initial_spread = {
        'Term' : [1,	2,	3,	5,	7,	10,	20,	30 ],
        'AAA'  : [ 0.0016,	0.0028,	0.0035,	0.0037,	0.0042,	0.0054,	0.0069,	0.0084 ],
        'AA'   : [ 0.0019,	0.0034,	0.0042,	0.0048,	0.0055,	0.007,	0.0085,	0.0099 ],
        'A'	   : [ 0.0023,	0.0042,	0.0052,	0.0062,	0.0095,	0.0109,	0.0105,	0.0127 ],
        'BBB'  : [ 0.0044,	0.0082,	0.0092,	0.0114,	0.0156,	0.0162,	0.0161,	0.0183 ],
        'BB'   : [ 0.012,	0.0162,	0.0193,	0.0234,	0.0267,	0.0306,	0.0337,	0.0368 ],
        'B'	   : [ 0.0183,	0.0237,	0.0277,	0.0331,	0.0373,	0.0421,	0.046,	0.0499 ],
        'CCC'  : [ 0.0546,	0.0579,	0.0602,	0.0631,	0.0655,	0.0684,	0.0705,	0.0726 ]
    }
    
    run_control.ultimate_spread = {
        'Term' : [1,	2,	3,	5,	7,	10,	20,	30 ],
        'AAA'  : [ 0.0049,	0.0053,	0.0058,	0.0065,	0.0066,	0.0062,	0.0065,	0.008],
        'AA'   : [ 0.0053,	0.0059,	0.0066,	0.0076,	0.0081,	0.0081,	0.0091,	0.0107 ],
        'A'	   : [ 0.0073,	0.0081,	0.009,	0.0106,	0.0114,	0.0117,	0.0134,	0.0154 ],
        'BBB'  : [ 0.0123,	0.0136,	0.0149,	0.0173,	0.0187,	0.0196,	0.0219,	0.0238 ],
        'BB'   : [ 0.0295,	0.0311,	0.0328,	0.0357,	0.0375,	0.0386,	0.0407,	0.0421 ],
        'B'	   : [ 0.0492,	0.0569,	0.059,	0.0626,	0.0647,	0.0661,	0.068,	0.0681 ],
        'CCC'  : [ 0.1221,	0.1255,	0.1269,	0.1288,	0.1287,	0.1263,	0.1196,	0.1129 ]
    }

#%% Scenario

class Scen_Control:
    
    Comp = { 'Scen_Name'               : 'Comprehensive',
             'IR_Stress_Type'          : 'Parallel' ,
             'IR_Parallel_Shift_bps'   : -30 ,
             'Alts_Retrun'             : -0.1395174,
             'MLIII_Return'            : -0.142767256132,
             'PC_PYD'                  : 0.076405094,
             'Liab_Spread_Beta'        : 0.65,
             'LT_Reserve'              : 0,
             'Longevity shock'         : 0,
             'mortality shock'         : 0,	
             'Expense shock_Permanent' : 0,	
             'Expense shock_Inflation' : 0,	
             'Lapse shock'             : 0,	
             'Morbidity shock'         : 0,	
             'Longevity Trend shock'   : 0
            }


#%% BSCR 
    
class BSCR_Control:
    
    BSCR_Charge = { 'FI_Risk_Agg' :  0.0268018320960826, #1Q19: 0.0263825726068971,
                'FI_Risk_LT' :   0.0272798114401723, #1Q19: 0.0269484605206746,
                'FI_Risk_GI' :  0.0239813253283309,  #1Q19: 0.0230680384263096,
                'Eq_Risk' :  0.2, 
                'Concentration_Risk_Agg' :  0.00294254230231262, #1Q19: 0.00198793229160904,
                'Concentration_Risk_LT' :  0.00327858437261978,  #1Q19: 0.0032289119855899,
                'Concentration_Risk_GI' :  0.00200653044491279,  #1Q19: 0.0016875698643556,
                'Currency_Risk_Agg' : 0.00053413874763841,
                'Currency_Risk_LT' : 0.000624656980449651,
                'Currency_Risk_GI' : 0,
                'OpRiskCharge' :  0.05 }

    Reserve_Risk_Charge_BMA_Standard = { 'Property' : 0.43845, 'Personal_Accident': 0.29666, 'US_Casualty': 0.43018, 'US_Casualty_NP': 0.48842, 'US_Specialty': 0.46517, 'US_Specialty_NP': 0.48276 }
    Reserve_Risk_Charge_BMA_bespoke  = { 'Property' : 0.325,   'Personal_Accident': 0.2967,  'US_Casualty': 0.33225, 'US_Casualty_NP': 0.42312, 'US_Specialty': 0.34,    'US_Specialty_NP': 0.36 }
    
    RM_Cost_of_Capital = 0.06
    
    # ZZZZZZZZZZZZZZZZ Reserve Risk charge needs to be defined by valuation dates ZZZZZZZZZZZZZZZZZZZZZZZZZZZ
    Reserve_Risk_Charge = { 
            'BMA'     : Reserve_Risk_Charge_BMA_Standard,
            'Bespoke' : Reserve_Risk_Charge_BMA_bespoke
            }
    
    
    BSCR_Mort_LOB = ['UL', 'WL', 'ROP']
    
    #Xi 7/2/2019
    Mort_Charge = {1000000000:0.00397,
                   5000000000:0.0018,
                   10000000000:0.00144,
                   50000000000:0.00129,
                   10000000000000:0.00113}
    
    Long_Charge = {"Inpay": {"0-55" : 0.02,
                             "56-65": 0.03,
                             "66-70": 0.04,
                             "71-80": 0.05,
                             "81+"  : 0.06
                             },
                  "Deferred": {"0-55" : 0.02,
                               "56-60": 0.03,
                               "61-65": 0.04,
                               "66-70": 0.05,
                               "71-75": 0.06,
                               "76+"  : 0.07
                               },                           
                    "ult_c": {"inpay"   : 0.06, 
                              "deferred": 0.07
                              }
                    }
    
    Morb_Charge = {"Disability income: claims in payment Waiver of premium and long-term care":0.07,
                   "Disability income: claims in payment Other accident and sickness":0.1,
                   "Disability Income: Active Lives, Prem guar ≤ 1 Yr; Benefit Period > 2 Years":0.12,
                   "Disability Income: Active Lives, Prem guar > 5 years; Benefit Period > 2 Years":0.3,
                   "Disability Income: Active lives, Other Accident and Sickness":0.12}
    
    Other_Charge = {"Mortality (term insurance, whole life, universal life)":0.02,
                    "Critical Illness (including accelerated critical illness products)":0.02,
                    "Longevity (immediate pay-out annuities, contingent annuities, pension pay-outs)":0.005,
                    "Longevity (deferred pay-out annuities, future contingent annuities, future pension pay-outs)":0.005,
                    "Annuities certain only":0.005,
                    "Deferred accumulation annuities":0.005,
                    "Disability Income: active lives - including waiver of premium and long-term care":0.02,
                    "Disability Income: active lives - other accident and sickness":0.02,
                    "Disability Income: claims in payment - including waiver of premium and long-term care":0.005,
                    "Disability Income: claims in payment - other accident and sickness":0.005,
                    "Group Life":0.005,
                    "Group Disability":0.005,
                    "Group Health":0.005,
                    "Stop Loss arrangements":0.02,
                    "Riders (all other products not included above)":0.02
                    }
    
     
    PC_corre = {'Property'          : [1.00, 0.25, 0.25, 0.25, 0.25, 0.25],
                'Personal_Accident' : [0.25, 1.00, 0.25, 0.25, 0.25, 0.25],
                'US_Casualty'       : [0.25, 0.25, 1.00, 0.50, 0.25, 0.25],
                'US_Casualty_NP'    : [0.25, 0.25, 0.50, 1.00, 0.25, 0.25],
                'US_Specialty'      : [0.25, 0.25, 0.25, 0.25, 1.00, 0.50],
                'US_Specialty_NP'   : [0.25, 0.25, 0.25, 0.25, 0.50, 1.00]}
    
    #PC_corre = {'Property'          : [1.00, 0, 0, 0, 0, 0],
    #            'Personal_Accident' : [0, 1.00, 0, 0, 0, 0],
    #            'US_Casualty'       : [0, 0, 1.00, 0, 0, 0],
    #            'US_Casualty_NP'    : [0, 0, 0, 1.00, 0, 0],
    #            'US_Specialty'      : [0, 0, 0, 0, 1.00, 0],
    #            'US_Specialty_NP'   : [0, 0, 0, 0, 0, 1.00]}
    
    PC_Matrix = np.array(  [ 
                            [1.00, 0.25, 0.25, 0.25, 0.25, 0.25],
                            [0.25, 1.00, 0.25, 0.25, 0.25, 0.25],
                            [0.25, 0.25, 1.00, 0.50, 0.25, 0.25],
                            [0.25, 0.25, 0.50, 1.00, 0.25, 0.25],
                            [0.25, 0.25, 0.25, 0.25, 1.00, 0.50],
                            [0.25, 0.25, 0.25, 0.25, 0.50, 1.00]
                            ]
                        )
    
    pc_cor = pd.DataFrame(data = PC_corre,index = ['Property', 'Personal_Accident', 'US_Casualty','US_Casualty_NP','US_Specialty', 'US_Specialty_NP' ])
    
    LT_corre = {'Mortality' :   [1.00,  0.75,  0.75,  0.25,  -0.50,  0.00,  0.125],
                 'Stop_loss':   [0.75,  1.00,  0.75,  0.00,  -0.50,  0.00,  0.25],
                 'Riders':      [0.75,  0.75,  1.00,  0.00,  -0.50,  0.00,  0.25],
                 'Morbidity':   [0.25,  0.00,  0.00,  1.00,   0.00,  0.00,  0.25],
                 'Longevity':   [-0.50,-0.50, -0.50,  0.00,   1.00,  0.00,  0.25],
                 'VA':          [0.00,  0.00,  0.00,  0.00,   0.00,  1.00,  0.25],
                 'Other':       [0.125,  0.25,  0.25,  0.25,   0.25,  0.25,  1.00]}
    
    
    LT_Matrix = np.array(  [ 
                            [1.00,  0.75,  0.75,  0.25,  -0.50,  0.00,  0.125],
                            [0.75,  1.00,  0.75,  0.00,  -0.50,  0.00,  0.25],
                            [0.75,  0.75,  1.00,  0.00,  -0.50,  0.00,  0.25],
                            [0.25,  0.00,  0.00,  1.00,   0.00,  0.00,  0.25],
                            [-0.50,-0.50, -0.50,  0.00,   1.00,  0.00,  0.25],
                            [0.00,  0.00,  0.00,  0.00,   0.00,  1.00,  0.25],
                            [0.125,  0.25,  0.25,  0.25,   0.25,  0.25,  1.00]
                            ]
                        )
    
    #LT_corre = { 'Mortality':   [1,  0,  0,  0,  0,  0,  0],
    #             'Stop_loss':   [0,  1,  0,  0,  0,  0,  0],
    #             'Riders':      [0,  0,  1,  0,  0,  0,  0],
    #             'Morbidity':   [0,  0,  0,  1,  0,  0,  0],
    #             'Longevity':   [0,  0,  0,  0,  1,  0,  0],
    #             'VA':          [0,  0,  0,  0,  0,  1,  0],
    #             'Other':       [0,  0,  0,  0,  0,  0,  1]}
    
    LT_cor = pd.DataFrame(data = LT_corre,index = ['Mortality', 'Stop_loss', 'Riders','Morbidity','Longevity', 'VA', 'Other' ])
    
    Market_corre_Current = {'Fixed_income' : [1.00, 0, 0, 0, 0],
                            'Equity'       : [0, 1.00, 0, 0, 0],
                            'Interest_rate': [0, 0, 1.00, 0, 0],
                            'Currency'     : [0, 0, 0, 1.00, 0],
                            'Concentration': [0, 0, 0, 0, 1.00]
                            }
    
    Market_corre_Future = {'Fixed_income' : [1.00, 0.50, 0.25, 0.25, 0.00],
                           'Equity'       : [0.50, 1.00, 0.25, 0.25, 0.00],
                           'Interest_rate': [0.25, 0.25, 1.00, 0.25, 0.00],
                           'Currency'     : [0.25, 0.25, 0.25, 1.00, 0.00],
                           'Concentration': [0.00, 0.00, 0.00, 0.00, 1.00]
                           }
    
    Market_cor_Current =  pd.DataFrame(data = Market_corre_Current, index = ['Fixed_income', 'Equity', 'Interest_rate','Currency','Concentration'])
    Market_cor_Future  =  pd.DataFrame(data = Market_corre_Future, index = ['Fixed_income', 'Equity', 'Interest_rate','Currency','Concentration'])
    
    Equity_corre = {'Type_1': [1.00, 0.75, 0.75, 0.50],
                    'Type_2': [0.75, 1.00, 0.75, 0.50],
                    'Type_3': [0.75, 0.75, 1.00, 0.50],
                    'Type_4': [0.50, 0.50, 0.50, 1.00] }
    
    Equity_cor = pd.DataFrame(data = Equity_corre, index = ['Type_1', 'Type_2', 'Type_3', 'Type_4'])
    
    Total_corre = {'Market_Risk': [1.00,    0.25,   0.125,  0.125],
                   'Credit_Risk': [0.25,    1.00,   0.50,   0.25],
                   'PC_Risk'    : [0.125,   0.50,   1.00,   0.00],   
                   'LT_Risk'    : [0.125,   0.25,   0.00,   1.00] }
    
    Total_cor = pd.DataFrame(data = Total_corre, index = ['Market_Risk', 'Credit_Risk', 'PC_Risk','LT_Risk'])
    
    
    
    PC_BSCR_Group = ['Property', 'Personal_Accident', 'US_Casualty', 'US_Casualty_NP', 'US_Specialty', 'US_Specialty_NP']
    
    PC_Reserve_mapping =  {
        15 :   { 'Property' : 0.0000, 'Personal_Accident' : 0.0,         'US_Casualty' : 0.0,           'US_Casualty_NP' : 0.0,         'US_Specialty' : 0.0,         'US_Specialty_NP' : 0 },
        35 :   { 'Property' : 0.0000, 'Personal_Accident' : 0.0,         'US_Casualty' : 0.0,           'US_Casualty_NP' : 1.0,         'US_Specialty' : 0.0,         'US_Specialty_NP' : 0 },
        36 :   { 'Property' : 0.0000, 'Personal_Accident' : 0.0,         'US_Casualty' : 0.56488795476, 'US_Casualty_NP' : 0.435112045, 'US_Specialty' : 0.0,         'US_Specialty_NP' : 0 },
        37 :   { 'Property' : 0.0000, 'Personal_Accident' : 0.0,         'US_Casualty' : 0.825103272,   'US_Casualty_NP' : 0.174896728, 'US_Specialty' : 0.0,         'US_Specialty_NP' : 0 },
        38 :   { 'Property' : 0.0000, 'Personal_Accident' : 0.0,         'US_Casualty' : 0.25,          'US_Casualty_NP' : 0.75,        'US_Specialty' : 0.0,         'US_Specialty_NP' : 0 },
        39 :   { 'Property' : 0.0000, 'Personal_Accident' : 0.0,         'US_Casualty' : 0.733,         'US_Casualty_NP' : 0.267,       'US_Specialty' : 0.0,         'US_Specialty_NP' : 0 },
        40 :   { 'Property' : 0.0000, 'Personal_Accident' : 0.0,         'US_Casualty' : 0.0,           'US_Casualty_NP' : 0.0,         'US_Specialty' : 0.283728596, 'US_Specialty_NP' : 0.716271404 },
        41 :   { 'Property' : 0.0000, 'Personal_Accident' : 0.0,         'US_Casualty' : 0.0,           'US_Casualty_NP' : 1.0,         'US_Specialty' : 0.0,         'US_Specialty_NP' : 0 },
        42 :   { 'Property' : 0.0000, 'Personal_Accident' : 0.419472068, 'US_Casualty' : 0.0,           'US_Casualty_NP' : 0.580527932, 'US_Specialty' : 0.0,         'US_Specialty_NP' : 0 },
        43 :   { 'Property' : 0.0000, 'Personal_Accident' : 0.0,         'US_Casualty' : 0.221745588,   'US_Casualty_NP' : 0.778254412, 'US_Specialty' : 0.0,         'US_Specialty_NP' : 0 },
        44 :   { 'Property' : 0.0000, 'Personal_Accident' : 0.0,         'US_Casualty' : 0.0,           'US_Casualty_NP' : 1.0,         'US_Specialty' : 0.0,         'US_Specialty_NP' : 0 },
        45 :   { 'Property' : 0.0000, 'Personal_Accident' : 0.0,         'US_Casualty' : 0.95,          'US_Casualty_NP' : 0.05,        'US_Specialty' : 0.0,         'US_Specialty_NP' : 0 }
    }               
            
    
    
    ################### Longevity Assumptions Deferred by Base Valuation Date      
    
    Longevity_LOB = ['SS', 'SPIA', 'TFA', 'ALBA']      
    
    Longevity_Charge = {"inpayment": {"0-55" : 0.02,
                             "56-65": 0.03,
                             "66-70": 0.04,
                             "71-80": 0.05,
                             "81+"  : 0.06
                             },
                  "deferred": {"0-55" : 0.02,
                               "56-60": 0.03,
                               "61-65": 0.04,
                               "66-70": 0.05,
                               "71-75": 0.06,
                               "76+"  : 0.07
                               },                           
                    "Ultimate": {"inpayment"   : 0.06, 
                              "deferred": 0.07
                              }
                    }
    
    longevity_pay_split ={"SS"     :{"inpayment"   : 0.409744552526238, "deferred" : 0.590255447473762},
                          "SPIA"   :{"inpayment"   : 0.874721445504917, "deferred" : 0.125278554495083},
                          "TFA"    :{"inpayment"   : 0.841584099874696, "deferred" : 0.158415900125304},
                          "ALBA"   :{"inpayment"   : 0.422224573846380, "deferred" : 0.577775426153620}
                          }
    
    longevity_age_average = {
            'SS'       : { 'inpayment' : 51.7859288765259, 'deferred' : 40.1261333454091 },
            'SPIA'     : { 'inpayment' : 74.6664702347134, 'deferred' : 72.1116110424958 },
            'TFA'      : { 'inpayment' : 69.5420583550923, 'deferred' : 60.1188077321654 },
            'ALBA'     : { 'inpayment' : 69.0671539181792, 'deferred' : 57.3008976171722 },
            'Ultimate' : { 'inpayment' : 81, 'deferred' : 76 }
       }
    
    longevity_age_split = {
    
            'SS' : {
                    'inpayment': { "0-55" : 0.5461662268348700,
                                   "56-65": 0.2545314867167770, 
                                   "66-70": 0.0852147385804457,
                                   "71-80": 0.0953678963051677,
                                   "81+"  : 0.0187196515627395
                                  },
    
                  'deferred': {"0-55" : 0.7887830243726350,
                               "56-60": 0.0805754041375093, 
                               "61-65": 0.0681470747780306,
                               "66-70": 0.0389987304418374, 
                               "71-75": 0.0170482002445230,
                               "76+"  : 0.0064475660254647
                               },                           
    
                    },
                    
    
            'SPIA' : {
                    'inpayment': { "0-55" : 0.0974507310727962, 
                                   "56-65": 0.0573458055387673, 
                                   "66-70": 0.0811166577338227, 
                                   "71-80": 0.3509738355043370, 
                                   "81+"  : 0.4131129701502770
                                  },
    
                  'deferred': {"0-55" : 0.1385811134621300,
                               "56-60": 0.0395106875887056, 
                               "61-65": 0.0877472196254331,
                               "66-70": 0.1123153325247080, 
                               "71-75": 0.1381804596634760,
                               "76+"  : 0.4836651871355480
                               },                           
    
                    },
    
    
            'TFA' : {
                    'inpayment': { "0-55" : 0.1076814990669880, 
                                   "56-65": 0.0949355473839442, 
                                   "66-70": 0.2007181932785390, 
                                   "71-80": 0.3602314606804970, 
                                   "81+"  : 0.2364332995900320
                                  },
    
                  'deferred': {"0-55" : 0.1480811027669170,
                               "56-60": 0.3412180127984280, 
                               "61-65": 0.4277835645126450,
                               "66-70": 0.0486988289641064, 
                               "71-75": 0.0198145376311520,
                               "76+"  : 0.0144039533267508
                               },                           
    
                    },
    
    
            'ALBA' : {
                    'inpayment': { "0-55" : 0.0015430574424368, 
                                   "56-65": 0.2220244771611000, 
                                   "66-70": 0.4075272963866020, 
                                   "71-80": 0.3682443824873840, 
                                   "81+"  : 0.0006607865224781
                                  },
    
                  'deferred': {"0-55" : 0.3352247876051390,
                               "56-60": 0.3938150357466250, 
                               "61-65": 0.2704809401853730,
                               "66-70": 0.0003545409114745,    # Vincent - update to be same as 4Q18
                               "71-75": 0,                     # Vincent - update to be same as 4Q18
                               "76+"  : 0.0001246955513895     # Vincent - update to be same as 4Q18
                               },                           
    
                    }
        }
    
    
    
    Morbidity_LOB = ['AH', 'LTC', 'PC'] # NUFIC's BSCR_LOB is PC
    Morbidity_split = {
            "LTC"  :{"active":0.662, "inpayment": 0.338},
            "AH"   :{"active":0.334,"critical":0.553,"inpayment": 0.113},
            "PC"   :{"active":0.334,"critical":0.553,"inpayment": 0.113}
            }
    
    
    Other_Ins_Risk_LOB = ['UL','WL','ROP', 'AH', 'LTC', 'SS','TFA','SPIA','ALBA', 'PC']
    
    BSCR_Asset_Risk_Charge_v1 = {  'Bonds Cash and Govt' : { 'Risk_Charge'  :  0 , 'Concentration_Charge' :  0  },
                                        'Bonds_1' : { 'Risk_Charge'  :  0.004 , 'Concentration_Charge' :  0.004  },
                                        'Bonds_2' : { 'Risk_Charge'  :  0.008 , 'Concentration_Charge' :  0.008  },
                                        'Bonds_3' : { 'Risk_Charge'  :  0.015 , 'Concentration_Charge' :  0.015  },
                                        'Bonds_4' : { 'Risk_Charge'  :  0.03 , 'Concentration_Charge' :  0.03  },
                                        'Bonds_5' : { 'Risk_Charge'  :  0.08 , 'Concentration_Charge' :  0.08  },
                                        'Bonds_6' : { 'Risk_Charge'  :  0.15 , 'Concentration_Charge' :  0.15  },
                                        'Bonds_7' : { 'Risk_Charge'  :  0.263 , 'Concentration_Charge' :  0.263  },
                                        'Bonds_8' : { 'Risk_Charge'  :  0.35 , 'Concentration_Charge' :  0.35  },
                                        'RMBS_1' : { 'Risk_Charge'  :  0.006 , 'Concentration_Charge' :  0.006  },
                                        'RMBS_2' : { 'Risk_Charge'  :  0.012 , 'Concentration_Charge' :  0.012  },
                                        'RMBS_3' : { 'Risk_Charge'  :  0.02 , 'Concentration_Charge' :  0.02  },
                                        'RMBS_4' : { 'Risk_Charge'  :  0.04 , 'Concentration_Charge' :  0.04  },
                                        'RMBS_5' : { 'Risk_Charge'  :  0.11 , 'Concentration_Charge' :  0.11  },
                                        'RMBS_6' : { 'Risk_Charge'  :  0.25 , 'Concentration_Charge' :  0.25  },
                                        'RMBS_7' : { 'Risk_Charge'  :  0.35 , 'Concentration_Charge' :  0.35  },
                                        'RMBS_8' : { 'Risk_Charge'  :  0.35 , 'Concentration_Charge' :  0.35  },
                                        'CMBS_1' : { 'Risk_Charge'  :  0.005 , 'Concentration_Charge' :  0.005  },
                                        'CMBS_2' : { 'Risk_Charge'  :  0.01 , 'Concentration_Charge' :  0.01  },
                                        'CMBS_3' : { 'Risk_Charge'  :  0.018 , 'Concentration_Charge' :  0.018  },
                                        'CMBS_4' : { 'Risk_Charge'  :  0.035 , 'Concentration_Charge' :  0.035  },
                                        'CMBS_5' : { 'Risk_Charge'  :  0.1 , 'Concentration_Charge' :  0.1  },
                                        'CMBS_6' : { 'Risk_Charge'  :  0.2 , 'Concentration_Charge' :  0.2  },
                                        'CMBS_7' : { 'Risk_Charge'  :  0.3 , 'Concentration_Charge' :  0.3  },
                                        'CMBS_8' : { 'Risk_Charge'  :  0.35 , 'Concentration_Charge' :  0.35  },
                                        'Bond Mutual Funds Cash and Govt' : { 'Risk_Charge'  :  0 , 'Concentration_Charge' :  0  },
                                        'Bond Mutual Funds 1' : { 'Risk_Charge'  :  0.004 , 'Concentration_Charge' :  0.004  },
                                        'Bond Mutual Funds 2' : { 'Risk_Charge'  :  0.008 , 'Concentration_Charge' :  0.008  },
                                        'Bond Mutual Funds 3' : { 'Risk_Charge'  :  0.015 , 'Concentration_Charge' :  0.015  },
                                        'Bond Mutual Funds 4' : { 'Risk_Charge'  :  0.03 , 'Concentration_Charge' :  0.03  },
                                        'Bond Mutual Funds 5' : { 'Risk_Charge'  :  0.08 , 'Concentration_Charge' :  0.08  },
                                        'Bond Mutual Funds 6' : { 'Risk_Charge'  :  0.15 , 'Concentration_Charge' :  0.15  },
                                        'Bond Mutual Funds 7' : { 'Risk_Charge'  :  0.263 , 'Concentration_Charge' :  0.263  },
                                        'Bond Mutual Funds 8' : { 'Risk_Charge'  :  0.35 , 'Concentration_Charge' :  0.35  },
                                        'Insured/Guaranteed Mortgages' : { 'Risk_Charge'  :  0.003 , 'Concentration_Charge' :  0.144  },
                                        'Other Commercial and Farm Mortgages' : { 'Risk_Charge'  :  0.05 , 'Concentration_Charge' :  0.1  },
                                        'Other Residential Mortgages' : { 'Risk_Charge'  :  0.015 , 'Concentration_Charge' :  0.2  },
                                        'Mortgages Not In Good Standing' : { 'Risk_Charge'  :  0.25 , 'Concentration_Charge' :  0.35  },
                                        'Other Loans' : { 'Risk_Charge'  :  0.05 , 'Concentration_Charge' :  0.05  },
                                        'Cash Cash and Govt' : { 'Risk_Charge'  :  0 , 'Concentration_Charge' :  0  },
                                        'Cash BSCR Rating 1' : { 'Risk_Charge'  :  0.001 , 'Concentration_Charge' :  0.001  },
                                        'Cash BSCR Rating 2' : { 'Risk_Charge'  :  0.002 , 'Concentration_Charge' :  0.002  },
                                        'Cash BSCR Rating 3' : { 'Risk_Charge'  :  0.003 , 'Concentration_Charge' :  0.003  },
                                        'Cash BSCR Rating 4' : { 'Risk_Charge'  :  0.005 , 'Concentration_Charge' :  0.005  },
                                        'Cash BSCR Rating 5' : { 'Risk_Charge'  :  0.015 , 'Concentration_Charge' :  0.015  },
                                        'Cash BSCR Rating 6' : { 'Risk_Charge'  :  0.04 , 'Concentration_Charge' :  0.04  },
                                        'Cash BSCR Rating 7' : { 'Risk_Charge'  :  0.06 , 'Concentration_Charge' :  0.06  },
                                        'Cash BSCR Rating 8' : { 'Risk_Charge'  :  0.09 , 'Concentration_Charge' :  0.09  },
                                        'Alternatives' : { 'Risk_Charge'  :  0.2 , 'Concentration_Charge' :  0.2  },
                                        'LOC' : { 'Risk_Charge'  :  0.2 , 'Concentration_Charge' :  0.2  },
                                        'ML III' : { 'Risk_Charge'  :  0.2 , 'Concentration_Charge' :  0.2  },
                                        'DTA' : { 'Risk_Charge'  :  0.2 , 'Concentration_Charge' :  0  },
                                        'Derivative' : { 'Risk_Charge'  :  0.2 , 'Concentration_Charge' :  0  },
                                        'Policy loan' : { 'Risk_Charge'  :  0 , 'Concentration_Charge' :  0  },
            }
    
    
    BSCR_Asset_Risk_Charge_v2 = {   'Bonds Cash and Govt' : { 'Risk_Charge'  :  0 , 'Concentration_Charge' :  0  },
                                    'Bonds_1' : { 'Risk_Charge'  :  0.004 , 'Concentration_Charge' :  0.004  },
                                    'Bonds_2' : { 'Risk_Charge'  :  0.008 , 'Concentration_Charge' :  0.008  },
                                    'Bonds_3' : { 'Risk_Charge'  :  0.015 , 'Concentration_Charge' :  0.015  },
                                    'Bonds_4' : { 'Risk_Charge'  :  0.03 , 'Concentration_Charge' :  0.03  },
                                    'Bonds_5' : { 'Risk_Charge'  :  0.08 , 'Concentration_Charge' :  0.08  },
                                    'Bonds_6' : { 'Risk_Charge'  :  0.15 , 'Concentration_Charge' :  0.15  },
                                    'Bonds_7' : { 'Risk_Charge'  :  0.263 , 'Concentration_Charge' :  0.263  },
                                    'Bonds_8' : { 'Risk_Charge'  :  0.35 , 'Concentration_Charge' :  0.35  },
                                    'RMBS_1' : { 'Risk_Charge'  :  0.006 , 'Concentration_Charge' :  0.006  },
                                    'RMBS_2' : { 'Risk_Charge'  :  0.012 , 'Concentration_Charge' :  0.012  },
                                    'RMBS_3' : { 'Risk_Charge'  :  0.02 , 'Concentration_Charge' :  0.02  },
                                    'RMBS_4' : { 'Risk_Charge'  :  0.04 , 'Concentration_Charge' :  0.04  },
                                    'RMBS_5' : { 'Risk_Charge'  :  0.11 , 'Concentration_Charge' :  0.11  },
                                    'RMBS_6' : { 'Risk_Charge'  :  0.25 , 'Concentration_Charge' :  0.25  },
                                    'RMBS_7' : { 'Risk_Charge'  :  0.35 , 'Concentration_Charge' :  0.35  },
                                    'RMBS_8' : { 'Risk_Charge'  :  0.35 , 'Concentration_Charge' :  0.35  },
                                    'CMBS_1' : { 'Risk_Charge'  :  0.005 , 'Concentration_Charge' :  0.005  },
                                    'CMBS_2' : { 'Risk_Charge'  :  0.01 , 'Concentration_Charge' :  0.01  },
                                    'CMBS_3' : { 'Risk_Charge'  :  0.018 , 'Concentration_Charge' :  0.018  },
                                    'CMBS_4' : { 'Risk_Charge'  :  0.035 , 'Concentration_Charge' :  0.035  },
                                    'CMBS_5' : { 'Risk_Charge'  :  0.1 , 'Concentration_Charge' :  0.1  },
                                    'CMBS_6' : { 'Risk_Charge'  :  0.2 , 'Concentration_Charge' :  0.2  },
                                    'CMBS_7' : { 'Risk_Charge'  :  0.3 , 'Concentration_Charge' :  0.3  },
                                    'CMBS_8' : { 'Risk_Charge'  :  0.35 , 'Concentration_Charge' :  0.35  },
                                    'Bond Mutual Funds Cash and Govt' : { 'Risk_Charge'  :  0 , 'Concentration_Charge' :  0  },
                                    'Bond Mutual Funds 1' : { 'Risk_Charge'  :  0.004 , 'Concentration_Charge' :  0.004  },
                                    'Bond Mutual Funds 2' : { 'Risk_Charge'  :  0.008 , 'Concentration_Charge' :  0.008  },
                                    'Bond Mutual Funds 3' : { 'Risk_Charge'  :  0.015 , 'Concentration_Charge' :  0.015  },
                                    'Bond Mutual Funds 4' : { 'Risk_Charge'  :  0.03 , 'Concentration_Charge' :  0.03  },
                                    'Bond Mutual Funds 5' : { 'Risk_Charge'  :  0.08 , 'Concentration_Charge' :  0.08  },
                                    'Bond Mutual Funds 6' : { 'Risk_Charge'  :  0.15 , 'Concentration_Charge' :  0.15  },
                                    'Bond Mutual Funds 7' : { 'Risk_Charge'  :  0.263 , 'Concentration_Charge' :  0.263  },
                                    'Bond Mutual Funds 8' : { 'Risk_Charge'  :  0.35 , 'Concentration_Charge' :  0.35  },
                                    'Insured/Guaranteed Mortgages' : { 'Risk_Charge'  :  0.003 , 'Concentration_Charge' :  0.144  },
                                    'Other Commercial and Farm Mortgages' : { 'Risk_Charge'  :  0.05 , 'Concentration_Charge' :  0.1  },
                                    'Other Residential Mortgages' : { 'Risk_Charge'  :  0.015 , 'Concentration_Charge' :  0.2  },
                                    'Mortgages Not In Good Standing' : { 'Risk_Charge'  :  0.25 , 'Concentration_Charge' :  0.35  },
                                    'Other Loans' : { 'Risk_Charge'  :  0.05 , 'Concentration_Charge' :  0.05  },
                                    'Cash Cash and Govt' : { 'Risk_Charge'  :  0 , 'Concentration_Charge' :  0  },
                                    'Cash BSCR Rating 1' : { 'Risk_Charge'  :  0.001 , 'Concentration_Charge' :  0.001  },
                                    'Cash BSCR Rating 2' : { 'Risk_Charge'  :  0.002 , 'Concentration_Charge' :  0.002  },
                                    'Cash BSCR Rating 3' : { 'Risk_Charge'  :  0.003 , 'Concentration_Charge' :  0.003  },
                                    'Cash BSCR Rating 4' : { 'Risk_Charge'  :  0.005 , 'Concentration_Charge' :  0.005  },
                                    'Cash BSCR Rating 5' : { 'Risk_Charge'  :  0.015 , 'Concentration_Charge' :  0.015  },
                                    'Cash BSCR Rating 6' : { 'Risk_Charge'  :  0.04 , 'Concentration_Charge' :  0.04  },
                                    'Cash BSCR Rating 7' : { 'Risk_Charge'  :  0.06 , 'Concentration_Charge' :  0.06  },
                                    'Cash BSCR Rating 8' : { 'Risk_Charge'  :  0.09 , 'Concentration_Charge' :  0.09  },
                                    'Alternatives' : { 'Risk_Charge'  :  0.2 , 'Concentration_Charge' :  0.45  },
                                    'LOC' : { 'Risk_Charge'  :  0.2 , 'Concentration_Charge' :  0.2  },
                                    'ML III' : { 'Risk_Charge'  :  0.2 , 'Concentration_Charge' :  0.45  },
                                    'DTA' : { 'Risk_Charge'  :  0 , 'Concentration_Charge' :  0  },
                                    'Derivative' : { 'Risk_Charge'  :  0.2 , 'Concentration_Charge' :  0  },
                                    'Policy loan' : { 'Risk_Charge'  :  0 , 'Concentration_Charge' :  0  },
            }
    
    def asset_charge(workDir, fileName):
        
        os.chdir(workDir)
        
        RiskChargeInputFile = pd.ExcelFile(fileName)
        AssetRiskCharge = pd.read_excel(RiskChargeInputFile, sheet_name='Asset_Risk_Charge')
        
        return AssetRiskCharge
    
#%% Rating Mapping
        
class Rating_Mapping_Control:
    
    SP_Rating = {   'AAA' : 1 ,
                    'AA+' : 2 ,
                    'AA' : 2 ,
                    'AA-' : 2 ,
                    'A+' : 3 ,
                    'A' : 3 ,
                    'A-' : 3 ,
                    'BBB+' : 4 ,
                    'BBB' : 4 ,
                    'BBB-' : 4 ,
                    'BB+' : 5 ,
                    'BB' : 5 ,
                    'BB-' : 5 ,
                    'B+' : 6 ,
                    'B' : 6 ,
                    'B-' : 6 ,
                    'CCC+' : 7 ,
                    'CCC' : 7 ,
                    'CCC-' : 7 ,
                    'CC' : 8 ,
                    'D' : 8 ,
                    'NR' : 0 
                    }
    
    Moodys_Rating = {   'Aaa' : 1 ,
                        'Aa1' : 2 ,
                        'Aa2' : 2 ,
                        'Aa3' : 2 ,
                        'A1' : 3 ,
                        'A2' : 3 ,
                        'A3' : 3 ,
                        'Baa1' : 4 ,
                        'Baa2' : 4 ,
                        'Baa3' : 4 ,
                        'Ba1' : 5 ,
                        'Ba2' : 5 ,
                        'Ba3' : 5 ,
                        'B1' : 6 ,
                        'B2' : 6 ,
                        'B3' : 6 ,
                        'Caa1' : 7 ,
                        'Caa2' : 7 ,
                        'Caa3' : 7 ,
                        'Ca' : 8 ,
                        'C' : 8 ,
                        'WR' : 0 ,
                        'NR' : 0 
                        }
    
    Fitch_Rating = {    'AAA' : 1 ,
                        'AA+' : 2 ,
                        'AA' : 2 ,
                        'AA-' : 2 ,
                        'A+' : 3 ,
                        'A' : 3 ,
                        'A-' : 3 ,
                        'BBB+' : 4 ,
                        'BBB' : 4 ,
                        'BBB-' : 4 ,
                        'BB+' : 5 ,
                        'BB' : 5 ,
                        'BB-' : 5 ,
                        'B+' : 6 ,
                        'B' : 6 ,
                        'B-' : 6 ,
                        'CCC+' : 7 ,
                        'CCC' : 7 ,
                        'CCC-' : 7 ,
                        'C' : 8 ,
                        'D' : 8 ,
                        'CC' : 8 ,
                        'WD' : 0 ,
                        'NR' : 0 
            }
    
    AIG_Rating = {  'AAA' : 1 ,
                    'AA' : 2 ,
                    'A' : 3 ,
                    'BBB' : 4 ,
                    'BB' : 5 ,
                    'B' : 6 ,
                    'CCC' : 7 ,
                    'CC' : 8 ,
                    'C' : 8 ,
                    'D' : 8 ,
                    'NR' : 8 ,
                    'NA' : 8 
            }
    
    AC_Mapping_to_BMA = {   'ABS'                       : 'CMBS' ,
                            'CDO'                       : 'Bonds' ,
                            'CMBS Agency'               : 'CMBS' ,
                            'CMBS Non-Agency'           : 'CMBS' ,
                            'Cash'                      : 'Bonds Cash and Govt' ,
                            'Cash Fund'                 : 'Bonds Cash and Govt' ,
                            'Short Term Securities'     : 'Bonds Cash and Govt' ,
                            'Collateral Loan'           : 'Other Commercial and Farm Mortgages' ,
                            'Commercial Mortgage Loan'  : 'Other Commercial and Farm Mortgages' ,
                            'Common Equity'             : 'Alternatives' ,
                            'Corporate Bond'            : 'Bonds' ,
                            'Credit Loan'               : 'Bonds' ,
                            'Derivative'                : 'Derivative' ,
                            'Hedge Fund'                : 'Alternatives' ,
                            'Mezzanine Mortgage Loan'   : 'Other Commercial and Farm Mortgages' ,
                            'National Govt'             : 'Bonds Cash and Govt' ,
                            'Other Invested Assets'     : 'Alternatives' ,
                            'Private Equity Fund'       : 'Alternatives' ,
                            'RMBS Agency'               : 'RMBS' ,
                            'RMBS Non-Agency'           : 'RMBS' ,
                            'Regional Govt'             : 'Bonds' ,
                            'Supranational'             : 'Bonds Cash and Govt' ,
                            'Residential Mortgage Loan' : 'Other Residential Mortgages' ,
                            'Consumer Loan'             : 'Policy Loan' ,
                            'ALBA_Hedge'                : 'Derivative' 
            }
    
    Legal_Entity = {'Owning Entity Name': {0: 'American General Life Insurance Company',
                      1: 'The United States Life Insurance Company in the City of New York',
                      2: 'The Variable Annuity Life Insurance Company',
                      3: 'National Union Fire Insurance Company of Pittsburgh, Pa.',
                      4: 'Lexington Insurance Company',
                      5: 'American Home Assurance Company',
                      6: 'Fortitude Reinsurance Company Ltd.',
                      7: 'American International Reinsurance Company, Ltd.',
                      8: 'USLSAMRE',
                      9: 'VALSAMRE',
                      10: 'AHSAMRE',
                      11: 'AGLSAMRE',
                      12: 'AGLSAMRE DTC'},
                     'Owning Entity GEMS ID': {0: 23455,
                      1: 23539,
                      2: 23460,
                      3: 10118,
                      4: 10104,
                      5: 10029,
                      6: 50451,
                      7: 10050,
                      8: 0,
                      9: 0,
                      10: 0,
                      11: 0,
                      12: 0},
                     'Category': {0: 'ModCo',
                      1: 'ModCo',
                      2: 'ModCo',
                      3: 'LPT',
                      4: 'LPT',
                      5: 'LPT',
                      6: 'Surplus',
                      7: 'ALBA',
                      8: 'ModCo',
                      9: 'ModCo',
                      10: 'LPT',
                      11: 'ModCo',
                      12: 'ModCo'}}
          
    Rating = {'NAIC Rating': {0: '1',
              1: '1',
              2: '1',
              3: '1-',
              4: '1-',
              5: '1=',
              6: '1=',
              7: '1AM',
              8: '1AM',
              9: '1AM',
              10: '1FE',
              11: '1FE',
              12: '1FE',
              13: '1FE',
              14: '1FM',
              15: '1FM',
              16: '1FM',
              17: '1FM',
              18: '1FM',
              19: '1FM',
              20: '1FM',
              21: '1FM',
              22: '1FM',
              23: '1FM',
              24: '1PL',
              25: '1PL',
              26: '1PL',
              27: '1Z',
              28: '1Z',
              29: '2-',
              30: '2+',
              31: '2=',
              32: '2AM',
              33: '2FE',
              34: '2FE',
              35: '2FE',
              36: '2FM',
              37: '2FM',
              38: '2FM',
              39: '2FM',
              40: '2PL',
              41: '2S-',
              42: '2Z',
              43: '3+',
              44: '3AM',
              45: '3AM',
              46: '3FE',
              47: '3FE',
              48: '3FE',
              49: '3FM',
              50: '3FM',
              51: '3FM',
              52: '3PL',
              53: '3PL',
              54: '4-',
              55: '4AM',
              56: '4FE',
              57: '4FE',
              58: '4FE',
              59: '4FM',
              60: '4FM',
              61: '4Z',
              62: '5FE',
              63: '5FE',
              64: '5FM',
              65: '5GI',
              66: '5Z',
              67: '6',
              68: '6FE',
              69: '6FE',
              70: '6FE',
              71: '6FE',
              72: '6FM',
              73: '6FM',
              74: '6FM',
              75: '6FM',
              76: '6PL',
              77: 'L',
              78: 'RP1FE',
              79: 'RP1VFE',
              80: 'SOURCE UNDEFINED',
              81: 'SOURCE UNDEFINED',
              82: 'SOURCE UNDEFINED',
              83: 'SOURCE UNDEFINED',
              84: 'SOURCE UNDEFINED',
              85: 'Z',
              86: '5FM'},
              
             'AIG Derived Rating': {0: 'AA',
              1: 'AAA',
              2: 'BBB',
              3: 'A',
              4: 'AA',
              5: 'AA',
              6: 'BBB',
              7: 'AA',
              8: 'BBB',
              9: 'BBB',
              10: 'A',
              11: 'AA',
              12: 'AAA',
              13: 'BBB',
              14: 'A',
              15: 'AA',
              16: 'AAA',
              17: 'B',
              18: 'BB',
              19: 'BBB',
              20: 'C',
              21: 'CC',
              22: 'CCC',
              23: 'D',
              24: 'A',
              25: 'AA',
              26: 'AAA',
              27: 'A',
              28: 'AA',
              29: 'BBB',
              30: 'BBB',
              31: 'BBB',
              32: 'BBB',
              33: 'A',
              34: 'BB',
              35: 'BBB',
              36: 'BBB',
              37: 'CC',
              38: 'CCC',
              39: 'D',
              40: 'BBB',
              41: 'BBB',
              42: 'BBB',
              43: 'BB',
              44: 'BB',
              45: 'BBB',
              46: 'B',
              47: 'BB',
              48: 'BBB',
              49: 'BB',
              50: 'CCC',
              51: 'D',
              52: 'BB',
              53: 'BBB',
              54: 'B',
              55: 'B',
              56: 'B',
              57: 'BB',
              58: 'CCC',
              59: 'B',
              60: 'CCC',
              61: 'B',
              62: 'CCC',
              63: 'D',
              64: 'CCC',
              65: 'CCC',
              66: 'CCC',
              67: 'C',
              68: 'BBB',
              69: 'C',
              70: 'CC',
              71: 'D',
              72: 'C',
              73: 'CC',
              74: 'CCC',
              75: 'D',
              76: 'BBB',
              77: None,
              78: 'AA',
              79: 'AA',
              80: 'A',
              81: 'AA',
              82: 'B',
              83: 'BBB',
              84: None,
              85: None,
              86: 'CC'},
             
             'Derived Rating Modified': {0: 'AA',
              1: 'AAA',
              2: 'A',
              3: 'A',
              4: 'AA',
              5: 'AA',
              6: 'A',
              7: 'AA',
              8: 'A',
              9: 'A',
              10: 'A',
              11: 'AA',
              12: 'AAA',
              13: 'A',
              14: 'A',
              15: 'AA',
              16: 'AAA',
              17: 'A',
              18: 'A',
              19: 'A',
              20: 'A',
              21: 'A',
              22: 'A',
              23: 'A',
              24: 'A',
              25: 'AA',
              26: 'AAA',
              27: 'A',
              28: 'AA',
              29: 'BBB',
              30: 'BBB',
              31: 'BBB',
              32: 'BBB',
              33: 'BBB',
              34: 'BBB',
              35: 'BBB',
              36: 'BBB',
              37: 'BBB',
              38: 'BBB',
              39: 'BBB',
              40: 'BBB',
              41: 'BBB',
              42: 'BBB',
              43: 'BB',
              44: 'BB',
              45: 'BB',
              46: 'BB',
              47: 'BB',
              48: 'BB',
              49: 'BB',
              50: 'BB',
              51: 'BB',
              52: 'BB',
              53: 'BB',
              54: 'B',
              55: 'B',
              56: 'B',
              57: 'B',
              58: 'B',
              59: 'B',
              60: 'B',
              61: 'B',
              62: 'CCC',
              63: 'CCC',
              64: 'CCC',
              65: 'CCC',
              66: 'CCC',
              67: 'CC',
              68: 'CC',
              69: 'CC',
              70: 'CC',
              71: 'CC',
              72: 'CC',
              73: 'CC',
              74: 'CC',
              75: 'CC',
              76: 'CC',
              77: 'A',
              78: 'AA',
              79: 'A',
              80: 'NA-BBB',
              81: 'NA-BBB',
              82: 'NA-BBB',
              83: 'NA-BBB',
              84: 'NA-BBB',
              85: 'A',
              86: 'CCC'}}
