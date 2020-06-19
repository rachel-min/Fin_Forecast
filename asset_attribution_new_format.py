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
import Lib_Market_Akit_new_format   as IAL_App
import IALPython3        as IAL
#import User_Input_Dic    as UI
#import Lib_BSCR_Model    as BSCR
#import Config_BSCR       as BSCR_Cofig
from pandas.tseries.offsets import MonthEnd


def Run_asset_Attribution(valDate,market_factor, EBS_Cal_Dates_all,Price_Date,asset_workDir, curveType = "Treasury", mappingFile = '.\Mapping.xlsx', KRD_Term = IAL_App.KRD_Term_new_format):
    
    
    num_periods = 0
    eval_period = []
    
    for each_date in EBS_Cal_Dates_all:
        eval_period.append(each_date)
        num_periods = num_periods + 1   
        
    
    asset_attribution = {}
    
    for each_date_idx in range(0, num_periods-1, 1):
        
        each_date_attribution_results = []

        eval_date_prev    = eval_period[each_date_idx]
        eval_date_current = eval_period[each_date_idx + 1]

#        ebs_prev          = EBS_DB_results[eval_date_prev].asset_holding
#        ebs_current       = EBS_DB_results[eval_date_current].asset_holding

##      cusip level   
        os.chdir(asset_workDir)
        asset_fileName_prev = r'.\Asset_Holdings_' + eval_date_prev.strftime('%Y%m%d') + '_update_oas.xlsx'
        asset_fileName_current = r'.\Asset_Holdings_' + eval_date_current.strftime('%Y%m%d') + '_update_oas.xlsx'
#        
#        leMapFile = pd.ExcelFile(mappingFile)
#        leMap = leMapFile.parse('LegalEntity')
#    
        portFile_prev = pd.ExcelFile(asset_fileName_prev)
        portInput_prev = pd.read_excel(portFile_prev, sheet_name='AssetSummaryFromPython')
#        portInput_prev = pd.read_excel(portFile_prev, sheet_name='DSA RE Holdings', skiprows=[0, 1, 2, 3, 4, 5, 6])

        portInput_prev = portInput_prev.dropna(axis=0, how='all')
        portInput_prev = portInput_prev.dropna(axis=1, how='all')
        
        portFile_current = pd.ExcelFile(asset_fileName_current)
        portInput_current= pd.read_excel(portFile_current, sheet_name='AssetSummaryFromPython')

        portInput_current = portInput_current.dropna(axis=0, how='all')
        portInput_current = portInput_current.dropna(axis=1, how='all')

        ebs_prev = portInput_prev
        ebs_current = portInput_current

#        Load Interest Rate Curves
        irCurve_USD_prev = IAL_App.createAkitZeroCurve(eval_date_prev, curveType, "USD")
        irCurve_GBP_prev = IAL_App.load_BMA_Std_Curves(valDate,"GBP",eval_date_prev)

        irCurve_USD_current = IAL_App.createAkitZeroCurve(eval_date_current, curveType, "USD")
        irCurve_GBP_current = IAL_App.load_BMA_Std_Curves(valDate,"GBP",eval_date_current)
        
        ccy_prev  = market_factor[(market_factor['val_date'] == eval_date_prev)]['GBP'].iloc[0]
        ccy_current  = market_factor[(market_factor['val_date'] == eval_date_current)]['GBP'].iloc[0]



###    adjuste fort re corporate segment 
#        ebs_prev['fort re corporate segment'] = np.where((ebs_prev['BMA_Category'] == "ML III"),"ML III",ebs_prev['fort re corporate segment'])
#        ebs_current['fort re corporate segment'] = np.where((ebs_current['BMA_Category'] == "ML III"),"ML III",ebs_current['fort re corporate segment'])
        ebs_prev['fort re corporate segment'] = np.where((ebs_prev['issuer name'] == "LSTREET II, LLC"),"ML III",ebs_prev['fort re corporate segment'])
        ebs_current['fort re corporate segment'] = np.where((ebs_current['issuer name'] == "LSTREET II, LLC"),"ML III",ebs_current['fort re corporate segment'])
        ebs_prev['fort re corporate segment'] = np.where((ebs_prev['fort re corporate segment'] == "LR ModCo"),"ModCo",ebs_prev['fort re corporate segment'])
        ebs_current['fort re corporate segment'] = np.where((ebs_current['fort re corporate segment'] == "LR ModCo"),"ModCo",ebs_current['fort re corporate segment'])
        ebs_prev['fort re corporate segment'] = np.where((ebs_prev['fort re corporate segment'] == "PC LPT"),"LPT",ebs_prev['fort re corporate segment'])
        ebs_current['fort re corporate segment'] = np.where((ebs_current['fort re corporate segment'] == "PC LPT"),"LPT",ebs_current['fort re corporate segment'])

        ebs_current['illiquid asset adj']= 0
        ebs_prev['illiquid asset adj'] = 0
    
