import os
import numpy as np
import pandas as pd
#import xlwings as xlw
import Lib_Market_Akit  as IAL_App
import Config_Rating_Mapping as Rating_Cofig
import Config_BSCR as BSCR_Cofig
import datetime

### Kyle:
### Inputs of actual_portfolio_feed is changed but Inputs of daily_portfolio_feed is not updated

def daily_portfolio_feed(eval_date, valDate_base, workDir, fileName, asset_fileName_T_plus_1, Price_Date, market_factor, output = 0, mappingFile = '.\Mapping.xlsx', ratingMapFile = '.\Rating_Mapping.xlsx'):
    def wavg(val_col_name, wt_col_name):
        def inner(group):
            return (group[val_col_name] * group[wt_col_name]).sum() / group[wt_col_name].sum()

        inner.__name__ = 'wtd_avg'
        return inner

#    workDir = r'L:\\DSA Re\\Workspace\\Production\\EBS Dashboard\\Python_Code\\Asset_Holding_Feed'
    os.chdir(workDir)

#    fileName = r'.\DSA RE Holdings.xlsx'

    portFile = pd.ExcelFile(fileName)
    portInput = pd.read_excel(portFile, sheet_name='DSA RE Holdings', skiprows=[0, 1, 2, 3, 4, 5, 6])

    portInput = portInput.dropna(axis=0, how='all')
    portInput = portInput.dropna(axis=1, how='all')
    # portInput = portInput.fillna('')
  
    leMapFile = pd.ExcelFile(mappingFile)
    leMap = leMapFile.parse('LegalEntity')
    portInput = portInput.merge(leMap, how='left', left_on=['Owning Entity Name', 'Owning Entity GEMS ID'],
                                right_on=['Owning Entity Name', 'Owning Entity GEMS ID'])

    ratingMapFile = pd.ExcelFile(ratingMapFile)
    ratingMap = ratingMapFile.parse('naic')

    portInput = portInput.merge(ratingMap, how='left', left_on=['NAIC Rating', 'AIG Derived Rating'],
                                right_on=['NAIC Rating', 'AIG Derived Rating'])

    # Two CUSIPs are missing in the asset summary as their 'AIG Asset Class 3' is N/A.
    portInput.loc[portInput['Lot Number Unique ID'] == '218521143_121643527_1951603', ['AIG Asset Class 3']] = 'Corporate Bond'
    portInput.loc[portInput['Lot Number Unique ID'] == '218521146_121464874_1951604', ['AIG Asset Class 3']] = 'Corporate Bond'
    
    # Split out ML-III B Notes
    portInput['AIG Asset Class 3'] = np.where((portInput['Issuer Name'] == 'LSTREET II, LLC'), "ML-III B-Notes",
                                              portInput['AIG Asset Class 3'])

    # Default setting NA 'AIG Derived Rating' to 'BBB'
    portInput['AIG Derived Rating'].fillna('NA-BBB', inplace=True)

    # Handling surplus account
    portInput['SurplusAccount'] = 'Not-Surplus'

    portInput['SurplusAccount'] = np.where(
        ((portInput['Category'] == "Surplus") & (portInput['Strategy (Hld) Long Desc'] == "SAM RE OVERSEAS POOL LIFE")),
        "Long Term Surplus", portInput['SurplusAccount'])

    portInput['SurplusAccount'] = np.where(
        ((portInput['Category'] == "Surplus") & (portInput['Strategy (Hld) Long Desc'] == "SAM RE OVERSEAS POOL PC")),
        "General Surplus", portInput['SurplusAccount'])

    portInput['SurplusAccount'] = np.where(
        ((portInput['SurplusAccount'] == 'Not-Surplus') &
         (portInput['Category'] == "Surplus") & (portInput['Encumbrance Program Level 4 Desc'] == 'DSA REINSURANCE PC')),
        "General Surplus", portInput['SurplusAccount'])

    portInput['SurplusAccount'] = np.where(
        ((portInput['SurplusAccount'] == 'Not-Surplus') &
         (portInput['Category'] == "Surplus") & (portInput['Encumbrance Program Level 4 Desc'] == 'DSA REINSURANCE LR')),
        "Long Term Surplus", portInput['SurplusAccount'])

    portInput['SurplusAccount'] = np.where(
        ((portInput['SurplusAccount'] == 'Not-Surplus') &
         (portInput['Category'] == "Surplus") & (
                 portInput['Encumbrance Program Level 4 Desc'] == 'DSA RE/AGL Trust- DSA REINSURANCE LR')),
        "Long Term Surplus", portInput['SurplusAccount'])

    portInput['SurplusAccount'] = np.where(
        ((portInput['SurplusAccount'] == 'Not-Surplus') &
         (portInput['Category'] == "Surplus") & (
                 portInput['Encumbrance Program Level 4 Desc'] == 'DSA RE/USL Trust - DSA REINSURANCE LR')),
        "Long Term Surplus", portInput['SurplusAccount'])

    portInput['SurplusAccount'] = np.where(
        ((portInput['SurplusAccount'] == 'Not-Surplus') &
         (portInput['Category'] == "Surplus") & (
                 portInput['Encumbrance Program Level 4 Desc'] == 'DSA RE/VALIC Trust - DSA REINSURANCE LR')),
        "Long Term Surplus", portInput['SurplusAccount'])

    portInput['Category'] = np.where(
        ((portInput['SurplusAccount'] == 'Not-Surplus') &
         (portInput['Category'] == "Surplus") & (portInput['Encumbrance Program Level 4 Desc'] == 'SOURCE UNDEFINED')),
        "ModCo", portInput['Category'])

    portInput.dropna(axis=0, how='all', subset=['Category'], inplace=True)

    portInput['Category'] = np.where((portInput['SurplusAccount'] != 'Not-Surplus'),
                                     portInput['SurplusAccount'], portInput['Category'])

    # clean up fake booking due to accounting system migration
    portInput = portInput[[not v.startswith('F-') for (i, v) in portInput['Portfolio (Source) Long Name'].iteritems()]]


    # Report ModCo Currency derivatives
    Cur_Der = portInput.loc[(portInput['AIG Asset Class 1'] == 'Derivative') & (portInput['Owning Entity Name'] != 'American International Reinsurance Company, Ltd.' ) & (portInput['Security Desc DESC'].str[:2] == 'FX'), "Market Value USD GAAP"].sum()
    ModCo_Cur_Der = portInput.loc[(portInput['AIG Asset Class 1'] == 'Derivative') & (portInput['Category'] == 'ModCo' ) & (portInput['Security Desc DESC'].str[:2] == 'FX'), "Market Value USD GAAP"].sum()    
    
    print('Currency_Derivative_' + eval_date.strftime('%Y%m%d') + ': ' + str(Cur_Der))
    print('ModCo_Currency_Derivative_' + eval_date.strftime('%Y%m%d') + ': ' + str(ModCo_Cur_Der))
    
    if eval_date > datetime.datetime(2019, 8, 31):
        # Illiquidity impact estimation
        Yield_Change_0 = market_factor[market_factor['val_date'] == eval_date]['IR'].values[0] - market_factor[market_factor['val_date'] == Price_Date[0]]['IR'].values[0] \
                       + 0.8 * (market_factor[market_factor['val_date'] == eval_date]['Credit_Spread'].values[0]/10000 - market_factor[market_factor['val_date'] == Price_Date[0]]['Credit_Spread'].values[0]/10000)
                       
        Yield_Change_1 = market_factor[market_factor['val_date'] == eval_date]['IR'].values[0] - market_factor[market_factor['val_date'] == Price_Date[1]]['IR'].values[0] \
                       + 0.8 * (market_factor[market_factor['val_date'] == eval_date]['Credit_Spread'].values[0]/10000 - market_factor[market_factor['val_date'] == Price_Date[1]]['Credit_Spread'].values[0]/10000)
      
        Initial_mv_acc_int = portInput.loc[(portInput['Price Date'] <= Price_Date[1]) & (portInput['AIG Asset Class 1'] == 'Fixed Income') & (portInput['Effective Duration (WAMV)'].notnull() ) & (portInput['Effective Duration (WAMV)'] != 0), 'Market Value with Accrued Int USD GAAP'].sum()
        
        portInput.loc[(portInput['Price Date'] > Price_Date[0]) & (portInput['Price Date'] <= Price_Date[1]) & (portInput['AIG Asset Class 1'] == 'Fixed Income') & (portInput['Effective Duration (WAMV)'].notnull() ) & (portInput['Effective Duration (WAMV)'] != 0), "Market Value with Accrued Int USD GAAP"] = portInput['Market Value with Accrued Int USD GAAP'] * (1 + portInput['Effective Duration (WAMV)'] * -Yield_Change_1) 
        portInput.loc[(portInput['Price Date'] <= Price_Date[0]) & (portInput['AIG Asset Class 1'] == 'Fixed Income') & (portInput['Effective Duration (WAMV)'].notnull() ) & (portInput['Effective Duration (WAMV)'] != 0), "Market Value with Accrued Int USD GAAP"] = portInput['Market Value with Accrued Int USD GAAP'] * (1 + portInput['Effective Duration (WAMV)'] * -Yield_Change_0) 
                
        total_illiquid_adj = portInput.loc[(portInput['Price Date'] <= Price_Date[1]) & (portInput['AIG Asset Class 1'] == 'Fixed Income') & (portInput['Effective Duration (WAMV)'].notnull() ) & (portInput['Effective Duration (WAMV)'] != 0), 'Market Value with Accrued Int USD GAAP'].sum() - Initial_mv_acc_int
       
        portInput.fillna(0, inplace=True)
        portInput['Market Value USD GAAP'] = portInput['Market Value with Accrued Int USD GAAP'] - portInput['Accrued Int USD GAAP']
        
        print(eval_date.strftime('%Y%m%d') + 'Yield_Change_' + Price_Date[0].strftime('%Y%m%d') + ': ' + str(Yield_Change_0))
        print(eval_date.strftime('%Y%m%d') + 'Yield_Change_' + Price_Date[1].strftime('%Y%m%d') + ': ' + str(Yield_Change_1))
        print(eval_date.strftime('%Y%m%d') + '_Initial_mv_acc_int: ' + str(Initial_mv_acc_int))
        print(eval_date.strftime('%Y%m%d') + '_total_illiquid_adj: ' + str(total_illiquid_adj))
        
    ### === Prepare Asset Summary File === ###
    portInput['AIG Derived Rating Update'] = portInput['AIG Derived Rating']

    portInput['AIG Derived Rating Update'] = np.where(((portInput['AIG Asset Class 3'] == 'CMBS Agency') | (
            portInput['AIG Asset Class 3'] == 'CMBS Non-Agency') | (portInput['AIG Asset Class 3'] == 'RMBS Agency') | (
                                                               portInput['AIG Asset Class 3'] == 'RMBS Non-Agency')),
                                                      portInput['Derived Rating Modified'], portInput['AIG Derived Rating'])
    
    # temporarily write to file for validation purpose
    # portWriter = pd.ExcelWriter('./output/FRL_0228.xlsx')
    # portInput.to_excel(portWriter, sheet_name='asset_port', index=False)
    # portWriter.save()

    groupByFields = ['Category', 'AIG Asset Class 3', 'AIG Derived Rating Update']

    reportFields = {"YTW": "Market Value USD GAAP", \
                    "OAS": "Market Value USD GAAP", \
                    "Effective Duration (WAMV)": "Market Value USD GAAP", \
                    "Effective Convexity": "Market Value USD GAAP", \
                    "Spread Duration": "Market Value USD GAAP", \
                    "Spread Convexity": "Market Value USD GAAP", \
                    "WAL": "Quantity", \
                    "KRD 1M": "Market Value USD GAAP", \
                    "KRD 2M": "Market Value USD GAAP", \
                    "KRD 3M": "Market Value USD GAAP", \
                    "KRD 6M": "Market Value USD GAAP", \
                    "KRD 9M": "Market Value USD GAAP", \
                    "KRD 1Y": "Market Value USD GAAP", \
                    "KRD 2Y": "Market Value USD GAAP", \
                    "KRD 3Y": "Market Value USD GAAP", \
                    "KRD 5Y": "Market Value USD GAAP", \
                    "KRD 7Y": "Market Value USD GAAP", \
                    "KRD 10Y": "Market Value USD GAAP", \
                    "KRD 15Y": "Market Value USD GAAP", \
                    "KRD 20Y": "Market Value USD GAAP", \
                    "KRD 30Y": "Market Value USD GAAP"}

    sumFields = groupByFields.copy()
    sumFields.append('Market Value USD GAAP')
    mv = portInput.loc[pd.notnull(portInput['Market Value USD GAAP']), sumFields].groupby(groupByFields).sum()

    sumFields = groupByFields.copy()
    sumFields.append('Market Value with Accrued Int USD GAAP')
    mv_acc = portInput.loc[pd.notnull(portInput['Market Value with Accrued Int USD GAAP']), sumFields].groupby(
        groupByFields).sum()

    sumFields = groupByFields.copy()
    sumFields.append('Book Value USD STAT')
    bv = portInput.loc[pd.notnull(portInput['Book Value USD STAT']), sumFields].groupby(groupByFields).sum()

    sumFields = groupByFields.copy()
    sumFields.append('Book Value With Accrued Int USD STAT')
    bv_acc = portInput.loc[pd.notnull(portInput['Book Value With Accrued Int USD STAT']), sumFields].groupby(
        groupByFields).sum()

    merge = pd.merge(left=mv, left_index=True, right=mv_acc, right_index=True, how='outer')
    merge = pd.merge(left=merge, left_index=True, right=bv, right_index=True, how='outer')
    merge = pd.merge(left=merge, left_index=True, right=bv_acc, right_index=True, how='outer')

    for key, val in reportFields.items():
        ds = portInput[pd.notnull(portInput[key])].groupby(groupByFields).apply(wavg(key, val))
        df = pd.DataFrame(data=ds, columns=[key])
        merge = pd.merge(left=merge, left_index=True, right=df, right_index=True, how='outer')

    asset_count = merge.shape[0]
    cal_category    = []
    cal_asset_class = []
    cal_rating      = []
    
    merge.fillna(0, inplace=True)
    
    for idx in range(0, asset_count, 1):
        cal_category.append(merge.index[idx][0])
        cal_asset_class.append(merge.index[idx][1])
        cal_rating.append(merge.index[idx][2])
    
    merge['category_f']     = cal_category
    merge['asset_class_f'] = cal_asset_class
    merge['rating_f']       = cal_rating


