# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 15:06:26 2019

@author: jozhou
"""
import numpy as np
import os
import pandas as pd
#import pyodbc
import datetime
#import Lib_Utility as Util
# load akit DLL into python
akit_dir = 'C:/AKit v4.1.0/BIN'
os.sys.path.append(akit_dir)

# load Corp Model Folder DLL into python
corp_model_dir = 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code'
os.sys.path.append(corp_model_dir)

#import Class_Corp_Model  as Corpclass
import Lib_Market_Akit   as IAL_App
#import IALPython3        as IAL
#import User_Input_Dic    as UI
#import Lib_BSCR_Model    as BSCR
#import Config_BSCR       as BSCR_Cofig
from pandas.tseries.offsets import MonthEnd

    
eval_date    = datetime.datetime(2020, 5, 31)
price_date_0 = eval_date + MonthEnd(-2)
price_date_1 = eval_date + MonthEnd(-1)

eval_dates     = [ eval_date ] + [price_date_0] + [price_date_1] 
eval_dates     = list(set(eval_dates))
curveType = "Treasury"
market_factor         = IAL_App.Set_Dashboard_MarketFactors(eval_dates, curveType, 10, "BBB", 'A', IAL_App.KRD_Term, "USD")


KRD_Term = IAL_App.KRD_Term_new_format
mappingFile = '.\Mapping_v2.xlsx'
asset_workDir  = r'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\Asset_Holding_Feed'

os.chdir(asset_workDir)
asset_fileName = r'.\Asset_Holdings_' + eval_date.strftime('%Y%m%d') + '_update_OAS.xlsx'
        
leMapFile = pd.ExcelFile(mappingFile)
leMap = leMapFile.parse('LegalEntity')

ratingMapFile = '.\Rating_Mapping_v2.xlsx'
ratingMapFile = pd.ExcelFile(ratingMapFile)
ratingMap = ratingMapFile.parse('naic')

    
portFile = pd.ExcelFile(asset_fileName)
#portInput = pd.read_excel(portFile, sheet_name='DSA RE Holdings', skiprows=[0, 1, 2, 3, 4, 5, 6])
portInput = pd.read_excel(portFile, sheet_name='AssetSummaryFromPython')


portInput = portInput.dropna(axis=0, how='all')
portInput = portInput.dropna(axis=1, how='all')
        
portInput['aig asset class 3'] = np.where((portInput['issuer name'] == 'LSTREET II, LLC'), "ML-III B-Notes",portInput['aig asset class 3'])

portInput = portInput.merge(ratingMap, how='left', left_on=['naic rating', 'aig derived rating rollup'],\
                                              right_on=['naic rating', 'aig derived rating rollup'])
        
portInput['aig derived rating rollup'].fillna('NA-BBB', inplace=True)

ebs    = portInput.merge(leMap, how='left', left_on=['owning entity', 'owning entity gems id'],\
                                           right_on=['owning entity', 'owning entity gems id'])
        
ebs['aig derived rating update'] = ebs['aig derived rating rollup']

ebs['aig derived rating update'] = np.where(((ebs['aig asset class 3'] == 'CMBS Agency') | (
                ebs['aig asset class 3'] == 'CMBS Non-Agency') | (ebs['aig asset class 3'] == 'RMBS Agency') | (
                                                               ebs['aig asset class 3'] == 'RMBS Non-Agency')),
                                                      ebs['Derived Rating Modified'], ebs['aig derived rating rollup'])


#       update category        
#ebs['SurplusAccount'] = 'Not-Surplus'
#ebs['SurplusAccount'] = np.where(((ebs['Category'] == "Surplus") & (ebs['Strategy (Hld) Long Desc'] == "SAM RE OVERSEAS POOL LIFE")),\
#                "Long Term Surplus", ebs['SurplusAccount'])
#ebs['SurplusAccount'] = np.where(((ebs['Category'] == "Surplus") & (ebs['Strategy (Hld) Long Desc'] == "SAM RE OVERSEAS POOL PC")),\
#                "General Surplus", ebs['SurplusAccount'])
#ebs['SurplusAccount'] = np.where(((ebs['SurplusAccount'] == 'Not-Surplus') & (ebs['Category'] == "Surplus") & \
#                (ebs['Encumbrance Program Level 4 Desc'] == 'DSA REINSURANCE PC')),"General Surplus", ebs['SurplusAccount'])
#ebs['SurplusAccount'] = np.where(((ebs['SurplusAccount'] == 'Not-Surplus') & (ebs['Category'] == "Surplus") & \
#                (ebs['Encumbrance Program Level 4 Desc'] == 'DSA REINSURANCE LR')),"Long Term Surplus", ebs['SurplusAccount'])
#ebs['SurplusAccount'] = np.where(((ebs['SurplusAccount'] == 'Not-Surplus') & (ebs['Category'] == "Surplus") & \
#                (ebs['Encumbrance Program Level 4 Desc'] == 'DSA RE/AGL Trust- DSA REINSURANCE LR')),"Long Term Surplus", ebs['SurplusAccount'])
#ebs['SurplusAccount'] = np.where(((ebs['SurplusAccount'] == 'Not-Surplus') & (ebs['Category'] == "Surplus") & \
#                (ebs['Encumbrance Program Level 4 Desc'] == 'DSA RE/USL Trust - DSA REINSURANCE LR')),"Long Term Surplus", ebs['SurplusAccount'])
#ebs['SurplusAccount'] = np.where(((ebs['SurplusAccount'] == 'Not-Surplus') & (ebs['Category'] == "Surplus") & \
#                (ebs['Encumbrance Program Level 4 Desc'] == 'DSA RE/VALIC Trust - DSA REINSURANCE LR')),"Long Term Surplus", ebs['SurplusAccount'])
#ebs['Category'] = np.where(((ebs['SurplusAccount'] == 'Not-Surplus') & (ebs['Category'] == "Surplus") & \
#                (ebs['Encumbrance Program Level 4 Desc'] == 'SOURCE UNDEFINED')),"ModCo", ebs['Category'])
#ebs.dropna(axis=0, how='all', subset=['Category'], inplace=True)
#ebs['Category'] = np.where((ebs['SurplusAccount'] != 'Not-Surplus'), ebs['SurplusAccount'], ebs['Category'])
ebs['fort re corporate segment'] = np.where(
            (ebs['fort re corporate segment'] == "LR ModCo"),"ModCo",ebs['fort re corporate segment'])
ebs['fort re corporate segment'] = np.where(
            (ebs['fort re corporate segment'] == "PC LPT"),"LPT",ebs['fort re corporate segment'])

ebs['Category'] = ebs['fort re corporate segment']

         
ebs.sort_values('market value usd aig gaap',inplace=True)
ebs.drop_duplicates('unique lot id',inplace=True)
        
#if eval_date > datetime.datetime(2019, 8, 31):
#    # Illiquidity impact estimation
#       
#    Yield_Change_0 = market_factor[market_factor['val_date'] == eval_date]['IR'].values[0] - market_factor[market_factor['val_date'] == price_date_0]['IR'].values[0] \
#                       + 0.5 * (market_factor[market_factor['val_date'] == eval_date]['Credit_Spread'].values[0]/10000 - market_factor[market_factor['val_date'] == price_date_0]['Credit_Spread'].values[0]/10000)
#                       
#    Yield_Change_1 = market_factor[market_factor['val_date'] == eval_date]['IR'].values[0] - market_factor[market_factor['val_date'] == price_date_1]['IR'].values[0] \
#                       + 0.5 * (market_factor[market_factor['val_date'] == eval_date]['Credit_Spread'].values[0]/10000 - market_factor[market_factor['val_date'] == price_date_1]['Credit_Spread'].values[0]/10000)
#
#    Initial_mv_acc_int = ebs.loc[(ebs['Price Date'] <= price_date_1) & (ebs['aig asset class 1'] == 'Fixed Income') & (ebs['effective duration'].notnull() ) & (ebs['effective duration'] != 0), 'market value with accrued int usd'].sum()
#            
#    ebs.loc[(ebs['Price Date'] > price_date_0) & (ebs['Price Date'] <= price_date_1) & (ebs['aig asset class 1'] == 'Fixed Income') & (ebs['effective duration'].notnull() ) & (ebs['effective duration'] != 0), "market value with accrued int usd"] = ebs['market value with accrued int usd'] * (1 + ebs['effective duration'] * -Yield_Change_1) 
#    ebs.loc[(ebs['Price Date'] <= price_date_0) & (ebs['aig asset class 1'] == 'Fixed Income') & (ebs['effective duration'].notnull() ) & (ebs['effective duration'] != 0), "market value with accrued int usd"] = ebs['market value with accrued int usd'] * (1 + ebs['effective duration'] * -Yield_Change_0) 
#    ebs.fillna(0, inplace=True)
#    ebs['market value usd aig gaap'] = ebs['market value with accrued int usd'] - ebs['accrued interest usd']

            
#asset     = ebs[((ebs['owning entity'] != "American International Reinsurance Company, Ltd."))&\
#                                            (ebs['Security Desc DESC'].str[:13] != 'Interest Rate')]        
ebs['market value usd aig gaap'] = np.where(((ebs['aig asset class 3'] == 'Derivative')) & (ebs['owning entity'] != "American International Reinsurance Company, Ltd.")\
                ,0, ebs['market value usd aig gaap'])  
ebs['market value with accrued int usd'] = np.where(((ebs['aig asset class 3'] == 'Derivative')) & (ebs['owning entity'] != "American International Reinsurance Company, Ltd.")\
                ,0, ebs['market value with accrued int usd'])       

ebs['market value usd aig gaap'] = np.where(
            ((ebs['aig asset class 1'] =='Derivative') &(ebs['fort re corporate segment'] == 'ALBA')& (ebs['quantity'] == 0)) ,0, ebs['market value usd aig gaap'])
    
ebs['market value with accrued int usd'] = np.where(
            ((ebs['aig asset class 1'] =='Derivative') &(ebs['fort re corporate segment'] == 'ALBA')& (ebs['quantity'] == 0) ) ,0, ebs['market value with accrued int usd'])

ebs['market value usd aig gaap'] = np.where(
            ((ebs['security currency'] =='USD') &(ebs['fort re corporate segment'] == 'ALBA')) ,0, ebs['market value usd aig gaap'])
    
ebs['market value with accrued int usd'] = np.where(
            ((ebs['security currency'] =='USD') &(ebs['fort re corporate segment'] == 'ALBA')) ,0, ebs['market value with accrued int usd'])



asset = ebs
colnames = ['unique lot id','Category','aig asset class 3','aig derived rating rollup','market value usd aig gaap','accrued interest usd',\
                                                'market value with accrued int usd','ytw','avg life','effective duration','effective convexity',\
                                                'spread duration','spread convexity','current face usd','aig asset class 4', 'issuer name']



for key, value in KRD_Term.items():
    colnames.append("krd_" + key)    

        
each_date_cusip = pd.DataFrame(columns=colnames)
each_date_cusip['unique lot id']=asset['unique lot id']
each_date_cusip['Category'] = asset['Category']
each_date_cusip['aig derived rating rollup']=asset['aig derived rating update']
each_date_cusip['aig asset class 3'] = asset['aig asset class 3']
each_date_cusip['market value usd aig gaap']= asset['market value usd aig gaap']
each_date_cusip['accrued interest usd']= asset['accrued interest usd']
each_date_cusip['market value with accrued int usd']= asset['market value with accrued int usd']
each_date_cusip['ytw'] = asset['ytw']
each_date_cusip['avg life'] = asset['avg life']
each_date_cusip['effective duration'] = asset['effective duration']
each_date_cusip['effective convexity'] = asset['effective convexity']
each_date_cusip['spread duration'] = asset['spread duration']
each_date_cusip['spread convexity'] = asset['spread convexity']
each_date_cusip['aig asset class 4'] = asset['aig asset class 4']
each_date_cusip['issuer name'] = asset['issuer name']
each_date_cusip['current face usd'] = asset['current face usd']

        
for key, value in KRD_Term.items():
    KRD_name        = "krd_" + key
    each_date_cusip[KRD_name] = asset[KRD_name]
            
asset_filename = 'cusip_EBS_'+'_'+eval_date.strftime('%m%d%Y') + '.xlsx'
outputWriter = pd.ExcelWriter(asset_filename)
each_date_cusip.to_excel(outputWriter, sheet_name= asset_filename, index=False)
outputWriter.save()
       

            



