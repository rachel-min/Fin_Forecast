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
    
    for each_date in EBS_Cal_Dates_all:
        eval_period.append(each_date)
        num_periods = num_periods + 1   
        
    
    asset_attribution = {}
    
    for each_date_idx in range(0, num_periods-1, 1):
        
        each_date_attribution_results = []

        eval_date_prev    = eval_period[each_date_idx]
        eval_date_current = eval_period[each_date_idx + 1]
        
##      cusip level   
        os.chdir(asset_workDir)
        asset_fileName_prev = r'.\Asset_Holdings_' + eval_date_prev.strftime('%Y%m%d') + '.xlsx'
        asset_fileName_current = r'.\Asset_Holdings_' + eval_date_current.strftime('%Y%m%d') + '.xlsx'
        portFile_prev = pd.ExcelFile(asset_fileName_prev)
        portInput_prev = pd.read_excel(portFile_prev, sheet_name='DSA RE Holdings', skiprows=[0, 1, 2, 3, 4, 5, 6])

        portInput_prev = portInput_prev.dropna(axis=0, how='all')
        portInput_prev = portInput_prev.dropna(axis=1, how='all')
        
        portFile_current = pd.ExcelFile(asset_fileName_current)
        portInput_current = pd.read_excel(portFile_current, sheet_name='DSA RE Holdings', skiprows=[0, 1, 2, 3, 4, 5, 6])

        portInput_current = portInput_current.dropna(axis=0, how='all')
        portInput_current = portInput_current.dropna(axis=1, how='all')


#        Load Interest Rate Curves
        irCurve_USD_prev = IAL_App.createAkitZeroCurve(eval_date_prev, curveType, "USD")
#        irCurve_GBP_prev = IAL_App.load_BMA_Std_Curves(valDate,"GBP",eval_date_prev)

        irCurve_USD_current = IAL_App.createAkitZeroCurve(eval_date_current, curveType, "USD")
#        irCurve_GBP_current = IAL_App.load_BMA_Std_Curves(valDate,"GBP",eval_date_current)
        
#        ccy_prev  = market_factor[(market_factor['val_date'] == eval_date_prev)]['GBP'].iloc[0]
#        ccy_current  = market_factor[(market_factor['val_date'] == eval_date_current)]['GBP'].iloc[0]
        
        ebs_prev    = portInput_prev
        ebs_current = portInput_current
        

        asset_prev         = ebs_prev[(ebs_prev['AIG Asset Class 3'] != "Derivative")&( ebs_prev['AIG Asset Class 3'] != "Hedge Fund")&(ebs_prev['AIG Asset Class 3'] != "Private Equity Fund")&(ebs_prev['AIG Asset Class 3'] != "Other Invested Assets")&(ebs_prev['AIG Asset Class 3'] != "Common Equity")&(ebs_prev['AIG Asset Class 3'] != "Cash")&(ebs_prev['AIG Asset Class 3'] != "Cash Fund")&(ebs_prev['AIG Asset Class 3'] != "TBD")&(ebs_prev['Issuer Name'] != "LSTREET II, LLC")&(ebs_prev['Encumbrance Program Level 4 Desc']!="DSA Reinsurance ceding - AIRCO ALBA")]
        asset_current      = ebs_current[(ebs_current['AIG Asset Class 3'] != "Derivative")&( ebs_current['AIG Asset Class 3'] != "Hedge Fund")&(ebs_current['AIG Asset Class 3'] != "Private Equity Fund")&(ebs_current['AIG Asset Class 3'] != "Other Invested Assets")&(ebs_current['AIG Asset Class 3'] != "Common Equity")&(ebs_current['AIG Asset Class 3'] != "Cash")&(ebs_current['AIG Asset Class 3'] != "Cash Fund")&(ebs_current['AIG Asset Class 3'] != "TBD")&(ebs_current['Issuer Name'] != "LSTREET II, LLC")&(ebs_current['Encumbrance Program Level 4 Desc']!="DSA Reinsurance ceding - AIRCO ALBA")]
        asset_prev.fillna(value=0,inplace=True)
        asset_current.fillna(value=0,inplace=True)
        
