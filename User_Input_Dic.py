# -*- coding: utf-8 -*-
"""
Created on Wed May 22 19:28:00 2019

@author: seongpar
"""
import datetime
import pandas as pd
import os

### For Dashboard
EBS_Inputs  = { datetime.datetime(2019, 3, 29) : 

                       { 'LT' : {  'Policy_Loan'        : 450685868.5,
                                   'LOC'                : 0,
                                   'Tax_Payable'        : -30891147.85,
                                   'Settlement_Payable' : 507961678.2,
                                   'GOE'                : 16047780.85, 
                                   'pre_Tax_Surplus'    : 2535152756.34402,
                                   'DTA'                : 21032414.000,
                                   'Other_Assets_adj'   : -1553450,
                                   'Other_Liabilities'  : 9177541.75049096,
                                   'Derivative_Dur'     : 0.8811,
                                   'Settlement_Date'    : datetime.datetime(2019, 6, 10),
                                   'LTIC'               : 243414184.1,
                                   'LTIC_Dur'           :-3.8566794852585,
                                   'LTIC_Cap'           : 330000000                                   
                                  } ,
    
    
                        'GI' : {   'Policy_Loan'        : 0,
                                   'LOC'                : 550000000,
                                   'Tax_Payable'        : 34522224.47,
                                   'Settlement_Payable' : 130982401.2,
                                   'GOE'                : 69128938.04,
                                   'pre_Tax_Surplus'    : 956890207.496267 ,
                                   'DTA'                : 85929931.7745805,
                                   'Other_Assets_adj'   : 25651312,
                                   'Other_Liabilities'  : 9444937.68950916,
                                   'Derivative_Dur'     : 0.0,
                                   'Settlement_Date'    : datetime.datetime(2019, 5, 31),
                                   'LTIC'               : 0,
                                   'LTIC_Dur'           : 0,
                                   'LTIC_Cap'           : 0 
                                   }                        
                        },               

                datetime.datetime(2019, 3, 31) : 

                       { 'LT' : {  'Policy_Loan'        : 450685868.5,
                                   'LOC'                : 0,
                                   'Tax_Payable'        : -30891147.85,
                                   'Settlement_Payable' : 507961678.2,
                                   'GOE'                : 16047780.85, 
                                   'pre_Tax_Surplus'    : 2535152756.34402,
                                   'DTA'                : 21032414.000,
                                   'Other_Assets_adj'   : -1553450,
                                   'Other_Liabilities'  : 9177541.75049096,
                                   'Derivative_Dur'     : 0.8811,
                                   'Settlement_Date'    : datetime.datetime(2019, 6, 10),
                                   'LTIC'               : 243414184.1,
                                   'LTIC_Dur'           :-3.8566794852585,
                                   'LTIC_Cap'           : 330000000                                   
                                  } ,
    
    
                        'GI' : {   'Policy_Loan'        : 0,
                                   'LOC'                : 550000000,
                                   'Tax_Payable'        : 34522224.47,
                                   'Settlement_Payable' : 130982401.2,
                                   'GOE'                : 69128938.04,
                                   'pre_Tax_Surplus'    : 956890207.496267 ,
                                   'DTA'                : 85929931.7745805,
                                   'Other_Assets_adj'   : 25651312,
                                   'Other_Liabilities'  : 9444937.68950916,
                                   'Derivative_Dur'     : 0.0,
                                   'Settlement_Date'    : datetime.datetime(2019, 5, 31),
                                   'LTIC'               : 0,
                                   'LTIC_Dur'           : 0,
                                   'LTIC_Cap'           : 0 
                                   }                        
                        },
                        
                datetime.datetime(2019, 6, 28) : 

                       { 'LT' : {  'Policy_Loan'        : 442021567.001516,   # Update Quarterly from EBS
                                   'LOC'                : 0,
                                   'Tax_Payable'        : 15628343.6079697,   # Update Quarterly from EBS
                                   'Settlement_Payable' : 494359718.079957,   # Update Quarterly from EBS
                                   'GOE'                : 25469495.0225,      # Update Quarterly from EBS 
                                   'pre_Tax_Surplus'    : 2391679407.592346,  # Update Quarterly from EBS
                                   'DTA'                : 91183534.4283181,   # Update Quarterly from EBS
                                   'Other_Assets_adj'   :-6883191.88000006,   # Update Quarterly from EBS: other assets (exc. Surplus Asset Acc Int)
                                   'Other_Liabilities'  : 11415503,           # Update Quarterly from EBS
#                                   'Derivative_Dur'     : 0.795303965889861,  # Update Quarterly from EBS: not being used anymore
                                   'Settlement_Date'    : datetime.datetime(2019, 8, 30),
                                   'LTIC'               : 330000000,          # Update Quarterly from EBS
                                   'LTIC_Dur'           :-3.8566794852585,    # pending
                                   'LTIC_Cap'           : 330000000,
                                   'AccInt_IDR_to_IA'   : 3673205.4356998,    # Update Quarterly from Asset Adjustment
                                   'True_up_FWA_LT'     :-160546562,          # Update Quarterly from Asset Adjustment
                                   'Repo_Paid_Date'     : datetime.datetime(2019, 7, 26),
#                                   'True_up_Cash_LT'    : 7781621.3,          # Update Quarterly from Asset Adjustment
#                                   'Surplus_AccInt_LT'  : 8124732.44,         # not needed
#                                   'AccInt_ALBA'        : 11859664            # Update Quarterly from Asset Adjustment
                                  } ,
    
    
                        'GI' : {   'Policy_Loan'        : 0,
                                   'LOC'                : 550000000,          # Update Quarterly from EBS
                                   'Tax_Payable'        : 17826375.1929009,   # Update Quarterly from EBS
                                   'Settlement_Payable' : 115335972,          # Update Quarterly from EBS
                                   'GOE'                : 55361392.9075,      # Update Quarterly from EBS
                                   'pre_Tax_Surplus'    : 858947473.2549553,  # Update Quarterly from EBS
                                   'DTA'                : 126778322.130307,   # Update Quarterly from EBS
                                   'Other_Assets_adj'   : 25000000,           # Update Quarterly from EBS: other assets (exc. Surplus Asset Acc Int) from Loan Receivable to TPA company
                                   'Other_Liabilities'  : 0,                  # Update Quarterly from EBS
#                                   'Derivative_Dur'     : 0.0,
                                   'Settlement_Date'    : datetime.datetime(2019, 8, 26),
                                   'LTIC'               : 0,
                                   'LTIC_Dur'           : 0,
                                   'LTIC_Cap'           : 0,
                                   'AccInt_IDR_to_IA'   : 184293.433699985,    # Update Quarterly from Asset Adjustment
#                                   'True_up_Cash_GI'    : 33370983.12,         # Update Quarterly from Asset Adjustment
#                                   'Surplus_AccInt_GI'  : 6215661.34,          # not needed
                                   'True_up_FWA_GI'     : 33083788.28,          # Update Quarterly from Asset Adjustment
                                   'Repo_Paid_Date'     : datetime.datetime(2019, 7, 26)
                                   } 
                        } ,
                        
                datetime.datetime(2019, 9, 30) : 

                       { 'LT' : {  'Policy_Loan'        : 442021567.00,   # Update Quarterly from EBS
                                   'LOC'                : 0,
                                   'Tax_Payable'        : 117730814.75473,   # Update Quarterly from EBS
                                   'Settlement_Payable' : 545078583.08,   # Update Quarterly from EBS
                                   'GOE'                : 13064395.4200000,      # Update Quarterly from EBS 
                                   'pre_Tax_Surplus'    : 2096116683.348280,  # Update Quarterly from EBS
                                   'DTA'                : 224109211.721473,   # Update Quarterly from EBS
                                   'Other_Assets_adj'   :-10211335.340000,   # Update Quarterly from EBS: other assets (exc. Surplus Asset Acc Int)
                                   'Other_Liabilities'  : 55075295.881545,   # Update Quarterly from EBS
#                                   'Derivative_Dur'     : 0.795303965889861,  # Update Quarterly from EBS: not being used anymore
                                   'Settlement_Date'    : datetime.datetime(2019, 11, 27),
                                   'LTIC'               : 900000000,          # Update Quarterly from EBS
                                   'LTIC_Dur'           :-3.8566794852585,    # pending
                                   'LTIC_Cap'           : 330000000,
                                   'AccInt_IDR_to_IA'   : 6044449.810445,    # Update Quarterly from Asset Adjustment
                                   'True_up_FWA_LT'     : 0,          #Q3:-12462519.3747343, Update Quarterly from Asset Adjustment
#                                   'Repo_Paid_Date'     : datetime.datetime(2019, 7, 26),
                                   'True_up_Cash_LT'    : 0,          # Q3:32334131.4499995 ,Update Quarterly from Asset Adjustment
#                                   'Surplus_AccInt_LT'  : 8124732.44,         # not needed
                                   'AccInt_ALBA'        : 12932663.5583980            # Update Quarterly from Asset Adjustment
                                  } ,
    
    
                        'GI' : {   'Policy_Loan'        : 0,
                                   'LOC'                : 550000000,          # Update Quarterly from EBS
                                   'Tax_Payable'        : -27850434.6713817,   # Update Quarterly from EBS
                                   'Settlement_Payable' : 125126956.550003,          # Update Quarterly from EBS
                                   'GOE'                : 34282182.0600000,      # Update Quarterly from EBS
                                   'pre_Tax_Surplus'    : 843434663.955281,  # Update Quarterly from EBS
                                   'DTA'                : 101753433.733019,   # Update Quarterly from EBS
                                   'Other_Assets_adj'   : 26696601.020000,    # Update Quarterly from EBS: other assets (exc. Surplus Asset Acc Int) from Loan Receivable to TPA company
                                   'Other_Liabilities'  : -18922383.029074,   # Update Quarterly from EBS
#                                   'Derivative_Dur'     : 0.0,
                                   'Settlement_Date'    : datetime.datetime(2019, 11, 27),
                                   'LTIC'               : 0,
                                   'LTIC_Dur'           : 0,
                                   'LTIC_Cap'           : 0,
                                   'AccInt_IDR_to_IA'   : 167151.835390,    # Update Quarterly from Asset Adjustment
                                   'True_up_Cash_GI'    : 0,             #Q3: 5043460.3400001 Update Quarterly from Asset Adjustment
#                                   'Surplus_AccInt_GI'  : 6215661.34,          # not needed
                                   'True_up_FWA_GI'     : 0,              #Q3: 1295377.6788536 Update Quarterly from Asset Adjustment
#                                   'Repo_Paid_Date'     : datetime.datetime(2019, 7, 26)
                                   'Loan_Receivable_charge' : 1283268.16
                                   }
                        
                        }   
                }

