# -*- coding: utf-8 -*-
"""
Created on Thu May 23 16:00:37 2019

@author: seongpar
"""
import os
import pandas as pd
import numpy as np
import datetime

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

Reserve_Risk_Charge_BMA_Standard = { 'Property' : 0.43845, 'Personal_Accident': 0.29666, 'US_Casualty': 0.43018, 'US_Casualty_NP': 0.48842, 'US_Specialty': 0.465067, 'US_Specialty_NP': 0.48276 }
Reserve_Risk_Charge_BMA_bespoke  = { 'Property' : 0.325,   'Personal_Accident': 0.532,  'US_Casualty': 0.341, 'US_Casualty_NP': 0.37, 'US_Specialty': 0.579,    'US_Specialty_NP': 0.579 }

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

# Up - if the binding scenario of ALM Risk Charge is market Up: 1Q20
Market_corre_Future_BMA_up = {'Fixed_income' : [1.00, 0.50, 0.00, 0.25, 0.00],
                              'Equity'       : [0.50, 1.00, 0.00, 0.25, 0.00],
                              'Interest_rate': [0.00, 0.00, 1.00, 0.25, 0.00],
                              'Currency'     : [0.25, 0.25, 0.25, 1.00, 0.00],
                              'Concentration': [0.00, 0.00, 0.00, 0.00, 1.00]
                              }

# Down - if the binding scenario of ALM Risk Charge is market Down: 4Q19
Market_corre_Future_BMA_dn = {'Fixed_income' : [1.00, 0.50, 0.25, 0.25, 0.00],
                              'Equity'       : [0.50, 1.00, 0.25, 0.25, 0.00],
                              'Interest_rate': [0.25, 0.25, 1.00, 0.25, 0.00],
                              'Currency'     : [0.25, 0.25, 0.25, 1.00, 0.00],
                              'Concentration': [0.00, 0.00, 0.00, 0.00, 1.00]
                              }

Market_cor_Current =  pd.DataFrame(data = Market_corre_Current, index = ['Fixed_income', 'Equity', 'Interest_rate','Currency','Concentration'])

Market_cor_Future  =  {datetime.datetime(2019, 12, 31): pd.DataFrame(data = Market_corre_Future_BMA_dn, index = ['Fixed_income', 'Equity', 'Interest_rate','Currency','Concentration']),
                       datetime.datetime(2020,  3, 31): pd.DataFrame(data = Market_corre_Future_BMA_up, index = ['Fixed_income', 'Equity', 'Interest_rate','Currency','Concentration'])
                       }

# Update for 4Q19 future regime
Equity_corre = {'Type_1': [1.00, 0, 0, 0],
                'Type_2': [0, 1.00, 0, 0],
                'Type_3': [0, 0, 1.00, 0],
                'Type_4': [0, 0, 0, 1.00] }

# Equity_corre = {'Type_1': [1.00, 0.75, 0.75, 0.50],
#                 'Type_2': [0.75, 1.00, 0.75, 0.50],
#                 'Type_3': [0.75, 0.75, 1.00, 0.50],
#                 'Type_4': [0.50, 0.50, 0.50, 1.00] }

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

