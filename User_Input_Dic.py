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
                        },
                datetime.datetime(2019, 12, 31) : 

                       { 'LT' : {  'Policy_Loan'        : 444566868.34,   # Update Quarterly from EBS
                                   'LOC'                : 0,
                                   'Tax_Payable'        : -87923467,   # Update Quarterly from EBS
                                   'Settlement_Payable' : 491402475.11,   # Update Quarterly from EBS
                                   'GOE'                : 6186968.09999999,      # Update Quarterly from EBS 
                                   'pre_Tax_Surplus'    : 2169480479.77343,  # Update Quarterly from EBS
                                   'DTA'                : 109633594.586028  ,   # Update Quarterly from EBS
                                   'Other_Assets_adj'   : -8744147.56368878,   # Update Quarterly from EBS: other assets (exc. Surplus Asset Acc Int)
                                   'Other_Liabilities'  : 33400827.6928407,           # Update Quarterly from EBS
                                   'Settlement_Date'    : datetime.datetime(2020, 2, 27),
                                   'LTIC'               : 330000000,          # Update Quarterly from EBS
                                   'LTIC_Dur'           : 0,    # pending -3.8566794852585
                                   'LTIC_Cap'           : 330000000,
                                   'AccInt_IDR_to_IA'   : 3446518.90912157,       # Update Quarterly from Asset Adjustment
                                   'True_up_FWA_LT'     : 330623395,   #230508292.8 FWA Cash +  72459844 derivative,           
                                   'True_up_Cash_LT'    : 0,          # Update Quarterly from Asset Adjustment
                                   'AccInt_ALBA'        : 15223773.99648,            # Update Quarterly from Asset Adjustment
                                   'CFT_Settlement'     : 272000000, 
                                   'Macro_Hedge_credit' : 153152087.9186,
                                   'PC_bespoke'         : 0,
                                   'ML_III_loss'        : 250000000, #for dates between 3/20 and 3/30
                                   'alts_loss'          : 40000000,  #for dates between 3/20 and 3/30
                                   'NCF_end_of_quarter' : 517279166.96919686,
                                   'end_of_quarter'     : datetime.datetime(2020,3,31)
                                    } ,
    
    
                        'GI' : {   'Policy_Loan'        : 0,
                                   'LOC'                : 550000000,          # Update Quarterly from EBS
                                   'Tax_Payable'        : 21474274,   # Update Quarterly from EBS
                                   'Settlement_Payable' : 113162248.680002,          # Update Quarterly from EBS
                                   'GOE'                : 27833711.27,      # Update Quarterly from EBS
                                   'pre_Tax_Surplus'    : 1021054129.65896,   # before update:954618501.053859,  # Update Quarterly from EBS
                                   'DTA'                : 98954910.0616592,   # Update Quarterly from EBS
                                   'Other_Assets_adj'   : 26073393.2436888,           # Update Quarterly from EBS: other assets (exc. Surplus Asset Acc Int) from Loan Receivable to TPA company
                                   'Other_Liabilities'  : -2075106.05309111,                  # Update Quarterly from EBS
                                   'Settlement_Date'    : datetime.datetime(2020, 3, 17),
                                   'LTIC'               : 0,
                                   'LTIC_Dur'           : 0,
                                   'LTIC_Cap'           : 0,
                                   'AccInt_IDR_to_IA'   : 193159.389121572,    # Update Quarterly from Asset Adjustment
                                   'True_up_Cash_GI'    : 0,         # Update Quarterly from Asset Adjustment
                                   'True_up_FWA_GI'     : 15921089.3543658, #15921089.3543658,          # Update Quarterly from Asset Adjustment
                                   'Loan_Receivable_charge' : 1350219.4955,
                                   'Macro_Hedge_credit' : 18117892.1601293,
                                   'PC_bespoke'         : 0, #85043733.6292596, #pc bespoke factor for reserve risk
                                   'NCF_end_of_quarter' : 130241935.20512448,
                                   'end_of_quarter'     : datetime.datetime(2020,3,31)
                                   },
                        'Agg':{    'Macro_Hedge_credit' : 171207127.9186,
                                   'PC_bespoke'         : 0,     #85043733.6292596,
                                   'NCF_end_of_quarter' : 647521102.1743213, 
                                   'end_of_quarter'     : datetime.datetime(2020,3,31)
                                }
                        
                        },
                datetime.datetime(2020, 3, 31) : 

                       { 'LT' : {  'Policy_Loan'        : 433933376.36,   # Update Quarterly from EBS
                                   'LOC'                : 0,
                                   'Tax_Payable'        : 129447195.4775,   # Update Quarterly from EBS
                                   'Settlement_Payable' : 499646926.569999,   # Update Quarterly from EBS
                                   'GOE'                : 26681540.39,      # Update Quarterly from EBS 
                                   'pre_Tax_Surplus'    : 1426224117.24088,  # Update Quarterly from EBS
                                   'DTA'                : 435476055.252992  ,   # Update Quarterly from EBS
                                   'Other_Assets_adj'   : -4185126,   # Update Quarterly from EBS: other assets (exc. Surplus Asset Acc Int)
                                   'Other_Liabilities'  : 68599294.096558,           # Update Quarterly from EBS
                                   'Settlement_Date'    : datetime.datetime(2020,5, 29),
                                   'LTIC'               : 330000000,          # Update Quarterly from EBS
                                   'LTIC_Dur'           : 0,    # pending -3.8566794852585
                                   'LTIC_Cap'           : 330000000,
                                   'AccInt_IDR_to_IA'   : 3162592.78174376,       # Update Quarterly from Asset Adjustment
                                   'True_up_FWA_LT'     : 39507952.7214321,   # FWA Cash ,           
                                   'True_up_Cash_LT'    : 0,          #-20569501.55  # Update Quarterly from Asset Adjustment
                                   'AccInt_ALBA'        : 0,            # Update Quarterly from Asset Adjustment
                                   'CFT_Settlement'     : 0, 
                                   'Macro_Hedge_credit' : 156661403.289811,
                                   'PC_bespoke'         : 0,
                                   'ML_III_loss'        : 250000000, #for dates between 3/20 and 3/30
                                   'alts_loss'          : 40000000,  #for dates between 3/20 and 3/30
                                   'URGL_Alt_Surplus'   : -3231352,
#                                   'NCF_end_of_quarter' : 517279166.96919686,
#                                   'end_of_quarter'     : datetime.datetime(2020,6,30)
                                    } ,
    
    
                        'GI' : {   'Policy_Loan'        : 0,
                                   'LOC'                : 550000000,          # Update Quarterly from EBS
                                   'Tax_Payable'        : 35603124.61,   # Update Quarterly from EBS
                                   'Settlement_Payable' : 98415381.9299994,          # Update Quarterly from EBS
                                   'GOE'                : 10736904.48,      # Update Quarterly from EBS
                                   'pre_Tax_Surplus'    : 854389272.663355,   # before update:954618501.053859,  # Update Quarterly from EBS
                                   'DTA'                : 146193227.394759,   # Update Quarterly from EBS
                                   'Other_Assets_adj'   : 19066759.99,           # Update Quarterly from EBS: other assets (exc. Surplus Asset Acc Int) from Loan Receivable to TPA company
                                   'Other_Liabilities'  : -53214644.4352774,                  # Update Quarterly from EBS
                                   'Settlement_Date'    : datetime.datetime(2020, 5, 31),
                                   'LTIC'               : 0,
                                   'LTIC_Dur'           : 0,
                                   'LTIC_Cap'           : 0,
                                   'AccInt_IDR_to_IA'   : 128995.618516311,    # Update Quarterly from Asset Adjustment
                                   'True_up_Cash_GI'    : 0,         #7803792.26000001 # Update Quarterly from Asset Adjustment
                                   'True_up_FWA_GI'     : 7296201.63000204, #15921089.3543658,          # Update Quarterly from Asset Adjustment
                                   'Loan_Receivable'    :  25000000 ,
                                   'Loan_Receivable_charge' :  1250000 ,
                                   'Macro_Hedge_credit' : 16464658.9877396,
                                   'PC_bespoke'         : 0, #85043733.6292596, #pc bespoke factor for reserve risk
                                   'URGL_Alt_Surplus'   :  -922450.00,
#                                   'NCF_end_of_quarter' : 130241935.20512448,
#                                   'end_of_quarter'     : datetime.datetime(2020,3,31)
                                   },
                        'Agg':{    'Macro_Hedge_credit' : 173126062.277551,
                                   'PC_bespoke'         : 0,     #85043733.6292596,
#                                   'NCF_end_of_quarter' : 647521102.1743213, 
#                                   'end_of_quarter'     : datetime.datetime(2020,3,31)
                                }
                        
                        }
                }