#       adding illiquid asset adj to cusip
        if eval_date_prev > datetime.datetime(2019, 8, 31):
#            price_date_0 = eval_date_prev + MonthEnd(-2)
            price_date_1 = eval_date_prev + MonthEnd(-1)
#
            ebs_prev['price date'] = np.where(((ebs_prev['price date'] == "00:00:00")|(ebs_prev['price date'] == 0)), price_date_1 , ebs_prev['price date']) 
            ebs_prev['price date'] = ebs_prev['price date'].apply(
                       lambda x: (datetime.datetime.fromtimestamp(x/1e9) if isinstance(x,int) == True and np.isnan(x) == False else x ))        
            ebs_prev['price date'] = ebs_prev['price date'].apply(
                       lambda x: (x.replace(hour=0) if isinstance(x,datetime.datetime)  else x ))        
            ebs_prev['illiquid asset adj']= np.where(((ebs_prev['price date'] <= price_date_1) & (ebs_prev['aig asset class 1'] == 'Fixed Income')  & (ebs_prev['effective duration'] != 0) & (ebs_prev['issuer name'] != 'LSTREET II, LLC')),ebs_prev['market value usd aig gaap']-ebs_prev['mkt_val_fnc_gaap'],ebs_prev['illiquid asset adj'])

#
#            Yield_Change_0 = market_factor[market_factor['val_date'] == eval_date_prev]['IR'].values[0] - market_factor[market_factor['val_date'] == price_date_0]['IR'].values[0] + 0.5 * (market_factor[market_factor['val_date'] == eval_date_prev]['Credit_Spread'].values[0]/10000 - market_factor[market_factor['val_date'] == price_date_0]['Credit_Spread'].values[0]/10000)
#                       
#            Yield_Change_1 = market_factor[market_factor['val_date'] == eval_date_prev]['IR'].values[0] - market_factor[market_factor['val_date'] == price_date_1]['IR'].values[0] + 0.5 * (market_factor[market_factor['val_date'] == eval_date_prev]['Credit_Spread'].values[0]/10000 - market_factor[market_factor['val_date'] == price_date_1]['Credit_Spread'].values[0]/10000)
#                       
#            ebs_prev.loc[(ebs_prev['price date'] > price_date_0) & (ebs_prev['price date'] <= price_date_1) & (ebs_prev['aig asset class 1'] == 'Fixed Income') & (ebs_prev['effective duration'].notnull() ) & (ebs_prev['effective duration'] != 0), "illiquid asset adj"] = ebs_prev['market value with accrued int usd'] * (ebs_prev['effective duration'] * -Yield_Change_1) 
#            ebs_prev.loc[(ebs_prev['price date'] <= price_date_0) & (ebs_prev['aig asset class 1'] == 'Fixed Income') & (ebs_prev['effective duration'].notnull() ) & (ebs_prev['effective duration'] != 0), "illiquid asset adj"] = ebs_prev['market value with accrued int usd'] * (ebs_prev['effective duration'] * -Yield_Change_0) 
#        else:
#            ebs_prev['illiquid asset adj'] = 0

        if eval_date_current > datetime.datetime(2019, 8, 31):
#            price_date_0 = eval_date_current + MonthEnd(-2)
            price_date_1 = eval_date_current + MonthEnd(-1)