#    Private Equity MV ajustment based on SPX
    pe_return = IAL_App.eval_PE_return(eval_date, valDate_base)
    mv_adj = []
    mv_acc = []
    for index, row in merge.iterrows():
        if row['asset_class_f'] == "Private Equity Fund":
            mv_adj.append(row['Market Value USD GAAP'] * (1 + pe_return) )
            mv_acc
        else:
            mv_adj.append(row['Market Value USD GAAP'])

    merge['mv_adj'] = mv_adj
    
#   MV * Duration Calculations
    merge['mv_dur']         = merge['mv_adj'] * merge['Effective Duration (WAMV)'] 
    merge['acc_int']        = merge['Market Value with Accrued Int USD GAAP'] - merge['Market Value USD GAAP']
    merge['mv_acc_int_adj'] = merge['mv_adj'] + merge['acc_int']

    
#   Remove ModCo derivative
    for i in range(0, len(merge.loc[('ModCo','Derivative'), "Market Value USD GAAP"]) , 1):
        merge.loc[('ModCo','Derivative'), "Market Value USD GAAP"][i]                  = ModCo_Cur_Der
        merge.loc[('ModCo','Derivative'), "Market Value with Accrued Int USD GAAP"][i] = ModCo_Cur_Der
        merge.loc[('ModCo','Derivative'), "mv_adj"][i]         = ModCo_Cur_Der   
        merge.loc[('ModCo','Derivative'), "mv_acc_int_adj"][i] = ModCo_Cur_Der
        
