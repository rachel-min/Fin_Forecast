# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 17:11:06 2019

@author: seongpar
"""
import Class_CFO as cfo
import datetime as dt
import redshift_database as db
import pandas as pd
#import Lib_Corp_Model as Corp
import Lib_Market_Akit   as IAL_App

if __name__ == '__main__':

#%%Example 1    
    print('Start Projection')

    test_results = {}

    actual_estimate = "Estimate"
    valDate         = dt.datetime(2019, 6,28)
    date_start      = dt.datetime(2019, 6,28)
    date_end        = dt.datetime(2029, 12, 28)
    freq            = 'A'
    scen            = 'Base'
    
    
    CF_Database    = r'L:\DSA Re\Workspace\Production\2019_Q2\BMA Best Estimate\Main_Run_v003\0_CORP_20190510_00_AggregateCFs_Result.accdb'
    CF_TableName   = "I_LBA____062019____________00"

    Step1_Database = r'L:\DSA Re\Workspace\Production\2019_Q2\BMA Best Estimate\Main_Run_v003\1_CORP_20190510_00_Output.accdb'
    PVBE_TableName         = "O_PVL____062019_062019_____01"
    bindingScen      = 1
    numOfLoB         = 45
    Proj_Year        = 70
    work_dir       = 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\2019Q2'
    cash_flow_freq = 'A'
    
    curveType        = "Treasury"
    base_GBP         = 1.26977 # 1Q19: 1.3004; 2Q19: 1.26977    
    liab_spread_beta = 0.65


    liab_val_base = {
        'CF_Database'    : CF_Database, 
        'CF_TableName'   : CF_TableName, 
        'Step1_Database' : Step1_Database, 
        'PVBE_TableName' : PVBE_TableName, 
        'bindingScen'    : bindingScen, 
        'numOfLoB'       : numOfLoB, 
        'Proj_Year'      : Proj_Year, 
        'work_dir'       : work_dir, 
        'cash_flow_freq' : cash_flow_freq,
        'curve_type'     : curveType,
        'bae_GBP'        : base_GBP,
        'liab_benchmark' : "BBB",
        'liab_spread_beta': liab_spread_beta
    }

    liab_val_alt = None

    proj_cash_flows = {
        'CF_Database'    : CF_Database, 
        'CF_TableName'   : CF_TableName, 
        'Step1_Database' : Step1_Database, 
        'PVBE_TableName' : PVBE_TableName, 
        'bindingScen'    : bindingScen, 
        'numOfLoB'       : numOfLoB, 
        'Proj_Year'      : Proj_Year, 
        'work_dir'       : work_dir, 
        'cash_flow_freq' : cash_flow_freq,
        'curve_type'     : curveType        
    }

    liab_val_alt = None

#   Initializing CFO
    cfo_work = cfo.cfo(valDate, date_start, freq, date_end, scen, actual_estimate, liab_val_base, liab_val_alt, proj_cash_flows)
    cfo_work.load_dates()
    cfo_work.init_fin_proj()

#   Set the liability valuation cash flows
    cfo_work.set_base_cash_flow()
    cfo_work.set_base_liab_value(curveType, base_GBP, numOfLoB, "BBB")
    cfo_work.set_base_liab_summary(numOfLoB)

#   This should go to an economic scenario generator module - an illustration with the base case only
    base_irCurve_USD = IAL_App.createAkitZeroCurve(valDate, curveType, "USD")
    base_irCurve_GBP = IAL_App.load_BMA_Std_Curves(valDate,"GBP",valDate)
   

    cfo_work.fin_proj[t]['Forecast'].run_dashboard_liab_value(valDate, each_date, curveType, numOfLoB, 0 ,liab_spread_beta, IAL_App.KRD_Term, base_irCurve_USD, base_irCurve_GBP, base_GBP)
    cfo_work.fin_proj[t]['Forecast'].set_dashboard_liab_summary(numOfLoB) 



      
#   illustration of how the capital financial object can be used for forecasting purpose with Eric's interview question: "Fibonacci sequence function"
    for t in range(0, cfo_work._proj_t, 1):
        
        each_date = cfo_work.fin_proj[t]['date']

#        cfo_work.fin_proj[t]['Econ_Scen'].update( {'IR_USD' : base_irCurve_USD, 'IR_GBP' : base_irCurve_GBP})

        if t == 0:
            cfo_work.fin_proj[t]['Forecast'].EBS['LT'].cash = 0
#            cfo_work.fin_proj[t]['Forecast'].set_base_cash_flow(valDate, CF_Database, CF_TableName, Step1_Database, PVBE_TableName, bindingScen, numOfLoB, Proj_Year, work_dir, cash_flow_freq)
#            cfo_work.fin_proj[t]['Forecast'].set_base_liab_value(valDate, curveType, base_GBP, numOfLoB, "BBB")
#            cfo_work.fin_proj[t]['Forecast'].set_base_liab_summary(numOfLoB)
            
        elif t == 1:
            cfo_work.fin_proj[t]['Forecast'].EBS['LT'].cash = 1            
        else:
            cfo_work.fin_proj[t]['Forecast'].EBS['LT'].cash = cfo_work.fin_proj[t-1]['Forecast'].EBS['LT'].cash + cfo_work.fin_proj[t-2]['Forecast'].EBS['LT'].cash


#       use the same base line cash flow information for all projections
        cfo_work.fin_proj[t]['Forecast'].liability['base']    = cfo_work._liab_val_base
        cfo_work.fin_proj[t]['Forecast'].liab_summary['base'] = cfo_work._liab_summary_base

            
#       Projections
        cfo_work.fin_proj[t]['Forecast'].run_dashboard_liab_value(valDate, each_date, curveType, numOfLoB, 0 ,liab_spread_beta, IAL_App.KRD_Term, base_irCurve_USD, base_irCurve_GBP, base_GBP)
        cfo_work.fin_proj[t]['Forecast'].set_dashboard_liab_summary(numOfLoB) 
            
        
        print('Projection ' + str(t) + ' is completed' )


    test_results['test'] = cfo_work
    
    
    print('End Projection')
    
    
#%%Example Loading LBA
    
    print('Start LBA loading test')
    
#    timeStart = time.time()
    
    date_start = dt.datetime(2019, 3, 31)
    date_end = dt.datetime(2019, 12, 31)
    freq = 'Q'
    scen = 'BMABASELINETREASPAR'

    
    valDate = cfo_work.get_date_start

    sql_Loading = "SELECT iteration_number FROM cm_input_liability_cashflow_loading WHERE valuation_year = %s and valuation_quarter = %d and scenario = '%s';"  %(valDate.year, valDate.month / 3, scen)
    
    configFile = r'.\redshift_alm.config'
    db_conn_str = db.db_connection_string(configFile)
    redshift_connection_pool = db.connect_redshift(db_conn_str)
    loadin = db.runSQL(sql_Loading, redshift_connection_pool)
    iter_num = loadin[0][0] # iter num and scen are 1-1 mapped
    
    sql_LBA = 'SELECT name, scenario_id, lob_id, proj_period, proj_year, total_net_cashflow, total_net_face_amount, total_premium FROM cm_input_liability_cashflow_annual ' \
          'WHERE valuation_year = %s and valuation_quarter = %d and iteration_number = %d and run_id = %d' \
          ' ORDER BY scenario_id, lob_id, proj_period;' %(valDate.year, valDate.month / 3, iter_num, 0)
    lba = db.runSQL(sql_LBA, redshift_connection_pool)
    lba = pd.DataFrame(lba, columns = ['Name', 'Scenario Id', 'LOB_ID', 'RowNo', 'Row', 'Total net cashflow', 'Total net face amount', 'Total premium'])

#    print('Time used: %.2d' %(timeStart - time.time()))