#
            ebs_current['price date'] = np.where(((ebs_current['price date'] == "00:00:00")|(ebs_current['price date'] == 0)), price_date_1 , ebs_current['price date']) 
            ebs_current['price date'] = ebs_current['price date'].apply(
                       lambda x: (datetime.datetime.fromtimestamp(x/1e9) if isinstance(x,int) == True and np.isnan(x) == False else x ))        
            ebs_current['price date'] = ebs_current['price date'].apply(
                       lambda x: (x.replace(hour=0) if isinstance(x,datetime.datetime)  else x ))        
            ebs_current['illiquid asset adj']= np.where(((ebs_current['price date'] <= price_date_1) & (ebs_current['aig asset class 1'] == 'Fixed Income')  & (ebs_current['effective duration'] != 0) & (ebs_current['issuer name'] != 'LSTREET II, LLC')),ebs_current['market value usd aig gaap']-ebs_current['mkt_val_fnc_gaap'],ebs_current['illiquid asset adj'])
#            
#            Yield_Change_0 = market_factor[market_factor['val_date'] == eval_date_current]['IR'].values[0] - market_factor[market_factor['val_date'] == price_date_0]['IR'].values[0] + 0.5 * (market_factor[market_factor['val_date'] == eval_date_current]['Credit_Spread'].values[0]/10000 - market_factor[market_factor['val_date'] == price_date_0]['Credit_Spread'].values[0]/10000)
#                       
#            Yield_Change_1 = market_factor[market_factor['val_date'] == eval_date_current]['IR'].values[0] - market_factor[market_factor['val_date'] == price_date_1]['IR'].values[0] + 0.5 * (market_factor[market_factor['val_date'] == eval_date_current]['Credit_Spread'].values[0]/10000 - market_factor[market_factor['val_date'] == price_date_1]['Credit_Spread'].values[0]/10000)
#
#            ebs_current.loc[(ebs_current['price date'] > price_date_0) & (ebs_current['price date'] <= price_date_1) & (ebs_current['aig asset class 1'] == 'Fixed Income') & (ebs_current['effective duration'].notnull() ) & (ebs_current['effective duration'] != 0), ["illiquid asset adj"]] = ebs_current['market value with accrued int usd'] * (ebs_current['effective duration'] * -Yield_Change_1) 
#            ebs_current.loc[(ebs_current['price date'] <= price_date_0) & (ebs_current['aig asset class 1'] == 'Fixed Income') & (ebs_current['effective duration'].notnull() ) & (ebs_current['effective duration'] != 0), ["illiquid asset adj"]] = ebs_current['market value with accrued int usd'] * (ebs_current['effective duration'] * -Yield_Change_0) 
#        else:
#            ebs_current['illiquid asset adj'] = 0

#      delete duplicate cusip with empty market value
        ebs_prev.sort_values('market value usd aig gaap',inplace=True)
        ebs_prev.drop_duplicates('unique lot id',inplace=True)
        ebs_current.sort_values('market value usd aig gaap',inplace=True)
        ebs_current.drop_duplicates('unique lot id',inplace=True)
        
        ebs_prev.fillna(value=0,inplace=True)
        ebs_current.fillna(value=0,inplace=True)
        ebs_prev=ebs_prev[ebs_prev['market value usd aig gaap']!=0]
        ebs_current = ebs_current[ebs_current['market value usd aig gaap']!= 0]
        asset_prev         = ebs_prev[(ebs_prev['aig asset class 3'] != "Derivative")&( ebs_prev['aig asset class 3'] != "Hedge Fund")&(ebs_prev['aig asset class 3'] != "Private Equity Fund")&(ebs_prev['aig asset class 3'] != "Other Invested Assets")&(ebs_prev['aig asset class 3'] != "Common Equity")&(ebs_prev['aig asset class 3'] != "Cash")&(ebs_prev['aig asset class 3'] != "Cash Fund")&(ebs_prev['aig asset class 3'] != "TBD")]
        asset_current      = ebs_current[(ebs_current['aig asset class 3'] != "Derivative")&( ebs_current['aig asset class 3'] != "Hedge Fund")&(ebs_current['aig asset class 3'] != "Private Equity Fund")&(ebs_current['aig asset class 3'] != "Other Invested Assets")&(ebs_current['aig asset class 3'] != "Common Equity")&(ebs_current['aig asset class 3'] != "Cash")&(ebs_current['aig asset class 3'] != "Cash Fund")&(ebs_current['aig asset class 3'] != "TBD")]

        asset_current['IR_01']= (asset_current['market value with accrued int usd'])*asset_current['effective duration'] * 0.0001/1000000
        asset_current['IR_01_cv']= 0.5*(asset_current['market value with accrued int usd'])*asset_current['effective convexity'] * 0.0001/1000000

        asset_prev['oas_mv']=asset_prev['oas']*asset_prev['market value usd aig gaap']
        asset_current['oas_mv']=asset_current['oas']*asset_current['market value usd aig gaap']
        


