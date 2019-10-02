import os
#import math
import pandas as pd
import numpy as np
import pyodbc
import datetime
import Config_BSCR as BSCR_config
#import scipy.optimize
import Lib_Utility as Util
# load akit DLL into python
akit_dir = 'C:/AKit v4.1.0/BIN'
os.sys.path.append(akit_dir)

# =============================================================================
# # load Corp Model Folder DLL into python
# corp_model_dir = 'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code'
# os.sys.path.append(corp_model_dir)
# =============================================================================

import Class_Corp_Model  as Corpclass
import Lib_Market_Akit   as IAL_App
import IALPython3        as IAL
import User_Input_Dic    as UI
import Lib_BSCR_Model    as BSCR
import Config_BSCR       as BSCR_Cofig

tsyCurveDict = {'USD': 'IR.USD.GOVT.NOMINAL.ZERO.BASE',
                'EUR': 'IR.EUR.GOVT.NOMINAL.ZERO.BASE',
                'GBP': 'IR.GBP.GOVT.NOMINAL.ZERO.BASE',
                'JPY': 'IR.JPY.GOVT.NOMINAL.ZERO.BASE',
                'AUD': 'IR.AUD.GOVT.NOMINAL.ZERO.BASE'}

swapCurveDict = {'USD': 'IR.USD.LIBOR.3M.ZERO.BASE',
                 'EUR': 'IR.EUR.EURIBOR.6M.ZERO.BASE',
                 'GBP': 'IR.GBP.LIBOR.6M.ZERO.BASE',
                 'JPY': 'IR.JPY.LIBOR.6M.ZERO.BASE',
                 'AUD': 'IR.AUD.BBSW.6M.ZERO.BASE'}

