#import os
import pandas as pd
import Class_Corp_Model as Corpclass
import Lib_Corp_Model as Corp
import Lib_Corp_Model_Forecast as Corp_Proj
import datetime as dt

class cfo():
    '''
    Input Variables:
        val_date:   valuation date; dt.datetime format; usually quarter end
        date_start: starting of projection dates; dt.datetime format; 
        freq:       frequency of projections; str "A" for annually, "Q" for quarterly
        date_end:   ending of projection dates; dt.datetime format;
        scen:       currently only "base" is supported
        actual_estimate:       str "Actual" or "Estimate"
        input_liab_val_base:   dict of information for reading base liability data
        input_liab_val_alt:    currently None
        input_proj_cash_flows: dict of information for reading cashflow projection
        run_control_ver:       the name of run control file; str
    '''
    
    def __init__(self, val_date, date_start, freq, date_end, scen, actual_estimate, input_liab_val_base, input_liab_val_alt, input_proj_cash_flows, run_control_ver):
        self._val_date                = val_date
        self._date_start              = date_start
        self._freq                    = freq
        self._date_end                = date_end
        self._scenario                = scen
        self._actual_estimate         = actual_estimate
        self._input_liab_val_base     = input_liab_val_base
        self._input_liab_val_alt      = input_liab_val_alt
        self._input_proj_cash_flows   = input_proj_cash_flows
        self._liab_val_base           = None
        self._liab_summary_base       = None
        self._liab_val_alt            = None
        self._proj_cash_flows         = None
        self._proj_cash_flows_summary = None
        self._run_control             = run_control(run_control_ver,
                                                    val_date = val_date, 
                                                    date_start = date_start, 
                                                    date_end = date_end, 
                                                    freq = freq) # A class below

        # adding objects 
        self.load_dates()
        self.fin_proj = {}
        

    def load_dates(self):
        dates = [self._val_date]
        dates.extend(list(pd.date_range(start=self._date_start, end=self._date_end, freq=self._freq)))
        self._proj_t = len(dates)
        self._dates = [dates[i].date() for i in range(self._proj_t)]
        
    # Temporarily loaded as pd.Series

    def init_fin_proj(self):        
        for t in range(0, self._proj_t, 1):
            self.fin_proj[t] = {
                'date'    : self._dates[t],
                'Forecast': Corpclass.EBS_Dashboard(self._dates[t], self._actual_estimate, self._val_date, 'Step_3'), 
                'Econ_Scen' : {}
                }
            
    def set_base_cash_flow(self): 
        self._liab_val_base = Corp.get_liab_cashflow(
                           actual_estimate = self._actual_estimate, 
                           valDate         = self._val_date, 
                           CF_Database     = self._input_liab_val_base['CF_Database'], 
                           CF_TableName    = self._input_liab_val_base['CF_TableName'], 
                           Step1_Database  = self._input_liab_val_base['Step1_Database'], 
                           PVBE_TableName  = self._input_liab_val_base['PVBE_TableName'], 
                           bindingScen     = self._input_liab_val_base['bindingScen'],
                           numOfLoB        = self._input_liab_val_base['numOfLoB'],
                           Proj_Year       = self._input_liab_val_base['Proj_Year'],
                           work_dir        = self._input_liab_val_base['work_dir'], 
                           freq            = self._input_liab_val_base['cash_flow_freq'] )
        
    def set_base_projection(self): 
        self._proj_cash_flows = Corp.get_liab_cashflow(
                                actual_estimate = self._actual_estimate, 
                                valDate         = self._val_date, 
                                CF_Database     = self._input_proj_cash_flows['CF_Database'], 
                                CF_TableName    = self._input_proj_cash_flows['CF_TableName'], 
                                Step1_Database  = self._input_proj_cash_flows['Step1_Database'], 
                                PVBE_TableName  = self._input_proj_cash_flows['PVBE_TableName'], 
                                bindingScen     = self._input_proj_cash_flows['projScen'],
                                numOfLoB        = self._input_proj_cash_flows['numOfLoB'],
                                Proj_Year       = self._input_proj_cash_flows['Proj_Year'],
                                work_dir        = self._input_proj_cash_flows['work_dir'], 
                                freq            = self._input_proj_cash_flows['cash_flow_freq'] )
  
    def set_base_liab_value(self, base_irCurve_USD, base_irCurve_GBP):
        self._liab_val_base = Corp.Set_Liab_Base(valDate       = self._val_date, 
                                                 curveType     = self._input_liab_val_base['curve_type'], 
                                                 curr_GBP      = self._input_liab_val_base['base_GBP'], 
                                                 numOfLoB      = self._input_liab_val_base['numOfLoB'], 
                                                 liabAnalytics = self._liab_val_base, 
                                                 rating        = self._input_liab_val_base['liab_benchmark'], 
                                                 irCurve_USD   = base_irCurve_USD, 
                                                 irCurve_GBP   = base_irCurve_GBP)

    def set_liab_GAAP_base(self):
        Corp.Set_Liab_GAAP_Base(self._val_date, self._run_control.GAAP_Reserve, self._liab_val_base)

    def set_base_liab_summary(self):
        self._liab_summary_base = Corp.summary_liab_analytics(self._liab_val_base, self._input_liab_val_base['numOfLoB'])
        
    def run_TP_forecast(self, input_irCurve_USD = 0, input_irCurve_GBP = 0):
        Corp_Proj.run_TP_forecast(fin_proj            = self.fin_proj, 
                                  proj_t              = self._proj_t, 
                                  valDate             = self._val_date, 
                                  liab_val_base       = self._liab_val_base, 
                                  liab_summary_base   = self._liab_summary_base, 
                                  input_liab_val_base = self._input_liab_val_base, 
                                  base_irCurve_USD    = input_irCurve_USD, 
                                  base_irCurve_GBP    = input_irCurve_GBP)

    def run_fin_forecast(self, Asset_holding, Asset_adjustment, base_irCurve_USD, Regime, work_dir):
        ####def run_fin_forecast(fin_proj, proj_t, numOfLoB, proj_cash_flows, Asset_holding, Asset_adjustment, run_control, valDate, curveType = 'Treasury', base_irCurve_USD = 0 ):        
        Corp_Proj.run_fin_forecast(fin_proj         = self.fin_proj, 
                                   proj_t           = self._proj_t, 
                                   numOfLoB         = self._input_liab_val_base['numOfLoB'], 
                                   proj_cash_flows  = self._proj_cash_flows, 
                                   Asset_holding    = Asset_holding, 
                                   Asset_adjustment = Asset_adjustment, 
                                   #SFS_BS_fileName  = SFS_BS_fileName, 
                                   Regime           = Regime, 
                                   work_dir         = work_dir, 
                                   run_control      = self._run_control, 
                                   valDate          = self._val_date, 
                                   curveType        = self._input_liab_val_base['curve_type'], 
                                   base_irCurve_USD = base_irCurve_USD)


    '''
    B 	business day frequency
    C 	custom business day frequency
    D 	calendar day frequency
    W 	weekly frequency
    M 	month end frequency
    SM 	semi-month end frequency (15th and end of month)
    BM 	business month end frequency
    CBM 	custom business month end frequency
    MS 	month start frequency
    SMS 	semi-month start frequency (1st and 15th)
    BMS 	business month start frequency
    CBMS 	custom business month start frequency
    Q 	quarter end frequency
    BQ 	business quarter end frequency
    QS 	quarter start frequency
    BQS 	business quarter start frequency
    A, Y 	year end frequency
    BA, BY 	business year end frequency
    AS, YS 	year start frequency
    BAS, BYS 	business year start frequency
    BH 	business hour frequency
    H 	hourly frequency
    T, min 	minutely frequency
    S 	secondly frequency
    L, ms 	milliseconds
    U, us 	microseconds
    N 	nanoseconds
    '''
    