#        weighted_OAS_prev  = asset_prev['oas_mv'].sum()/asset_prev['market value usd aig gaap'].sum()            
#        weighted_OAS_current = asset_current['oas_mv'].sum()/asset_current['market value usd aig gaap'].sum()
#        print("OAS:"+str(eval_date_prev)+str(weighted_OAS_prev) )
#        print("OAS:"+str(eval_date_current)+str(weighted_OAS_current))

#       sort cusip by category
        Category = ['ModCo','LPT','ALBA','Long Term Surplus','General Surplus',"ML III"]
        for each_category in Category:
            
#       IR_01            
            IR_01 = asset_current[asset_current['fort re corporate segment']==each_category]['IR_01'].sum()
            IR_01_cv = asset_current[asset_current['fort re corporate segment']==each_category]['IR_01_cv'].sum()
#       sort cusip
            ID_current         = asset_current[asset_current['fort re corporate segment']== each_category][asset_current['market value usd aig gaap']!=0]["unique lot id"]
            ID_prev            = asset_prev[asset_prev['fort re corporate segment']== each_category][asset_prev['market value usd aig gaap']!=0]["unique lot id"]
            purchase_ID        = list(set(ID_current).difference(set(ID_prev)))
            sale_ID            = list(set(ID_prev).difference(set(ID_current)))
            common_ID          = list(set(ID_prev).intersection(set(ID_current)))
            asset_count        = len(common_ID)



#       calculate the sale amount and purchase amount        
            purchase = 0
            for idx in range(0,len(purchase_ID),1):
                idxx    = purchase_ID[idx]
                purchase += asset_current.loc[asset_current["unique lot id"]==idxx]['market value usd aig gaap'].iloc[0]
                
            sale = 0
            for idx in range(0,len(sale_ID),1):
                idxx    = sale_ID[idx]
                sale   += asset_prev.loc[asset_prev["unique lot id"]==idxx]['market value usd aig gaap'].iloc[0]
        
    #  zzzzzzzzzzzzzzzzzzz get all asset group between the two dates  zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz        
    #        asset_temp = pd.concat([asset_prev,asset_current],axis=0)
    #        asset_index_temp = asset_temp.groupby(asset_temp['unique lot id']).first()
    #        asset_count      = asset_index_temp.count()[0]
    #        print(asset_count)
            

                
            agg_carry      = 0
            agg_prev_mv    = sale
            agg_current_mv = purchase
            agg_IR_attr    = 0
            agg_IR_cv_attr = 0
            agg_OAS_att    = 0
            agg_unexplained= 0
            agg_ccy_attr   = 0
            agg_illiquid_adj_prev    = 0
            agg_illiquid_adj_current = 0
            agg_illiquid_adj_change  = 0
            agg_credit_01          = 0
            agg_illiquid_ir_01     = 0
            agg_illiquid_cs_01     = 0
            
#           Calculate weighted average OAS
            weighted_OAS_prev    = asset_prev[asset_prev['fort re corporate segment']== each_category]['oas_mv'].sum()/asset_prev[asset_prev['fort re corporate segment']== each_category]['market value usd aig gaap'].sum()            
            weighted_OAS_current = asset_current[asset_current['fort re corporate segment']== each_category]['oas_mv'].sum()/asset_current[asset_current['fort re corporate segment']== each_category]['market value usd aig gaap'].sum()
            
    
            for idx in range(0, asset_count,1):
                index_name = common_ID[idx]
                each_asset         = asset_prev.loc[asset_prev['unique lot id']==index_name]