### For Actual BMA Reporting - Needs update each quarter           
Tax_sharing = {'Agg': 495708591, 'LT': 325134436, 'GI': 170574155}
 
ALBA_adj = 16560000 # 4Q18 & 1Q19: 13983740.1700001; 2Q19:14509113; 3Q19: 14509113; 4Q19: 16560000

#Future regime ALM BSCR - up/down scenario ALBA hedge and Swap hedge 
Hedge_effect ={datetime.datetime(2019, 12, 31): {'Up'   : -436815113,
                                                 'Down' :1227462309}
               }

### Input - SFS_BS - Vincent 07/08/2019
### Can process either dataframe or file path 
def SFS_BS(SFS_File):
    if isinstance(SFS_File, str):
        SFS_File = pd.ExcelFile(SFS_File)
        SFS_BS = SFS_File.parse('SFS BS')
    else:
        SFS_BS = SFS_File
    SFS_BS = SFS_BS.fillna(0)
    
    ### Trim all the columns
    SFS_BS_obj = SFS_BS.select_dtypes(['object'])
    SFS_BS[SFS_BS_obj.columns] = SFS_BS_obj.apply(lambda x: x.str.strip())
    
    return SFS_BS

##123
asset_workDir           = r'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\Asset_Holding_Feed'
surplus_account_CF_file = 'Overseas pool August.xlsx'
derivatives_IR01_file   = 'derivatives_IR01_revised_one_day_lag.xlsx'
 
