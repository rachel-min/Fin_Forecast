# -*- coding: utf-8 -*-
"""
Created on Thu May 23 16:00:37 2019

@author: seongpar
"""
import os
import pandas as pd
import numpy as np

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
        


def asset_charge(workDir, fileName):
    
    os.chdir(workDir)
    
    RiskChargeInputFile = pd.ExcelFile(fileName)
    AssetRiskCharge = pd.read_excel(RiskChargeInputFile, sheet_name='Asset_Risk_Charge')
    
    return AssetRiskCharge