#                asset_class_prev   = each_asset['aig asset class 3'].iloc[0]
#                asset_cat_prev     = each_asset['Encumbrance Program Level 4 Code'].iloc[0]
                mv_prev            = each_asset['market value usd aig gaap'].iloc[0]
                duration           = each_asset['effective duration'].iloc[0]
                convexity          = each_asset['effective convexity'].iloc[0]
                OAS_prev           = each_asset['oas'].iloc[0]
                Spread_dur         = each_asset['spread duration'].iloc[0]
                YTW                = each_asset['ytw'].iloc[0]
                illiquid_adj_prev  = each_asset['illiquid asset adj'].iloc[0]
#                mv_acc_prev        = each_asset['market value with accrued int usd'].iloc[0]
#                if illiquid_adj_prev != 0:
#                    agg_illiquid_ir_01 += mv_acc_prev*duration* 0.0001/1000000

    
                each_asset_current = asset_current.loc[asset_current['unique lot id']==index_name]
#                asset_cat_current  = each_asset_current['Encumbrance Program Level 4 Code'].iloc[0]
#                asset_class_current= each_asset_current['aig asset class 3'].iloc[0]
                mv_current         = each_asset_current['market value usd aig gaap'].iloc[0]
                illiquid_adj_current= each_asset_current['illiquid asset adj'].iloc[0]            
                OAS_current        = each_asset_current['oas'].iloc[0]

#                each_attribution = { 'asset group':index_name,'Base_Date':eval_date_prev,'Eval_Date':eval_date_current, 'MV USD GAAP_prev': mv_prev, 'MV USD GAAP_current': mv_current, 'MV_change' : mv_current - mv_prev,'asset_category prev':asset_cat_prev,'asset_category current':asset_cat_current,'effdur_pre':duration,'asset class prev':asset_class_prev,'asset class current':asset_class_current}
    
                agg_prev_mv    += mv_prev
                agg_current_mv += mv_current
                agg_credit_01  += mv_prev*Spread_dur
#                if illiquid_adj_prev != 0:
#                    agg_illiquid_cs_01 += mv_prev*Spread_dur
                
                IR_attribution = 0     
    
                if  each_category == "ALBA":
                    irCurve_prev       = irCurve_GBP_prev
                    ccy_rate_prev      = ccy_prev
                    irCurve_current    = irCurve_GBP_current
                    ccy_rate_current   = ccy_current    
                else:
                    irCurve_prev       = irCurve_USD_prev
                    ccy_rate_prev      = 1.0
                    irCurve_current    = irCurve_USD_current
                    ccy_rate_current   = 1.0
            
    #            Step 1: asset Carry
                return_year_frac = IAL.Date.yearFrac("ACT/365",  eval_date_prev, eval_date_current)
                carry_cost       = mv_prev * YTW/100*return_year_frac
                
                if each_category == "ML III":
                    agg_carry   += 0
                else:
                    agg_carry       += carry_cost
               
                
#                each_attribution.update( { 'YTW'                : YTW/100  })
#                each_attribution.update( { 'OAS'                : OAS_prev / 10000 } )
#                each_attribution.update( { 'carry'              : carry_cost } )
                
    
    #            Step 2: Interest Rate Attributions
                mv_ex_carry         = mv_prev +carry_cost
                for key, value in KRD_Term.items():
                    KRD_name        = "krd_" + key
                    IR_Term         = "IR_" + key
    
                    key_rate_prev        = market_factor[(market_factor['val_date'] == eval_date_prev)][IR_Term].values[0]
                    key_rate_current     = market_factor[(market_factor['val_date'] == eval_date_current)][IR_Term].values[0]
                    key_rate_change      = key_rate_current - key_rate_prev
                    
                    
                    each_KRD             = each_asset[KRD_name].iloc[0]
    
    
                    key_rate_attribution = -mv_ex_carry* each_KRD * key_rate_change  
                    IR_attribution      += key_rate_attribution
                    if illiquid_adj_prev != 0:
                        agg_illiquid_ir_01 += key_rate_attribution

                    