### For Actual BMA Reporting - update each quarter           
Tax_sharing = {'Agg': 495708591, 'LT': 325134436, 'GI': 170574155}
 
ALBA_adj = 0 # 4Q18 & 1Q19: 13983740.1700001; 2Q19:14509113; 3Q19: 14509113; 4Q19: 16560000; 1Q20: 0

#Future regime ALM BSCR - up/down scenario ALBA hedge and Swap hedge 
Hedge_effect ={datetime.datetime(2019, 12, 31): {'Up'   : -436815113,
                                                 'Down' : 1227462309},
               datetime.datetime(2020, 3 , 31): {'Up'   : -870117781.892538,
                                                 'Down' : 1661804786.20788}
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


# FI BSCR credit
FI_Charge_Credit_Life =	{datetime.datetime(2019, 12, 31): 153152087.9186,
                         datetime.datetime(2020,  3, 31): 154148804.75097}

FI_Charge_Credit_PC	  = {datetime.datetime(2019, 12, 31): 18117892.1601293,
                         datetime.datetime(2020,  3, 31): 16210857.5265809}

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

# Updated for 4Q19 - Main run v004 - 22/04/2020
morbidity = {"LTC"  :{"active":0.658871664821211, "inpayment": 0.341128335178789},
             "AH"   :{"active":0.337190962023665,"critical":0.548536525536174,"inpayment": 0.11427251244016}}


# Last Update: 2019 Q4 Main Run v004
PC_mapping =  {'Property':         [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
               'Personal_Accident':[0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.327591408501980, 0.0000, 0.0000, 0.0000], 
               'US_Casualty':      [0.0000, 0.512764787122216, 0.802904311723108, 0.318027814568074, 0.7490, 0.0000, 0.0000, 0.0000, 0.310472321640324, 0.0000, 0.9500],
               'US_Casualty_NP':   [1.0000, 0.487235212877784, 0.197095688276892, 0.681972185431926, 0.2510, 0.0000, 1.0000, 0.672408591498020, 0.689527678359676, 1.0000, 0.0500],
               'US_Specialty':     [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.290578784073283, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
               'US_Specialty_NP':  [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.709421215926717, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]}


# Macro Hedge
HYG_Option_Price = { datetime.datetime(2019, 12, 31) : {
                                                        50   :	39171856.48,
                                                        53.13:	35283646.12,
                                                        56.25:	31395590.58,
                                                        59.38:	27508665.67,
                                                        62.5 :	23627537.26,
                                                        65.63:	19768413.97,
                                                        68.75:	15972780.9,
                                                        71.88:	12321090.26,
                                                        75   :	8932855.8,
                                                        78.13:	5943275.32,
                                                        81.25:	3462923.04,
                                                        84.38:	1541766.28,
                                                        87.5 :	157404.16,
                                                        90.63:	-770396.81,
                                                        93.75:	-1349802.76,
                                                        96.88:	-1688010.1,
                                                        100  : 	-1873307.68
                                                        },
                     datetime.datetime(2020, 3, 31) : {                         # datetime.datetime(2020, 3, 31) to be updated
                                                        50   :	39171856.48,
                                                        53.13:	35283646.12,
                                                        56.25:	31395590.58,
                                                        59.38:	27508665.67,
                                                        62.5 :	23627537.26,
                                                        65.63:	19768413.97,
                                                        68.75:	15972780.9,
                                                        71.88:	12321090.26,
                                                        75   :	8932855.8,
                                                        78.13:	5943275.32,
                                                        81.25:	3462923.04,
                                                        84.38:	1541766.28,
                                                        87.5 :	157404.16,
                                                        90.63:	-770396.81,
                                                        93.75:	-1349802.76,
                                                        96.88:	-1688010.1,
                                                        100  : 	-1873307.68
                                                        }
                    }

Starting_Level = {'CDX IG': 45.266, 'HYG': 87.785}
Beta = {'CDX IG': 0.724612038445358, 'HYG': 1.32350068750397}	 
HYG_Duration =	4.56	

	
Macro_Hedge_Holdings = { datetime.datetime(2019, 12, 31): {'Corp IG': {'Aggregate': {'Holding': 16695, 'Index Notional': 8400},
                                                                            'Life': {'Holding': 14569, 'Index Notional': 7728},
                                                                              'PC': {'Holding': 2126,  'Index Notional': 672}  },
                                                           'Corp HY': {'Aggregate': {'Holding': 483,   'Index Notional': 100},
                                                                            'Life': {'Holding': 483,   'Index Notional': 100},
                                                                              'PC': {'Holding': 0,     'Index Notional': 0}    } 
                                                          },
                         datetime.datetime(2020,  3, 31): {'Corp IG': {'Aggregate': {'Holding': 16504, 'Index Notional': 7600},
                                                                            'Life': {'Holding': 14672, 'Index Notional': 6992},
                                                                              'PC': {'Holding': 1832,  'Index Notional': 608}  },
                                                           'Corp HY': {'Aggregate': {'Holding': 465,   'Index Notional': 100},
                                                                            'Life': {'Holding': 465,   'Index Notional': 100},
                                                                              'PC': {'Holding': 0,     'Index Notional': 0}    }
                                                          },                        
                        }
         
                
Parent_Injection_Comp = 135000000                     
     
def Get_macro_hedge_value(valDate, CDG_IG, HYG): 
    # CDX   
    CDX_Options = pd.ExcelFile('./Macro_Hedge - CDX_Options.xlsx')
    CDX_Options = CDX_Options.parse('CDX Options')
    
    CDG_Level = CDG_IG * Beta['CDX IG'] + Starting_Level['CDX IG']
    
    CDG_Profit_Agg = CDX_Options[min(list(CDX_Options.columns.values), key = lambda key: abs(key - CDG_Level))] / 10**6
    CDG_Profit_Agg = CDG_Profit_Agg.values[0]
    CDG_Profit_LT  = CDG_Profit_Agg * Macro_Hedge_Holdings[valDate]['Corp IG']['Life']['Index Notional'] / Macro_Hedge_Holdings[valDate]['Corp IG']['Aggregate']['Index Notional']
    CDG_Profit_GI  = CDG_Profit_Agg * Macro_Hedge_Holdings[valDate]['Corp IG']['PC']['Index Notional']   / Macro_Hedge_Holdings[valDate]['Corp IG']['Aggregate']['Index Notional']
       
    # HYG
    HYG_Spread_Shock = min(710, HYG) *  Beta['HYG']
    HYG_Level_Price  = (1 + -HYG_Spread_Shock * HYG_Duration/10000) * Starting_Level['HYG']
        
    key_list = {}  
    for key, value in HYG_Option_Price[valDate].items():
       key_list[key] = abs(key - HYG_Level_Price)
    
    HYG_Level_1 = min(key_list, key = key_list.get)
    key_list.pop(HYG_Level_1, None)
    HYG_Level_2 = min(key_list, key = key_list.get)
    
    HYG_Level_Below = min(HYG_Level_1, HYG_Level_2)
    HYG_Level_Above = max(HYG_Level_1, HYG_Level_2)
    
    HYG_Profit_Below = HYG_Option_Price[valDate].get(HYG_Level_Below)/10**6
    HYG_Profit_Above = HYG_Option_Price[valDate].get(HYG_Level_Above)/10**6

    HYG_Profit_Agg = HYG_Profit_Below + (HYG_Profit_Above - HYG_Profit_Below) * ( (HYG_Level_Price - HYG_Level_Below) / (HYG_Level_Above - HYG_Level_Below) ) 
    HYG_Profit_LT  = HYG_Profit_Agg * Macro_Hedge_Holdings[valDate]['Corp HY']['Life']['Index Notional'] / Macro_Hedge_Holdings[valDate]['Corp HY']['Aggregate']['Index Notional']
    HYG_Profit_GI  = HYG_Profit_Agg * Macro_Hedge_Holdings[valDate]['Corp HY']['PC']['Index Notional']   / Macro_Hedge_Holdings[valDate]['Corp HY']['Aggregate']['Index Notional']

    if CDG_IG <= 0:
        CDG_Profit_Agg = 0
        CDG_Profit_LT  = 0
        CDG_Profit_GI  = 0
        
    if HYG <= 0:
        HYG_Profit_Agg = 0
        HYG_Profit_LT  = 0
        HYG_Profit_GI  = 0
        
    Macro_hedge_value = {'CDG_Profit': {'Agg': CDG_Profit_Agg,
                                        'LT' : CDG_Profit_LT,
                                        'GI' : CDG_Profit_GI},
                         'HYG_Profit': {'Agg': HYG_Profit_Agg,
                                        'LT' : HYG_Profit_LT,
                                        'GI' : HYG_Profit_GI}
                         }
    
    # Different approach used fpr 1Q20, hence set marco hege value to be 0.
    if valDate != datetime.datetime(2019, 12, 31):
        Macro_hedge_value = {'CDG_Profit': {'Agg': 0,
                                            'LT' : 0,
                                            'GI' : 0},
                             'HYG_Profit': {'Agg': 0,
                                            'LT' : 0,
                                            'GI' : 0}
                             }
    
    return Macro_hedge_value 