#   Rectify the derivative on 1-day lag  
    try:
        asset_file_T_plus_1 = pd.ExcelFile(asset_fileName_T_plus_1)
        asset_T_plus_1 = pd.read_excel(asset_file_T_plus_1, sheet_name='AssetSummaryFromPython')
        
        der_T_plus_1_mv_USD_GAAP    = asset_T_plus_1.loc[(asset_T_plus_1.Category == 'ModCo') & (asset_T_plus_1['AIG Asset Class 3'] == 'Derivative'), "Market Value USD GAAP"].sum()
        der_T_plus_1_mv_adj         = asset_T_plus_1.loc[(asset_T_plus_1.Category == 'ModCo') & (asset_T_plus_1['AIG Asset Class 3'] == 'Derivative'), "mv_adj"].sum()
        der_T_plus_1_mv_acc_int_adj = asset_T_plus_1.loc[(asset_T_plus_1.Category == 'ModCo') & (asset_T_plus_1['AIG Asset Class 3'] == 'Derivative'), "mv_acc_int_adj"].sum()
                
        ori_der = merge.loc[('ModCo','Derivative'), "Market Value USD GAAP"].sum()
        print(str(eval_date) + '_Original: ' + str(ori_der) )
        print(str(eval_date) + '_Revised: '  + str(der_T_plus_1_mv_adj) )
        
        for i in range(0, len(merge.loc[('ModCo','Derivative'), "Market Value USD GAAP"]) , 1):            
            if i == 0:
                merge.loc[('ModCo','Derivative'), "Market Value USD GAAP"][i] = der_T_plus_1_mv_USD_GAAP
                merge.loc[('ModCo','Derivative'), "mv_adj"][i]                = der_T_plus_1_mv_adj
                merge.loc[('ModCo','Derivative'), "mv_acc_int_adj"][i]        = der_T_plus_1_mv_acc_int_adj
            else:   # if there is more than one row of ModCo derivatives
                merge.loc[('ModCo','Derivative'), "Market Value USD GAAP"][i] = 0
                merge.loc[('ModCo','Derivative'), "mv_adj"][i]                = 0
                merge.loc[('ModCo','Derivative'), "mv_acc_int_adj"][i]        = 0
                
        if output == 1:
            out_file = fileName[0:25] + "_summary_Der_revised.xlsx" 
            assetSummary = pd.ExcelWriter(out_file)
            merge.to_excel(assetSummary, sheet_name='AssetSummaryFromPython', index=True, merge_cells=False)
            assetSummary.save()
            """
            wb=xlw.Book.caller()
            wb.sheets[0].range('A1').value = merge
            wb.sheets[1].range('A1').value = portInput
            """
        return merge
         
    except:              
        if output == 1:
            out_file = fileName[0:25] + "_summary.xlsx"
            assetSummary = pd.ExcelWriter(out_file)
            merge.to_excel(assetSummary, sheet_name='AssetSummaryFromPython', index=True, merge_cells=False)
            assetSummary.save()
            """
            wb=xlw.Book.caller()
            wb.sheets[0].range('A1').value = merge
            wb.sheets[1].range('A1').value = portInput
            """
        return merge