#                    each_attribution.update( { 'mv_ex_carry'           : mv_ex_carry } )
#                    each_attribution.update( { KRD_name                : each_KRD } )
#                    each_attribution.update( { 'key_rate_prev'         : key_rate_prev } )
#                    each_attribution.update( { 'key_rate_current'      : key_rate_current } )
#                    each_attribution.update( { 'key_rate_change'       : key_rate_change } )
#                    each_attribution.update( { 'key_rate_attribution'  : key_rate_attribution } )
#    
#                each_attribution.update( { 'IR_attribution'  : IR_attribution } )
                if each_category == "ML III":
                    agg_IR_attr   += 0
                else:
                    agg_IR_attr     += IR_attribution
    
                
    
    #            Step 3: Interest Rate Convexity Attribution
                current_rate = irCurve_current.zeroRate( max(1, duration) ) 
                prev_rate    = irCurve_prev.zeroRate(max(1, duration))            
                
                ir_rate_change_dur       = current_rate - prev_rate
    
                IR_covexity_attribution  = mv_ex_carry * 1/2 * convexity * ir_rate_change_dur * ir_rate_change_dur * 100
    
                if each_category == "ML III":
                    agg_IR_cv_attr   += 0
                else:
                    agg_IR_cv_attr += IR_covexity_attribution
    
#                each_attribution.update( { 'prev_rate'               : prev_rate } )
#                each_attribution.update( { 'current_rate'            : current_rate } )
#                each_attribution.update( { 'ir_rate_change_dur'      : ir_rate_change_dur } )
#                each_attribution.update( { 'ir_convexity'            : convexity } )
#                each_attribution.update( { 'IR_covexity_attribution' : IR_covexity_attribution } )
    
    #            Step 4: OAS Change Attribution
                OAS_change       = ( OAS_current - OAS_prev ) / 10000
                OAS_attribution  = -mv_ex_carry * Spread_dur * OAS_change
                if each_category == "ML III":
                    agg_OAS_att   += 0
                else:
                    agg_OAS_att     += OAS_attribution
                if illiquid_adj_prev != 0:
                    agg_illiquid_cs_01 += OAS_attribution
#    
#                each_attribution.update( { 'prev_OAS'         : OAS_prev  / 10000 } )
#                each_attribution.update( { 'current_OAS'      : OAS_current  / 10000 } )
#                each_attribution.update( { 'OAS_change'       : OAS_change } )
#                each_attribution.update( { 'Spread Duration'  : Spread_dur } )
#                each_attribution.update( { 'OAS_attribution'  : OAS_attribution } )
    
#                Step 5: Currency Attribution
                Currency_attribution  = mv_current / ccy_rate_current  * (ccy_rate_current - ccy_rate_prev)
                agg_ccy_attr         += Currency_attribution
#    
#                each_attribution.update( { 'ccy_rate_prev'    : ccy_rate_prev } )
#                each_attribution.update( { 'ccy_rate_current' : ccy_rate_current } )
#                each_attribution.update( { 'ccy_change'       : ccy_rate_current-ccy_rate_prev } )
#                each_attribution.update( { 'Currency_attribution'  : Currency_attribution } )
    
    #            Step 6: Unexplained
                if each_category == "ML III":
                    Unexplained       = mv_current - mv_prev 
                else:
                    Unexplained       = mv_current - mv_prev - carry_cost - IR_attribution - IR_covexity_attribution - OAS_attribution - Currency_attribution 
                agg_unexplained  += Unexplained
#                each_attribution.update( { 'Unexplained'  : Unexplained } )
    
    #            each_date_attribution_results.append(each_attribution)
            
    #            Step 7: illiquid asset adjustment
                illiquid_adj_change = illiquid_adj_current-illiquid_adj_prev
                if each_category == "ML III":
                    agg_illiquid_adj_prev    += 0
                    agg_illiquid_adj_current += 0
                    agg_illiquid_adj_change  += 0 
                else:
                    agg_illiquid_adj_prev    += illiquid_adj_prev
                    agg_illiquid_adj_current += illiquid_adj_current
                    agg_illiquid_adj_change  += illiquid_adj_change    
    
    #       cash movement                        
            cash_prev           = ebs_prev[((ebs_prev['aig asset class 3'] == "Cash")|(ebs_prev['aig asset class 3'] == "Cash Fund")|(ebs_prev['aig asset class 3'] == "TBD"))&
                                            (ebs_prev['fort re corporate segment']== each_category)]
            cash_current        = ebs_current[((ebs_current['aig asset class 3'] == "Cash")|(ebs_current['aig asset class 3'] == "Cash Fund")|(ebs_current['aig asset class 3'] == "TBD"))&
                                               (ebs_current['fort re corporate segment']== each_category)]
