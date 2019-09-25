import os
#import pandas as pd
#import pyodbc
#import datetime
#import Lib_Utility as Util
# load akit DLL into python
akit_dir = 'C:/AKit v4.1.0/BIN'
os.sys.path.append(akit_dir)

# =============================================================================
# # load Corp Model Folder DLL into python
# corp_model_dir = 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code'
# os.sys.path.append(corp_model_dir)
# =============================================================================

#import Class_Corp_Model  as Corpclass
import Lib_Market_Akit   as IAL_App
import IALPython3        as IAL
#import User_Input_Dic    as UI
#import Lib_BSCR_Model    as BSCR
#import Config_BSCR       as BSCR_Cofig

def Run_Liab_Attribution(valDate, EBS_DB_Results, market_factor, market_factor_GBP, numOfLoB, curveType = "Treasury", KRD_Term = IAL_App.KRD_Term):
    
    
    num_periods = 0
    eval_period = []
    
    for each_date in EBS_DB_Results:
        eval_period.append(each_date)
        num_periods = num_periods + 1        
    
    liab_attribution = {}
    
    for each_date_idx in range(0, num_periods-1, 1):
        
        each_date_attribution_results = []

        eval_date_prev    = eval_period[each_date_idx]
        eval_date_current = eval_period[each_date_idx + 1]

#        Load Interest Rate Curves
        irCurve_USD_prev = IAL_App.createAkitZeroCurve(eval_date_prev, curveType, "USD")
        irCurve_GBP_prev = IAL_App.load_BMA_Std_Curves(valDate,"GBP",eval_date_prev)

        irCurve_USD_current = IAL_App.createAkitZeroCurve(eval_date_current, curveType, "USD")
        irCurve_GBP_current = IAL_App.load_BMA_Std_Curves(valDate,"GBP",eval_date_current)

        
        ebs_prev    = EBS_DB_Results[eval_date_prev]
        ebs_current = EBS_DB_Results[eval_date_current]
        
        liab_prev    = ebs_prev.liability['dashboard']
        liab_current = ebs_current.liability['dashboard']
    
        for idx in range(1, numOfLoB + 1, 1):

            each_liab         = liab_prev[idx]
            each_liab_current = liab_current[idx]

            each_attribution = { 'Base_Date':eval_date_prev,'Eval_Date':eval_date_current, 'LOB' : idx, 'PVBE_prev': each_liab.PV_BE, 'PVBE_current': each_liab_current.PV_BE, 'PVBE_change' : each_liab_current.PV_BE - each_liab.PV_BE }
            
            IR_attribution = 0
            ccy           = each_liab.get_LOB_Def('Currency')        

            if ccy == "GBP":
                irCurve_prev       = irCurve_GBP_prev
                irCurve_current    = irCurve_GBP_current
                ccy_rate_prev      = each_liab.ccy_rate
                ccy_rate_current   = each_liab_current.ccy_rate
    
            else:
                irCurve_prev       = irCurve_USD_prev
                irCurve_current    = irCurve_USD_current
                ccy_rate_prev      = 1.0
                ccy_rate_current   = 1.0

#            Step 1: Liability Carry
#            zzzzzzzzzzzzzzzzzzz carry_cost should be replaced by YTM when available  zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
            carry_rf_rate    = irCurve_prev.zeroRate(max(1, each_liab.duration))
            carry_cost_rate  = carry_rf_rate + each_liab.OAS / 10000            
            return_year_frac = IAL.Date.yearFrac("ACT/365",  eval_date_prev, eval_date_current)
            carry_cost       = each_liab.PV_BE * carry_cost_rate * return_year_frac
            
            
            each_attribution.update( { 'carry_rf'           : carry_rf_rate } )
            each_attribution.update( { 'OAS'                : each_liab.OAS / 10000 } )
            each_attribution.update( { 'carry_cost_rate'    : carry_cost_rate } )
            each_attribution.update( { 'return_period_year' : return_year_frac } )
            each_attribution.update( { 'carry'              : carry_cost } )
            

#            Step 2: Interest Rate Attributions
            for key, value in KRD_Term.items():
                KRD_name        = "KRD_" + key
                IR_Term         = "IR_" + key
                KRD_change      = "key_rate_change_" + key

                key_rate_prev             = market_factor[(market_factor['val_date'] == eval_date_prev)][IR_Term].values[0]
                key_rate_current          = market_factor[(market_factor['val_date'] == eval_date_current)][IR_Term].values[0]
                key_rate_change                       = key_rate_current - key_rate_prev
                each_KRD             = each_liab.get_KRD_value(KRD_name, 0)

                key_rate_attribution = -each_liab.PV_BE * each_KRD * key_rate_change
                IR_attribution      += key_rate_attribution
                
                each_attribution.update( { KRD_name                : each_KRD } )
                each_attribution.update( { 'key_rate_prev'         : key_rate_prev } )
                each_attribution.update( { 'key_rate_current'      : key_rate_current } )
                each_attribution.update( { KRD_change              : key_rate_change } )
                each_attribution.update( { 'key_rate_attribution'  : key_rate_attribution } )

            each_attribution.update( { 'IR_attribution'  : IR_attribution } )
                

#            Step 3: Interest Rate Convexity Attribution
            current_rate = irCurve_current.zeroRate( max(1, each_liab.duration) )
            prev_rate    = irCurve_prev.zeroRate(max(1, each_liab.duration))            
            
            ir_rate_change_dur       = current_rate - prev_rate
            IR_convexity_attribution  = each_liab.PV_BE * 1/2 * each_liab.convexity * ir_rate_change_dur * ir_rate_change_dur*100

            each_attribution.update( { 'prev_rate'               : prev_rate } )
            each_attribution.update( { 'current_rate'            : current_rate } )
            each_attribution.update( { 'ir_rate_change_dur'      : ir_rate_change_dur } )
            each_attribution.update( { 'ir_convexity'            : each_liab.convexity } )
            each_attribution.update( { 'IR_convexity_attribution' : IR_convexity_attribution } )