### Input to be reviewed less frequently maybe on yearly basis
tax_rate = 0.21
Inv_Fee_GBP = 0.0004
Cost_of_Capital = 0.06


long_f = {"inpayment"   :   {"SS"   :[0.5461662268348700, 0.2545314867167770, 0.0852147385804457, 0.0953678963051677, 0.0187196515627395],
                             "SPIA" :[0.0974507310727962, 0.0573458055387673, 0.0811166577338227, 0.3509738355043370, 0.4131129701502770],
                             "TFA"  :[0.1076814990669880, 0.0949355473839442, 0.2007181932785390, 0.3602314606804970, 0.2364332995900320],
                             "ALBA" :[0.0015430574424368, 0.2220244771611000, 0.4075272963866020, 0.3682443824873840, 0.0006607865224781]
                             },
                        
          "deferred"    :   {"SS"   :[0.7887830243726350, 0.0805754041375093, 0.0681470747780306, 0.0389987304418374, 0.0170482002445230, 0.0064475660254647],
                             "SPIA" :[0.1385811134621300, 0.0395106875887056, 0.0877472196254331, 0.1123153325247080, 0.1381804596634760, 0.4836651871355480],
                             "TFA"  :[0.1480811027669170, 0.3412180127984280, 0.4277835645126450, 0.0486988289641064, 0.0198145376311520, 0.0144039533267508],
                             "ALBA" :[0.3352247876051390, 0.3938150357466250, 0.2704809401853730, 0.0003545409114745, 0, 0.0001246955513895]
                             }
          }