#            key_prev            = ebs_prev['Security Desc DESC'].astype(str)
#            key_current         = ebs_current['Security Desc DESC'].astype(str)
    
#            criteria            = 'Interest Rate'
#            deri_prev           = ebs_prev[key_prev.apply(lambda x: criteria in x)]
#            deri_current        = ebs_current[key_current.apply(lambda x: criteria in x)]
        
#            modco_deri_prev     = deri_prev[((deri_prev['Owning Entity Name'] != "American International Reinsurance Company, Ltd."))&
#                                            (deri_prev['fort re corporate segment']== each_category)]
#            modco_deri_current  = deri_current[((deri_current['Owning Entity Name'] != "American International Reinsurance Company, Ltd."))&
#                                               (deri_current['fort re corporate segment']== each_category)]
#            prev_deri_mv        = modco_deri_prev.sum(axis=0)['market value usd aig gaap']
#            current_deri_mv     = modco_deri_current.sum(axis=0)['market value usd aig gaap']
            
#            deri_change         = current_deri_mv-prev_deri_mv

#            prev_deri_mv           = ebs_prev[((ebs_prev["unique lot id"]=='ModCo derivative')|(ebs_prev["unique lot id"]=='LPT derivative')|\
#                                            (ebs_prev["unique lot id"]=='Long Term Surplus derivative'))]['MV_USD_GAAP'].sum()

#            current_deri_mv           = ebs_current[((ebs_current["unique lot id"]=='ModCo derivative')|(ebs_current["unique lot id"]=='LPT derivative')|\
#                                            (ebs_current["unique lot id"]=='Long Term Surplus derivative'))]['MV_USD_GAAP'].sum()

#            deri_change         = current_deri_mv - prev_deri_mv
#### in new format, prev_deri_mv/current_deri_mv is no longer in IDR
            prev_deri_mv        = 0
            current_deri_mv     = 0
            deri_change         = 0
        
            cash_ID_current     = cash_current["unique lot id"]
            cash_ID_prev        = cash_prev["unique lot id"]
            cash_purchase_ID    = list(set(cash_ID_current).difference(set(cash_ID_prev)))
            cash_sale_ID        = list(set(cash_ID_prev).difference(set(cash_ID_current)))
    
            
            cash_sale = 0
            for idx in range(0,len(cash_sale_ID),1):
                idxx         = cash_sale_ID[idx]
                cash_sale   += cash_prev.loc[cash_prev["unique lot id"]==idxx]['market value usd aig gaap'].iloc[0]
                
            cash_purchase = 0
            for idx in range(0,len(cash_purchase_ID),1):
                idxx           = cash_purchase_ID[idx]
                cash_purchase += cash_current.loc[cash_current["unique lot id"]==idxx]['market value usd aig gaap'].iloc[0]
                
            cash_mv_prev       = cash_prev.sum(axis=0)['market value usd aig gaap']
            cash_mv_current    = cash_current.sum(axis=0)['market value usd aig gaap']
                    
            cash_change        = cash_mv_current - cash_mv_prev
            
            