#       sort cusip
        ID_current         = asset_current["Lot Number Unique ID"]
        ID_prev            = asset_prev["Lot Number Unique ID"]
        purchase_ID        = list(set(ID_current).difference(set(ID_prev)))
        sale_ID            = list(set(ID_prev).difference(set(ID_current)))
        common_ID          = list(set(ID_current).intersection(set(ID_prev)))
        asset_count        = len(common_ID)

#       calculate the sale amount and purchase amount        
        purchase = 0
        for idx in range(0,len(purchase_ID),1):
            idxx    = purchase_ID[idx]
            purchase += asset_current.loc[asset_current["Lot Number Unique ID"]==idxx]['Market Value USD GAAP'].iloc[0]
            
        sale = 0
        for idx in range(0,len(sale_ID),1):
            idxx    = sale_ID[idx]
            sale   += asset_prev.loc[asset_prev["Lot Number Unique ID"]==idxx]['Market Value USD GAAP'].iloc[0]
    
#  zzzzzzzzzzzzzzzzzzz get all asset group between the two dates  zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz        
#        asset_temp = pd.concat([asset_prev,asset_current],axis=0)
#        asset_index_temp = asset_temp.groupby(asset_temp['Lot Number Unique ID']).first()
#        asset_count      = asset_index_temp.count()[0]
#        print(asset_count)
        
        agg_carry      = 0
        agg_prev_mv    = sale
        agg_current_mv = purchase
        agg_IR_attr    = 0
        agg_IR_cv_attr = 0
        agg_OAS_att    = 0
        agg_unexplained= 0
         
        

        for idx in range(1, asset_count,1):
            index_name = common_ID[idx]
            each_asset         = asset_prev.loc[asset_prev['Lot Number Unique ID']==index_name]
            asset_class_prev   = each_asset['AIG Asset Class 3'].iloc[0]
            asset_cat_prev     = each_asset['Encumbrance Program Level 4 Code'].iloc[0]
            mv_prev            = each_asset['Market Value USD GAAP'].iloc[0]
            duration           = each_asset['Effective Duration (WAMV)'].iloc[0]
            convexity          = each_asset['Effective Convexity'].iloc[0]
            OAS_prev           = each_asset['OAS'].iloc[0]
            Spread_dur         = each_asset['Spread Duration'].iloc[0]
            YTW                = each_asset['YTW'].iloc[0]

            each_asset_current = asset_current.loc[asset_current['Lot Number Unique ID']==index_name]
            asset_cat_current  = each_asset_current['Encumbrance Program Level 4 Code'].iloc[0]
            asset_class_current= each_asset_current['AIG Asset Class 3'].iloc[0]
            mv_current         = each_asset_current['Market Value USD GAAP'].iloc[0]
            
            OAS_current        = each_asset_current['OAS'].iloc[0]
            

                
            each_attribution = { 'asset group':index_name,'Base_Date':eval_date_prev,'Eval_Date':eval_date_current, 'MV USD GAAP_prev': mv_prev, 'MV USD GAAP_current': mv_current, 'MV_change' : mv_current - mv_prev,'asset_category prev':asset_cat_prev,'asset_category current':asset_cat_current,'effdur_pre':duration,'asset class prev':asset_class_prev,'asset class current':asset_class_current}

            agg_prev_mv    += mv_prev
            agg_current_mv += mv_current
            
            IR_attribution = 0     

#            if  asset_cat_prev == "DSA Reinsurance ceding - AIRCO ALBA":
#                irCurve_prev       = irCurve_GBP_prev
#                ccy_rate_prev      = ccy_prev
#                   
#            else:
            irCurve_prev       = irCurve_USD_prev
#                ccy_rate_prev      = 1.0

#            if  asset_cat_current == "DSA Reinsurance ceding - AIRCO ALBA":
#                irCurve_current    = irCurve_GBP_current
#                ccy_rate_current   = ccy_current
                   
#            else:
            irCurve_current    = irCurve_USD_current
#                ccy_rate_current   = 1.0
    