#def actual_portfolio_feed(workDir, fileName, AssetRiskCharge):
    
#    os.chdir(workDir)
    
#    portFile = pd.ExcelFile(fileName)
#    portInput = pd.read_excel(portFile, sheet_name='Microstrategy_Holdings')
               
#    portInput = pd.merge(portInput, AssetRiskCharge, how ='left', left_on='BMA_Category', right_on='BMA_Category')
   
#    portInput['AssetCharge_Current'] = portInput.MV_USD_GAAP * portInput.Capital_factor_Current
#    portInput['AssetCharge_Future'] = portInput.MV_USD_GAAP * portInput.Capital_factor_Future
    
#    portInput['mv_dur']=portInput.MV_USD_GAAP * portInput['Effective Duration (WAMV)']
    
    # Existing Asset Charge    
#    portInput['FIIndicator'] = portInput.BMA_Category.apply(
#               lambda x: (0 if (x == 'Alternatives' or x == 'ML III' ) else 1))        
#    portInput['EquityIndicator'] = portInput.BMA_Category.apply(
#               lambda x: (1 if (x == 'Alternatives' or x == 'ML III') else 0))    
         
#    return portInput
        
def Asset_Adjustment_feed(AssetAdjustment):
    
    AssetRiskCharge = pd.DataFrame(BSCR_Cofig.BSCR_Asset_Risk_Charge_v1).transpose()
    AssetRiskCharge['BMA_Category'] = AssetRiskCharge.index 
    
    AssetAdjustment = pd.merge(AssetAdjustment, AssetRiskCharge, how ='left', left_on='BMA_Category', right_on='BMA_Category')
    
    AssetAdjustment['AssetCharge_Current'] = AssetAdjustment.MV_USD_GAAP * AssetAdjustment.Risk_Charge

    AssetAdjustment['AssetCharge_Future'] = AssetAdjustment.MV_USD_GAAP * AssetAdjustment.Risk_Charge
    
    # Existing Asset Charge    
    AssetAdjustment['FIIndicator'] = AssetAdjustment.BMA_Category.apply(
               lambda x: (0 if x == 'LOC' else 1))        
    AssetAdjustment['EquityIndicator'] = AssetAdjustment.BMA_Category.apply(
               lambda x: (1 if x == 'LOC' else 0))  
    
    return AssetAdjustment
    