# Vincent 07/30/2019
def set_SFS_BS(workSFS, SFS_File):
    SFS_BS = UI.SFS_BS(SFS_File)
    
    accounts = ['Agg', 'LT','GI']
    for each_account in accounts:
        workSFS[each_account].cash = SFS_BS[SFS_BS['Ledger'] == 'Cash'][each_account].values[0] * 10 ** 6
        
        workSFS[each_account].short_term_investments = SFS_BS[SFS_BS['Ledger'] == 'Short term investments'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Bonds_AFS              = SFS_BS[SFS_BS['Ledger'] == 'Bonds AFS'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Other_invested_assets  = SFS_BS[SFS_BS['Ledger'] == 'Other invested assets'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Total_investments      = SFS_BS[SFS_BS['Ledger'] == 'Total investments'][each_account].values[0] * 10 ** 6
        
        workSFS[each_account].FWA_Host                    = SFS_BS[SFS_BS['Ledger'] == 'FWA - Host'][each_account].values[0] * 10 ** 6
        workSFS[each_account].FWA_Embedded_derivative     = SFS_BS[SFS_BS['Ledger'] == 'FWA - Embedded derivative'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Total_funds_withheld_assets = SFS_BS[SFS_BS['Ledger'] == 'Total funds withheld assets'][each_account].values[0] * 10 ** 6
        
        workSFS[each_account].Loan_receivable = SFS_BS[SFS_BS['Ledger'] == 'Loan receivable'][each_account].values[0] * 10 ** 6
        workSFS[each_account].DTA             = SFS_BS[SFS_BS['Ledger'] == 'Deferred tax asset'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Other_assets    = SFS_BS[SFS_BS['Ledger'] == 'Other assets'][each_account].values[0] * 10 ** 6        
        workSFS[each_account].Total_assets    = SFS_BS[SFS_BS['Ledger'] == 'Total assets'][each_account].values[0] * 10 ** 6
        
        # Liability 
        workSFS[each_account].Liability_for_unpaid_losses_and_claim_adj_exp = SFS_BS[SFS_BS['Ledger'] == 'Liability for unpaid losses and claim adj. exp'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Unearned_premiums                             = SFS_BS[SFS_BS['Ledger'] == 'Unearned premiums'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Future_policyholders_benefits                 = SFS_BS[SFS_BS['Ledger'] == 'Future policyholders benefits'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Policyholder_contract_deposits                = SFS_BS[SFS_BS['Ledger'] == 'Policyholder contract deposits'][each_account].values[0] * 10 ** 6
        workSFS[each_account].DTL                                           = SFS_BS[SFS_BS['Ledger'] == 'Deferred tax liability'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Current_tax_payable                           = SFS_BS[SFS_BS['Ledger'] == 'Current tax payable'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Amounts_due_to_related_parties_settlement     = SFS_BS[SFS_BS['Ledger'] == 'Amounts due to related parties - settlement'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Amounts_due_to_related_parties_other          = SFS_BS[SFS_BS['Ledger'] == 'Amounts due to related parties - other'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Deferred_gain_on_reinsurance                  = SFS_BS[SFS_BS['Ledger'] == 'Deferred gain on reinsurance'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Other_liabilities                             = SFS_BS[SFS_BS['Ledger'] == 'Other liabilities'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Total_liabilities                             = SFS_BS[SFS_BS['Ledger'] == 'Total liabilities'][each_account].values[0] * 10 ** 6
        
        # Equity
        workSFS[each_account].Common_stock      = SFS_BS[SFS_BS['Ledger'] == 'Common stock'][each_account].values[0] * 10 ** 6
        workSFS[each_account].APIC              = SFS_BS[SFS_BS['Ledger'] == 'APIC'][each_account].values[0] * 10 ** 6
        workSFS[each_account].Retained_earnings = SFS_BS[SFS_BS['Ledger'] == 'Retained earnings'][each_account].values[0] * 10 ** 6
        workSFS[each_account].AOCI              = SFS_BS[SFS_BS['Ledger'] == 'AOCI'][each_account].values[0] * 10 ** 6       
        workSFS[each_account].Total_equity      = SFS_BS[SFS_BS['Ledger'] == 'Total equity'][each_account].values[0] * 10 ** 6
        
        workSFS[each_account].Total_liabilities_and_equity = SFS_BS[SFS_BS['Ledger'] == 'Total liabilities and equity'][each_account].values[0] * 10 ** 6
    
    return workSFS
 
#%%
def gen_liab_CF(dateTxt, scen, database, sql, lobNum, work_dir, freq = 'Q', val_month = 12):

    curr_dir = os.getcwd()
    if database in ['alm', 'cm']:

        if freq == 'Q':
            print("Currently not LBQ is not supported")
            return
    
        if database == 'alm':
            configFile = r'.\redshift_alm.config'
        else:
            configFile = r'.\redshift.config'
        db_conn_str = Util.db_connection_string(configFile)
        redshift_connection_pool = Util.connect_redshift(db_conn_str)
        df = Util.run_SQL('Redshift', sql, redshift_connection_pool)
        data = pd.DataFrame(df, columns = ['Name', 'Scenario Id', 'LOB_ID', 'RowNo', 'Row', 'Total net cashflow', 'Total net face amount', 'Total premium',
                                        'Net benefits - death', 'Net benefits - maturity', 'Net benefits - annuity', 'Net - AH benefits', \
                                        'Net benefits - P&C claims', 'Net benefits - surrender', 'Total commission', 'Maintenance expenses', \
                                        'Net premium tax', 'Net cash dividends', 'Total Stat Res - Net Res', 'Total Tax Res - Net Res', \
                                        'UPR', 'BV asset backing liab', 'MV asset backing liab', 'Net investment Income', 'CFT reserve', \
                                        'Interest maintenance reserve (NAIC)', 'Accrued Income'])
    
    else:
        dbConn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + database + r';')
        data = pd.read_sql(sql, dbConn)
        dbConn.close()

    os.chdir(work_dir)  # To read the GOE file

    cashflow = pd.DataFrame(columns=data.columns)

    for idx in range(1, lobNum+1, 1):
        if idx < 10:  ### first 10 LOB is interest rate sensitive
            res = data[
                (data['LOB_ID'] == idx) & (data['Scenario Id'] == scen)]
        else:
            res = data[(data['LOB_ID'] == idx) & (data['Scenario Id'] == 0)]

        num = res['Name'].count()
        
        if freq == 'Q':
            res['Period'] = pd.date_range(dateTxt, periods=num, freq = freq)
        
        elif freq == 'A':
            if val_month == 12:
                res['Period'] = pd.date_range(dateTxt, periods = num, freq = 'A')    
    
            else:
                date_current = pd.date_range(dateTxt, periods = 1, freq = 'Q')
                date_annual =  pd.date_range(dateTxt, periods = num - 1, freq = 'A')    
                res['Period'] = date_current.union(date_annual)

        cashflow = cashflow.append(res)

    goeFile = pd.ExcelFile('./GOE.xlsx')
    goeData = goeFile.parse('GOE')

    cashflow = cashflow.merge(goeData, how='left', \
                            left_on=['LOB_ID', 'Scenario Id', 'RowNo'], right_on=['LOB_ID', 'Scenario Id', 'RowNo'])
    
    cashflow.fillna(0, inplace=True)
    
    cashflow['aggregate cf'] = cashflow['Total net cashflow'] + cashflow['GOE']
    
    os.chdir(curr_dir)
    # Need currency

    return cashflow[['LOB_ID', 'Scenario Id', 'Period', 'RowNo', 'Total net cashflow', 'GOE', 'aggregate cf', 'Total net face amount', 'Total premium', \
                     'Net benefits - death', 'Net benefits - maturity', 'Net benefits - annuity', 'Net - AH benefits', \
                     'Net benefits - P&C claims', 'Net benefits - surrender', 'Total commission', 'Maintenance expenses', \
                     'Net premium tax', 'Net cash dividends', 'Total Stat Res - Net Res', 'Total Tax Res - Net Res', \
                     'UPR', 'BV asset backing liab', 'MV asset backing liab', 'Net investment Income', 'CFT reserve', \
                     'Interest maintenance reserve (NAIC)', 'Accrued Income', 'Name']]	


def get_liab_cashflow(actual_estimate, valDate, CF_Database, CF_TableName, Step1_Database, PVBE_TableName, bindingScen, numOfLoB, Proj_Year, work_dir, freq, iter_num = 0, runID = 0): ### Vincent 07/02/2019

    # getting liability cash flows
    ### Vincent 07/09/2019: adding [Total net face amount] and [Total premium]
    # getting liability cash flows

    if CF_Database in ['alm', 'cm']:
        sql_liab_cf = 'SELECT name, scenario_id, lob_id, proj_period, proj_year, total_net_cashflow, total_net_face_amount, total_premium, \
                        net_benefits_death, net_benefits_maturity, net_benefits_annuity, net_ah_benefits, net_benefits_pc_claims, net_benefits_surrender, \
                        total_commission, maintenance_expenses, net_premium_tax, net_cash_dividends, total_stat_res_net_res, total_tax_res_net_res, upr, bv_asset_backing_liab, \
                        mv_asset_backing_liab, net_investment_income, cft_reserve, interest_maintenance_reserve_naic, accrued_income FROM cm_input_liability_cashflow_annual \
                        WHERE valuation_year = %s and valuation_quarter = %d and iteration_number = %d and run_id = %d \
                        ORDER BY scenario_id, lob_id, proj_period;' %(valDate.year, valDate.month / 3, iter_num, runID)
        
        cashflow = gen_liab_CF(valDate.strftime('%m/%d/%Y'), bindingScen, CF_Database, sql_liab_cf, numOfLoB, work_dir, freq, valDate.month)

    else:
        sql_liab_cf = "SELECT TB_A.Name, TB_A.[Scenario Id], TB_A.LOB_ID, TB_A.RowNo, TB_A.Row, TB_A.[Total net cashflow], TB_A.[Total net face amount], \
                    TB_A.[Total premium], TB_A.[Net benefits - death], TB_A.[Net benefits - maturity], TB_A.[Net benefits - annuity], TB_A.[Net - AH benefits], \
                    TB_A.[Net benefits - P&C claims], TB_A.[Net benefits - surrender], TB_A.[Total commission], TB_A.[Maintenance expenses], \
                    TB_A.[Net premium tax], TB_A.[Net cash dividends], TB_A.[Total Stat Res - Net Res], TB_A.[Total Tax Res - Net Res], \
                    TB_A.[UPR], TB_A.[BV asset backing liab], TB_A.[MV asset backing liab], TB_A.[Net investment Income], TB_A.[CFT reserve], \
                    TB_A.[Interest maintenance reserve (NAIC)], TB_A.[Accrued Income] FROM " + CF_TableName + " TB_A ORDER BY TB_A.[Scenario Id], TB_A.LOB_ID, TB_A.RowNo;"

        cashflow = gen_liab_CF(valDate.strftime('%m/%d/%Y'), bindingScen, CF_Database, sql_liab_cf, numOfLoB, work_dir, freq, valDate.month)

    if actual_estimate == 'Estimate': ### Vincent 07/02/2019
        # getting technical provision results
        sql_PVBE      = "SELECT * FROM " + PVBE_TableName + " TB_A Where TB_A.O_Year = 0 ORDER BY TB_A.O_LOB_ID;"
        pvbeData      = Util.run_SQL(Step1_Database, sql_PVBE)
        
    calc_liabAnalytics = {}
    
    curr_dir = os.getcwd()
    os.chdir(work_dir)
    LOB_File = pd.ExcelFile('./LOB_Definition.xlsx')
    LOB_Def  = LOB_File.parse()
    os.chdir(curr_dir)

    for idx in range(1, numOfLoB + 1, 1):

        clsLiab = Corpclass.LiabAnalyticsUnit(idx)
        cal_LOB_def = LOB_Def[LOB_Def['LOB ID'] == idx]

        # LOB definition        
        clsLiab.set_LOB_Def('LOB Name',                 cal_LOB_def['LOB Name'].values[0])
        clsLiab.set_LOB_Def('Portfolio Name',           cal_LOB_def['Portfolio Name'].values[0])
        clsLiab.set_LOB_Def('Legal Entities',           cal_LOB_def['Legal Entities'].values[0])
        clsLiab.set_LOB_Def('CIO',                      cal_LOB_def['CIO'].values[0])
        clsLiab.set_LOB_Def('Legacy Segments',          cal_LOB_def['Legacy Segments'].values[0])
        clsLiab.set_LOB_Def('Agg LOB',                  cal_LOB_def['Agg LOB'].values[0])
        clsLiab.set_LOB_Def('BSCR LOB',                 cal_LOB_def['BSCR LOB'].values[0])
        clsLiab.set_LOB_Def('Profit Center',            cal_LOB_def['Profit Center'].values[0])
        clsLiab.set_LOB_Def('Risk Type',                cal_LOB_def['Risk Type'].values[0])
        clsLiab.set_LOB_Def('PC_Life',                  cal_LOB_def['PC_Life'].values[0])
        clsLiab.set_LOB_Def('Currency',                 cal_LOB_def['Currency'].values[0])

        # Load Cash Flows 
        if actual_estimate == 'Estimate': ### Vincent 07/02/2019
            clsLiab.cashflow = cashflow[cashflow['LOB_ID'] == idx]
            
        elif actual_estimate == 'Actual':
            for t in range(0, Proj_Year + 1, 1):
                clsLiab.cashflow[t] = cashflow[cashflow['LOB_ID'] == idx][cashflow['RowNo'] > t]
                clsLiab.cashflow[t] = clsLiab.cashflow[t].reset_index(drop=True)
                              
        if actual_estimate == 'Estimate': ### Vincent 07/02/2019
            # set technical provisions
            clsLiab.PV_BE               = pvbeData[pvbeData['O_LOB_ID'] == idx]['O_PVBE_w_Adj'].values[0]
            clsLiab.risk_margin         = pvbeData[pvbeData['O_LOB_ID'] == idx]['O_Risk_Margin'].values[0]
            clsLiab.technical_provision = pvbeData[pvbeData['O_LOB_ID'] == idx]['O_Tech_Prov'].values[0]

        calc_liabAnalytics[idx] = clsLiab

    return calc_liabAnalytics

#%%

def Set_Liab_Base(valDate, curveType, curr_GBP, numOfLoB, liabAnalytics, rating = "BBB", KRD_Term = IAL_App.KRD_Term, irCurve_USD = 0, irCurve_GBP = 0):
    
    if irCurve_USD == 0:
        irCurve_USD = IAL_App.createAkitZeroCurve(valDate, curveType, "USD")

    if irCurve_GBP == 0:        
        irCurve_GBP = IAL_App.load_BMA_Std_Curves(valDate,"GBP",valDate)
    
#    irCurve_USD = IAL_App.createAkitZeroCurve(valDate, curveType, "USD")
#    irCurve_GBP = IAL_App.load_BMA_Std_Curves(valDate,"GBP",valDate)
    # irCurve_GBP = IAL_App.createAkitZeroCurve(valDate, curveType, "GBP")    
    # CreditCurve = IAL_App.createAkitZeroCurve(valDate, "Credit", "USD", rating)    

    for idx in range(1, numOfLoB + 1, 1):

        clsLiab = liabAnalytics[idx]
        ccy     = clsLiab.get_LOB_Def('Currency')        
        
        if ccy == "GBP":
            irCurve = irCurve_GBP
            ccy_rate = curr_GBP

        else:
            irCurve = irCurve_USD
            ccy_rate = 1.0

        cf_idx   = clsLiab.cashflow
        cfHandle = IAL.CF.createSimpleCFs(cf_idx["Period"],cf_idx["aggregate cf"])

        oas      = IAL.CF.OAS(cfHandle, irCurve, valDate, -clsLiab.PV_BE/ccy_rate)
        effDur   = IAL.CF.effDur(cfHandle, irCurve, valDate, oas)
        ytm      = IAL.CF.YTM(cfHandle, -clsLiab.PV_BE/ccy_rate, valDate)
        conv     = IAL.CF.effCvx(cfHandle, irCurve, valDate, oas)
        # ir_rate  = irCurve.zeroRate(effDur * 365)
        # credit_rate  = CreditCurve.zeroRate(effDur * 365)

        clsLiab.duration  = effDur
        clsLiab.YTM       = ytm
        clsLiab.convexity = conv
        clsLiab.OAS       = oas
        clsLiab.ccy_rate  = ccy_rate
        
        for key, value in KRD_Term.items():
            KRD_name        = "KRD_" + key
            clsLiab.set_KRD_value(KRD_name, IAL.CF.keyRateDur(cfHandle, irCurve, valDate, key, oas))
        # clsLiab.set_liab_value('IR_Rate', ir_rate )
        # clsLiab.set_liab_value('Credit_Rate', credit_rate)
        # clsLiab.set_liab_value('Credit_Spread', (credit_rate - ir_rate)*10000)
                    
        # print('LOB:', idx, 'Dur:',clsLiab.get_liab_value('Effective Duration') )

        liabAnalytics[idx] = clsLiab
        
    return liabAnalytics


def Run_Liab_DashBoard(valDate, EBS_Calc_Date, curveType, numOfLoB, baseLiabAnalytics, market_factor, liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term, irCurve_USD = 0, irCurve_GBP = 0, gbp_rate = 0, BSCR_PC_group = BSCR_config.PC_BSCR_Group, BSCR_PC_RSV_Map = BSCR_config.PC_Reserve_mapping ):
   
    if irCurve_USD == 0:
        irCurve_USD = IAL_App.createAkitZeroCurve(EBS_Calc_Date, curveType, "USD")

    if irCurve_GBP == 0:        
        irCurve_GBP = IAL_App.load_BMA_Std_Curves(valDate,"GBP",EBS_Calc_Date)
#    irCurve_GBP = IAL_App.createAkitZeroCurve(valDate, curveType, "GBP")    

#    zzzzzzzzzzzzzzzzzzzzzzzz for liability Attribution Analysis zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
#    irCurve_USD_rollforward = IAL_App.createAkitZeroCurve(valDate, curveType, "USD", "BBB", "Y", EBS_Calc_Date)
#    irCurve_GBP_rollforward = IAL_App.load_BMA_Std_Curves(valDate,"GBP",valDate, "Y", EBS_Calc_Date)
    if len(market_factor) == 0:
        liab_spread_change   = 0
        ccy_rate_ebs         = gbp_rate

    else:
        credit_spread_base   = market_factor[(market_factor['val_date'] == valDate)].Credit_Spread.values[0]
        credit_spread_ebs    = market_factor[(market_factor['val_date'] == EBS_Calc_Date)].Credit_Spread.values[0]
        credit_spread_change = credit_spread_ebs - credit_spread_base  
        liab_spread_change   = credit_spread_change * liab_spread_beta
        ccy_rate_ebs         = market_factor[(market_factor['val_date'] == EBS_Calc_Date)].GBP.values[0]
    
    calc_liabAnalytics = {}
    for idx in range(1, numOfLoB + 1, 1):
        
        base_liab = baseLiabAnalytics[idx]
        clsLiab = Corpclass.LiabAnalyticsUnit(idx)
        clsLiab.LOB_Def = base_liab.LOB_Def
        clsLiab.cashflow = base_liab.cashflow
        clsLiab.ccy_rate = base_liab.ccy_rate

        ccy       = clsLiab.get_LOB_Def('Currency')        
#        ccy_rate  = clsLiab.ccy_rate                
        
        if ccy == "GBP":
            irCurve            = irCurve_GBP
            ccy_rate_dashboard = ccy_rate_ebs

        else:
            irCurve            = irCurve_USD
            ccy_rate_dashboard = 1.0
        
        cf_idx   = clsLiab.cashflow
        cfHandle = IAL.CF.createSimpleCFs(cf_idx["Period"],cf_idx["aggregate cf"])
        oas      = base_liab.OAS  + liab_spread_change
        
        Net_CF     = cf_idx.loc[cf_idx["Period"] == EBS_Calc_Date, ["aggregate cf"]].sum()
        Net_CF_val = Net_CF["aggregate cf"]

        pvbe     = IAL.CF.PVFromCurve(cfHandle, irCurve, EBS_Calc_Date, oas)
        effDur   = IAL.CF.effDur(cfHandle, irCurve, EBS_Calc_Date, oas)
        ytm      = IAL.CF.YTM(cfHandle, pvbe, EBS_Calc_Date)
        conv     = IAL.CF.effCvx(cfHandle, irCurve, EBS_Calc_Date, oas)

#        date_30y = IAL.Util.addTerms(EBS_Calc_Date, "30M")
#        cf_idx_30y = np.where((cf_idx['Period'] <= xxx))
        
        clsLiab.PV_BE     = -pvbe * ccy_rate_dashboard
        clsLiab.net_cf    = -Net_CF_val * ccy_rate_dashboard
        clsLiab.PV_BE_net = clsLiab.PV_BE - clsLiab.net_cf 
        clsLiab.duration  = effDur
        clsLiab.YTM       = ytm
        clsLiab.convexity = conv
        clsLiab.OAS       = oas
        clsLiab.ccy_rate  = ccy_rate_dashboard
        clsLiab.risk_margin = clsLiab.PV_BE * base_liab.risk_margin / base_liab.PV_BE
        clsLiab.technical_provision = clsLiab.PV_BE + clsLiab.risk_margin
        
        for key, value in KRD_Term.items():
            KRD_name        = "KRD_" + key
            clsLiab.set_KRD_value(KRD_name, IAL.CF.keyRateDur(cfHandle, irCurve, EBS_Calc_Date, key, oas))

        BSCR_LOB = clsLiab.LOB_Def['Agg LOB']
        
        for each_group in BSCR_PC_group:
#            print ('idx = ' + str(idx) + 'group ' + each_group)

            if BSCR_LOB == "PC":
                reserve_split = BSCR_PC_RSV_Map[idx][each_group]
                clsLiab.PC_PVBE_BSCR.update( { each_group : clsLiab.PV_BE_net * reserve_split } ) 
            else:
                clsLiab.PC_PVBE_BSCR.update( { each_group : 0 } )

        calc_liabAnalytics[idx] = clsLiab
        
    return calc_liabAnalytics

# output key results
def exportLobAnalytics(liabAnalytics, outFileName, work_dir, valDate, EBS_Calc_Date):

    colNames =['Eval_Date', 'Liab_Base_Date', 'LOB', 'PVBE',"Risk_Margin", "TP", 'Eff Duration', 'OAS', 'Convexity', 'YTM', 'PVBE_Reporting_Currency', 'PVBE_Local_Currency', 'Local_Currency', 'CCY_Rate']
    output = pd.DataFrame([],columns = colNames)

    for key, val in liabAnalytics.items():
        print('Exporting - ', key)
        output = output.append(pd.DataFrame([[EBS_Calc_Date.strftime('%Y%m%d'), valDate.strftime('%Y%m%d'), key, val.PV_BE,val.risk_margin, val.technical_provision, val.duration, val.OAS, val.convexity, val.YTM, val.PV_BE, val.PV_BE/val.ccy_rate, val.LOB_Def['Currency'], val.ccy_rate]], columns = colNames), ignore_index = True)

    curr_dir = os.getcwd()
    os.chdir(work_dir)
    outputWriter = pd.ExcelWriter(outFileName)
    output.to_excel(outputWriter, sheet_name= 'EBS_Dashboard', index=False)
    outputWriter.save()
    os.chdir(curr_dir)

#output PVBE time zero and projection
def exportLobAnalytics_proj(cfo, outFileName, work_dir):

    colNames = ['Date','LOB','PVBE']
    output = pd.DataFrame([],columns = colNames)
    
    for k in cfo.fin_proj:
        liab = cfo.fin_proj[k]['Forecast'].EBS
        date = cfo.fin_proj[k]['date']
        
        for key, val in liab.items():
            output = output.append(pd.DataFrame([[date, key, val.PV_BE]], columns = colNames), ignore_index = True)

    curr_dir = os.getcwd()
    os.chdir(work_dir)
    outputWriter = pd.ExcelWriter(outFileName)
    output.to_excel(outputWriter, sheet_name= 'EBS_Dashboard', index=False)
    outputWriter.save()
    os.chdir(curr_dir)

def get_asset_holding(valDate, work_dir):

    curr_dir = os.getcwd()
    os.chdir(work_dir)
    asset_holding_File = pd.ExcelFile('./Asset_Holding.xlsx')
    asset_holding_data  = asset_holding_File.parse()
    asset_holding_data.fillna(0, inplace=True)    
    os.chdir(curr_dir)
    
    calc_assetAnalytics = {}
    
    work_assetAnalytics = Corpclass.AssetAnalytics()
    work_assetAnalytics.set_asset_value('holding_date', valDate)
    work_assetAnalytics.set_asset_value('asset_holding', asset_holding_data)
    
    
    calc_assetAnalytics['base'] = work_assetAnalytics
    
    return calc_assetAnalytics

def Run_Asset_DashBoard(valDate, EBS_Calc_Date, calc_assetAnalytics, market_factor, KRD_Term = IAL_App.KRD_Term):

    work_assetAnalytics = Corpclass.AssetAnalytics()
    asset_base          = calc_assetAnalytics['base'].get_asset_value('asset_holding')
    work_assetAnalytics.set_asset_value('EBS_date', EBS_Calc_Date)
    work_assetAnalytics.set_asset_value('asset_holding', asset_base)
    calc_assetAnalytics['DashBoard'] = work_assetAnalytics

    asset_ebs   = calc_assetAnalytics['DashBoard'].get_asset_value('asset_holding')
    asset_count = asset_ebs.shape[0]  
    ebs_assetAnalytics = Corpclass.AssetAnalytics()
    
    ebs_KRD_MV_change         = []
    ebs_IR_Conv_MV_Change     = []
    ebs_spread_dur_MV_Change  = []
    ebs_spread_conv_MV_Change = []
    ebs_MV_change_tot         = []
    ebs_MV                    = []

    for idx in range(0, asset_count, 1):
        
        KRD_MV_change = 0
        
        # Key rate change sum
        for key, value in KRD_Term.items():
            IR_key_name     = "IR_"  + key
            KRD_name        = "KRD " + key
            key_rate_change = market_factor[(market_factor['val_date'] == EBS_Calc_Date)][IR_key_name].values[0] - market_factor[(market_factor['val_date'] == valDate)][IR_key_name].values[0]
            KRD             = asset_ebs.loc[[idx]][KRD_name].values[0]
            KRD_MV_change   += key_rate_change * KRD
        
        IR_change_bps        = (market_factor[(market_factor['val_date'] == EBS_Calc_Date)]['IR'].values[0] - market_factor[(market_factor['val_date'] == valDate)]['IR'].values[0])*10000
        calc_IR_convexity    = asset_ebs.loc[[idx]]['Effective Convexity'].values[0]
        IR_Conv_MV_Change    = 1/2 * calc_IR_convexity * IR_change_bps * IR_change_bps /1000000


        spread_change_bps     = (market_factor[(market_factor['val_date'] == EBS_Calc_Date)]['Credit_Spread'].values[0] - market_factor[(market_factor['val_date'] == valDate)]['Credit_Spread'].values[0])*10000
        calc_spread_duration  = asset_ebs.loc[[idx]]['Spread Duration'].values[0]
        spread_dur_MV_Change  = spread_change_bps / 10000 * calc_spread_duration
        
        calc_spread_convexity = asset_ebs.loc[[idx]]['Spread Convexity'].values[0]
        spread_conv_MV_Change  = 1/2 * calc_spread_convexity * spread_change_bps * spread_change_bps /1000000
        
        ebs_KRD_MV_change.append(-asset_ebs.loc[[idx]]['Market Value with Accrued Int USD GAAP'].values[0] * KRD_MV_change)
        ebs_IR_Conv_MV_Change.append(asset_ebs.loc[[idx]]['Market Value with Accrued Int USD GAAP'].values[0] * IR_Conv_MV_Change)
        ebs_spread_dur_MV_Change.append(-asset_ebs.loc[[idx]]['Market Value with Accrued Int USD GAAP'].values[0] * spread_dur_MV_Change)
        ebs_spread_conv_MV_Change.append(asset_ebs.loc[[idx]]['Market Value with Accrued Int USD GAAP'].values[0] * spread_conv_MV_Change)
        ebs_MV_change_tot.append(asset_ebs.loc[[idx]]['Market Value with Accrued Int USD GAAP'].values[0] * (-KRD_MV_change + IR_Conv_MV_Change - spread_dur_MV_Change + spread_conv_MV_Change))        
        ebs_MV.append(asset_ebs.loc[[idx]]['Market Value with Accrued Int USD GAAP'].values[0] * (1-KRD_MV_change + IR_Conv_MV_Change - spread_dur_MV_Change + spread_conv_MV_Change))

    asset_ebs['MV_Change_IR_KRD']      = ebs_KRD_MV_change
    asset_ebs['MV_Change_IR_Conv']     = ebs_IR_Conv_MV_Change
    asset_ebs['MV_Change_Spread_Dur']  = ebs_spread_dur_MV_Change
    asset_ebs['MV_Change_Spread_Conv'] = ebs_spread_conv_MV_Change
    asset_ebs['MV_Change_Tot']         = ebs_MV_change_tot    
    asset_ebs['MV_EBS']                = ebs_MV
#    asset_ebs.fillna(0, inplace=True)
    
    ebs_assetAnalytics.set_asset_value('EBS_date', EBS_Calc_Date)
    ebs_assetAnalytics.set_asset_value('asset_holding', asset_ebs)
    calc_assetAnalytics['DashBoard'] = ebs_assetAnalytics

    return calc_assetAnalytics
   
   
def run_liab_analytics(valDate, curveType, curr_GBP, numOfLoB, liabAnalytics, rating = "BBB", KRD_Term = IAL_App.KRD_Term):
    
    irCurve_USD = IAL_App.createAkitZeroCurve(valDate, curveType, "USD")
    irCurve_GBP = IAL_App.createAkitZeroCurve(valDate, curveType, "GBP")    
#    CreditCurve = IAL_App.createAkitZeroCurve(valDate, "Credit", "USD", rating)    

    for idx in range(1, numOfLoB + 1, 1):

        clsLiab = liabAnalytics[idx]
        ccy     = clsLiab.get_LOB_Def('Currency')        
        
        if ccy == "GBP":
            irCurve = irCurve_GBP
            ccy_rate = curr_GBP

        else:
            irCurve = irCurve_USD
            ccy_rate = 1.0

        cf_idx   = clsLiab.get_cashflow('Liab Cash Flow')
        cfHandle = IAL.CF.createSimpleCFs(cf_idx["Period"],cf_idx["aggregate cf"]/ccy_rate)

        oas      = IAL.CF.OAS(cfHandle, irCurve, valDate, -clsLiab.get_liab_value('PV_BE')/ccy_rate)
        effDur   = IAL.CF.effDur(cfHandle, irCurve, valDate, oas)
        ytm      = IAL.CF.YTM(cfHandle, -clsLiab.get_liab_value('PV_BE')/ccy_rate, valDate)
        conv     = IAL.CF.effCvx(cfHandle, irCurve, valDate, oas)
#        ir_rate  = irCurve.zeroRate(effDur * 365)
#        credit_rate  = CreditCurve.zeroRate(effDur * 365)

        clsLiab.set_liab_value('Effective Duration', effDur)
        clsLiab.set_liab_value('YTM', ytm)
        clsLiab.set_liab_value('Convexity', conv)
        clsLiab.set_liab_value('OAS', oas)
        clsLiab.set_liab_value('CCY_Rate', ccy_rate)
        
               # Key rate change sum
   
            
#        clsLiab.set_liab_value('IR_Rate', ir_rate )
#        clsLiab.set_liab_value('Credit_Rate', credit_rate)
#        clsLiab.set_liab_value('Credit_Spread', (credit_rate - ir_rate)*10000)
                
#        print('LOB:', idx, 'Dur:',clsLiab.get_liab_value('Effective Duration') )

        liabAnalytics[idx] = clsLiab
        
    return liabAnalytics


def run_EBS_base(valDate, work_EBS, liab_summary, EBS_asset, AssetAdjustment, SFS_BS):
    accounts = ['LT','GI']
    
#    EBS_asset['mv_dur'] = EBS_asset.MV_USD_GAAP * EBS_asset['Effective Duration (WAMV)']
    
    asset_mv_summary     = EBS_asset.groupby(['Fort Re Corp Segment'])['MV_USD_GAAP'].agg('sum')
    asset_mv_dur_summary = EBS_asset.groupby(['Fort Re Corp Segment'])['mv_dur'].agg('sum') 
    asset_mv_acc_int_summary = EBS_asset.groupby(['Fort Re Corp Segment'])['Accrued Int USD GAAP'].agg('sum')
    
    asset_mv_dur_bma_cat_summary  = EBS_asset.groupby(['BMA_Category'])['mv_dur'].agg('sum')
#    Actual_asset_mv_issuer_summary = EBS_asset.groupby(['Issuer Name'])['MV_USD_GAAP'].agg('sum')
    asset_mv_ac_summary = EBS_asset.groupby(['Fort Re Corp Segment','AIG Asset Class 3'])['MV_USD_GAAP'].agg('sum')
        
    asset_adjustment_summary = AssetAdjustment.groupby(['Asset_Adjustment'])['MV_USD_GAAP'].agg('sum')
       
     # surplus alternatives
    alts_mv_summary          = EBS_asset.groupby(['Fort Re Corp Segment','BMA_Asset_Class'])['MV_USD_GAAP'].sum()
    alts_mv_summary_LT       = alts_mv_summary.loc[(['Long Term Surplus'],['Alternatives']),].sum()
    alts_mv_summary_PC       = alts_mv_summary.loc[(['General Surplus'],['Alternatives']),].sum()
    
    # surplus cash
    cash_summary_LT          = asset_mv_ac_summary.loc[(['Long Term Surplus'],['Cash']),].sum() + asset_adjustment_summary['True_up_Cash_LT'].sum()
    cash_summary_PC          = asset_mv_ac_summary.loc[(['General Surplus'],['Cash']),].sum() + asset_adjustment_summary['True_up_Cash_GI'].sum()

    # FWA Alternatives
    alts_ac = ['Alternatives']
    LT_cat  = ['ALBA', 'ModCo']
    GI_cat  = ['LPT']
    LT_otherasset = ['Other Assets - LT','Surplus_AccInt_LT']
    PC_otherasset = ['Other Assets - GI','Surplus_AccInt_GI', 'Loan receivable']
    
    fwa_alts_mv_summary          = EBS_asset.groupby(['Fort Re Corp Segment','BMA_Asset_Class'])['MV_USD_GAAP'].sum()
    fwa_alts_mv_summary_LT       = fwa_alts_mv_summary.loc[(LT_cat, alts_ac),].sum()
    fwa_alts_mv_summary_PC       = fwa_alts_mv_summary.loc[(GI_cat, alts_ac),].sum()

#    # FWA FI
#    fwa_MV_LT           = asset_mv_summary['ALBA'] + asset_mv_summary['LR ModCo']
#    fwa_MV_FI_LT        = fwa_MV_LT - fwa_alts_mv_summary_LT
#    
#    fwa_MV_PC           = asset_mv_summary['PC LPT']
#    fwa_MV_FI_PC        = fwa_MV_PC - fwa_alts_mv_summary_PC
    
    # surplus FI
    fixed_inv_surplus_LT = asset_mv_summary['Long Term Surplus'] - alts_mv_summary_LT - cash_summary_LT + asset_adjustment_summary['True_up_Surplus_LT'].sum() + asset_adjustment_summary['True_up_Cash_LT'].sum()
    fixed_inv_surplus_PC = asset_mv_summary['General Surplus'] - alts_mv_summary_PC - cash_summary_PC + asset_adjustment_summary['True_up_Cash_GI'].sum()
    
#    # surplus cash
#    cash_LT              = cash_summary_LT
#    cash_PC              = cash_summary_PC
    
    Other_Assets_LT      = asset_adjustment_summary[LT_otherasset].sum()
    Other_Assets_PC      = asset_adjustment_summary[PC_otherasset].sum()
    
    Actual_derivatives_IR01 = Actual_load_derivatives_IR01(valDate)
    
    for each_account in accounts:
        work_EBS[each_account].PV_BE               = liab_summary[each_account]['PV_BE']
        work_EBS[each_account].risk_margin         = liab_summary[each_account]['risk_margin']
        work_EBS[each_account].technical_provision = liab_summary[each_account]['technical_provision']
        
        if each_account == 'LT':
            work_EBS[each_account].fwa_MV            = asset_mv_summary['ALBA'] + asset_mv_summary['ModCo'] + asset_adjustment_summary['True_up_FWA_LT'].sum()
            work_EBS[each_account].fwa_MV_FI         = work_EBS[each_account].fwa_MV - fwa_alts_mv_summary_LT
            work_EBS[each_account].fwa_MV_alts       = fwa_alts_mv_summary_LT
            
            work_EBS[each_account].fwa_acc_int       = (asset_mv_acc_int_summary['ALBA'] + asset_mv_acc_int_summary['ModCo']) + asset_adjustment_summary['AccInt_IDR_to_IA_LT'].sum()
            work_EBS[each_account].alts_inv_surplus  = alts_mv_summary_LT
            work_EBS[each_account].cash              = cash_summary_LT
            work_EBS[each_account].fixed_inv_surplus = fixed_inv_surplus_LT
            work_EBS[each_account].surplus_asset_acc_int = asset_mv_acc_int_summary['Long Term Surplus'] - asset_mv_summary['Long Term Surplus']


            work_EBS[each_account].fwa_policy_loan       = AssetAdjustment[AssetAdjustment['BMA_Category'] == 'Policy Loan']['MV_USD_GAAP'].values[0]
            work_EBS[each_account].LOC                   = 0
            work_EBS[each_account].LTIC                  = AssetAdjustment[AssetAdjustment['BMA_Category'] == 'LTIC']['MV_USD_GAAP'].values[0]
            work_EBS[each_account].current_tax_payble    = SFS_BS[each_account].Current_tax_payable
            work_EBS[each_account].net_settlement_payble = abs( AssetAdjustment[AssetAdjustment['Asset_Adjustment'] == 'Settlement Payable - LR']['MV_USD_GAAP'].values[0] )
            work_EBS[each_account].amount_due_other      = SFS_BS[each_account].Amounts_due_to_related_parties_other 
            work_EBS[each_account].other_liab            = abs( AssetAdjustment[AssetAdjustment['Asset_Adjustment'] == 'Other Liability - LT']['MV_USD_GAAP'].values[0] )
            work_EBS[each_account].Other_Assets          = Other_Assets_LT
            work_EBS[each_account].acc_int_liab          = work_EBS[each_account].fwa_acc_int - asset_adjustment_summary['AccInt_ALBA'].sum()
            
            FI_Dur_MV = ( work_EBS[each_account].fwa_MV_FI + work_EBS[each_account].fixed_inv_surplus + work_EBS[each_account].cash + work_EBS[each_account].Other_Assets)
            Deriv_Dur = Actual_derivatives_IR01 / (0.0001 * FI_Dur_MV)
            
#            work_EBS[each_account].FI_Dur                = (asset_mv_dur_summary['ALBA'] + asset_mv_dur_summary['ModCo'] + asset_mv_dur_summary['Long Term Surplus']) / (FI_Dur_MV) + Deriv_Dur
            work_EBS[each_account].FI_Dur                = (asset_mv_dur_summary['ALBA'] + asset_mv_dur_summary['ModCo'] + asset_mv_dur_summary['Long Term Surplus'] - asset_mv_dur_bma_cat_summary['ML III']) / (FI_Dur_MV) + Deriv_Dur
            work_EBS[each_account].Derivative_IR01       = Actual_derivatives_IR01
            work_EBS[each_account].Derivative_Dur        = Deriv_Dur
         
        elif each_account == 'GI':
            work_EBS[each_account].fwa_MV                = asset_mv_summary['LPT'] + asset_adjustment_summary['True_up_FWA_GI'].sum()
            work_EBS[each_account].fwa_MV_FI             = work_EBS[each_account].fwa_MV - fwa_alts_mv_summary_PC
            work_EBS[each_account].fwa_MV_alts           = fwa_alts_mv_summary_PC
            
            work_EBS[each_account].fwa_acc_int           = asset_mv_acc_int_summary['LPT'] + asset_adjustment_summary['AccInt_IDR_to_IA_GI'].sum()
            work_EBS[each_account].alts_inv_surplus      = alts_mv_summary_PC
            work_EBS[each_account].cash                  = cash_summary_PC            
            work_EBS[each_account].fixed_inv_surplus     = fixed_inv_surplus_PC
            work_EBS[each_account].surplus_asset_acc_int = asset_mv_acc_int_summary['General Surplus'] - asset_mv_summary['General Surplus']

            work_EBS[each_account].fwa_policy_loan       = 0
            work_EBS[each_account].LOC                   = AssetAdjustment[AssetAdjustment['BMA_Category'] == 'LOC']['MV_USD_GAAP'].values[0]
            work_EBS[each_account].LTIC                  = 0            
            work_EBS[each_account].current_tax_payble    = SFS_BS[each_account].Current_tax_payable        
            work_EBS[each_account].net_settlement_payble = abs( AssetAdjustment[AssetAdjustment['Asset_Adjustment'] == 'Settlement Payable - PC']['MV_USD_GAAP'].values[0] )
            work_EBS[each_account].amount_due_other      = SFS_BS[each_account].Amounts_due_to_related_parties_other
            work_EBS[each_account].other_liab            = abs( AssetAdjustment[AssetAdjustment['Asset_Adjustment'] == 'Other Liability - GI']['MV_USD_GAAP'].values[0] )
            work_EBS[each_account].Other_Assets          = Other_Assets_PC
            work_EBS[each_account].acc_int_liab          = work_EBS[each_account].fwa_acc_int
            
            FI_Dur_MV = ( work_EBS[each_account].fwa_MV_FI + work_EBS[each_account].fixed_inv_surplus + work_EBS[each_account].cash + work_EBS[each_account].Other_Assets)
            Actual_derivatives_IR01 = 0
            Deriv_Dur = Actual_derivatives_IR01 / (0.0001 * FI_Dur_MV)
            work_EBS[each_account].FI_Dur                = (asset_mv_dur_summary['LPT'] + asset_mv_dur_summary['General Surplus']) / (FI_Dur_MV) + Deriv_Dur
            work_EBS[each_account].Derivative_IR01       = 0
            work_EBS[each_account].Derivative_Dur        = Deriv_Dur    
                                            
        # Aggregate Account    
        work_EBS['Agg'].PV_BE                 = work_EBS['LT'].PV_BE + work_EBS['GI'].PV_BE
        work_EBS['Agg'].risk_margin           = work_EBS['LT'].risk_margin + work_EBS['GI'].risk_margin
        work_EBS['Agg'].technical_provision   = work_EBS['LT'].technical_provision + work_EBS['GI'].technical_provision
        work_EBS['Agg'].fwa_MV                = work_EBS['LT'].fwa_MV + work_EBS['GI'].fwa_MV
        work_EBS['Agg'].fwa_MV_FI             = work_EBS['LT'].fwa_MV_FI + work_EBS['GI'].fwa_MV_FI
        work_EBS['Agg'].fwa_MV_alts           = work_EBS['LT'].fwa_MV_alts + work_EBS['GI'].fwa_MV_alts        
        work_EBS['Agg'].fwa_acc_int           = work_EBS['LT'].fwa_acc_int + work_EBS['GI'].fwa_acc_int
        work_EBS['Agg'].alts_inv_surplus      = work_EBS['LT'].alts_inv_surplus + work_EBS['GI'].alts_inv_surplus
        work_EBS['Agg'].cash                  = work_EBS['LT'].cash + work_EBS['GI'].cash        
        work_EBS['Agg'].fixed_inv_surplus     = work_EBS['LT'].fixed_inv_surplus + work_EBS['GI'].fixed_inv_surplus
        work_EBS['Agg'].surplus_asset_acc_int = work_EBS['LT'].surplus_asset_acc_int + work_EBS['GI'].surplus_asset_acc_int
        work_EBS['Agg'].fwa_policy_loan       = work_EBS['LT'].fwa_policy_loan + work_EBS['GI'].fwa_policy_loan
        work_EBS['Agg'].LOC                   = work_EBS['LT'].LOC + work_EBS['GI'].LOC
        work_EBS['Agg'].LTIC                  = work_EBS['LT'].LTIC + work_EBS['GI'].LTIC
        work_EBS['Agg'].current_tax_payble    = work_EBS['LT'].current_tax_payble + work_EBS['GI'].current_tax_payble
        work_EBS['Agg'].net_settlement_payble = work_EBS['LT'].net_settlement_payble + work_EBS['GI'].net_settlement_payble        
        work_EBS['Agg'].amount_due_other      = work_EBS['LT'].amount_due_other + work_EBS['GI'].amount_due_other     
        work_EBS['Agg'].Other_Assets          = work_EBS['LT'].Other_Assets + work_EBS['GI'].Other_Assets 
        work_EBS['Agg'].other_liab            = work_EBS['LT'].other_liab + work_EBS['GI'].other_liab
        work_EBS['Agg'].acc_int_liab          = work_EBS['LT'].acc_int_liab + work_EBS['GI'].acc_int_liab 
        work_EBS['Agg'].FI_Dur                = ((work_EBS['LT'].FI_Dur * (work_EBS['LT'].fwa_MV_FI + work_EBS['LT'].fixed_inv_surplus +  work_EBS['LT'].cash + work_EBS['LT'].Other_Assets )) \
                                              + (work_EBS['GI'].FI_Dur * (work_EBS['GI'].fwa_MV_FI + work_EBS['GI'].fixed_inv_surplus + work_EBS['GI'].cash + work_EBS['GI'].Other_Assets))) \
                                              / (work_EBS['Agg'].fwa_MV_FI + work_EBS['Agg'].fixed_inv_surplus + work_EBS['Agg'].cash + work_EBS['Agg'].Other_Assets )
        
        work_EBS['Agg'].Derivative_IR01       = work_EBS['LT'].Derivative_IR01 + work_EBS['GI'].Derivative_IR01
        work_EBS['Agg'].Derivative_Dur        = ((work_EBS['LT'].Derivative_Dur * (work_EBS['LT'].fwa_MV_FI + work_EBS['LT'].fixed_inv_surplus +  work_EBS['LT'].cash + work_EBS['LT'].Other_Assets )) \
                                              + (work_EBS['GI'].Derivative_Dur * (work_EBS['GI'].fwa_MV_FI + work_EBS['GI'].fixed_inv_surplus + work_EBS['GI'].cash + work_EBS['GI'].Other_Assets))) \
                                              / (work_EBS['Agg'].fwa_MV_FI + work_EBS['Agg'].fixed_inv_surplus + work_EBS['Agg'].cash + work_EBS['Agg'].Other_Assets )
                                                                                                 
    accounts = ['Agg', 'LT','GI']               
    for each_account in accounts:
        # Asset Aggregation    
        work_EBS[each_account].fwa_tot = work_EBS[each_account].fwa_MV \
                                       + work_EBS[each_account].fwa_acc_int \
                                       + work_EBS[each_account].fwa_policy_loan \
                                       + work_EBS[each_account].STAT_security_adj \
                                       + work_EBS[each_account].GAAP_derivative_adj \
                                       + work_EBS[each_account].GAAP_GRE_FMV_adj
                                                   
        work_EBS[each_account].total_invested_assets = work_EBS[each_account].cash \
                                                     + work_EBS[each_account].fixed_inv_surplus \
                                                     + work_EBS[each_account].alts_inv_surplus \
                                                     + work_EBS[each_account].fwa_tot \
                                                     + work_EBS[each_account].Other_Assets
        
        # Liability Aggregation            
        work_EBS[each_account].total_liabilities = work_EBS[each_account].technical_provision \
                                                     + work_EBS[each_account].current_tax_payble \
                                                     + work_EBS[each_account].net_settlement_payble \
                                                     + work_EBS[each_account].amount_due_other \
                                                     + work_EBS[each_account].acc_int_liab \
                                                     + work_EBS[each_account].other_liab

        # ====== DTA Calculations based on SFS - Vincent 07/08/2019 ====== # 
        print('  Calculating ' + each_account + ' DTA ...')                       
        # Pre-tax Surplus               
        EBS_pre_tax_surplus = work_EBS[each_account].cash \
                            + work_EBS[each_account].fixed_inv_surplus \
                            + work_EBS[each_account].alts_inv_surplus \
                            + work_EBS[each_account].fwa_tot \
                            + work_EBS[each_account].Other_Assets \
                            - work_EBS[each_account].total_liabilities
                                                                                       

        
        SFS_pre_tax_surplus = SFS_BS[each_account].Total_assets - SFS_BS[each_account].DTA - SFS_BS[each_account].Total_liabilities
                    
        # EBS DTA = SFS DTA with adjustment
        work_EBS[each_account].DTA_DTL = SFS_BS[each_account].DTA - (EBS_pre_tax_surplus - SFS_pre_tax_surplus) * UI.tax_rate
        # ====== End: DTA Calculations ====== #
        
        work_EBS[each_account].total_assets = work_EBS[each_account].cash \
                                            + work_EBS[each_account].net_settlement_receivable \
                                            + work_EBS[each_account].fixed_inv_surplus \
                                            + work_EBS[each_account].alts_inv_surplus \
                                            + work_EBS[each_account].fwa_tot \
                                            + work_EBS[each_account].DTA_DTL \
                                            + work_EBS[each_account].LOC \
                                            + work_EBS[each_account].LTIC \
                                            + work_EBS[each_account].Other_Assets    

        work_EBS[each_account].total_assets_excl_LOCs = work_EBS[each_account].total_assets - work_EBS[each_account].LOC                                                 
        work_EBS[each_account].capital_surplus = work_EBS[each_account].total_assets - work_EBS[each_account].total_liabilities   
        work_EBS[each_account].tot_liab_econ_capital_surplus = work_EBS[each_account].capital_surplus + work_EBS[each_account].total_liabilities                                                                                                        
        
    return work_EBS
    

def run_EBS_dashboard(evalDate, re_valDate, work_EBS, asset_holding, liab_summary, numOfLoB, market_factor):
   
#    liab_summary = summary_liab_analytics(dbLiabAnalytics, numOfLoB)
    accounts                 = ['LT','GI']

    asset_mv_summary         = asset_holding.groupby(['Category'])['mv_adj'].agg('sum')
    asset_mv_dur_summary     = asset_holding.groupby(['Category'])['mv_dur'].agg('sum')   
    asset_mv_acc_int_summary = asset_holding.groupby(['Category'])['mv_acc_int_adj'].agg('sum')    

    alts_mv_summary          = asset_holding.groupby(['Category','AIG Asset Class 3'])['mv_adj'].sum()
    alts_mv_summary_LT       = alts_mv_summary.loc[(['Long Term Surplus'],['ML-III B-Notes','Private Equity Fund']),].sum()
    
    alts_mv_summary_PC       = alts_mv_summary.loc[(['General Surplus'],['ML-III B-Notes','Private Equity Fund']),].sum()
    cash_summary_LT          = alts_mv_summary.loc[(['Long Term Surplus'],['Cash', 'Cash Fund']),].sum() # + UI.EBS_Inputs[evalDate]['LT']['True_up_Cash_LT']
    cash_summary_PC          = alts_mv_summary.loc[(['General Surplus'],['Cash', 'Cash Fund']),].sum() # + UI.EBS_Inputs[evalDate]['GI']['True_up_Cash_GI']
    
# Kellie 0529 add asset class into summary to remove MLIII notes from being calculated into FI duration     
    asset_mv_dur_ac_summary     = asset_holding.groupby(['AIG Asset Class 3'])['mv_dur'].agg('sum')
#    asset_mv_dur_alt            = asset_mv_dur_ac_summary['ML-III B-Notes']
    
    alts_ac = ['Hedge Fund', 'Other Invested Assets', 'Private Equity Fund', "Common Equity"]
    LT_cat  = ['ALBA', 'ModCo'] ### Please note: 'LR ModCo' for MicroStrategy asset while 'ModCo' for daily asset hodling
    GI_cat  = ['LPT']

    fwa_alts_mv_summary          = asset_holding.groupby(['Category','AIG Asset Class 3'])['mv_adj'].sum()
    fwa_alts_mv_summary_LT       = fwa_alts_mv_summary.loc[(LT_cat, alts_ac),].sum()
    fwa_alts_mv_summary_PC       = fwa_alts_mv_summary.loc[(GI_cat, alts_ac),].sum()

    surplus_actual_cf = load_surplus_account_cash_flow( evalDate, re_valDate )
    Deriv_val         = load_derivatives_IR01(re_valDate)
    IR01_Deriv        = Deriv_val['IR01_Deriv']
    Init_Margin       = Deriv_val['Init_Margin']

### Vincent update 06/28/2019 - LTIC estimation
    IR_change_bps     = (market_factor[(market_factor['val_date'] == re_valDate)]['IR'].values[0] - market_factor[(market_factor['val_date'] == evalDate)]['IR'].values[0])*10000    
    spread_change_bps = (market_factor[(market_factor['val_date'] == re_valDate)]['Credit_Spread'].values[0] - market_factor[(market_factor['val_date'] == evalDate)]['Credit_Spread'].values[0])
    total_change_bps  = IR_change_bps + spread_change_bps
        
   
    for each_account in accounts:
        work_EBS[each_account].PV_BE               = liab_summary[each_account]['PV_BE']
        work_EBS[each_account].risk_margin         = liab_summary[each_account]['risk_margin']
        work_EBS[each_account].technical_provision = liab_summary[each_account]['technical_provision']
        
        if each_account == 'LT':
            work_EBS[each_account].fwa_MV           = asset_mv_summary['ALBA'] + asset_mv_summary['ModCo'] + \
                                                      UI.EBS_Inputs[evalDate][each_account]['True_up_FWA_LT'] * (re_valDate < UI.EBS_Inputs[evalDate][each_account]['Repo_Paid_Date'])
                                                      
            work_EBS[each_account].fwa_MV_FI        = work_EBS[each_account].fwa_MV - fwa_alts_mv_summary_LT
            work_EBS[each_account].fwa_MV_alts      = fwa_alts_mv_summary_LT
            
            work_EBS[each_account].fwa_acc_int      = (asset_mv_acc_int_summary['ALBA'] + asset_mv_acc_int_summary['ModCo']) - (asset_mv_summary['ALBA'] + asset_mv_summary['ModCo']) + UI.EBS_Inputs[evalDate][each_account]['AccInt_IDR_to_IA']
            ALBA_acc_int = asset_mv_acc_int_summary['ALBA'] - asset_mv_summary['ALBA']
            
            work_EBS[each_account].alts_inv_surplus = alts_mv_summary_LT
            work_EBS[each_account].cash             = cash_summary_LT
            
            work_EBS[each_account].fixed_inv_surplus = asset_mv_summary['Long Term Surplus'] - alts_mv_summary_LT - cash_summary_LT
                                                       # UI.EBS_Inputs[evalDate]['LT']['True_up_Cash_LT']
                                                       
            work_EBS[each_account].surplus_asset_acc_int = asset_mv_acc_int_summary['Long Term Surplus'] - asset_mv_summary['Long Term Surplus']
            
            work_EBS[each_account].fwa_policy_loan       = UI.EBS_Inputs[evalDate][each_account]['Policy_Loan']
            work_EBS[each_account].LOC                   = UI.EBS_Inputs[evalDate][each_account]['LOC']
            work_EBS[each_account].LTIC                  = min(UI.EBS_Inputs[evalDate][each_account]['LTIC'] + UI.EBS_Inputs[evalDate][each_account]['LTIC_dur'] * total_change_bps * 1000000, UI.EBS_Inputs[evalDate][each_account]['LTIC_cap']) ### Vincent update 06/28/2019 - Read from UI
            work_EBS[each_account].current_tax_payble    = UI.EBS_Inputs[evalDate][each_account]['Tax_payable'] - surplus_actual_cf[each_account]['actual_tax']
            work_EBS[each_account].ALBA_Adjustment       = UI.ALBA_adj
            
            net_settlement_date = UI.EBS_Inputs[evalDate][each_account]['Settlement_Date']
            if re_valDate >= net_settlement_date:
                unsettled = 0
            else:
                unsettled = 1
            
            work_EBS[each_account].net_settlement_payble = ( UI.EBS_Inputs[evalDate][each_account]['Settlement_payable'] - surplus_actual_cf[each_account]['actual_settlement']) * unsettled

#            5/29/2019 SWP: Incorporate actual cash flows from surplus account
            work_EBS[each_account].amount_due_other      = UI.EBS_Inputs[evalDate][each_account]['GOE'] - surplus_actual_cf[each_account]['actual_expense'] 
            work_EBS[each_account].other_assets_adj      = UI.EBS_Inputs[evalDate][each_account]['other_assets_adj'] + Init_Margin ### Vincent update 05/27/2019
            work_EBS[each_account].Other_Assets          = work_EBS[each_account].surplus_asset_acc_int + work_EBS[each_account].other_assets_adj
            work_EBS[each_account].other_liab            = UI.EBS_Inputs[evalDate][each_account]['other_liabilities'] ### Vincent update 05/27/2019
            
#            6/3/2019 SWP: added derivative druation column
            FI_Dur_MV = ( work_EBS[each_account].fwa_MV_FI + work_EBS[each_account].fixed_inv_surplus + work_EBS[each_account].cash + work_EBS[each_account].Other_Assets)
            Deriv_Dur = IR01_Deriv / (0.0001 * FI_Dur_MV)
            
            work_EBS[each_account].FI_Dur                = (asset_mv_dur_summary['ALBA'] + asset_mv_dur_summary['ModCo'] + asset_mv_dur_summary['Long Term Surplus'] - asset_mv_dur_ac_summary['ML-III B-Notes']) / (FI_Dur_MV) + Deriv_Dur
            work_EBS[each_account].Derivative_IR01       = IR01_Deriv
            work_EBS[each_account].Derivative_Dur        = Deriv_Dur
                                                            
#                                                            + UI.EBS_Inputs[evalDate][each_account]['Derivative_Dur']
# Kellie 0529: FI duration to remove MLIII duration, and take into account exposure in cash in surplus account and other assets          
        elif each_account == 'GI':
            work_EBS[each_account].fwa_MV                = asset_mv_summary['LPT'] + \
                                                           UI.EBS_Inputs[evalDate][each_account]['True_up_FWA_GI'] * (re_valDate < UI.EBS_Inputs[evalDate][each_account]['Repo_Paid_Date'])
                                                                                                                     
            work_EBS[each_account].fwa_MV_FI        = work_EBS[each_account].fwa_MV - fwa_alts_mv_summary_PC
            work_EBS[each_account].fwa_MV_alts      = fwa_alts_mv_summary_PC
            work_EBS[each_account].fwa_acc_int           = asset_mv_acc_int_summary['LPT'] - asset_mv_summary['LPT'] + UI.EBS_Inputs[evalDate][each_account]['AccInt_IDR_to_IA']
            work_EBS[each_account].alts_inv_surplus      = alts_mv_summary_PC
            work_EBS[each_account].cash                  = cash_summary_PC 
            
            work_EBS[each_account].fixed_inv_surplus = asset_mv_summary['General Surplus'] - alts_mv_summary_PC - cash_summary_PC
                                                      # UI.EBS_Inputs[evalDate]['GI']['True_up_Cash_GI']
                                                                                                              
            work_EBS[each_account].surplus_asset_acc_int = asset_mv_acc_int_summary['General Surplus'] - asset_mv_summary['General Surplus']

            work_EBS[each_account].fwa_policy_loan      = UI.EBS_Inputs[evalDate][each_account]['Policy_Loan']
            work_EBS[each_account].LOC                   = UI.EBS_Inputs[evalDate][each_account]['LOC']
            work_EBS[each_account].LTIC                  = min(UI.EBS_Inputs[evalDate][each_account]['LTIC'] + UI.EBS_Inputs[evalDate][each_account]['LTIC_dur'] * total_change_bps * 1000000, UI.EBS_Inputs[evalDate][each_account]['LTIC_cap']) ### Should be 0 for PC. Vincent update 06/28/2019 - Read from UI
#            5/29/2019 SWP: Incorporate actual cash flows from surplus account            
            work_EBS[each_account].current_tax_payble    = UI.EBS_Inputs[evalDate][each_account]['Tax_payable'] - surplus_actual_cf[each_account]['actual_tax']
            work_EBS[each_account].ALBA_Adjustment       = 0
            
            net_settlement_date = UI.EBS_Inputs[evalDate][each_account]['Settlement_Date']
            if re_valDate >= net_settlement_date:
                unsettled = 0
            else:
                unsettled = 1
            
            work_EBS[each_account].net_settlement_payble = ( UI.EBS_Inputs[evalDate][each_account]['Settlement_payable'] - surplus_actual_cf[each_account]['actual_settlement']) * unsettled
            work_EBS[each_account].amount_due_other      = UI.EBS_Inputs[evalDate][each_account]['GOE'] - surplus_actual_cf[each_account]['actual_expense'] 
            work_EBS[each_account].other_assets_adj      = UI.EBS_Inputs[evalDate][each_account]['other_assets_adj'] ### Vincent update 05/27/2019
            work_EBS[each_account].Other_Assets          = work_EBS[each_account].surplus_asset_acc_int + work_EBS[each_account].other_assets_adj
            work_EBS[each_account].other_liab            = UI.EBS_Inputs[evalDate][each_account]['other_liabilities'] ### Vincent update 05/27/2019

#            6/3/2019 SWP: added derivative druation column
            FI_Dur_MV = ( work_EBS[each_account].fwa_MV_FI + work_EBS[each_account].fixed_inv_surplus + work_EBS[each_account].cash + work_EBS[each_account].Other_Assets)
            IR01_Deriv = 0
            Deriv_Dur = IR01_Deriv / (0.0001 * FI_Dur_MV)
            work_EBS[each_account].FI_Dur                = (asset_mv_dur_summary['LPT'] + asset_mv_dur_summary['General Surplus']) / (FI_Dur_MV) + Deriv_Dur
            work_EBS[each_account].Derivative_IR01       = 0
            work_EBS[each_account].Derivative_Dur        = Deriv_Dur

# Kellie 0529: FI duration to take into account cash in surplus account and other assets    
                                            
    # Aggregate Account    
    work_EBS['Agg'].PV_BE                 = work_EBS['LT'].PV_BE + work_EBS['GI'].PV_BE
    work_EBS['Agg'].risk_margin           = work_EBS['LT'].risk_margin + work_EBS['GI'].risk_margin
    work_EBS['Agg'].technical_provision   = work_EBS['LT'].technical_provision + work_EBS['GI'].technical_provision
    work_EBS['Agg'].fwa_MV                = work_EBS['LT'].fwa_MV + work_EBS['GI'].fwa_MV
    work_EBS['Agg'].fwa_MV_FI             = work_EBS['LT'].fwa_MV_FI + work_EBS['GI'].fwa_MV_FI
    work_EBS['Agg'].fwa_MV_alts           = work_EBS['LT'].fwa_MV_alts + work_EBS['GI'].fwa_MV_alts        
    work_EBS['Agg'].fwa_acc_int           = work_EBS['LT'].fwa_acc_int + work_EBS['GI'].fwa_acc_int
    work_EBS['Agg'].alts_inv_surplus      = work_EBS['LT'].alts_inv_surplus + work_EBS['GI'].alts_inv_surplus
    work_EBS['Agg'].cash                  = work_EBS['LT'].cash + work_EBS['GI'].cash        
    work_EBS['Agg'].fixed_inv_surplus     = work_EBS['LT'].fixed_inv_surplus + work_EBS['GI'].fixed_inv_surplus
    work_EBS['Agg'].surplus_asset_acc_int = work_EBS['LT'].surplus_asset_acc_int + work_EBS['GI'].surplus_asset_acc_int
    work_EBS['Agg'].fwa_policy_loan       = work_EBS['LT'].fwa_policy_loan + work_EBS['GI'].fwa_policy_loan
    work_EBS['Agg'].LOC                   = work_EBS['LT'].LOC + work_EBS['GI'].LOC
    work_EBS['Agg'].LTIC                  = work_EBS['LT'].LTIC + work_EBS['GI'].LTIC
    work_EBS['Agg'].current_tax_payble    = work_EBS['LT'].current_tax_payble + work_EBS['GI'].current_tax_payble
    work_EBS['Agg'].ALBA_Adjustment       = work_EBS['LT'].ALBA_Adjustment + work_EBS['GI'].ALBA_Adjustment 
    work_EBS['Agg'].net_settlement_payble = work_EBS['LT'].net_settlement_payble + work_EBS['GI'].net_settlement_payble        
    work_EBS['Agg'].amount_due_other      = work_EBS['LT'].amount_due_other + work_EBS['GI'].amount_due_other     
    work_EBS['Agg'].other_assets_adj      = work_EBS['LT'].other_assets_adj + work_EBS['GI'].other_assets_adj ### Vincent update 05/27/2019
    work_EBS['Agg'].Other_Assets          = work_EBS['LT'].Other_Assets + work_EBS['GI'].Other_Assets 
    work_EBS['Agg'].other_liab            = work_EBS['LT'].other_liab + work_EBS['GI'].other_liab ### Vincent update 05/27/2019
    work_EBS['Agg'].FI_Dur                = ((work_EBS['LT'].FI_Dur * (work_EBS['LT'].fwa_MV_FI + work_EBS['LT'].fixed_inv_surplus +  work_EBS['LT'].cash + work_EBS['LT'].Other_Assets )) \
                                          + (work_EBS['GI'].FI_Dur * (work_EBS['GI'].fwa_MV_FI + work_EBS['GI'].fixed_inv_surplus + work_EBS['GI'].cash + work_EBS['GI'].Other_Assets))) \
                                          / (work_EBS['Agg'].fwa_MV_FI + work_EBS['Agg'].fixed_inv_surplus + work_EBS['Agg'].cash + work_EBS['Agg'].Other_Assets )
                   
#   6/3/2019 SWP: added derivative druation column
    work_EBS['Agg'].Derivative_IR01       = work_EBS['LT'].Derivative_IR01 + work_EBS['GI'].Derivative_IR01
    work_EBS['Agg'].Derivative_Dur        = ((work_EBS['LT'].Derivative_Dur * (work_EBS['LT'].fwa_MV_FI + work_EBS['LT'].fixed_inv_surplus +  work_EBS['LT'].cash + work_EBS['LT'].Other_Assets )) \
                                          + (work_EBS['GI'].Derivative_Dur * (work_EBS['GI'].fwa_MV_FI + work_EBS['GI'].fixed_inv_surplus + work_EBS['GI'].cash + work_EBS['GI'].Other_Assets))) \
                                          / (work_EBS['Agg'].fwa_MV_FI + work_EBS['Agg'].fixed_inv_surplus + work_EBS['Agg'].cash + work_EBS['Agg'].Other_Assets )
                                                                                        
# Kellie 0529: FI duration to take into account cash in surplus account and other assets         
    accounts = ['Agg', 'LT','GI']
                    
    for each_account in accounts:
            work_EBS[each_account].fwa_tot = work_EBS[each_account].fwa_MV \
                                           + work_EBS[each_account].fwa_acc_int \
                                           + work_EBS[each_account].fwa_policy_loan \
                                           + work_EBS[each_account].STAT_security_adj \
                                           + work_EBS[each_account].GAAP_derivative_adj \
                                           + work_EBS[each_account].GAAP_GRE_FMV_adj
                                                      
            work_EBS[each_account].total_invested_assets = work_EBS[each_account].cash \
                                                         + work_EBS[each_account].fixed_inv_surplus \
                                                         + work_EBS[each_account].alts_inv_surplus \
                                                         + work_EBS[each_account].fwa_tot \
                                                         + work_EBS[each_account].Other_Assets ### Vincent update 05/27/2019
            
#            Liability Aggregation            
            work_EBS[each_account].acc_int_liab = work_EBS[each_account].fwa_acc_int - ALBA_acc_int * (each_account in {'LT', 'Agg'} )
            
            work_EBS[each_account].total_liabilities = work_EBS[each_account].technical_provision \
                                                         + work_EBS[each_account].current_tax_payble \
                                                         + work_EBS[each_account].net_settlement_payble \
                                                         + work_EBS[each_account].amount_due_other \
                                                         + work_EBS[each_account].acc_int_liab \
                                                         + work_EBS[each_account].other_liab ### Vincent update 05/27/2019 

            # ====== DTA Calculations ====== # 
#            print('  Calculating ' + each_account + ' DTA ...')

            inv_asset_ex_net_settlement = work_EBS[each_account].total_invested_assets - work_EBS[each_account].net_settlement_payble 
            TP_acc_int                  = work_EBS[each_account].technical_provision + work_EBS[each_account].acc_int_liab + work_EBS[each_account].amount_due_other + work_EBS[each_account].other_liab + work_EBS[each_account].current_tax_payble
            pre_tax_surplus             = inv_asset_ex_net_settlement - TP_acc_int
            
            if each_account == 'Agg':
                pre_tax_surplus_base = UI.EBS_Inputs[evalDate]['LT']['pre_tax_surplus'] + UI.EBS_Inputs[evalDate]['GI']['pre_tax_surplus']
                dta_base             = UI.EBS_Inputs[evalDate]['LT']['DTA'] + UI.EBS_Inputs[evalDate]['GI']['DTA']
            
            else:
                pre_tax_surplus_base        = UI.EBS_Inputs[evalDate][each_account]['pre_tax_surplus']
                dta_base                    = UI.EBS_Inputs[evalDate][each_account]['DTA']
            
            change_in_pre_surpus            = pre_tax_surplus - pre_tax_surplus_base
            tax_impact                      = -change_in_pre_surpus * UI.tax_rate
            
            work_EBS[each_account].DTA_DTL = dta_base + tax_impact
        
            # ====== End: DTA Calculations ====== #
             
            work_EBS[each_account].total_assets = work_EBS[each_account].cash \
                                                + work_EBS[each_account].net_settlement_receivable \
                                                + work_EBS[each_account].fixed_inv_surplus \
                                                + work_EBS[each_account].alts_inv_surplus \
                                                + work_EBS[each_account].fwa_tot \
                                                + work_EBS[each_account].DTA_DTL \
                                                + work_EBS[each_account].LOC \
                                                + work_EBS[each_account].LTIC \
                                                + work_EBS[each_account].Other_Assets    

            work_EBS[each_account].total_assets_excl_LOCs = work_EBS[each_account].total_assets - work_EBS[each_account].LOC                                                 
            work_EBS[each_account].capital_surplus = work_EBS[each_account].total_assets - work_EBS[each_account].total_liabilities   
            work_EBS[each_account].tot_liab_econ_capital_surplus = work_EBS[each_account].capital_surplus + work_EBS[each_account].total_liabilities                                                                                                        
            
    return work_EBS

def summary_liab_analytics(work_liab_analytics, numOfLoB):

    GI_PV_BE       = 0
    GI_risk_margin = 0
    GI_technical_provision   = 0
    GI_PV_BE_Dur   = 0    

    LT_PV_BE       = 0
    LT_risk_margin = 0
    LT_technical_provision   = 0
    LT_PV_BE_Dur   = 0
    
    for idx in range(1, numOfLoB + 1, 1):

        clsLiab    = work_liab_analytics[idx]
        each_lob   = clsLiab.get_LOB_Def('Agg LOB')        
        
        if each_lob == "LR":
            LT_PV_BE               += clsLiab.PV_BE
            LT_risk_margin         += clsLiab.risk_margin
            LT_technical_provision += clsLiab.technical_provision
            LT_PV_BE_Dur           += ( (abs(clsLiab.PV_BE) - (idx == 34) * UI.ALBA_adj ) * clsLiab.duration ) 

        else:
            GI_PV_BE               += clsLiab.PV_BE
            GI_risk_margin         += clsLiab.risk_margin
            GI_technical_provision += clsLiab.technical_provision
            GI_PV_BE_Dur           += ( abs(clsLiab.PV_BE) * clsLiab.duration )

    tot_PV_BE               = GI_PV_BE + LT_PV_BE
    tot_risk_margin         = GI_risk_margin + LT_risk_margin
    tot_technical_provision = GI_technical_provision + LT_technical_provision
    tot_PV_BE_Dur           = ( LT_PV_BE_Dur + GI_PV_BE_Dur)
        
    summary_result = { 'Agg' : {'PV_BE' : abs(tot_PV_BE), 'risk_margin' : abs(tot_risk_margin), 'technical_provision' : abs(tot_technical_provision), 'duration' : tot_PV_BE_Dur / (abs(tot_PV_BE) - UI.ALBA_adj) },
                       'LT'  : {'PV_BE' : abs(LT_PV_BE),  'risk_margin' : abs(LT_risk_margin),  'technical_provision' : abs(LT_technical_provision),  'duration' : LT_PV_BE_Dur / (abs(LT_PV_BE) - UI.ALBA_adj)  },
                       'GI'  : {'PV_BE' : abs(GI_PV_BE),  'risk_margin' : abs(GI_risk_margin),  'technical_provision' : abs(GI_technical_provision),  'duration' : GI_PV_BE_Dur / (abs(GI_PV_BE) )  } }
        
    return summary_result


def Get_BSCR_Base(Step1_Database, BSCRRisk_agg_TableName, BSCRRisk_LR_TableName, BSCRRisk_PC_TableName):

    sql_BSCR            = "SELECT TB_bscr.[O_BSCR_FI],TB_bscr.[O_BSCR_Eq],TB_bscr.[O_BSCR_Interest],TB_bscr.[O_BSCR_Con],TB_bscr.[O_BSCR_Curr],TB_bscr.[O_BSCR_PC],TB_bscr.[O_BSCR_Mort],TB_bscr.[O_BSCR_Morb],TB_bscr.[O_BSCR_Long],TB_bscr.[O_BSCR_Other] FROM " + BSCRRisk_agg_TableName + " TB_bscr Where TB_bscr.O_Year = 0;"
    sql_BSCR_LR         = "SELECT TB_bscr.[O_BSCR_FI],TB_bscr.[O_BSCR_Eq],TB_bscr.[O_BSCR_Interest],TB_bscr.[O_BSCR_Con],TB_bscr.[O_BSCR_Curr],TB_bscr.[O_BSCR_PC],TB_bscr.[O_BSCR_Mort],TB_bscr.[O_BSCR_Morb],TB_bscr.[O_BSCR_Long],TB_bscr.[O_BSCR_Other] FROM " + BSCRRisk_LR_TableName + " TB_bscr Where TB_bscr.O_Year = 0;"
    sql_BSCR_PC         = "SELECT TB_bscr.[O_BSCR_FI],TB_bscr.[O_BSCR_Eq],TB_bscr.[O_BSCR_Interest],TB_bscr.[O_BSCR_Con],TB_bscr.[O_BSCR_Curr],TB_bscr.[O_BSCR_PC],TB_bscr.[O_BSCR_Mort],TB_bscr.[O_BSCR_Morb],TB_bscr.[O_BSCR_Long],TB_bscr.[O_BSCR_Other] FROM " + BSCRRisk_PC_TableName + " TB_bscr Where TB_bscr.O_Year = 0;"
    BSCR_Agg_Data       = Util.run_SQL(Step1_Database, sql_BSCR)
    BSCR_LR_Data        = Util.run_SQL(Step1_Database, sql_BSCR_LR)
    BSCR_PC_Data        = Util.run_SQL(Step1_Database, sql_BSCR_PC)
#    BSCR_Data           = BSCR_Agg_Data.copy()
#    BSCR_Data           = BSCR_Data.append(BSCR_LR_Data).append(BSCR_PC_Data)
#    BSCR_Data.index     = ['Agg','LR','PC']
#    BSCR_accounts       = ['Agg','LR','PC']
    
    return {'Agg' : BSCR_Agg_Data, "LT" : BSCR_LR_Data, "GI" : BSCR_PC_Data }

#Get_BSCR_Base()

def Set_BSCR_Base(BSCR_Base, Step1_Database, BSCRRisk_agg_TableName, BSCRRisk_LR_TableName, BSCRRisk_PC_TableName, Regime):

    calc_BSCR = Get_BSCR_Base(Step1_Database, BSCRRisk_agg_TableName, BSCRRisk_LR_TableName, BSCRRisk_PC_TableName)
    accounts = ['Agg', 'LT','GI']
    OpRiskCharge = BSCR_Cofig.BSCR_Charge['OpRiskCharge']

    for each_account in accounts:
        each_BSCR = calc_BSCR[each_account]
        
        BSCR_Base[each_account].FI_Risk             = each_BSCR.loc[[0]]['O_BSCR_FI'].values[0]
        BSCR_Base[each_account].Equity_Risk         = each_BSCR.loc[[0]]['O_BSCR_Eq'].values[0]
        BSCR_Base[each_account].IR_Risk             = each_BSCR.loc[[0]]['O_BSCR_Interest'].values[0]
        BSCR_Base[each_account].Currency_Risk       = each_BSCR.loc[[0]]['O_BSCR_Curr'].values[0]
        BSCR_Base[each_account].Concentration_Risk  = each_BSCR.loc[[0]]['O_BSCR_Con'].values[0]
        BSCR_Base[each_account].Net_Credit_Risk     = 0
        BSCR_Base[each_account].Premium_Risk        = 0
        BSCR_Base[each_account].Reserve_Risk        = each_BSCR.loc[[0]]['O_BSCR_PC'].values[0]
        BSCR_Base[each_account].Cat_Risk            = 0
        BSCR_Base[each_account].Mortality_Risk      = each_BSCR.loc[[0]]['O_BSCR_Mort'].values[0]
        BSCR_Base[each_account].StopLoss_Risk       = 0
        BSCR_Base[each_account].Riders_Risk         = 0
        BSCR_Base[each_account].Morbidity_Risk      = each_BSCR.loc[[0]]['O_BSCR_Morb'].values[0]
        BSCR_Base[each_account].Longevity_Risk      = each_BSCR.loc[[0]]['O_BSCR_Long'].values[0]
        BSCR_Base[each_account].VA_Guarantee_Risk   = 0
        BSCR_Base[each_account].OtherInsurance_Risk = each_BSCR.loc[[0]]['O_BSCR_Other'].values[0]
#        # For Future Regime, Market Risk and LT Risk are missing.
#        BSCR_Dashboard[each_account].Market_Risk = 
#        BSCR_Dashboard[each_account].LT_Risk = 
        
        BSCR_result = BSCR.BSCR_Aggregate(BSCR_Base[each_account], Regime, OpRiskCharge)

        BSCR_Base[each_account].BSCR_Bef_Correlation  = BSCR_result['BSCR_sum']
        BSCR_Base[each_account].Net_Market_Risk       = BSCR_result['BSCR_Net_Market_Risk']
        BSCR_Base[each_account].Net_Credit_Risk       = BSCR_result['Net_Credit_Risk']
        BSCR_Base[each_account].Net_PC_Insurance_Risk = BSCR_result['Net_PC_Insurance_Risk']
        BSCR_Base[each_account].Net_LT_Insurance_Risk = BSCR_result['Net_LT_Insurance_Risk']
        BSCR_Base[each_account].BSCR_Aft_Correlation  = BSCR_result['BSCR_agg']
        BSCR_Base[each_account].OpRisk_Chage_pct      = BSCR_result['OpRisk_Chage_pct']
        BSCR_Base[each_account].OpRisk_Chage          = BSCR_result['OpRisk_Chage']
        BSCR_Base[each_account].BSCR_Bef_Tax_Adj      = BSCR_result['BSCR_Bef_Tax_Adj']
        BSCR_Base[each_account].Tax_Credit            = 0                                                                               ### Vincent 07/19/2019
        BSCR_Base[each_account].BSCR_Aft_Tax_Adj      = BSCR_Base[each_account].BSCR_Bef_Tax_Adj - BSCR_Base[each_account].Tax_Credit   ### Vincent 07/19/2019
        
    return BSCR_Base


def run_BSCR_dashboard(BSCR_Dashboard, BSCR_Base, EBS_DB, base_liab_summary, db_liab_summary, actual_estimate, Regime):

    accounts = ['LT','GI', 'Agg']
    
    for each_account in accounts:
  
#Kellie: 5/29/2019 - FI_MV adjusted with other cash settlement value
        each_FI_MV     = EBS_DB[each_account].fwa_MV_FI + EBS_DB[each_account].fixed_inv_surplus + EBS_DB[each_account].cash +EBS_DB[each_account].Other_Assets - EBS_DB[each_account].net_settlement_payble - EBS_DB[each_account].amount_due_other - EBS_DB[each_account].current_tax_payble - EBS_DB[each_account].other_liab
        each_FI_Dur    = EBS_DB[each_account].FI_Dur
        each_alts_MV   = EBS_DB[each_account].fwa_MV_alts + EBS_DB[each_account].alts_inv_surplus 
        each_PVBE      = EBS_DB[each_account].PV_BE
        each_rm        = EBS_DB[each_account].risk_margin
        each_tp        = EBS_DB[each_account].technical_provision
        each_LOC       = EBS_DB[each_account].LOC
        each_DTA       = EBS_DB[each_account].DTA_DTL
        each_TAC       = EBS_DB[each_account].capital_surplus
        each_liab_dur  = db_liab_summary[each_account]['duration']
        each_PVBE_base = base_liab_summary[each_account]['PV_BE']
#       each_liab_dur_base = base_liab_summary[each_account]['duration']
        each_FI_MV_IntRisk = EBS_DB[each_account].fwa_MV_FI + EBS_DB[each_account].fixed_inv_surplus + EBS_DB[each_account].cash +EBS_DB[each_account].Other_Assets

# ====== To produce BSCR_Charge(%) in config_BSCR each quarter ====== #
#        print('each_FI_MV_' + each_account + ': ' + str(each_FI_MV))
#        print('FI_Risk' + each_account + ': ' + str(BSCR_Base[each_account].Concentration_Risk))
#        print('Curr_Risk' + each_account + ': ' + str(BSCR_Base[each_account].Currency_Risk))
#        print('Con_Risk' + each_account + ': ' + str(BSCR_Base[each_account].Concentration_Risk))
#        
#        FI_ratio = BSCR_Base[each_account].FI_Risk / each_FI_MV 
#        Curr_Ratio = BSCR_Base[each_account].Currency_Risk / each_FI_MV 
#        Con_Ratio = BSCR_Base[each_account].Concentration_Risk / each_FI_MV 
#        
#        print('FI_Risk_%' + each_account + ': ' + str(FI_ratio))
#        print('Curr_Risk_%' + each_account + ': ' + str(Curr_Ratio))
#        print('Con_Risk_%' + each_account + ': ' + str(Con_Ratio))
        
# Kellie: 5/29/2019 - IR risk exposure to be consistent with EBS reporting            
        BSCR_Dashboard[each_account].PV_BE    = each_PVBE
        BSCR_Dashboard[each_account].risk_margin    = each_rm
        BSCR_Dashboard[each_account].technical_provision    = each_tp
        BSCR_Dashboard[each_account].Liab_Dur = each_liab_dur
        BSCR_Dashboard[each_account].FI_MV    = each_FI_MV
        BSCR_Dashboard[each_account].FI_Dur   = each_FI_Dur
        BSCR_Dashboard[each_account].Alts_MV  = each_alts_MV
        BSCR_Dashboard[each_account].LOC      = each_LOC
        BSCR_Dashboard[each_account].DTA      = each_DTA
        BSCR_Dashboard[each_account].TAC      = each_TAC
        
        if actual_estimate == 'Estimate': ### Dashboard
            # Kellie: 6/12/2019 - have FI risk factor by account         
            BSCR_Dashboard[each_account].FI_Risk             = BSCR_Cofig.BSCR_Charge['FI_Risk_' + each_account] * each_FI_MV
            BSCR_Dashboard[each_account].Equity_Risk         = BSCR_Cofig.BSCR_Charge['Eq_Risk'] * (each_alts_MV + each_LOC + each_DTA)
    
            each_PVBE_adj                                    = EBS_DB[each_account].PV_BE - EBS_DB[each_account].ALBA_Adjustment 
            BSCR_Dashboard[each_account].IR_Risk             = BSCR.BSCR_IR_Risk(each_FI_MV_IntRisk, each_FI_Dur, each_PVBE_adj, each_liab_dur)

            # Kellie: 5/29/2019 - IR risk exposure to be consistent with EBS reporting        
            BSCR_Dashboard[each_account].Currency_Risk       = BSCR_Cofig.BSCR_Charge['Currency_Risk_' + each_account] * each_FI_MV
            
            # Vincent: 6/5/2019 - Concentration Risk: agg should not equal to LT + GI            
            BSCR_Dashboard[each_account].Concentration_Risk  = BSCR_Cofig.BSCR_Charge['Concentration_Risk_' + each_account] * each_FI_MV
        
        elif actual_estimate == 'Actual': ### Step 2
            BSCR_Dashboard[each_account].FI_Risk            = BSCR_Base['BSCR_FI'][each_account][0]
            BSCR_Dashboard[each_account].Equity_Risk        = BSCR_Base['BSCR_Eq'][each_account]
            BSCR_Dashboard[each_account].IR_Risk            = BSCR_Base['BSCR_IR'][each_account]
            BSCR_Dashboard[each_account].Currency_Risk      = BSCR_Base['BSCR_Ccy'][each_account]
            BSCR_Dashboard[each_account].Concentration_Risk = BSCR_Base['BSCR_ConRisk'][each_account]
            BSCR_Dashboard[each_account].Market_Risk        = BSCR_Base['BSCR_Market'][each_account]
        
        if each_account == 'Agg':
            BSCR_Dashboard[each_account].Net_Credit_Risk     = BSCR_Dashboard['LT'].Net_Credit_Risk      +   BSCR_Dashboard['GI'].Net_Credit_Risk
            BSCR_Dashboard[each_account].Premium_Risk        = BSCR_Dashboard['LT'].Premium_Risk         +   BSCR_Dashboard['GI'].Premium_Risk
            BSCR_Dashboard[each_account].Reserve_Risk        = BSCR_Dashboard['LT'].Reserve_Risk         +   BSCR_Dashboard['GI'].Reserve_Risk
            BSCR_Dashboard[each_account].Cat_Risk            = BSCR_Dashboard['LT'].Cat_Risk             +   BSCR_Dashboard['GI'].Cat_Risk
            BSCR_Dashboard[each_account].Mortality_Risk      = BSCR_Dashboard['LT'].Mortality_Risk       +   BSCR_Dashboard['GI'].Mortality_Risk
            BSCR_Dashboard[each_account].StopLoss_Risk       = BSCR_Dashboard['LT'].StopLoss_Risk        +   BSCR_Dashboard['GI'].StopLoss_Risk
            BSCR_Dashboard[each_account].Riders_Risk         = BSCR_Dashboard['LT'].Net_Credit_Risk      +   BSCR_Dashboard['GI'].Riders_Risk
            BSCR_Dashboard[each_account].Morbidity_Risk      = BSCR_Dashboard['LT'].Morbidity_Risk       +   BSCR_Dashboard['GI'].Morbidity_Risk
            BSCR_Dashboard[each_account].Longevity_Risk      = BSCR_Dashboard['LT'].Longevity_Risk       +   BSCR_Dashboard['GI'].Longevity_Risk
            BSCR_Dashboard[each_account].VA_Guarantee_Risk   = BSCR_Dashboard['LT'].VA_Guarantee_Risk    +   BSCR_Dashboard['GI'].VA_Guarantee_Risk
            BSCR_Dashboard[each_account].OtherInsurance_Risk = BSCR_Dashboard['LT'].OtherInsurance_Risk  +   BSCR_Dashboard['GI'].OtherInsurance_Risk
            BSCR_Dashboard[each_account].LT_Risk             = BSCR_Dashboard['LT'].LT_Risk              +   BSCR_Dashboard['GI'].LT_Risk
            BSCR_Dashboard[each_account].tax_sharing         = BSCR_Dashboard['LT'].tax_sharing          +   BSCR_Dashboard['GI'].tax_sharing
        
        else:
            if actual_estimate == 'Estimate': ### Dashboard
                BSCR_Dashboard[each_account].Net_Credit_Risk     = BSCR_Base[each_account].Net_Credit_Risk / each_PVBE_base * each_PVBE
                BSCR_Dashboard[each_account].Premium_Risk        = BSCR_Base[each_account].Premium_Risk / each_PVBE_base * each_PVBE
                BSCR_Dashboard[each_account].Reserve_Risk        = BSCR_Base[each_account].Reserve_Risk / each_PVBE_base * each_PVBE
                BSCR_Dashboard[each_account].Cat_Risk            = BSCR_Base[each_account].Cat_Risk / each_PVBE_base * each_PVBE
                BSCR_Dashboard[each_account].Mortality_Risk      = BSCR_Base[each_account].Mortality_Risk / each_PVBE_base * each_PVBE
                BSCR_Dashboard[each_account].StopLoss_Risk       = BSCR_Base[each_account].StopLoss_Risk / each_PVBE_base * each_PVBE
                BSCR_Dashboard[each_account].Riders_Risk         = BSCR_Base[each_account].Riders_Risk / each_PVBE_base * each_PVBE
                BSCR_Dashboard[each_account].Morbidity_Risk      = BSCR_Base[each_account].Morbidity_Risk / each_PVBE_base * each_PVBE
                BSCR_Dashboard[each_account].Longevity_Risk      = BSCR_Base[each_account].Longevity_Risk / each_PVBE_base * each_PVBE
                BSCR_Dashboard[each_account].VA_Guarantee_Risk   = BSCR_Base[each_account].VA_Guarantee_Risk / each_PVBE_base * each_PVBE
                BSCR_Dashboard[each_account].OtherInsurance_Risk = BSCR_Base[each_account].OtherInsurance_Risk / each_PVBE_base * each_PVBE
                
        
            elif actual_estimate == 'Actual': ### Step 2    
                if each_account == 'LT':
                    BSCR_Dashboard[each_account].Net_Credit_Risk     = 0
                    BSCR_Dashboard[each_account].Premium_Risk        = 0
                    BSCR_Dashboard[each_account].Reserve_Risk        = 0
                    BSCR_Dashboard[each_account].Cat_Risk            = 0
                    BSCR_Dashboard[each_account].Mortality_Risk      = BSCR_Base['BSCR_Mort']['Total'][0]
                    BSCR_Dashboard[each_account].StopLoss_Risk       = BSCR_Base['BSCR_Stoploss']['Total'][0]
                    BSCR_Dashboard[each_account].Riders_Risk         = BSCR_Base['BSCR_Riders']['Total'][0]
                    BSCR_Dashboard[each_account].Morbidity_Risk      = BSCR_Base['BSCR_Morb']['Total'][0]
                    BSCR_Dashboard[each_account].Longevity_Risk      = BSCR_Base['BSCR_Long']['Total'][0]
                    BSCR_Dashboard[each_account].VA_Guarantee_Risk   = BSCR_Base['BSCR_VA']['Total'][0]
                    BSCR_Dashboard[each_account].OtherInsurance_Risk = BSCR_Base['BSCR_Other']['Total'][0] 
                    BSCR_Dashboard[each_account].LT_Risk             = BSCR_Base['BSCR_LT'][0] 
                    BSCR_Dashboard[each_account].tax_sharing         = UI.Tax_sharing[each_account]        ### Xi 7/18/2019
                    
                if each_account == 'GI':
                    BSCR_Dashboard[each_account].Net_Credit_Risk     = 0
                    BSCR_Dashboard[each_account].Premium_Risk        = 0
                    BSCR_Dashboard[each_account].Reserve_Risk        = BSCR_Base['BSCR_PC']['PC'][0]
                    BSCR_Dashboard[each_account].Cat_Risk            = 0
                    BSCR_Dashboard[each_account].Mortality_Risk      = 0
                    BSCR_Dashboard[each_account].StopLoss_Risk       = 0
                    BSCR_Dashboard[each_account].Riders_Risk         = 0
                    BSCR_Dashboard[each_account].Morbidity_Risk      = 0
                    BSCR_Dashboard[each_account].Longevity_Risk      = 0
                    BSCR_Dashboard[each_account].VA_Guarantee_Risk   = 0
                    BSCR_Dashboard[each_account].OtherInsurance_Risk = 0
                    BSCR_Dashboard[each_account].tax_sharing         = UI.Tax_sharing[each_account]       ### Xi 7/18/2019

        BSCR_result = BSCR.BSCR_Aggregate(BSCR_Dashboard[each_account], Regime, OpRiskCharge = BSCR_Cofig.BSCR_Charge['OpRiskCharge'])
        
        BSCR_Dashboard[each_account].BSCR_Bef_Correlation  = BSCR_result['BSCR_sum']
        BSCR_Dashboard[each_account].Net_Market_Risk       = BSCR_result['BSCR_Net_Market_Risk']
        BSCR_Dashboard[each_account].Net_Credit_Risk       = BSCR_result['Net_Credit_Risk']
        BSCR_Dashboard[each_account].Net_PC_Insurance_Risk = BSCR_result['Net_PC_Insurance_Risk']
        BSCR_Dashboard[each_account].Net_LT_Insurance_Risk = BSCR_result['Net_LT_Insurance_Risk']
        BSCR_Dashboard[each_account].BSCR_Aft_Correlation  = BSCR_result['BSCR_agg']
        BSCR_Dashboard[each_account].OpRisk_Chage_pct      = BSCR_result['OpRisk_Chage_pct']
        BSCR_Dashboard[each_account].OpRisk_Chage          = BSCR_result['OpRisk_Chage']
        BSCR_Dashboard[each_account].BSCR_Bef_Tax_Adj      = BSCR_result['BSCR_Bef_Tax_Adj']
        
        BSCR_Dashboard[each_account].Tax_Credit            = BSCR.BSCR_TaxCredit(BSCR_Dashboard[each_account], EBS_DB[each_account], base_liab_summary[each_account], Regime)        
        BSCR_Dashboard[each_account].BSCR_Aft_Tax_Adj      = BSCR_Dashboard[each_account].BSCR_Bef_Tax_Adj - BSCR_Dashboard[each_account].Tax_Credit 
    

    # Diversfied BSCR    
    BSCR_Sum    = BSCR_Dashboard['LT'].BSCR_Aft_Tax_Adj  + BSCR_Dashboard['GI'].BSCR_Aft_Tax_Adj
    Div_Benefit = BSCR_Sum - BSCR_Dashboard['Agg'].BSCR_Aft_Tax_Adj
    
    BSCR_Dashboard['LT'].BSCR_Div = BSCR_Dashboard['LT'].BSCR_Aft_Tax_Adj - Div_Benefit * BSCR_Dashboard['LT'].BSCR_Aft_Tax_Adj / BSCR_Sum
    BSCR_Dashboard['GI'].BSCR_Div = BSCR_Dashboard['GI'].BSCR_Aft_Tax_Adj - Div_Benefit * BSCR_Dashboard['GI'].BSCR_Aft_Tax_Adj / BSCR_Sum
    BSCR_Dashboard['Agg'].BSCR_Div = BSCR_Dashboard['Agg'].BSCR_Aft_Tax_Adj
    
    BSCR_Dashboard['LT'].ECR_Ratio = BSCR_Dashboard['LT'].TAC / BSCR_Dashboard['LT'].BSCR_Div
    BSCR_Dashboard['GI'].ECR_Ratio = BSCR_Dashboard['GI'].TAC / BSCR_Dashboard['GI'].BSCR_Div
    BSCR_Dashboard['Agg'].ECR_Ratio = BSCR_Dashboard['Agg'].TAC / BSCR_Dashboard['Agg'].BSCR_Div
    
    BSCR_Dashboard['LT'].ECR_Ratio_SA = BSCR_Dashboard['LT'].TAC / BSCR_Dashboard['LT'].BSCR_Aft_Tax_Adj
    BSCR_Dashboard['GI'].ECR_Ratio_SA = BSCR_Dashboard['GI'].TAC / BSCR_Dashboard['GI'].BSCR_Aft_Tax_Adj
    BSCR_Dashboard['Agg'].ECR_Ratio_SA = BSCR_Dashboard['Agg'].TAC / BSCR_Dashboard['Agg'].BSCR_Aft_Tax_Adj

    return BSCR_Dashboard

    
def export_Dashboard(eval_date, actual_estimate, EBS_Analytics, BSCR_Analytics, work_dir, Regime):

    col_names = ["eval_date","actual_estimate","LOB","TAC", "ECR_Ratio","BSCR_Div","BSCR_Aft_Tax_Adj","ECR_Ratio_SA","PV_BE","risk_margin",
                       "technical_provision","FI_MV","Alts_MV","FI_Dur","Liab_Dur","AccountName","cash","net_settlement_payble","fixed_inv_surplus",	
                       "alts_inv_surplus","fwa_tot","fwa_MV","fwa_acc_int","fwa_policy_loan","fwa_MV_alts","fwa_MV_FI",
                       "DTA_DTL","LOC","LTIC","Other_Assets","total_assets","PV_BE","risk_margin","current_tax_payble",
                       "net_settlement_payble","amount_due_other","acc_int_liab","other_liab","total_liabilities","capital_surplus","tot_liab_econ_capital_surplus","Derivative_IR01","Derivative_Dur"
                       ]
    output = []
    

    output.append(col_names)

    for key, val in BSCR_Analytics.items():
        output.append([eval_date, actual_estimate, key, val.TAC,val.ECR_Ratio, val.BSCR_Div, val.BSCR_Aft_Tax_Adj, val.ECR_Ratio_SA, val.PV_BE, val.risk_margin, val.technical_provision
                       , val.FI_MV, val.Alts_MV, val.FI_Dur, val.Liab_Dur])

    idx = 1 

    for key, val in EBS_Analytics.items():
        output[idx] = output[idx] + [val.AccountName, val.cash, val.net_settlement_payble, val.fixed_inv_surplus, val.alts_inv_surplus, val.fwa_tot, val.fwa_MV, val.fwa_acc_int, val.fwa_policy_loan, val.fwa_MV_alts, val.fwa_MV_FI, val.DTA_DTL, val.LOC, val.LTIC, val.Other_Assets, val.total_assets, val.PV_BE,
                                     val.risk_margin, val.current_tax_payble, val.net_settlement_payble, val.amount_due_other, val.acc_int_liab, val.other_liab,val.total_liabilities, val.capital_surplus, val.tot_liab_econ_capital_surplus, val.Derivative_IR01, val.Derivative_Dur ]
        idx +=1
        
    outFileName = 'ebs_dashboard_run_' + eval_date.strftime('%Y%m%d') + '_' +  datetime.datetime.now().strftime('%Y%m%d_%H_%M_%S') + '_' + Regime + '.xlsx'
    
    Util.output_to_excel_file(work_dir, outFileName, output)
    
    return output

def export_BSCRDetail(eval_date, actual_estimate, BSCR_Analytics, work_dir, Regime):

    BSCRcol_names = ["eval_date","actual_estimate","LOB","TAC", "ECR_Ratio","BSCR_Div","BSCR_Aft_Tax_Adj","ECR_Ratio_SA","FI_Risk","Equity_Risk","IR_Risk","Currency_Risk",
                 "Concentration_Risk","Net_Credit_Risk", "Premium_Risk", "Reserve_Risk", "Cat_Risk","Mortality_Risk", "StopLoss_Risk","Riders_Risk", "Morbidity_Risk",
                 "Longevity_Risk", "VA_Guarantee_Risk","OtherInsurance_Risk", "BSCR_Bef_Correlation","Net_Market_Risk","Net_Credit_Risk","Net_PC_Insurance_Risk",
                 "Net_LT_Insurance_Risk","BSCR_Aft_Correlation","OpRisk_Chage_pct","OpRisk_Chage","BSCR_Bef_Tax_Adj","Tax_Credit"
                 
                    ]
    BSCRDetailoutput = []
    
    BSCRDetailoutput.append(BSCRcol_names)

    for key, val in BSCR_Analytics.items():
        BSCRDetailoutput.append([eval_date, actual_estimate, key, val.TAC,val.ECR_Ratio, val.BSCR_Div, val.BSCR_Aft_Tax_Adj, val.ECR_Ratio_SA, val.FI_Risk, val.Equity_Risk, val.IR_Risk, val.Currency_Risk,
                                 val.Concentration_Risk,val.Net_Credit_Risk, val.Premium_Risk, val.Reserve_Risk, val.Cat_Risk,val.Mortality_Risk, val.StopLoss_Risk,val.Riders_Risk, val.Morbidity_Risk,
                                 val.Longevity_Risk,val.VA_Guarantee_Risk,val.OtherInsurance_Risk,val.BSCR_Bef_Correlation,val.Net_Market_Risk,val.Net_Credit_Risk,val.Net_PC_Insurance_Risk,
                                 val.Net_LT_Insurance_Risk,val.BSCR_Aft_Correlation,val.OpRisk_Chage_pct,val.OpRisk_Chage,val.BSCR_Bef_Tax_Adj,val.Tax_Credit])
        
    BSCRoutFileName = 'BSCR_Detail_run_'+ eval_date.strftime('%Y%m%d') + '_' +  datetime.datetime.now().strftime('%Y%m%d_%H_%M_%S') + '_' + Regime + '.xlsx'
    Util.output_to_excel_file(work_dir, BSCRoutFileName, BSCRDetailoutput)
    return BSCRDetailoutput

def load_surplus_account_cash_flow(valDate, revalDate):

    work_dir  = UI.asset_workDir
    fileName  = UI.surplus_account_CF_file
    
    curr_dir = os.getcwd()
    os.chdir(work_dir)

    work_file_name = pd.ExcelFile(fileName)
    work_file      = pd.read_excel(work_file_name)
    os.chdir(curr_dir)
    
    summmary_1 = work_file.where( work_file['Value Date'] <= revalDate)
    summmary_2 = summmary_1.where( work_file['Value Date'] > valDate)
    #    cf_summary = summmary_2.groupby(['Account', 'Tag'])['Transaction Amount'].agg('sum')    
    #Kellie 0612,take difference between debit and credit to be the actual payment
    output = {}

    surplus_summary     = summmary_2.groupby(['Account', 'Tag', 'DR CR'])['Transaction Amount'].sum()

    LT_actual_tax   = surplus_summary.loc[(['LT'],['Tax Payment'],['D'])].sum()    
    GI_actual_tax   = surplus_summary.loc[(['GI'],['Tax Payment'],['D'])].sum()  

    LT_actual_expense   = surplus_summary.loc[(['LT'],['Expenses'],['D'])].sum()
    GI_actual_expense   = surplus_summary.loc[(['GI'],['Expenses'],['D'])].sum()  
    

    LT_actual_settlement   = surplus_summary.loc[(['LT'],['Quarterly Settlement'],['D'])].sum()
    GI_actual_settlement   = surplus_summary.loc[(['GI'],['Quarterly Settlement'],['D'])].sum()      
    
    output = { 'LT' : {'actual_tax' : LT_actual_tax, 'actual_expense' : LT_actual_expense, 'actual_settlement' : LT_actual_settlement },
               'GI' : {'actual_tax' : GI_actual_tax, 'actual_expense' : GI_actual_expense, 'actual_settlement' : GI_actual_settlement }
              }

    return output

def load_derivatives_IR01(revalDate):

    work_dir  = UI.asset_workDir
    fileName  = UI.derivatives_IR01_file
    
    curr_dir = os.getcwd()
    os.chdir(work_dir)
    work_file_name = pd.ExcelFile(fileName)
    work_file      = pd.read_excel(work_file_name)
    os.chdir(curr_dir)
    
    IR01_Calc     = work_file.groupby(['Date'])['Total'].sum()
    IR01_Deriv    = IR01_Calc.loc[([revalDate])].sum()    

    Init_Margin_Calc = work_file.groupby(['Date'])['Initial_Margin'].sum()
    Init_Margin      = Init_Margin_Calc.loc[([revalDate])].sum()    

    return { 'IR01_Deriv' : IR01_Deriv, 'Init_Margin' : Init_Margin }

    
def Actual_load_derivatives_IR01(valDate):

    work_dir  = UI.asset_workDir
    fileName  = UI.derivatives_IR01_file
    
    curr_dir = os.getcwd()
    os.chdir(work_dir)
    work_file_name = pd.ExcelFile(fileName)
    work_file      = pd.read_excel(work_file_name)
    os.chdir(curr_dir)
    
    work_file['SWAP'] = work_file['SWAP1'] + work_file['SWAP2']
    
    IR01_Calc     = work_file.groupby(['Date'])['SWAP'].sum() 
    IR01_Deriv    = IR01_Calc.loc[([valDate])].sum()
    
    return IR01_Deriv    

#%% Vincent
def set_stress_scenarios(work_dir):

    curr_dir = os.getcwd()    
    os.chdir(work_dir)
    Scen_Mapping_File = pd.ExcelFile('./M_Stress_Scenarios.xlsx')
    Scen_Def  = Scen_Mapping_File.parse()
    os.chdir(curr_dir)

    calc_Scen = {}
    
    for each_scen in Scen_Def['Scenario_No']:
        print(each_scen)
    
        cls_scen = Corpclass.Stress_Scenarios(each_scen)
        cal_Scen_def = Scen_Def[Scen_Def['Scenario_No'] == each_scen]
        
        # stress scenarios definition
        cls_scen.set_scen_Def('Scenario_No',                    each_scen)        
        cls_scen.set_scen_Def('Scen_Description',               cal_Scen_def['Scen_Description'].values[0])
        cls_scen.set_scen_Def('IR',                             cal_Scen_def['IR'].values[0])
        cls_scen.set_scen_Def('Yield_Curve',                    cal_Scen_def['Yield_Curve'].values[0])
        cls_scen.set_scen_Def('Yield_Curve_Liab',               cal_Scen_def['Yield_Curve_Liab'].values[0])
        cls_scen.set_scen_Def('Credit_Spread2',                 cal_Scen_def['Credit_Spread2'].values[0])
        cls_scen.set_scen_Def('Alts',                           cal_Scen_def['Alts'].values[0])
        cls_scen.set_scen_Def('ML III',                         cal_Scen_def['ML III'].values[0])        
        cls_scen.set_scen_Def('PC_Reserve',                     cal_Scen_def['PC_Reserve'].values[0])
        cls_scen.set_scen_Def('LT_Reserve',                     cal_Scen_def['LT_Reserve'].values[0])
        cls_scen.set_scen_Def('Liability Spread Sensitivity',   cal_Scen_def['Liability Spread Sensitivity'].values[0])
        cls_scen.set_scen_Def('Longevity shock',                cal_Scen_def['Longevity shock'].values[0])
        cls_scen.set_scen_Def('Mortality shock',                cal_Scen_def['Mortality shock'].values[0])
        cls_scen.set_scen_Def('Expense shock_Permanent',        cal_Scen_def['Expense shock_Permanent'].values[0])
        cls_scen.set_scen_Def('Expense shock_Inflation',        cal_Scen_def['Expense shock_Inflation'].values[0])
        cls_scen.set_scen_Def('Lapse shock',                    cal_Scen_def['Lapse shock'].values[0])
        cls_scen.set_scen_Def('Morbidity shock',                cal_Scen_def['Morbidity shock'].values[0])
        cls_scen.set_scen_Def('Longevity Trend shock',          cal_Scen_def['Longevity Trend shock'].values[0])
        cls_scen.set_scen_Def('Hedge',                          cal_Scen_def['Hedge'].values[0])
        cls_scen.set_scen_Def('Longevity shock_stress',         cal_Scen_def['Longevity shock_stress'].values[0])       
        cls_scen.set_scen_Def('Mortality shock_stress',         cal_Scen_def['Mortality shock_stress'].values[0])
        cls_scen.set_scen_Def('Expense shock_Permanent_stress', cal_Scen_def['Expense shock_Permanent_stress'].values[0])
        cls_scen.set_scen_Def('Expense shock_Inflation_stress', cal_Scen_def['Expense shock_Inflation_stress'].values[0])
        cls_scen.set_scen_Def('Lapse shock_stress',             cal_Scen_def['Lapse shock_stress'].values[0])
        cls_scen.set_scen_Def('Morbidity shock_stress',         cal_Scen_def['Morbidity shock_stress'].values[0])
        cls_scen.set_scen_Def('Longevity Trend shock_stress',   cal_Scen_def['Longevity Trend shock_stress'].values[0])
        cls_scen.set_scen_Def('IR_Stress',                      cal_Scen_def['IR_Stress'].values[0])
        cls_scen.set_scen_Def('YieldCurve_Stress',              cal_Scen_def['YieldCurve_Stress'].values[0])
        cls_scen.set_scen_Def('YieldCurve_Liab_Stress',         cal_Scen_def['YieldCurve_Liab_Stress'].values[0])
        cls_scen.set_scen_Def('Credit_Spread_Stress',           cal_Scen_def['Credit_Spread_Stress'].values[0])
        cls_scen.set_scen_Def('Alts_Stress',                    cal_Scen_def['Alts_Stress'].values[0])
        cls_scen.set_scen_Def('ML III_Stress',                  cal_Scen_def['ML III_Stress'].values[0])
        cls_scen.set_scen_Def('PC_Reserve_Stress',              cal_Scen_def['PC_Reserve_Stress'].values[0])
        cls_scen.set_scen_Def('LT_Reserve_Stress',              cal_Scen_def['LT_Reserve_Stress'].values[0])
        cls_scen.set_scen_Def('Liability Spread Stress',        cal_Scen_def['Liability Spread Stress'].values[0])
        cls_scen.set_scen_Def('Hedge_strategy',                 cal_Scen_def['Hedge_strategy'].values[0]) 
        
        cls_scen.set_scen_Def('AAA',                            cal_Scen_def['AAA'].values[0])
        cls_scen.set_scen_Def('AA',                             cal_Scen_def['AA'].values[0])
        cls_scen.set_scen_Def('A',                              cal_Scen_def['A'].values[0])
        cls_scen.set_scen_Def('BBB',                            cal_Scen_def['BBB'].values[0])
        cls_scen.set_scen_Def('BB',                             cal_Scen_def['BB'].values[0])
        cls_scen.set_scen_Def('B',                              cal_Scen_def['B'].values[0])
        cls_scen.set_scen_Def('CCC',                            cal_Scen_def['CCC'].values[0])
        cls_scen.set_scen_Def('CC',                             cal_Scen_def['CC'].values[0])
        cls_scen.set_scen_Def('C',                              cal_Scen_def['C'].values[0])
        cls_scen.set_scen_Def('D',                              cal_Scen_def['D'].values[0])
                
        calc_Scen[each_scen] = cls_scen

    return calc_Scen      

def Run_Stress_Liab_DashBoard(valDate, EBS_Calc_Date, curveType, numOfLoB, baseLiabAnalytics, Scen_market_factor, stress_scen, M_Stress_Scen, liab_spread_beta = 0.65, KRD_Term = IAL_App.KRD_Term):
    print('Running IR Curve ...')
    irCurve_USD = IAL_App.createAkitShockCurve(EBS_Calc_Date, M_Stress_Scen, stress_scen, curveType, "USD") ### IR shock is applied here
    print('USD IR Curve Done!')
    irCurve_GBP = IAL_App.load_BMA_Stress_Curves(valDate,"GBP",EBS_Calc_Date, M_Stress_Scen, stress_scen)   ### IR shock is applied here
    print('GBP IR Curve Done!')
#    irCurve_GBP = IAL_App.createAkitZeroCurve(valDate, curveType, "GBP")    

#    zzzzzzzzzzzzzzzzzzzzzzzz for liability Attribution Analysis zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
#    irCurve_USD_rollforward = IAL_App.createAkitZeroCurve(valDate, curveType, "USD", "BBB", "Y", EBS_Calc_Date)
#    irCurve_GBP_rollforward = IAL_App.load_BMA_Std_Curves(valDate,"GBP",valDate, "Y", EBS_Calc_Date)

    credit_spread_base   = Scen_market_factor[(Scen_market_factor['val_date'] == valDate)].Credit_Spread.values[0]
    credit_spread_ebs    = Scen_market_factor[(Scen_market_factor['val_date'] == EBS_Calc_Date)].Credit_Spread.values[0]
    credit_spread_change = credit_spread_ebs - credit_spread_base
    
#    spread_shock_rating: to be incorporated
    
    liab_spread_change   = (credit_spread_change + M_Stress_Scen[stress_scen].scen_Def['Credit_Spread2']) * liab_spread_beta ### credit spread shock is applied here
    ccy_rate_ebs         = Scen_market_factor[(Scen_market_factor['val_date'] == EBS_Calc_Date)].GBP.values[0]
    
    calc_liabAnalytics = {}
    for idx in range(1, numOfLoB + 1, 1):
        
        base_liab = baseLiabAnalytics[idx]
        clsLiab = Corpclass.LiabAnalyticsUnit(idx)
        clsLiab.LOB_Def = base_liab.LOB_Def
        clsLiab.cashflow = base_liab.cashflow
        clsLiab.ccy_rate = base_liab.ccy_rate

        ccy       = clsLiab.get_LOB_Def('Currency')        
#        ccy_rate  = clsLiab.ccy_rate                
        
        if ccy == "GBP":
            irCurve            = irCurve_GBP
            ccy_rate_dashboard = ccy_rate_ebs

        else:
            irCurve            = irCurve_USD
            ccy_rate_dashboard = 1.0
        
        cf_idx   = clsLiab.cashflow
        cfHandle = IAL.CF.createSimpleCFs(cf_idx["Period"],cf_idx["aggregate cf"])
        oas      = base_liab.OAS  + liab_spread_change

        pvbe     = IAL.CF.PVFromCurve(cfHandle, irCurve, EBS_Calc_Date, oas)
        effDur   = IAL.CF.effDur(cfHandle, irCurve, EBS_Calc_Date, oas)
#        ytm      = IAL.CF.YTM(cfHandle, pvbe, EBS_Calc_Date)
        conv     = IAL.CF.effCvx(cfHandle, irCurve, EBS_Calc_Date, oas)

#        date_30y = IAL.Util.addTerms(EBS_Calc_Date, "30M")
#        cf_idx_30y = np.where((cf_idx['Period'] <= xxx))
        
        clsLiab.PV_BE     = -pvbe * ccy_rate_dashboard
        clsLiab.duration  = effDur
#        clsLiab.YTM       = ytm
        clsLiab.convexity = conv
        clsLiab.OAS       = oas
        clsLiab.ccy_rate  = ccy_rate_dashboard
        clsLiab.risk_margin = clsLiab.PV_BE * base_liab.risk_margin / base_liab.PV_BE
        clsLiab.technical_provision = clsLiab.PV_BE + clsLiab.risk_margin
        
        for key, value in KRD_Term.items():
            KRD_name        = "KRD_" + key
            clsLiab.set_KRD_value(KRD_name, IAL.CF.keyRateDur(cfHandle, irCurve, EBS_Calc_Date, key, oas))
                
#       print('LOB:', idx, 'Dur:',clsLiab.get_liab_value('Effective Duration') )

        calc_liabAnalytics[idx] = clsLiab
        
    return calc_liabAnalytics

#%%
#def xnpv(rate, CFs, Dates):

#    if rate <= -1.0:
#        return float('inf')
    
#    d0 = min(Dates)   
#    return sum([ vi / (1.0 + rate)**((di - d0).days / 365.0) for vi, di in zip(CFs, Dates)] - CFs.values[0]) 

def run_EBS_PVBE(baseLiabAnalytics, valDate, numOfLoB, Proj_Year, bindingScen, BMA_curve_dir, Step1_Database, Disc_rate_TableName, base_GBP): ### Vincent 07/02/2019
        
    # Binding Scenario Portfolio Discount Rate
    sql_Disc_rate      = "SELECT * FROM " + Disc_rate_TableName + " TB_A Where TB_A.O_Run_ID = " + str(bindingScen) + " ORDER BY TB_A.O_Prt_ID;"
    Disc_rate_Data      = Util.run_SQL(Step1_Database, sql_Disc_rate) 
    
    for idx in range(1, numOfLoB + 1, 1): 
       
        clsPVBE = baseLiabAnalytics[idx]        
        
        print('LOB - ' + str(idx))
         
        if idx != 34:
            LOB_dis_rate = float(Disc_rate_Data[Disc_rate_Data['O_Prt_Name'] == baseLiabAnalytics[idx].LOB_Def['Portfolio Name']]['O_IRR_NoAlts_IE'].values)
                       
            for t in range(0, Proj_Year + 1, 1):
                
                cf_idx  = baseLiabAnalytics[idx].cashflow[t]
                Period  = cf_idx['Period']
                LOB_CFs = cf_idx['aggregate cf']
                                        
                if len(cf_idx) != 0:             
#                    EBS_PVBE_Time_0 = xnpv(LOB_dis_rate, LOB_CFs, Period)                      
                    
                    if t == 0:
                        cfHandle    = IAL.CF.createSimpleCFs(Period, LOB_CFs)
                        irCurve_BMA = IAL_App.load_BMA_Risk_Free_Curves(valDate)
                        EBS_PVBE_Time_0 = IAL.CF.npv(cfHandle, valDate, LOB_dis_rate * 100, 'ACT/365', 'Annual')
                        LOB_OAS     = IAL.CF.OAS(cfHandle, irCurve_BMA, valDate, EBS_PVBE_Time_0)
                        LOB_Dur     = IAL.CF.effDur(cfHandle, irCurve_BMA, valDate, LOB_OAS)
                        
                        clsPVBE.OAS                 = LOB_OAS
                        clsPVBE.PV_BE               = EBS_PVBE_Time_0
                        clsPVBE.EBS_PVBE[t]         = EBS_PVBE_Time_0
                        clsPVBE.duration            = LOB_Dur
                    
                    else:
                        cfHandle = IAL.CF.createSimpleCFs(Period, LOB_CFs)
                        LOB_PVBE = IAL.CF.PVFromCurve(cfHandle, irCurve_BMA, Period[0], LOB_OAS) - LOB_CFs.values[0]                  
                        
                        clsPVBE.EBS_PVBE[t] = LOB_PVBE
                                                                    
            baseLiabAnalytics[idx] = clsPVBE
         
        ### ALBA PVBE - Vincent 07/03/2019    
        elif idx == 34:
 
            cf_idx  = baseLiabAnalytics[idx].cashflow[0]
            Period  = cf_idx['Period']
            LOB_CFs = cf_idx['aggregate cf']
                
            curr_dir = os.getcwd()
            IAL_App.os.chdir(BMA_curve_dir)
            
            fileName = IAL_App.BMA_curve_file[valDate]                                    
            work_BMA_file = pd.ExcelFile(fileName)
            work_BMA_curves = pd.read_excel(work_BMA_file)
            
            ALBA_rate = work_BMA_curves['UK'] - UI.Inv_Fee_GBP
            
            ALBA_rate.loc[-1] = float(0)    # insert a row at front with 0 value
            ALBA_rate.index   = ALBA_rate.index + 1
            ALBA_rate         = ALBA_rate.sort_index()
            ALBA_rate         = pd.DataFrame(ALBA_rate)            
                        
            ALBA_rate['aggregate_cf']       = pd.DataFrame(LOB_CFs)['aggregate cf']
            ALBA_rate['Period']             = pd.DataFrame(Period)['Period']
            ALBA_rate['Year']               = ALBA_rate['Period'].map(lambda x: x.year)
            ALBA_rate['Month']              = ALBA_rate['Period'].map(lambda x: x.month)                        
            ALBA_rate['Dis_Period']         = (ALBA_rate['Year'] - ALBA_rate['Year'][0]) + (ALBA_rate['Month'] - ALBA_rate['Month'][0])/12           
            ALBA_rate['Dis_Period_2']       = ALBA_rate.Dis_Period.shift(1).astype(float).apply(np.ceil)        
            ALBA_rate['Dis_Rate']           = (ALBA_rate.Dis_Period - ALBA_rate.Dis_Period_2) * ALBA_rate.UK + (1 - (ALBA_rate.Dis_Period - ALBA_rate.Dis_Period_2) ) * ALBA_rate.UK.shift(1)            
            ALBA_rate['Dis_Factor']         = (1 + ALBA_rate.Dis_Rate ) ** ( - ALBA_rate.Dis_Period )
            ALBA_rate['Dis_Factor'][1]      = (1 + ALBA_rate['UK'][1] ) ** ( - ALBA_rate['Dis_Period'][1] )
            ALBA_rate['Dis_Factor_Shift']   = ALBA_rate.Dis_Factor.shift(-1) 
            ALBA_rate['aggregate_cf_Shift'] = ALBA_rate.aggregate_cf.shift(-1)
            
            ALBA_rate = ALBA_rate.fillna(0) 
                    
            for t in range(0, Proj_Year + 1, 1):
##               Below is only used if PVBE is calculated OAS method: 
#                cf_idx  = baseLiabAnalytics[idx].cashflow[t]
#                Period  = cf_idx['Period']
#                LOB_CFs = cf_idx['aggregate cf']
                           
                if len(cf_idx) != 0:
                                                                                                                        
                    if t == 0:
                        
                        ALBA_PVBE_Time_0 = sum( ALBA_rate.Dis_Factor_Shift * ALBA_rate.aggregate_cf_Shift ) / ALBA_rate['Dis_Factor'][t] * base_GBP                        
                        
                        cfHandle    = IAL.CF.createSimpleCFs(Period, LOB_CFs)
                        irCurve_GBP = IAL_App.load_BMA_Std_Curves(valDate, 'GBP', valDate)
                        ALBA_OAS    = IAL.CF.OAS(cfHandle, irCurve_GBP, valDate, ALBA_PVBE_Time_0 / base_GBP)
                        ALBA_Dur    = IAL.CF.effDur(cfHandle, irCurve_GBP, valDate, ALBA_OAS)
                        
                        clsPVBE.OAS              = ALBA_OAS                                                
                        clsPVBE.PV_BE            = ALBA_PVBE_Time_0 + (-UI.ALBA_adj) 
                        clsPVBE.EBS_PVBE[t]      = ALBA_PVBE_Time_0 # + (-UI.ALBA_adj) ALBA BSCR is based on PVBE w/o adjustment
                        clsPVBE.duration         = ALBA_Dur
                        
                    else:
                        
                        ALBA_rate = ALBA_rate.iloc[1:]     # dataframe without the first row.
                        ALBA_PVBE = sum( ALBA_rate.Dis_Factor_Shift * ALBA_rate.aggregate_cf_Shift ) / ALBA_rate['Dis_Factor'][t] * base_GBP 
#                        ALBA_PVBE = ALBA_PVBE + ALBA_PVBE / ALBA_PVBE_Time_0 * (-UI.ALBA_adj)

##                       Below is only used if PVBE is calculated OAS method:                        
#                        cfHandle      = IAL.CF.createSimpleCFs(cf_idx["Period"],cf_idx["aggregate cf"])                        
#                        ALBA_PVBE = ( IAL.CF.PVFromCurve(cfHandle, irCurve_GBP, Period[0], ALBA_OAS) - LOB_CFs.values[0] ) * UI.GBP_exc                  
                        
                        clsPVBE.EBS_PVBE[t] = ALBA_PVBE                                        
           
            baseLiabAnalytics[idx] = clsPVBE
            os.chdir(curr_dir)
            
    return baseLiabAnalytics

#%% RM Calc
def sumproduct (cashflows, disfactor):
    
    return sum([i * j for (i,j) in zip(cashflows, disfactor)])
    

def run_RM(BSCR, valDate, Proj_Year, regime, BMA_curve_dir, OpRiskCharge = BSCR_Cofig.BSCR_Charge['OpRiskCharge'], coc = UI.Cost_of_Capital):
    
    life_coc =  {}
    pc_coc =    {}
    p_coc =     {}
    l_coc =     {}
    disc_f =    {}
    period =    []
    rm =        {'PC': {}, 'Life': {}}

    
    # Calc cost of capital
#    if regime == 'Current':
#        
#        for t in range(0, Proj_Year + 1, 1):
#        
#            life_coc[t] = math.sqrt(((BSCR['BSCR_Mort']['Total'][t]) + BSCR['BSCR_Stoploss']['Total'][t] + BSCR['BSCR_Riders']['Total'][t])**2 + (BSCR['BSCR_Morb']['Total'][t])**2 + (BSCR['BSCR_Long']['Total'][t])**2 + (BSCR['BSCR_VA']['Total'][t])**2
#                    - 0.5*((BSCR['BSCR_Mort']['Total'][t] + BSCR['BSCR_Stoploss']['Total'][t] + BSCR['BSCR_Riders']['Total'][t])*BSCR['BSCR_Long']['Total'][t]) + (BSCR['BSCR_Other']['Total'][t])**2)*(1+OpRiskCharge)*coc
#                        
#    elif  regime == 'Future':
#        
#        life_cor = pd.DataFrame(data = BSCR_Cofig.LT_corre)
#        life_risk   = {}
#        life_risk_T = {}
#        
#        for t in range(0, Proj_Year + 1, 1):
#        
#            life_risk[t]   = [BSCR['BSCR_Mort']['Total'][t], BSCR['BSCR_Stoploss']['Total'][t], BSCR['BSCR_Riders']['Total'][t], BSCR['BSCR_Morb']['Total'][t], BSCR['BSCR_Long']['Total'][t], BSCR['BSCR_VA']['Total'][t], BSCR['BSCR_Other']['Total'][t]]
#            life_risk_T[t] = np.array(life_risk[t]). T. tolist()
#            
#            life_coc[t] = math.sqrt(np.dot(np.dot(life_risk[t], life_cor), life_risk_T[t]))*(1+OpRiskCharge)*coc
   
    for t in range(0, Proj_Year + 1, 1):
        
        life_coc[t] = BSCR['BSCR_LT'][t] * (1 + OpRiskCharge) * coc
        pc_coc[t]   = BSCR['BSCR_PC']['PC'][t] * (1 + OpRiskCharge) * coc
    
    p_coc[0] = [v for (t,v) in pc_coc.items()]
    l_coc[0] = [v for (t,v) in life_coc.items()]
   
    for i in range(1, len(p_coc[0])):
        p_coc[i] = p_coc[0][i:]
     
    for i in range(1, len(l_coc[0])):
        l_coc[i] = l_coc[0][i:]  
        
    # import risk free curve    
    curr_dir = os.getcwd()
    os.chdir(BMA_curve_dir) 
        
    fileName = IAL_App.BMA_curve_file[valDate]                                    
    work_BMA_file = pd.ExcelFile(fileName)
    work_BMA_curves = pd.read_excel(work_BMA_file)
    work_rates    = work_BMA_curves['BMA risk free']
    work_rates_shift = [0]
    for i in range(len(work_rates)-1):
        work_rates_shift.append(work_rates[i])
    
    os.chdir(curr_dir)
    # Calc discounting period
    p = int(valDate.strftime('%m'))/12 - 1*(int(valDate.strftime('%m'))/12==1)
    period = [1 - p]
    
    for i in range(1, len(work_rates)):
        period.append(1 - p + i)
   
    # Calc discounting factor   
    rates_f = [i*(1 - p) + j * p for (i,j) in zip (work_rates, work_rates_shift)]
    rates_f[0] = work_rates[0]
    
    disc_timezero = [(1 + i)**(-j) for (i,j) in zip (rates_f, period)]
    disc_f[0] = disc_timezero
    disc_timezero_shift = [1] + disc_timezero
    
    for i in range(1, len(disc_timezero)):
        disc_f[i] = disc_timezero[i:]
      
    # Cal risk margin
    for i in range(len(p_coc[0])):
        rm['PC'][i] = sumproduct(p_coc[i], disc_f[i])/disc_timezero_shift[i]
    
    for i in range(len(l_coc[0])):
        rm['Life'][i] = sumproduct(l_coc[i], disc_f[i])/disc_timezero_shift[i]
                    
    return rm

def run_TP(baseLiabAnalytics, baseBSCR, RM, numOfLoB, Proj_Year):
    TP = {}
    TP['LT'] = {}
    TP['PC'] = {}
    TP['Agg'] = {}
    
    PVBE = {}
    PVBE['Life']    = {}
    PVBE['Annuity'] = {}
    PVBE['PC']      = {}
    
    BSCR = {}
    BSCR['Life']    = {}
    BSCR['Annuity'] = {}
    BSCR['LT']      = {}
               
    for t in range(0, Proj_Year + 1, 1):            
        PVBE['Life'][t]    = 0
        PVBE['Annuity'][t] = 0
        PVBE['PC'][t]      = 0 
        
        BSCR['Life'][t]    = baseBSCR['BSCR_Mort']['Total'][t] + baseBSCR['BSCR_Morb']['Total'][t] + baseBSCR['BSCR_Other']['Life'][t]
        BSCR['Annuity'][t] = baseBSCR['BSCR_Long']['Total'][t] + baseBSCR['BSCR_Other']['Annuity'][t]
        
        BSCR['LT'][t] = BSCR['Life'][t] + BSCR['Annuity'][t]  
                  
    # Sum up PVBE for LT and PC               
    for t in range(0, Proj_Year + 1, 1):               
        for idx in range(1, numOfLoB + 1, 1):
            
            Agg_LOB  = baseLiabAnalytics[idx].LOB_Def['Agg LOB'] 
            BSCR_LOB = baseLiabAnalytics[idx].LOB_Def['BSCR LOB'] 
            
            if Agg_LOB == 'LR':               
                if BSCR_LOB in ['UL','WL','ROP', 'AH', 'LTC', 'PC']: # NUFIC's BSCR LOB is PC
                    try:
                        PVBE['Life'][t] += -baseLiabAnalytics[idx].EBS_PVBE[t]
                    except:
                        PVBE['Life'][t] += 0 
                        
                elif BSCR_LOB in ['SS','TFA','SPIA','ALBA']:
                    try:
                        PVBE['Annuity'][t] += -baseLiabAnalytics[idx].EBS_PVBE[t]
                    except:
                        PVBE['Annuity'][t] += 0
                              
            elif Agg_LOB == 'PC':
                try:
                    PVBE['PC'][t] += -baseLiabAnalytics[idx].EBS_PVBE[t]
                except:
                    PVBE['PC'][t] += 0
        
                 
    for idx in range(1, numOfLoB + 1, 1):
        
        Agg_LOB  = baseLiabAnalytics[idx].LOB_Def['Agg LOB'] 
        BSCR_LOB = baseLiabAnalytics[idx].LOB_Def['BSCR LOB']
        
        if Agg_LOB =='LR':
            for t in range(0, Proj_Year + 1, 1):              
                if BSCR_LOB in ['UL','WL','ROP', 'AH', 'LTC', 'PC']: # NUFIC's BSCR LOB is PC
                    try:
                        baseLiabAnalytics[idx].EBS_RM[t] = (baseLiabAnalytics[idx].EBS_PVBE[t] / PVBE['Life'][t]) * RM['Life'][t] * BSCR['Life'][t] / BSCR['LT'][t]
                        baseLiabAnalytics[idx].EBS_TP[t] = baseLiabAnalytics[idx].EBS_PVBE[t] + baseLiabAnalytics[idx].EBS_RM[t]
                    except:
                        baseLiabAnalytics[idx].EBS_RM[t] = 0
                        baseLiabAnalytics[idx].EBS_TP[t] = 0
                        
                elif BSCR_LOB in ['SS','TFA','SPIA','ALBA']:
                    try:
                        baseLiabAnalytics[idx].EBS_RM[t] = (baseLiabAnalytics[idx].EBS_PVBE[t] / PVBE['Annuity'][t]) * RM['Life'][t] * BSCR['Annuity'][t] / BSCR['LT'][t]
                        baseLiabAnalytics[idx].EBS_TP[t] = baseLiabAnalytics[idx].EBS_PVBE[t] + baseLiabAnalytics[idx].EBS_RM[t]
                    except:
                        baseLiabAnalytics[idx].EBS_RM[t] = 0
                        baseLiabAnalytics[idx].EBS_TP[t] = 0
                                                                       
        elif Agg_LOB =='PC':
            for t in range(0, Proj_Year + 1, 1):
                try:
                    baseLiabAnalytics[idx].EBS_RM[t] = (baseLiabAnalytics[idx].EBS_PVBE[t]/PVBE['PC'][t]) * RM['PC'][t]
                    baseLiabAnalytics[idx].EBS_TP[t] = baseLiabAnalytics[idx].EBS_PVBE[t] + baseLiabAnalytics[idx].EBS_RM[t]      
                except:
                    baseLiabAnalytics[idx].EBS_RM[t] = 0
                    baseLiabAnalytics[idx].EBS_TP[t] = 0
        # time-zero risk margin
        baseLiabAnalytics[idx].risk_margin = baseLiabAnalytics[idx].EBS_RM[0]
        baseLiabAnalytics[idx].technical_provision = baseLiabAnalytics[idx].PV_BE + baseLiabAnalytics[idx].risk_margin

    
    return baseLiabAnalytics