long_age = {"inpayment" : {"SS":51.7859288765259, "SPIA":74.6664702347134, "TFA":69.5420583550923, "ALBA":69.0671539181792},
            "deferred"  : {"SS":40.1261333454091, "SPIA":72.1116110424958, "TFA":60.1188077321654, "ALBA":57.3008976171722},
            "ult_inpay" : 81,
            "ult_def"   : 76        
            }
            
long_dis ={"SS"     :{"inpayment"   : 0.409744552526238, "deferred" : 0.590255447473762},
           "SPIA"   :{"inpayment"   : 0.874721445504917, "deferred" : 0.125278554495083},
           "TFA"    :{"inpayment"   : 0.841584099874696, "deferred" : 0.158415900125304},
           "ALBA"   :{"inpayment"   : 0.422224573846380, "deferred" : 0.577775426153620}
           }

morbidity = {"LTC"  :{"active":0.662, "inpayment": 0.337763183043341},
             "AH"   :{"active":0.334,"critical":0.553,"inpayment": 0.113211327872708}}

PC_mapping =  {'Property':         [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
               'Personal_Accident':[0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.4194720676382, 0.0000, 0.0000, 0.0000], 
               'US_Casualty':      [0.0000, 0.56488795476, 0.82510327218, 0.2500, 0.7330, 0.0000, 0.0000, 0.0000, 0.22174558759, 0.0000, 0.9500],
               'US_Casualty_NP':   [1.0000, 0.43511204524, 0.17489672782, 0.7500, 0.2670, 0.0000, 1.0000, 0.5805279323618, 0.778254412413576, 1.0000, 0.0500],
               'US_Specialty':     [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.283728595712923, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
               'US_Specialty_NP':  [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.716271404287077, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]}