#            Step 1: asset Carry
            return_year_frac = IAL.Date.yearFrac("ACT/365",  eval_date_prev, eval_date_current)
            carry_cost       = mv_prev * YTW/100*return_year_frac
            agg_carry       += carry_cost
           
            
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
                
                
                each_KRD             = each_asset[KRD_name].iloc[0]


                key_rate_attribution = -mv_ex_carry* each_KRD * key_rate_change  
                IR_attribution      += key_rate_attribution
                
                each_attribution.update( { 'mv_ex_carry'           : mv_ex_carry } )
                each_attribution.update( { KRD_name                : each_KRD } )
                each_attribution.update( { 'key_rate_prev'         : key_rate_prev } )
                each_attribution.update( { 'key_rate_current'      : key_rate_current } )
                each_attribution.update( { 'key_rate_change'       : key_rate_change } )
                each_attribution.update( { 'key_rate_attribution'  : key_rate_attribution } )

            each_attribution.update( { 'IR_attribution'  : IR_attribution } )
            agg_IR_attr     += IR_attribution

            

#            Step 3: Interest Rate Convexity Attribution
            current_rate = irCurve_current.zeroRate( max(1, duration) ) 
            prev_rate    = irCurve_prev.zeroRate(max(1, duration))            
            
            ir_rate_change_dur       = current_rate - prev_rate

            IR_covexity_attribution  = mv_ex_carry * 1/2 * convexity * ir_rate_change_dur * ir_rate_change_dur * 100

                
            agg_IR_cv_attr += IR_covexity_attribution

            each_attribution.update( { 'prev_rate'               : prev_rate } )
            each_attribution.update( { 'current_rate'            : current_rate } )
            each_attribution.update( { 'ir_rate_change_dur'      : ir_rate_change_dur } )
            each_attribution.update( { 'ir_convexity'            : convexity } )
            each_attribution.update( { 'IR_covexity_attribution' : IR_covexity_attribution } )

#            Step 4: OAS Change Attribution
            OAS_change       = ( OAS_current - OAS_prev ) / 10000
            OAS_attribution  = -mv_ex_carry * Spread_dur * OAS_change
            agg_OAS_att     += OAS_attribution
        

            each_attribution.update( { 'prev_OAS'         : OAS_prev  / 10000 } )
            each_attribution.update( { 'current_OAS'      : OAS_current  / 10000 } )
            each_attribution.update( { 'OAS_change'       : OAS_change } )
            each_attribution.update( { 'Spread Duration'  : Spread_dur } )
            each_attribution.update( { 'OAS_attribution'  : OAS_attribution } )

#            Step 5: Currency Attribution
#            Currency_attribution  = mv_current / ccy_rate_current  * (ccy_rate_current - ccy_rate_prev)
#
#            each_attribution.update( { 'ccy_rate_prev'    : ccy_rate_prev } )
#            each_attribution.update( { 'ccy_rate_current' : ccy_rate_current } )
#            each_attribution.update( { 'ccy_change'       : ccy_rate_current-ccy_rate_prev } )
#            each_attribution.update( { 'Currency_attribution'  : Currency_attribution } )

#            Step 6: Unexplained
            Unexplained       = mv_current - mv_prev - carry_cost - IR_attribution - IR_covexity_attribution - OAS_attribution 
            agg_unexplained  += Unexplained
            each_attribution.update( { 'Unexplained'  : Unexplained } )

#            each_date_attribution_results.append(each_attribution)


