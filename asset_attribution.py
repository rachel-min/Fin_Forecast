# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 15:06:26 2019

@author: jozhou
"""

import os
import pandas as pd
#import pyodbc
#import datetime
#import Lib_Utility as Util
# load akit DLL into python
akit_dir = 'C:/AKit v4.1.0/BIN'
os.sys.path.append(akit_dir)

# load Corp Model Folder DLL into python
corp_model_dir = 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code'
os.sys.path.append(corp_model_dir)

#import Class_Corp_Model  as Corpclass
import Lib_Market_Akit   as IAL_App
import IALPython3        as IAL
#import User_Input_Dic    as UI
#import Lib_BSCR_Model    as BSCR
#import Config_BSCR       as BSCR_Cofig

def Run_asset_Attribution(valDate, EBS_DB_Results, market_factor, market_factor_GBP, numOfLoB, curveType = "Treasury", KRD_Term = IAL_App.KRD_Term):
    
    
    num_periods = 0
    eval_period = []
    
    for each_date in EBS_DB_Results:
        eval_period.append(each_date)
        num_periods = num_periods + 1        
    
    asset_attribution = {}
    
    for each_date_idx in range(0, num_periods-1, 1):
        
        each_date_attribution_results = []

        eval_date_prev    = eval_period[each_date_idx]
        eval_date_current = eval_period[each_date_idx + 1]

#        Load Interest Rate Curves
        irCurve_USD_prev = IAL_App.createAkitZeroCurve(eval_date_prev, curveType, "USD")
        irCurve_GBP_prev = IAL_App.load_BMA_Std_Curves(valDate,"GBP",eval_date_prev)

        irCurve_USD_current = IAL_App.createAkitZeroCurve(eval_date_current, curveType, "USD")
        irCurve_GBP_current = IAL_App.load_BMA_Std_Curves(valDate,"GBP",eval_date_current)
        
        ccy_prev  = market_factor[(market_factor['val_date'] == eval_date_prev)]['GBP'].iloc[0]
        ccy_current  = market_factor[(market_factor['val_date'] == eval_date_current)]['GBP'].iloc[0]
        
        ebs_prev    = EBS_DB_Results[eval_date_prev]
        ebs_current = EBS_DB_Results[eval_date_current]
        
        asset_prev_temp    = ebs_prev.asset_holding
        asset_current_temp = ebs_current.asset_holding
        asset_prev         = asset_prev_temp[(asset_prev_temp['asset_class_f'] != "Derivative")&( asset_prev_temp['asset_class_f'] != "Hedge Fund")&(asset_prev_temp['asset_class_f'] != "Private Equity Fund")&(asset_prev_temp['asset_class_f'] != "Other Invested Assets")&(asset_prev_temp['asset_class_f'] != "Common Equity")&(asset_prev_temp['asset_class_f'] != "ML-III B-Notes")&(asset_prev_temp['asset_class_f'] != "Cash")&(asset_prev_temp['asset_class_f'] != "Cash Fund")&(asset_prev_temp['asset_class_f'] != "TBD")]
        asset_current      = asset_current_temp[(asset_current_temp['asset_class_f'] != "Derivative")&( asset_current_temp['asset_class_f'] != "Hedge Fund")&(asset_current_temp['asset_class_f'] != "Private Equity Fund")&(asset_current_temp['asset_class_f'] != "Other Invested Assets")&(asset_current_temp['asset_class_f'] != "Common Equity")&(asset_current_temp['asset_class_f'] != "ML-III B-Notes")&(asset_current_temp['asset_class_f'] != "Cash")&(asset_current_temp['asset_class_f'] != "Cash Fund")&(asset_current_temp['asset_class_f'] != "TBD")]

    
#  zzzzzzzzzzzzzzzzzzz get all asset group between the two dates  zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz        
        asset_temp = pd.concat([asset_prev,asset_current],axis=0)
        asset_index_temp = asset_temp.groupby(level=asset_temp.index.names).last()
        asset_count      = asset_index_temp.count()[0]
        print(asset_count)


        for idx in range(0, asset_count,1):
            index_name = asset_index_temp.index.values[idx]
            try:
                each_asset         = asset_prev.loc[index_name,:]
                asset_class_prev   = each_asset['asset_class_f']
                asset_cat_prev     = each_asset['category_f']
                mv_prev            = each_asset['Market Value USD GAAP'] 
                duration           = each_asset['Effective Duration (WAMV)']
                convexity          = each_asset['Effective Convexity']
                OAS_prev           = each_asset['OAS']
                Spread_dur         = each_asset['Spread Duration']
                YTW                = each_asset['YTW']
            except:
                mv_prev            = 0
                duration           = 0
                convexity          = 0
                OAS_prev           = 0
                asset_cat_prev     = 0 
                YTW                = 0
                asset_class_prev   = 0

            try:
                each_asset_current = asset_current.loc[index_name,:]
                asset_cat_current  = each_asset_current['category_f']
                asset_class_current= each_asset_current['asset_class_f']
                mv_current         = each_asset_current['Market Value USD GAAP']
                OAS_current        = each_asset_current['OAS']
            except:
                mv_current         = 0
                OAS_current        = 0
                asset_cat_current  = 0    
                asset_class_current= 0
            
            each_attribution = { 'asset group':index_name,'Base_Date':eval_date_prev,'Eval_Date':eval_date_current, 'MV USD GAAP_prev': mv_prev, 'MV USD GAAP_current': mv_current, 'MV_change' : mv_current - mv_prev,'asset_category prev':asset_cat_prev,'asset_category current':asset_cat_current,'effdur_pre':duration,'asset class prev':asset_class_prev,'asset class current':asset_class_current}
            
            IR_attribution = 0     

            if  asset_cat_prev == "ALBA":
                irCurve_prev       = irCurve_GBP_prev
                ccy_rate_prev      = ccy_prev
                   
            else:
                irCurve_prev       = irCurve_USD_prev
                ccy_rate_prev      = 1.0

            if  asset_cat_current == "ALBA":
                irCurve_current    = irCurve_GBP_current
                ccy_rate_current   = ccy_current
                   
            else:
                irCurve_current    = irCurve_USD_current
                ccy_rate_current   = 1.0
    


#            Step 1: asset Carry
            return_year_frac = IAL.Date.yearFrac("ACT/365",  eval_date_prev, eval_date_current)
            carry_cost       = mv_prev * YTW/100*return_year_frac
            
            
            each_attribution.update( { 'YTW'                : YTW/100  })
            each_attribution.update( { 'OAS'                : OAS_prev / 10000 } )
            each_attribution.update( { 'carry'              : carry_cost } )
            

#            Step 2: Interest Rate Attributions
            mv_ex_carry         = mv_prev +carry_cost
            for key, value in KRD_Term.items():
                KRD_name        = "KRD " + key
                IR_Term         = "IR_" + key

                key_rate_prev        = market_factor[(market_factor['val_date'] == eval_date_prev)][IR_Term].values[0]
                key_rate_current     = market_factor[(market_factor['val_date'] == eval_date_current)][IR_Term].values[0]
                key_rate_change      = key_rate_current - key_rate_prev
                each_KRD             = each_asset[KRD_name]

                key_rate_attribution = -mv_ex_carry* each_KRD * key_rate_change  
                IR_attribution      += key_rate_attribution
                
                each_attribution.update( { 'mv_ex_carry'           : mv_ex_carry } )
                each_attribution.update( { KRD_name                : each_KRD } )
                each_attribution.update( { 'key_rate_prev'         : key_rate_prev } )
                each_attribution.update( { 'key_rate_current'      : key_rate_current } )
                each_attribution.update( { 'key_rate_change'       : key_rate_change } )
                each_attribution.update( { 'key_rate_attribution'  : key_rate_attribution } )

            each_attribution.update( { 'IR_attribution'  : IR_attribution } )
                

#            Step 3: Interest Rate Convexity Attribution
            current_rate = irCurve_current.zeroRate( max(1, duration) ) 
            prev_rate    = irCurve_prev.zeroRate(max(1, duration))            
            
            ir_rate_change_dur       = current_rate - prev_rate
            IR_covexity_attribution  = mv_ex_carry * 1/2 * convexity * ir_rate_change_dur * ir_rate_change_dur * 100

            each_attribution.update( { 'prev_rate'               : prev_rate } )
            each_attribution.update( { 'current_rate'            : current_rate } )
            each_attribution.update( { 'ir_rate_change_dur'      : ir_rate_change_dur } )
            each_attribution.update( { 'ir_convexity'            : convexity } )
            each_attribution.update( { 'IR_covexity_attribution' : IR_covexity_attribution } )

#            Step 4: OAS Change Attribution
            OAS_change       = ( OAS_current - OAS_prev ) / 10000
            OAS_attribution  = -mv_ex_carry * Spread_dur * OAS_change

            each_attribution.update( { 'prev_OAS'         : OAS_prev  / 10000 } )
            each_attribution.update( { 'current_OAS'      : OAS_current  / 10000 } )
            each_attribution.update( { 'OAS_change'       : OAS_change } )
            each_attribution.update( { 'Spread Duration'         : Spread_dur } )
            each_attribution.update( { 'OAS_attribution'  : OAS_attribution } )

#            Step 5: Currency Attribution
            Currency_attribution  = mv_current / ccy_rate_current  * (ccy_rate_current - ccy_rate_prev)

            each_attribution.update( { 'ccy_rate_prev'    : ccy_rate_prev } )
            each_attribution.update( { 'ccy_rate_current' : ccy_rate_current } )
            each_attribution.update( { 'ccy_change'       : ccy_rate_current-ccy_rate_prev } )
            each_attribution.update( { 'Currency_attribution'  : Currency_attribution } )

#            Step 6: Unexplained
            Unexplained       = mv_current - mv_prev - carry_cost - IR_attribution - IR_covexity_attribution - OAS_attribution - Currency_attribution
            each_attribution.update( { 'Unexplained'  : Unexplained } )

            each_date_attribution_results.append(each_attribution)

        asset_attribution.update( {eval_date_current : each_date_attribution_results} )        

    return asset_attribution



#zzzzzzzzzzzzzzzzzzzzzzzzz Attribution Test zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
Attribution_Test = Run_asset_Attribution(valDate, EBS_DB_results, market_factor, market_factor_GBP_IR, numOfLoB)
#
#def exportasset_Att(Attribution_Test,  work_dir):
#    num_periods = 0
#    eval_period = []
#    for each_date in EBS_Cal_Dates_all:
#        eval_period.append(each_date)
#        num_periods = num_periods + 1        
#    
#    for each_date_idx in range(0, num_periods-1, 1):
#
#        eval_date_prev    = eval_period[each_date_idx].strftime('%m%d%Y')
#        eval_date_current = eval_period[each_date_idx + 1].strftime('%m%d%Y')
#        eval_key          = eval_period[each_date_idx + 1]
#        
#        for key, val in Attribution_Test.items(): 
#            order_attr  = Attribution_Test[eval_key]
#            order_attr
#            output=pd.DataFrame(order_attr)
#            os.chdir(work_dir)
#            asset_filename = 'asset_att'+'_'+eval_date_prev+eval_date_current + '.xlsx'
#            outputWriter = pd.ExcelWriter(asset_filename)
#            output.to_excel(outputWriter, sheet_name= asset_filename, index=False)
#            outputWriter.save()

def exportasset_Att(Attribution_Test,  work_dir):
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
            num_a       = len(order_attr)
            colNames =['prev date','current date','asset group',"MV USD GAAP prev","MV USD GAAP current","MV change","YTW","carry","IR_attribution",\
                       "current rate","prev rate","ir rate change duration","ir convexity","IR convexity attribution","prev OAS","current OAS",\
                       "OAS change","Spread Duration","OAS attribution","currency rate current","currency rate previous","currency change",\
                       "currency attribution","unexplained"]
            output_each = pd.DataFrame([],columns = colNames)
            for idx in range(0, num_a, 1):
                temp = order_attr[idx]


                prev_date     = temp.get("Base_Date")
                cur_date      = temp.get("Eval_Date")
                asset_group   = temp.get("asset group")
                mv_prev       = temp.get("MV USD GAAP_prev")
                mv_current    = temp.get("MV USD GAAP_current")
                mv_change     = temp.get("MV_change")
                YTW           = temp.get("YTW")
                carry         = temp.get("carry")
                IR_att        = temp.get("IR_attribution")
                cur_rate      = temp.get("current_rate")
                prev_rate     = temp.get("prev_rate")
                change_dur    = temp.get("ir_rate_change_dur")
                convexity     = temp.get("ir_convexity")
                IR_CV_att     = temp.get("IR_covexity_attribution")
                prev_OAS      = temp.get("prev_OAS")
                cur_OAS       = temp.get("current_OAS")
                OAS_change    = temp.get("OAS_change")
                spread_dur    = temp.get("Spread Duration")
                OAS_att       = temp.get("OAS_attribution")
                ccy_prev      = temp.get("ccy_rate_prev")
                ccy_current   = temp.get("ccy_rate_current")
                ccy_change    = temp.get("ccy_change")
                ccy_att       = temp.get("Currency_attribution")
                unexplained   = temp.get("Unexplained")
                                 
                output_each   = output_each.append(pd.DataFrame([[prev_date,cur_date,asset_group,mv_prev,mv_current,mv_change,YTW,carry,IR_att,cur_rate,prev_rate,change_dur,convexity,IR_CV_att,prev_OAS,cur_OAS,OAS_change,spread_dur,OAS_att,ccy_prev,ccy_current,ccy_change,ccy_att,unexplained]], columns = colNames), ignore_index = True)    
                
            output=pd.DataFrame(output_each)
            os.chdir(work_dir)
            asset_filename = 'asset_att'+'_'+eval_date_prev+eval_date_current + '.xlsx'
            outputWriter = pd.ExcelWriter(asset_filename)
            output.to_excel(outputWriter, sheet_name= asset_filename, index=False)
            outputWriter.save()

output_asset_attr = exportasset_Att(Attribution_Test, work_dir)