def actual_portfolio_feed(eval_date, valDate_base, workDir, fileName, ALBA_fileName, output):
    #def actual_portfolio_feed(eval_date, valDate_base, workDir,fileName, mapping, ALBA, output, ratingMapFile):
    def wavg(val_col_name, wt_col_name):
        def inner(group):
            return (group[val_col_name] * group[wt_col_name]).sum() / group[wt_col_name].sum()

        inner.__name__ = 'wtd_avg'
        return inner
    
    curr_dir = os.getcwd()
    os.chdir(workDir)

    portFile = pd.ExcelFile(fileName)
    #mapFile = pd.ExcelFile(mapping)
    
    try:
        albaFile = pd.ExcelFile(ALBA_fileName)
        ALBA = pd.read_excel(albaFile)
    except:
        pass
    
    #    if estimate, sheet_name='DSA RE Holdings'
    portInput = pd.read_excel(portFile, sheet_name='Microstrategy_Holdings', skiprows=[0, 1, 2, 3, 4, 5, 6])  
    leMap = pd.DataFrame(Rating_Cofig.Legal_Entity)

    RaMap_sp = pd.DataFrame(Rating_Cofig.SP_Rating, index=['BSCR rating_SP']).transpose()
    RaMap_sp["S&P"] = RaMap_sp.index
    
    RaMap_moodys = pd.DataFrame(Rating_Cofig.Moodys_Rating, index=['BSCR rating_Moodys']).transpose()
    RaMap_moodys["Moody's"] = RaMap_moodys.index
    
    RaMap_fitch = pd.DataFrame(Rating_Cofig.Fitch_Rating, index=['BSCR rating_Fitch']).transpose()
    RaMap_fitch["Fitch"] = RaMap_fitch.index
    
    RaMap_aig = pd.DataFrame(Rating_Cofig.AIG_Rating, index=['BSCR rating_AIG']).transpose()
    RaMap_aig["AIG Rating"] = RaMap_aig.index
    
    AsMap = pd.DataFrame(Rating_Cofig.AC_Mapping_to_BMA, index=['BMA Asset Category']).transpose()
    AsMap['AIG Asset class 3'] = AsMap.index 
    
    RcMap = pd.DataFrame(BSCR_Cofig.BSCR_Asset_Risk_Charge_v1).transpose()
    RcMap['BMA_Category'] = RcMap.index
    
    portInput = portInput.dropna(axis=0, how='all')
    portInput = portInput.dropna(axis=1, how='all')

    portInput = portInput.merge(leMap, how='left', left_on=['Owning Entity Name', 'Owning Entity GEMS ID'],
                                right_on=['Owning Entity Name', 'Owning Entity GEMS ID'])
    
    ratingMap = pd.DataFrame(Rating_Cofig.Rating)

    portInput = portInput.merge(ratingMap, how='left', left_on=['NAIC Rating', 'AIG Derived Rating'],
                                right_on=['NAIC Rating', 'AIG Derived Rating'])
    
    # Split out ML-III B Notes
    portInput['AIG Asset Class 3'] = np.where((portInput['Issuer Name'] == 'LSTREET II, LLC'), "ML-III B-Notes",
                                              portInput['AIG Asset Class 3'])

    # Handling surplus account
    portInput['SurplusAccount'] = 'Not-Surplus'

    portInput['SurplusAccount'] = np.where(
        ((portInput['Category'] == "Surplus") & (portInput['Strategy (Hld) Long Desc'] == "SAM RE OVERSEAS POOL LIFE")),
        "Long Term Surplus", portInput['SurplusAccount'])

    portInput['SurplusAccount'] = np.where(
        ((portInput['Category'] == "Surplus") & (portInput['Strategy (Hld) Long Desc'] == "SAM RE OVERSEAS POOL PC")),
        "General Surplus", portInput['SurplusAccount'])

    portInput['SurplusAccount'] = np.where(
        ((portInput['SurplusAccount'] == 'Not-Surplus') &
         (portInput['Category'] == "Surplus") & (portInput['Encumbrance Program Level 4 Desc'] == 'DSA REINSURANCE PC')),
        "General Surplus", portInput['SurplusAccount'])

    portInput['SurplusAccount'] = np.where(
        ((portInput['SurplusAccount'] == 'Not-Surplus') &
         (portInput['Category'] == "Surplus") & (portInput['Encumbrance Program Level 4 Desc'] == 'DSA REINSURANCE LR')),
        "Long Term Surplus", portInput['SurplusAccount'])

    portInput['SurplusAccount'] = np.where(
        ((portInput['SurplusAccount'] == 'Not-Surplus') &
         (portInput['Category'] == "Surplus") & (
                 portInput['Encumbrance Program Level 4 Desc'] == 'DSA RE/AGL Trust- DSA REINSURANCE LR')),
        "Long Term Surplus", portInput['SurplusAccount'])

    portInput['SurplusAccount'] = np.where(
        ((portInput['SurplusAccount'] == 'Not-Surplus') &
         (portInput['Category'] == "Surplus") & (
                 portInput['Encumbrance Program Level 4 Desc'] == 'DSA RE/USL Trust - DSA REINSURANCE LR')),
        "Long Term Surplus", portInput['SurplusAccount'])

    portInput['SurplusAccount'] = np.where(
        ((portInput['SurplusAccount'] == 'Not-Surplus') &
         (portInput['Category'] == "Surplus") & (
                 portInput['Encumbrance Program Level 4 Desc'] == 'DSA RE/VALIC Trust - DSA REINSURANCE LR')),
        "Long Term Surplus", portInput['SurplusAccount'])

    portInput['Category'] = np.where(
        ((portInput['SurplusAccount'] == 'Not-Surplus') &
         (portInput['Category'] == "Surplus") & (portInput['Encumbrance Program Level 4 Desc'] == 'SOURCE UNDEFINED')),
        "Long Term Surplus", portInput['Category'])

    portInput.dropna(axis=0, how='all', subset=['Category'], inplace=True)

    portInput['Category'] = np.where((portInput['SurplusAccount'] != 'Not-Surplus'),
                                     portInput['SurplusAccount'], portInput['Category'])
       
    ###-----Only for 4Q18 72M ModCo to LT surplus reclass-----###
    portInput['Category'] = np.where(
        ((portInput['Category'] == 'ModCo') &
         (portInput['Base Line Of Business Code'] == 'SOURCE UNDEFINED')),
        'Long Term Surplus', portInput['Category'])
    ###-----Only for 4Q18 72M ModCo to LT surplus reclass-----###
    
    portInput['Fort Re Corp Segment'] = portInput['Category']

    # clean up fake booking due to accounting system migration
    portInput = portInput[[not v.startswith('F-') for (i, v) in portInput['Portfolio (Source) Long Name'].iteritems()]]
    
    if valDate_base == datetime.datetime(2018, 12, 31, 0, 0):
        # zero out non-ALBA derivatives
        portInput['Market Value USD GAAP'] = np.where(
                ((portInput['AIG Asset Class 3'] =='Derivative') & (portInput['Owning Entity Name'] !='American International Reinsurance Company, Ltd.')),
                0, portInput['Market Value USD GAAP'])
    
    portInput['MV_USD_GAAP'] = portInput['Market Value USD GAAP']
    
    # Assign number scale to ratings
    portInput = portInput.merge(RaMap_sp, how = 'left', left_on = 'S&P Rating', right_on = 'S&P')\
                        .rename(columns = {'BSCR rating_SP': 'S&P_num'})\
                        .drop(columns = 'S&P')
 
    portInput = portInput.merge(RaMap_moodys, how = 'left', left_on = "Moody's Rating", right_on = "Moody's")\
                        .rename(columns = {'BSCR rating_Moodys': 'Moody_num'})\
                        .drop(columns = "Moody's")
                        
    portInput = portInput.merge(RaMap_fitch, how = 'left', left_on = 'Fitch Rating', right_on = 'Fitch')\
                        .rename(columns = {'BSCR rating_Fitch': 'Fitch_num'})\
                        .drop(columns = 'Fitch')

    portInput = portInput.merge(RaMap_aig, how = 'left', left_on = 'AIG Derived Rating', right_on = 'AIG Rating')\
                        .rename(columns = {'BSCR rating_AIG': 'AIG_num'})\
                        .drop(columns = 'AIG Rating')

    # Assign BSCR rating
    portInput['Mapped_BSCR_Rating'] = 0
   # ALBA and modco derivatives BSCR 3 equivelant rating 
    portInput['Mapped_BSCR_Rating'] = np.where(
            (portInput['AIG Asset Class 3'] =='Derivative'),3, portInput['Mapped_BSCR_Rating'])
    # Private placement bonds NAIC rating + 2
    portInput['Mapped_BSCR_Rating'] = np.where(
            ((portInput['Mapped_BSCR_Rating'] == 0) & (portInput['NAIC Rating Band STAT 2'] != "SOURCE UNDEFINED") & ((portInput['Analytical Segment 3'] == 'High Grade Corps/BnkLns (Private)')|(portInput['Analytical Segment 3'] == 'High Yield Corps/BnkLns (Private)'))),
            portInput['NAIC Rating Band STAT 2'].str.replace('SOURCE UNDEFINED', '0').fillna(0). astype(int) + 2, portInput['Mapped_BSCR_Rating'])
    # no rating agency and no AIG derived rating -> 8
    portInput['Mapped_BSCR_Rating'] = np. where(
            ((portInput['Mapped_BSCR_Rating'] == 0) & (portInput[['S&P_num', 'Moody_num', 'Fitch_num', 'AIG_num']].sum(axis = 1) == 0)), 8, portInput['Mapped_BSCR_Rating'])     
    # no rating agency ratings, assign AIG derived rating
    portInput['Mapped_BSCR_Rating'] = np. where(
            ((portInput['Mapped_BSCR_Rating'] == 0) & ((portInput[['S&P_num', 'Moody_num', 'Fitch_num']].sum(axis = 1) == 0) & (portInput['AIG_num'] != 0))), portInput['AIG_num'], portInput['Mapped_BSCR_Rating'])
    # take max of rating agency ratings if they are available
    portInput['Mapped_BSCR_Rating'] = np. where(
            ((portInput['Mapped_BSCR_Rating'] == 0) & (portInput[['S&P_num', 'Moody_num', 'Fitch_num']].sum(axis = 1) != 0)), portInput[['S&P_num', 'Moody_num', 'Fitch_num']].max(axis = 1), portInput['Mapped_BSCR_Rating'])
     # NA RMBS CMBS   NAIC 1 rated 
    portInput['Mapped_BSCR_Rating'] = np. where(
            (((portInput['AIG Asset Class 3'] =='CMBS Agency') | (portInput['AIG Asset Class 3'] =='CMBS Non-Agency') | (portInput['AIG Asset Class 3'] =='RMBS Agency') | (portInput['AIG Asset Class 3'] =='RMBS Non-Agency')) & (portInput['NAIC Rating Band STAT 2'].str.replace('SOURCE UNDEFINED', '0').fillna(0). astype(int) ==1)\
             & (portInput['Mapped_BSCR_Rating'] >3)), 3, portInput['Mapped_BSCR_Rating'])
      
    portInput['Mapped_BSCR_Rating'] = np. where(
            (((portInput['AIG Asset Class 3'] =='CMBS Agency') | (portInput['AIG Asset Class 3'] =='CMBS Non-Agency') | (portInput['AIG Asset Class 3'] =='RMBS Agency') | (portInput['AIG Asset Class 3'] =='RMBS Non-Agency')) & (portInput['NAIC Rating Band STAT 2'].str.replace('SOURCE UNDEFINED', '0').fillna(0). astype(int) > 1)),\
              portInput['NAIC Rating Band STAT 2'].str.replace('SOURCE UNDEFINED', '0').fillna(0). astype(int) + 2, portInput['Mapped_BSCR_Rating'])      

  # Merge BMA asset class
    portInput = portInput.merge(AsMap, how='left', left_on=['AIG Asset Class 3'],
                                right_on=['AIG Asset class 3']).drop(columns = 'AIG Asset class 3')
    portInput['BMA Asset Category'] = np. where(
            portInput['Issuer Name'] =='LSTREET II, LLC', 'Alternatives', portInput['BMA Asset Category'])
    portInput['BMA Asset Category'] = np. where(
            ((portInput['BMA Asset Category'] =='Bonds Cash and Govt') & (portInput['AIG Asset Class 3'] !="Cash") & (portInput['Mapped_BSCR_Rating']>2)), 
            "Bonds", portInput['BMA Asset Category'])
    portInput['BMA Asset Category'] = np. where(
            ((portInput['AIG Asset Class 3'] =="Derivative")), 
            "Bonds", portInput['BMA Asset Category'])
    
  # Combine ratings and asset class
    portInput['BMA_Category'] = portInput['BMA Asset Category']
    portInput['BMA_Category'] = np.where(
            portInput['Issuer Name'] =='LSTREET II, LLC', 'ML III', portInput['BMA_Category'])
    portInput['Mapped_BSCR_Rating'] = portInput['Mapped_BSCR_Rating'].astype(int)
    portInput['BMA_Category'] = np.where(
            ((portInput['BMA_Category'] == 'Bonds') | (portInput['BMA_Category'] == 'CMBS') | (portInput['BMA_Category'] == 'RMBS')),
            portInput['BMA_Category'] + "_" + portInput['Mapped_BSCR_Rating'].map(str), portInput['BMA_Category'])
 
    portInput = portInput.rename(columns = {'BMA Asset Category': 'BMA_Asset_Class'})

   # load ALBA duration and merge to portInput
    try:
        ALBA['dur'] = -ALBA['IR01']/ALBA['USD_MTM'] * 10000
        ALBA['POS_ID'] = ALBA['POS_ID'].astype(str)
        portInput['Lot Number DESC'] = portInput['Lot Number DESC'].astype(str)
        portInput = portInput.merge(ALBA[['POS_ID','dur']], how = 'left', left_on = 'Lot Number DESC', right_on = 'POS_ID').drop(columns = 'POS_ID')
        portInput['Effective Duration (WAMV)'] = portInput['Effective Duration (WAMV)'].fillna(portInput['dur'])
        portInput.drop(columns = 'dur')
    except:
        pass
    
    # Split out ML III Assets for concentration charge 
    portInput['Issuer Name'] = np.where(
            portInput['Issuer Name'] == 'LSTREET II, LLC', portInput['Issuer Name'] + '_' + portInput['Sec ID ID'].map(str), portInput['Issuer Name'])
    
    
    # Calculate cusip level charge
    portInput = portInput.merge(RcMap, how='left', left_on=['BMA_Category'],
                                right_on=['BMA_Category'])
    
    portInput['AssetCharge_Current'] = portInput['Market Value USD GAAP'] * portInput.Risk_Charge
    portInput['AssetCharge_Future'] = portInput['Market Value USD GAAP'] * portInput.Risk_Charge
    
    portInput['mv_dur']=portInput['Market Value USD GAAP'] * portInput['Effective Duration (WAMV)']
    
    # Existing Asset Charge    
    portInput['FIIndicator'] = portInput.BMA_Category.apply(
               lambda x: (0 if (x == 'Alternatives' or x == 'ML III' ) else 1))        
    portInput['EquityIndicator'] = portInput.BMA_Category.apply(
               lambda x: (1 if (x == 'Alternatives' or x == 'ML III') else 0))  
    
    portInput['FI Risk'] = 0
    portInput['FI Risk'] = np.where(
            portInput['FIIndicator'] == 1, portInput['AssetCharge_Current'], portInput['FI Risk'])
    portInput['Eq Risk_Current'] = 0
    portInput['Eq Risk_Current'] = np.where(
            portInput['EquityIndicator'] == 1, portInput['AssetCharge_Current'], portInput['Eq Risk_Current'])
    portInput['Eq Risk_Future'] = 0
    portInput['Eq Risk_Future'] = np.where(
            portInput['EquityIndicator'] == 1, portInput['AssetCharge_Future'], portInput['Eq Risk_Future'])
    
    portInput = portInput.drop_duplicates() 
    
    if output == 1:
        out_file = fileName + "_summary_test.xlsx" ### Vincent update 05/27/2019
        assetSummary = pd.ExcelWriter(out_file)
        portInput.to_excel(assetSummary, sheet_name='AssetSummaryFromPython', index=True, merge_cells=False)
        assetSummary.save()

    os.chdir(curr_dir)
    return portInput