#       cash movement        
        cash_prev    = ebs_prev[((ebs_prev['AIG Asset Class 3'] == "Cash")|(ebs_prev['AIG Asset Class 3'] == "Cash Fund"))&(ebs_prev['Owning Entity Name'] != "American International Reinsurance Company, Ltd.")]
        cash_current = ebs_current[((ebs_current['AIG Asset Class 3'] == "Cash")|(ebs_current['AIG Asset Class 3'] == "Cash Fund"))&(ebs_current['Owning Entity Name'] != "American International Reinsurance Company, Ltd.")]
        key_prev               = ebs_prev['Security Desc DESC'].astype(str)
        key_current            = ebs_current['Security Desc DESC'].astype(str)

        criteria              = 'Interest Rate'
        deri_prev           = ebs_prev[key_prev.apply(lambda x: criteria in x)]
        deri_current        = ebs_current[key_current.apply(lambda x: criteria in x)]
    
        modco_deri_prev  = deri_prev[(deri_prev['Owning Entity Name'] != "American International Reinsurance Company, Ltd.")]
        modco_deri_current  = deri_current[(deri_current['Owning Entity Name'] != "American International Reinsurance Company, Ltd.")]
        prev_deri_mv      = modco_deri_prev.sum(axis=0)['Market Value USD GAAP']
        current_deri_mv   = modco_deri_current.sum(axis=0)['Market Value USD GAAP']
        
        deri_change = current_deri_mv-prev_deri_mv
    
        cash_ID_current         = cash_current["Lot Number Unique ID"]
        cash_ID_prev            = cash_prev["Lot Number Unique ID"]
        cash_purchase_ID        = list(set(cash_ID_current).difference(set(cash_ID_prev)))
        cash_sale_ID            = list(set(cash_ID_prev).difference(set(cash_ID_current)))

        
        cash_sale = 0
        for idx in range(0,len(cash_sale_ID),1):
            idxx    = cash_sale_ID[idx]
            cash_sale   += cash_prev.loc[cash_prev["Lot Number Unique ID"]==idxx]['Market Value USD GAAP'].iloc[0]
            
        cash_purchase = 0
        for idx in range(0,len(cash_purchase_ID),1):
            idxx    = cash_purchase_ID[idx]
            cash_purchase += cash_current.loc[cash_current["Lot Number Unique ID"]==idxx]['Market Value USD GAAP'].iloc[0]
            
        cash_mv_prev  = cash_prev.sum(axis=0)['Market Value USD GAAP']
        cash_mv_current = cash_current.sum(axis=0)['Market Value USD GAAP']
                
        cash_change = cash_mv_current - cash_mv_prev
    
        agg_attribution  = {'Base_Date':eval_date_prev,'Eval_Date':eval_date_current,'previous market value': agg_prev_mv,'current market value': agg_current_mv,'mv change': agg_current_mv-agg_prev_mv,\
                            'carry':agg_carry,'Sale': sale,'IR Attribution': agg_IR_attr,'IR_convexity_attribution':agg_IR_cv_attr,\
                            'OAS attribution': agg_OAS_att,'Unexplained':agg_unexplained,'Purchase':purchase,\
                            'previous cash balance': cash_mv_prev,'current cash balance': cash_mv_current,'cash sale': cash_sale,\
                            'cash purchase':cash_purchase,'derivative change': deri_change,'previous derivative MV':prev_deri_mv,\
                            'current derivative MV':current_deri_mv,'cash change': cash_change}        
        
        each_date_attribution_results.append(agg_attribution)

      
        asset_attribution.update( {eval_date_current : each_date_attribution_results} )        

    return asset_attribution



#zzzzzzzzzzzzzzzzzzzzzzzzz Attribution Test zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
Attribution_Test = Run_asset_Attribution(valDate, EBS_DB_results, market_factor, market_factor_GBP_IR, numOfLoB)

def exportasset_Att(Attribution_Test,  work_dir):
    num_periods = 0
    eval_period = []
    for each_date in EBS_Cal_Dates_all:
        eval_period.append(each_date)
        num_periods = num_periods + 1        
    
    for each_date_idx in range(0, num_periods-1, 1):

        eval_date_prev    = eval_period[each_date_idx].strftime('%m%d%Y')
        eval_date_current = eval_period[each_date_idx + 1].strftime('%m%d%Y')

        
        for key, val in Attribution_Test.items(): 
            order_attr = Attribution_Test[key]
            order_attr
            output=pd.DataFrame(order_attr)
            os.chdir(work_dir)
            asset_filename = 'ass_cu'+'_'+eval_date_prev+eval_date_current + '.xlsx'
            outputWriter = pd.ExcelWriter(asset_filename)
            output.to_excel(outputWriter, sheet_name= asset_filename, index=False)
            outputWriter.save()
output_asset_attr = exportasset_Att(Attribution_Test, work_dir)