class run_control(object):
    def __init__(self,
                 run_control_ver,
                 val_date = dt.datetime(2018, 12, 31), 
                 date_start = dt.datetime(2019, 12, 31), 
                 date_end = dt.datetime(2039, 12, 31), 
                 freq = 'A'):
        
        self._run_control_ver         = run_control_ver
        self._val_date                = val_date
        self._date_start              = date_start
        self._freq                    = freq
        self._date_end                = date_end
        self.Div_Cap_SFS_CnS          = 0.25
        self.Div_Cap_SFS_Cap          = 0.15
        self.dividend_model           = 'Aggregate capital target'
        self.DivFloorSwitch           = 'N' 
        self.div_SFSCapConstraint     = 'N'
        self.div_LiquidityConstraint  = 'Y'
        self.FI_Surplus_model_port    = {'Port1' : {'Maturity' : 6, 'Rating' : 'A', 'Weight' : 0.5}, 'Port2': {'Maturity' : 6, 'Rating' : 'BBB', 'Weight' : 0.5}}
        self.initial_spread           = {}
        self.ultimate_spread          = {}
        self.ultimate_period          = 5
        self.inv_mgmt_fee             = {'LPT' : 0.15 / 100, 'Surplus_FI'  : 0.15 / 100, 'Surplus_Alt'  : 0.15 / 100  }
        self.initial_LOC              = {'Tier2':  150000000, 'Tier3' :  400000000 }
        self.LOC_BMA_Limit            = {'Tier2':  0.667, 'Tier3_over_Tier1_2' :  0.1765, 'Tier3_over_Tier1' :  0.667 }
        self.LOC_SFS_Limit_YN         = 'N'
        self.proj_schedule            = self.init_schedule()
        self.asset_proj_modco         = None
        self.asset_proj_modco_agg     = None
        self.modco_BSCR_mapping       = {'IG'         : { 'Bonds_1': 0.0262, 'Bonds_2': 0.1243, 'Bonds_3': 0.2926, 'Bonds_4': 0.5073, 'Bonds_5': 0.0273, 'Bonds Cash and Govt': 0.0219}, 
                                         'New_Inv'    : { 'Bonds_3': 0.5,   'Bonds_4': 0.5 },
                                         'Structured' : { 'Bonds_1': 0.0015, 'Bonds_2': 0.0035, 'Bonds_3': 0.0048, 'CMBS_1': 0.0753, 'CMBS_2': 0.0857, 'CMBS_3': 0.0606, 'CMBS_4': 0.0102, 'CMBS_5': 0.0062, 'Other Commercial and Farm Mortgages': 0.3387,  'RMBS_1': 0.0024, 'RMBS_2': 0.2107, 'RMBS_3': 0.1818, 'RMBS_4': 0.0033, 'RMBS_6': 0.0100, 'RMBS_8': 0.0023},
                                         'HY'         : { 'Bonds_5': 0.6005, 'Bonds_6': 0.3663, 'Bonds_7': 0.0313, 'Bonds_8': 0.0019}, 
                                         'Alts'       : { 'Alternatives' : 1.0                 }
                                        }
        self.GAAP_Reserve_method     = 'Roll-forward'  #### 'Product_Level" or 'Roll-forward'        
    
    @property
    def val_date(self):
        return self._val_date.strftime('%Y-%m-%d')

    def load_dates(self):
        dates = [self._val_date]
        dates.extend(list(pd.date_range(start= self._date_start, end= self._date_end, freq= self._freq)))
        self._proj_t = len(dates)
        self._dates = [dates[i].date() for i in range(self._proj_t)]

    def load_excel_input(self, excelFile):
        self.Forecast_Scalars = excelFile.parse('Forecast_Scalars', index_col = 0)
        self.SurplusSplit_LR_PC = excelFile.parse('SurplusSplit_LR_PC', index_col = 0)
        self.ML_III_inputs = excelFile.parse('ML_III_inputs', index_col = 0)
        self.Asset_Adjustment = excelFile.parse('Asset_Adjustment')
        self.Asset_Risk_Charge = excelFile.parse('Asset_Risk_Charge')
        self.SFS_BS = excelFile.parse('SFS_BS')
        self.GAAP_Reserve = excelFile.parse('GAAP_Reserve')
        self.LPT_EPA_Dur = excelFile.parse('PC_EPA_Dur')
        
    def init_schedule(self):        
        self.load_dates()
        proj_schedule = {}
        for t in range(0, self._proj_t, 1):
            proj_schedule[t] = {
                'date'                  : self._dates[t],
                'div_earnings_pct'      : 1.0  ,
                'dividend_schedule'     : 'N'  ,
                'dividend_schedule_amt' : 0    ,
                'Target_ECR_Ratio'      : 1.5  ,
                'Capital_Pecking_Order' : 'Agg',
                'Actual_Capital_Ratio'  : 1.5  ,
                'Tax_Rate'              : 0.21 ,
                'LOC_fee'               : 0.54/100 if t <= 1 else 2.5/100,
                'PL_int_rate'           : 0.05,
                'LOC_SFS_Limit'         : 0.25
                }
            
        return proj_schedule