#            Step 4: OAS Change Attribution
            OAS_change       = ( each_liab_current.OAS - each_liab.OAS ) / 10000
            OAS_attribution  = -each_liab.PV_BE * each_liab.duration * OAS_change

            each_attribution.update( { 'prev_OAS'         : each_liab.OAS  / 10000 } )
            each_attribution.update( { 'current_OAS'      : each_liab_current.OAS  / 10000 } )
            each_attribution.update( { 'OAS_change'       : OAS_change } )
            each_attribution.update( { 'duration'         : each_liab.duration } )
            each_attribution.update( { 'OAS_attribution'  : OAS_attribution } )

#            Step 5: Currency Attribution
            Currency_attribution  = each_liab_current.PV_BE / ccy_rate_current  * (ccy_rate_current - ccy_rate_prev)

            each_attribution.update( { 'ccy_rate_prev'    : ccy_rate_prev } )
            each_attribution.update( { 'ccy_rate_current' : ccy_rate_current } )
            each_attribution.update( { 'ccy_change'       : ccy_rate_current-ccy_rate_prev } )
            each_attribution.update( { 'Currency_attribution'  : Currency_attribution } )

#            Step 6: Unexplained
            Unexplained       = each_liab_current.PV_BE - each_liab.PV_BE - carry_cost - IR_attribution - IR_convexity_attribution - OAS_attribution - Currency_attribution
            each_attribution.update( { 'Unexplained'  : Unexplained } )

            each_date_attribution_results.append(each_attribution)

        liab_attribution.update( {eval_date_current : each_date_attribution_results} )        

    return liab_attribution



#%%zzzzzzzzzzzzzzzzzzzzzzzzz Attribution Test zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
Attribution_Test = Run_Liab_Attribution(valDate, EBS_DB_results, market_factor, market_factor_GBP_IR, numOfLoB)

#liab_attr_file = r'.\liability_attribution.xlsx'  
#def exportLobLiab(Attribution_Test, outFileName, work_dir):
#    for key, val in Attribution_Test.items(): 
#        order_attr = Attribution_Test[key]
#        output=pd.DataFrame(order_attr)
#        os.chdir(work_dir)
#        outputWriter = pd.ExcelWriter(outFileName)
#        output.to_excel(outputWriter, sheet_name= 'liability attribution', index=False)
#        outputWriter.save()
#output_liab_attr = exportLobLiab(Attribution_Test, liab_attr_file, work_dir)

def exportLobLiab(Attribution_Test,  work_dir):
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
            colNames =['prev date','current date','LOB',"PVBE prev","PVBE current","PVBE change","carry_rf","OAS","carry cost rate","year fraction","carry",\
                       "IR_attribution","current rate","prev rate","ir rate change duration","ir convexity","IR convexity attribution","prev OAS",\
                       "current OAS","OAS change","Spread Duration","OAS attribution","currency rate current","currency rate previous","currency change",\
                       "currency attribution","unexplained"]
            output_each = pd.DataFrame([],columns = colNames)
            for idx in range(0, num_a, 1):
                temp = order_attr[idx]
                
                prev_date     = temp.get("Base_Date")
                cur_date      = temp.get("Eval_Date")
                LOB           = temp.get("LOB")
                PVBE_prev     = temp.get("PVBE_prev")
                PVBE_current  = temp.get("PVBE_current")
                PVBE_change   = temp.get("PVBE_change")
                carry_rf_rate = temp.get("carry_rf")
                OAS           = temp.get("OAS")               
                carry_cost    = temp.get("carry_cost_rate")
                year_frac     = temp.get("return_period_year")
#                YTW           = temp.get("YTW")
                carry         = temp.get("carry")
                IR_att        = temp.get("IR_attribution")
                cur_rate      = temp.get("current_rate")
                prev_rate     = temp.get("prev_rate")
                change_dur    = temp.get("ir_rate_change_dur")
                convexity     = temp.get("ir_convexity")
                IR_CV_att     = temp.get("IR_convexity_attribution")
                prev_OAS      = temp.get("prev_OAS")
                cur_OAS       = temp.get("current_OAS")
                OAS_change    = temp.get("OAS_change")
                dur           = temp.get("duration")
                OAS_att       = temp.get("OAS_attribution")
                ccy_prev      = temp.get("ccy_rate_prev")
                ccy_current   = temp.get("ccy_rate_current")
                ccy_change    = temp.get("ccy_change")
                ccy_att       = temp.get("Currency_attribution")
                unexplained   = temp.get("Unexplained")
                                 
                output_each   = output_each.append(pd.DataFrame([[prev_date,cur_date,LOB,PVBE_prev,PVBE_current,PVBE_change,carry_rf_rate,OAS,carry_cost,\
                                                                  year_frac,carry,IR_att,cur_rate,prev_rate,change_dur,convexity,IR_CV_att,prev_OAS,cur_OAS,\
                                                                  OAS_change,dur,OAS_att,ccy_current,ccy_prev,ccy_change,ccy_att,unexplained]],columns = colNames), ignore_index = True)    
                
            output=pd.DataFrame(output_each)
            os.chdir(work_dir)
            asset_filename = 'liab_att'+'_'+eval_date_prev+eval_date_current + '.xlsx'
            outputWriter = pd.ExcelWriter(asset_filename)
            output.to_excel(outputWriter, sheet_name= asset_filename, index=False)
            outputWriter.save()
            
output_liab_attr = exportLobLiab(Attribution_Test, work_dir)