#    ### === Prepare Asset Summary File === ###
#
#    ### This will distort BSCR calcualtion in 'Actual' ###
#    # Default setting NA 'AIG Derived Rating' to 'BBB'
#    portInput['AIG Derived Rating'].fillna('NA-BBB', inplace=True)
#    
#    portInput['AIG Derived Rating Update'] = portInput['AIG Derived Rating']
#
#    portInput['AIG Derived Rating Update'] = np.where(((portInput['AIG Asset Class 3'] == 'CMBS Agency') | (
#            portInput['AIG Asset Class 3'] == 'CMBS Non-Agency') | (portInput['AIG Asset Class 3'] == 'RMBS Agency') | (
#                                                               portInput['AIG Asset Class 3'] == 'RMBS Non-Agency')),
#                                                      portInput['Derived Rating Modified'], portInput['AIG Derived Rating'])
#    
#    # temporarily write to file for validation purpose
#    # portWriter = pd.ExcelWriter('./output/FRL_0228.xlsx')
#    # portInput.to_excel(portWriter, sheet_name='asset_port', index=False)
#    # portWriter.save()
#
#    groupByFields = ['Category', 'AIG Asset Class 3', 'AIG Derived Rating Update']
#
#    reportFields = {"YTW": "Market Value USD GAAP", \
#                    "OAS": "Market Value USD GAAP", \
#                    "Effective Duration (WAMV)": "Market Value USD GAAP", \
#                    "Effective Convexity": "Market Value USD GAAP", \
#                    "Spread Duration": "Market Value USD GAAP", \
#                    "Spread Convexity": "Market Value USD GAAP", \
#                    "WAL": "Quantity", \
#                    "KRD 1M": "Market Value USD GAAP", \
#                    "KRD 2M": "Market Value USD GAAP", \
#                    "KRD 3M": "Market Value USD GAAP", \
#                    "KRD 6M": "Market Value USD GAAP", \
#                    "KRD 9M": "Market Value USD GAAP", \
#                    "KRD 1Y": "Market Value USD GAAP", \
#                    "KRD 2Y": "Market Value USD GAAP", \
#                    "KRD 3Y": "Market Value USD GAAP", \
#                    "KRD 5Y": "Market Value USD GAAP", \
#                    "KRD 7Y": "Market Value USD GAAP", \
#                    "KRD 10Y": "Market Value USD GAAP", \
#                    "KRD 15Y": "Market Value USD GAAP", \
#                    "KRD 20Y": "Market Value USD GAAP", \
#                    "KRD 30Y": "Market Value USD GAAP"}
#
#    sumFields = groupByFields.copy()
#    sumFields.append('Market Value USD GAAP')
#    mv = portInput.loc[pd.notnull(portInput['Market Value USD GAAP']), sumFields].groupby(groupByFields).sum()
#
#    sumFields = groupByFields.copy()
#    sumFields.append('Market Value with Accrued Int USD GAAP')
#    mv_acc = portInput.loc[pd.notnull(portInput['Market Value with Accrued Int USD GAAP']), sumFields].groupby(
#        groupByFields).sum()
#
#    sumFields = groupByFields.copy()
#    sumFields.append('Book Value USD STAT')
#    bv = portInput.loc[pd.notnull(portInput['Book Value USD STAT']), sumFields].groupby(groupByFields).sum()
#
#    sumFields = groupByFields.copy()
#    sumFields.append('Book Value With Accrued Int USD STAT')
#    bv_acc = portInput.loc[pd.notnull(portInput['Book Value With Accrued Int USD STAT']), sumFields].groupby(
#        groupByFields).sum()
#
#    merge = pd.merge(left=mv, left_index=True, right=mv_acc, right_index=True, how='outer')
#    merge = pd.merge(left=merge, left_index=True, right=bv, right_index=True, how='outer')
#    merge = pd.merge(left=merge, left_index=True, right=bv_acc, right_index=True, how='outer')
#
#    for key, val in reportFields.items():
#        ds = portInput[pd.notnull(portInput[key])].groupby(groupByFields).apply(wavg(key, val))
#        df = pd.DataFrame(data=ds, columns=[key])
#        merge = pd.merge(left=merge, left_index=True, right=df, right_index=True, how='outer')
#
#    asset_count = merge.shape[0]
#    cal_category    = []
#    cal_asset_class = []
#    cal_rating      = []
#    
#    merge.fillna(0, inplace=True)
#    
#    for idx in range(0, asset_count, 1):
#        cal_category.append(merge.index[idx][0])
#        cal_asset_class.append(merge.index[idx][1])
#        cal_rating.append(merge.index[idx][2])
#    
#    merge['category_f']     = cal_category
#    merge['asset_class_f']  = cal_asset_class
#    merge['rating_f']       = cal_rating
#
#
##    Private Equity MV ajustment based on SPX
#    pe_return = IAL_App.eval_PE_return(eval_date, valDate_base)
#    mv_adj = []
#    mv_acc = []
#    for index, row in merge.iterrows():
#        if row['asset_class_f'] == "Private Equity Fund":
#            mv_adj.append(row['Market Value USD GAAP'] * (1 + pe_return) )
#            mv_acc
#        else:
#            mv_adj.append(row['Market Value USD GAAP'])
#
#    merge['mv_adj'] = mv_adj
#    
##   MV * Duration Calculations
#    merge['mv_dur']         = merge['mv_adj'] * merge['Effective Duration (WAMV)'] 
#    merge['acc_int']        = merge['Market Value with Accrued Int USD GAAP'] - merge['Market Value USD GAAP']
#    merge['mv_acc_int_adj'] = merge['mv_adj'] + merge['acc_int']
#    
#    if output == 1:
#        out_file = fileName[0:7] + "_summary.xlsx" ### fileName[0:25]
#        assetSummary = pd.ExcelWriter(out_file)
#        merge.to_excel(assetSummary, sheet_name='AssetSummaryFromPython', index=True, merge_cells=False)
#        assetSummary.save()
#        """
#        wb=xlw.Book.caller()
#        wb.sheets[0].range('A1').value = merge
#        wb.sheets[1].range('A1').value = portInput
#        """
##    return merge   
##       
##    if output == 1:
##        out_file = fileName[0:7] + "_summary_test.xlsx" ### Vincent update 05/27/2019
##        assetSummary = pd.ExcelWriter(out_file)
##        portInput.to_excel(assetSummary, sheet_name='AssetSummaryFromPython', index=True, merge_cells=False)
##        assetSummary.save()
#
#    return portInput, merge;


   
    
    
    
    
    
    