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
                                   'AccInt_ALBA'        : 12932663.5583980,            # Update Quarterly from Asset Adjustment
                                   'NCF_end_of_quarter' : 526609469.664638,     #for Q4 settlement (from Q3 2019 LBA)
                                   'end_of_quarter'     : datetime.datetime(2019, 12, 31)
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
                                   'Loan_Receivable_charge' : 1283268.16,
                                   'NCF_end_of_quarter' : 172524511.079335,    #for Q4 settlement (from Q3 2019 LBA)
                                   'end_of_quarter'     : datetime.datetime(2019, 12, 31)
                                   },
                        'Agg':{
                                   'NCF_end_of_quarter' : 699133980.743973,    #for Q4 settlement (from Q3 2019 LBA)
                                   'end_of_quarter'     : datetime.datetime(2019, 12, 31)
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
surplus_account_CF_file = 'Surplus_Account_CF.xlsx' #'Overseas pool August.xlsx'
derivatives_IR01_file   = 'derivatives_IR01_revised_one_day_lag.xlsx'
 
### Input to be reviewed less frequently maybe on yearly basis
tax_rate = 0.21
Inv_Fee_GBP = 0.0004
Cost_of_Capital = 0.06


# Last Update: 2019 Q4 Main Run v004
long_f = {"inpayment"   :   {"SS"   :[0.67558645753423800, 0.19655422082704300, 0.05834278649490480, 0.06086375377424740, 0.00865278136956639],
                             "SPIA" :[0.10282382553318500, 0.05987981639640980, 0.08395879420438730, 0.34542951154561300, 0.40790805232040600],
                             "TFA"  :[0.11782221333920000, 0.19054745824093600, 0.17234990253166300, 0.32208922152261800, 0.19719120436558300],
                             "ALBA" :[0.15094086150050300, 0.48682286655272700, 0.17357358741897800, 0.18735288698350600, 0.00130979754428531]
                             },
          
          "deferred"    :   {"SS"   :[0, 0, 0, 0, 0, 0],
                             "SPIA" :[0.01150069548723040, 0.00457447367368145, 0.05340972671524420, 0.05629152478495250, 0.07619995744649920, 0.79802362189239200],
                             "TFA"  :[0.23660734545365700, 0.34372895543602900, 0.28090644162543100, 0.09646717398700570, 0.03733716341552880, 0.00495292008234892],
                             "ALBA" :[0, 0, 0, 0, 0, 0]
                             }
          }

long_age = {"inpayment" : {"SS":45.6127553856134, "SPIA":74.6258256187035, "TFA":67.9362262784771, "ALBA":63.2356818941107},
            "deferred"  : {"SS":0, "SPIA":85.8886358870649, "TFA":59.3191313932475, "ALBA":0},
            "ult_inpay" : 81,
            "ult_def"   : 76
            }
            
long_dis ={"SS"     :{"inpayment"   : 1, "deferred" : 0},
           "SPIA"   :{"inpayment"   : 0.99216360697279500, "deferred" : 0.00783639302720451},
           "TFA"    :{"inpayment"   : 0.98652355064420000, "deferred" : 0.01347644935580010},
           "ALBA"   :{"inpayment"   : 1, "deferred" : 0}
           }

morbidity = {"LTC"  :{"active":0.662, "inpayment": 0.337763183043341},
             "AH"   :{"active":0.334,"critical":0.553,"inpayment": 0.113211327872708}}


# Last Update: 2019 Q4 Main Run v004
PC_mapping =  {'Property':         [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
               'Personal_Accident':[0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.327591408501980, 0.0000, 0.0000, 0.0000], 
               'US_Casualty':      [0.0000, 0.512764787122216, 0.802904311723108, 0.318027814568074, 0.7490, 0.0000, 0.0000, 0.0000, 0.310472321640324, 0.0000, 0.9500],
               'US_Casualty_NP':   [1.0000, 0.487235212877784, 0.197095688276892, 0.681972185431926, 0.2510, 0.0000, 1.0000, 0.672408591498020, 0.689527678359676, 1.0000, 0.0500],
               'US_Specialty':     [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.290578784073283, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
               'US_Specialty_NP':  [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.709421215926717, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]}
