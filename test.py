# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 09:43:21 2019

@author: seongpar
"""
from datetime import datetime

CF_TableName   = "I_LBA____122018____________00"                  



sql_liab_cf = "SELECT TB_A.Name, TB_A.[Scenario Id], TB_A.LOB_ID, TB_A.RowNo, TB_A.Row, TB_A.[Total net cashflow], TB_A.[Total net face amount], \
              TB_A.[Total premium], TB_A.[Net benefits - death], TB_A.[Net benefits - maturity], TB_A.[Net benefits - annuity], TB_A.[Net - AH benefits], \
              TB_A.[Net benefits - P&C claims], TB_A.[Net benefits - surrender], TB_A.[Total commission], TB_A.[Maintenance expenses], \
              TB_A.[Net premium tax], TB_A.[Net cash dividends], TB_A.[Total Stat Res - Net Res], TB_A.[Total Tax Res - Net Res], \
              TB_A.[UPR], TB_A.[BV asset backing liab], TB_A.[MV asset backing liab], TB_A.[Net investment Income], TB_A.[CFT reserve], \
              TB_A.[Interest maintenance reserve (NAIC)], TB_A.[Accrued Income] FROM " + CF_TableName + " TB_A ORDER BY TB_A.[Scenario Id], TB_A.LOB_ID, TB_A.RowNo;"


os.chdir(work_dir)
dbConn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + CF_Database + r';')
data = pd.read_sql(sql_liab_cf, dbConn)

cashflow = pd.DataFrame(columns=data.columns)

dateTxt = valDate.strftime('%m/%d/%Y')
idx = 2

scen = 0
idx = 1
for idx in range(1, numOfLoB+1, 1):
    if idx < 10:  ### first 10 LOB is interest rate sensitive
        res = data[
            (data['LOB_ID'] == idx) & (data['Scenario Id'] == scen)]
    else:
        res = data[(data['LOB_ID'] == idx) & (data['Scenario Id'] == 0)]

    num = res['Name'].count()
    val_month = datetime.strptime(dateTxt, '%m/%d/%Y').month
    
    if freq == 'Q':
        res['Period'] = pd.date_range(dateTxt, periods=num, freq = freq)
    
    elif freq == 'A':
        if val_month == 12:
            res['Period'] = pd.date_range(dateTxt, periods = num, freq = 'A')    

        else:
            date_current = pd.date_range(dateTxt, periods = 1, freq = 'Q')
            date_annual =  pd.date_range(dateTxt, periods = num - 1, freq = 'A')    
            res['Period'] = date_current.union(date_annual)



        test = date_current.union(date_annual).drop_duplicates()
        
        
        
        zzz.month