class liab_proj_items:
    
    '''
    Input Variables:
        cashFlow:   pandas dataframe of LBA outputs
        fin_proj:   basic financial reporting object
        run_contrl: run_control object
        t:          projection time, int, 0-70
        idx:        LOB ID, int, 1-45
    '''
    
    def __init__(self, cashFlow, fin_proj, run_contrl, t, idx):
        
        self.lobID       = idx
        self._scalar     = run_contrl.Forecast_Scalars.loc[idx]
        self._ccy_rate   = fin_proj[t]['Forecast'].liability['dashboard'][idx].ccy_rate
        self._cols_input = ['Total premium', 'Total net cashflow', 'GOE','GOE_F', 'aggregate cf', 'Total net face amount', 'Net benefits - death', \
                           'Net benefits - maturity', 'Net benefits - annuity', 'Net - AH benefits', 'Net benefits - P&C claims',                  \
                           'Net benefits - surrender', 'Total commission', 'Maintenance expenses', 'Net premium tax', 'Net cash dividends',        \
                           'Total Stat Res - Net Res', 'Total Tax Res - Net Res', 'UPR', 'BV asset backing liab', 'MV asset backing liab',         \
                           'Net investment Income', 'CFT reserve', 'Interest maintenance reserve (NAIC)', 'Accrued Income']
        
        items = cashFlow.loc[cashFlow['RowNo'] == t + 1, self._cols_input].sum() * self._ccy_rate ### Currency modification will be applied here
        
        self.each_prem          = items['Total premium']
        self.each_goe           = items['GOE'] / self._ccy_rate # No need for currency changes
        self.each_goe_f         = items['GOE_F'] / self._ccy_rate # No need for currency changes
        self.each_agg_cf        = items['aggregate cf']
        self.each_face          = items['Total net face amount']
        self.each_maturity      = items['Net benefits - maturity']
        self.each_ah_ben        = items['Net - AH benefits']
        self.each_gi_claim      = items['Net benefits - P&C claims']
        self.each_surrender     = items['Net benefits - surrender']
        self.each_commission    = items['Total commission']
        self.each_prem_tax      = items['Net premium tax']
        self.each_cash_div      = items['Net cash dividends']
        self.each_stat_rsv      = items['Total Stat Res - Net Res']
        self.each_tax_rsv       = items['Total Tax Res - Net Res']
        self.each_upr           = items['UPR']
        self.each_bva           = items['BV asset backing liab']
        self.each_mva           = items['MV asset backing liab']
        self.each_nii           = items['Net investment Income']
        self.each_cft_rsv       = items['CFT reserve']
        self.each_imr           = items['Interest maintenance reserve (NAIC)']
        self.each_acc_int       = items['Accrued Income']
        self.each_total_stat_rsv = self.each_stat_rsv + self.each_cft_rsv + self.each_imr + self.each_upr

        ######################## Scaled vector #################################
        ## Rsv scalar is applied on ALBA only for DTA Calc, Liab CFs shouldn't be affected; NO Rsv scalars needed for all other LOBs. (April 10/08/2019) ##
        if idx == 34:
            self.each_scaled_stat_rsv      = items['Total Stat Res - Net Res'] * self._scalar['STAT reserve (%)']
            self.each_scaled_tax_rsv       = items['Total Tax Res - Net Res'] * self._scalar['Tax reserve (%)']
            ## Coded for Validtion Purpose, which should be removed later ####################################    
            self.each_ncf                  = items['Total net cashflow'] * self._scalar['STAT reserve (%)']
            self.each_death                = items['Net benefits - death'] * self._scalar['STAT reserve (%)']
            self.each_annuity              = items['Net benefits - annuity'] * self._scalar['STAT reserve (%)']
            self.each_maint_exp            = items['Maintenance expenses'] * self._scalar['STAT reserve (%)']
            
        else:
            self.each_scaled_stat_rsv      = items['Total Stat Res - Net Res']
            self.each_scaled_tax_rsv       = items['Total Tax Res - Net Res']
            self.each_ncf                  = items['Total net cashflow']
            self.each_death                = items['Net benefits - death']
            self.each_annuity              = items['Net benefits - annuity']
            self.each_maint_exp            = items['Maintenance expenses']     

        self.each_scaled_total_stat_rsv = self.each_scaled_stat_rsv + self.each_cft_rsv + self.each_imr + self.each_upr 
        self.each_scaled_bva            = self.each_scaled_total_stat_rsv * self._scalar['BV of assets (%)']
        self.each_scaled_acc_int        = items['Accrued Income'] * self._scalar['Accrued Int (%)']
        
        if self.each_bva == 0:
            self.each_scaled_mva        = 0
            self.each_scaled_nii_abr    = 0
        else:
            self.each_scaled_mva        = self.each_scaled_bva * self._scalar['MV of assets (%)'] * self.each_mva / self.each_bva
            self.each_scaled_nii_abr    = self.each_nii * self.each_scaled_bva / self.each_total_stat_rsv 
            # NII from AXIS is adjusted for any scaling in BV of Assets
        
        ### temporarily subtract aggregate cash flows for each time ZZZZZ need to be refined to reflect the cash flow timing vs. valuation timing
        self.each_pv_be        = fin_proj[t]['Forecast'].liability['dashboard'][idx].PV_BE_net # + items['aggregate cf'] * self._ccy_rate 
        self.each_rm           = fin_proj[t]['Forecast'].liability['dashboard'][idx].Risk_Margin
        self.each_tp           = self.each_pv_be + self.each_rm
        self.GAAP_Reserve_disc = fin_proj[t]['Forecast'].liability['dashboard'][idx].GAAP_Reserve_disc
        self.GAAP_IRR          = fin_proj[t]['Forecast'].liability['dashboard'][idx].GAAP_IRR
        self.GAAP_Margin       = fin_proj[t]['Forecast'].liability['dashboard'][idx].GAAP_Margin        
        
        
        
        # self.each_LTIC  = (self.each_pv_be - pvbe secondary) * LTIC/(LR PVBE - LR PVBE seconddary) ### THIS NEEDS TO BE POPULATED AT LOB LEVEL
        self.each_pv_GOE = fin_proj[t]['Forecast'].liability['dashboard'][idx].PV_GOE
        if self.each_pv_be == 0:
            self.each_GOE_Provision = 0
        else:
            self.each_GOE_Provision = self.each_pv_GOE * self.each_tp / self.each_pv_be
        
        self.each_pvbe_sec     = fin_proj[t]['Forecast'].liability['dashboard'][idx].PV_BE_sec
        self.each_pvbe_sec_net = fin_proj[t]['Forecast'].liability['dashboard'][idx].PV_BE_sec_net
        
        ### Use PV_BE_net and PV_BE_sec_net
        pvbe_LR_nonALBA      = fin_proj[t]['Forecast'].liab_summary['dashboard']['LT']['PV_BE_net'] - fin_proj[t]['Forecast'].liability['dashboard'][34].PV_BE_net
        pvbe_sec_LR_nonALBA  = fin_proj[t]['Forecast'].liab_summary['dashboard']['LT']['PV_BE_sec_net'] - fin_proj[t]['Forecast'].liability['dashboard'][34].PV_BE_sec_net
        if idx >= 34 or pvbe_LR_nonALBA - pvbe_sec_LR_nonALBA == 0:
            self.each_pvbe_ratio = 0
        else:
            self.each_pvbe_ratio = (fin_proj[t]['Forecast'].liability['dashboard'][idx].PV_BE_net - self.each_pvbe_sec_net) / (pvbe_LR_nonALBA - pvbe_sec_LR_nonALBA)
        pvbe_Agg             = fin_proj[t]['Forecast'].liab_summary['dashboard']['Agg']['PV_BE_net']
        pvbe_sec_Agg         = fin_proj[t]['Forecast'].liab_summary['dashboard']['Agg']['PV_BE_sec_net']
        pvbe_diff_t0         = fin_proj[0]['Forecast'].liab_summary['dashboard']['Agg']['PV_BE_net'] - fin_proj[0]['Forecast'].liab_summary['dashboard']['Agg']['PV_BE_sec_net']
   
        if pvbe_diff_t0 == 0:
            self.ltic_agg = 0
        else:
            self.ltic_agg = (pvbe_Agg - pvbe_sec_Agg) / pvbe_diff_t0 * run_contrl.time0_LTIC
    
                  
    def _record(self, items, Dashboard_obj):
        
        Dashboard_obj._records['LOBs'].append(self.lobID)
        for i in items:
            if i in Dashboard_obj._records.keys():
                Dashboard_obj._records[i].append(getattr(self, i))
            else:
                Dashboard_obj._records[i] = [getattr(self, i)]