#####     alternative changes
            alts_prev           = ebs_prev[((ebs_prev['aig asset class 3'] == "Common Equity")|(ebs_prev['aig asset class 3'] == "Hedge Fund")|
                                            (ebs_prev['aig asset class 3'] == "Private Equity Fund")|(ebs_prev['aig asset class 3'] == "Other Invested Assets"))&
                                            (ebs_prev['fort re corporate segment']== each_category)]

            alts_current           = ebs_current[((ebs_current['aig asset class 3'] == "Common Equity")|(ebs_current['aig asset class 3'] == "Hedge Fund")|
                                            (ebs_current['aig asset class 3'] == "Private Equity Fund")|(ebs_current['aig asset class 3'] == "Other Invested Assets"))&
                                            (ebs_current['fort re corporate segment']== each_category)]

            alts_ID_current     = alts_current["unique lot id"]
            alts_ID_prev        = alts_prev["unique lot id"]
            alts_purchase_ID    = list(set(alts_ID_current).difference(set(alts_ID_prev)))
            alts_sale_ID        = list(set(alts_ID_prev).difference(set(alts_ID_current)))

            alts_sale = 0
            for idx in range(0,len(alts_sale_ID),1):
                idxx         = alts_sale_ID[idx]
                alts_sale   += alts_prev.loc[alts_prev["unique lot id"]==idxx]['market value usd aig gaap'].iloc[0]
                
            alts_purchase = 0
            for idx in range(0,len(alts_purchase_ID),1):
                idxx           = alts_purchase_ID[idx]
                alts_purchase += alts_current.loc[alts_current["unique lot id"]==idxx]['market value usd aig gaap'].iloc[0]
                
            alts_mv_prev       = alts_prev.sum(axis=0)['market value usd aig gaap']
            alts_mv_current    = alts_current.sum(axis=0)['market value usd aig gaap']
                    
            alts_income        = alts_mv_current - alts_mv_prev + alts_purchase - alts_sale 


        
            agg_attribution    = {'Group':each_category,'Base_Date':eval_date_prev,'Eval_Date':eval_date_current,'previous market value': agg_prev_mv,'current market value': agg_current_mv,'mv change': agg_current_mv-agg_prev_mv,
                                'carry':agg_carry,'Sale': sale,'IR Attribution': agg_IR_attr,'IR_convexity_attribution':agg_IR_cv_attr,
                                'OAS attribution': agg_OAS_att,'Unexplained':agg_unexplained,'Purchase':purchase,
                                'previous cash balance': cash_mv_prev,'current cash balance': cash_mv_current,'cash sale': cash_sale,
                                'cash purchase':cash_purchase,'derivative change': deri_change,'previous derivative MV':prev_deri_mv,
                                'current derivative MV':current_deri_mv,'cash change': cash_change,'currency attribution':agg_ccy_attr,
                                'illiquid asset adj prev':agg_illiquid_adj_prev,'illiquid asset adj current':agg_illiquid_adj_current,
                                'illiquid asset adj change': agg_illiquid_adj_change,'w IR_01': IR_01,'w IR_01_Convexity':IR_01_cv,
                                'weighted average OAS prev':weighted_OAS_prev, 'weighted average OAS current': weighted_OAS_current,
                                'x Alternatives MV prev': alts_mv_prev, 'x Alternatives MV current': alts_mv_current,
                                'x Alternatives income': alts_income, 'x Alternatives sale': alts_sale, 'x Alternatives purchase': alts_purchase,
                                'x credit_01':agg_credit_01, 'x illiquid_ir_att':agg_illiquid_ir_01,
                                'x illiquid_oas_att': agg_illiquid_cs_01}
            
            each_date_attribution_results.append(agg_attribution)

      
        asset_attribution.update( {eval_date_current : each_date_attribution_results} )        

    return asset_attribution



#zzzzzzzzzzzzzzzzzzzzzzzzz Attribution Test zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
#Attribution_Test = Run_asset_Attribution(valDate, market_factor, EBS_Cal_Dates_all,Price_Date,asset_workDir)


def exportasset_Att(Attribution_Test, EBS_Cal_Dates_all, work_dir):
    num_periods = 0
    eval_period = []
    for each_date in EBS_Cal_Dates_all:
        eval_period.append(each_date)
        num_periods = num_periods + 1        
    
    for each_date_idx in range(0, num_periods-1, 1):

        eval_date_prev    = eval_period[each_date_idx].strftime('%m%d%Y')
        eval_date_current = eval_period[each_date_idx + 1].strftime('%m%d%Y')
        eval_key          = eval_period[each_date_idx + 1]
        
        for key, val in Attribution_Test.items(): 
            order_attr  = Attribution_Test[eval_key]
            order_attr
            output=pd.DataFrame(order_attr)
            os.chdir(work_dir)
            asset_filename = 'ass_cu'+'_'+eval_date_prev+eval_date_current + '.xlsx'
            outputWriter = pd.ExcelWriter(asset_filename)
            output.to_excel(outputWriter, index=False)
            outputWriter.save()
#output_asset_attr = exportasset_Att(Attribution_Test, EBS_Cal_Dates_all,work_dir)
