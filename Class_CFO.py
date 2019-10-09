import pandas as pd
import Class_Corp_Model as Corpclass
import Lib_Corp_Model as Corp
import Lib_Corp_Model_Forecast as Corp_Proj


class cfo():
    def __init__(self, val_date, date_start, freq, date_end, scen, actual_estimate, input_liab_val_base, input_liab_val_alt, input_proj_cash_flows):
        self._val_date                = val_date
        self._date_start              = date_start
        self._freq                    = freq
        self._date_end                = date_end
        self._scenario                = scen
        self._actual_estimate         = actual_estimate
        self._input_liab_val_base     = input_liab_val_base
        self._input_liab_val_alt      = input_liab_val_alt
        self._input_proj_cash_flows   = input_proj_cash_flows
        self._dates                   = None
        self._liab_val_base           = None
        self._liab_summary_base       = None
        self._liab_val_alt            = None
        self._proj_cash_flows         = None
        self._proj_cash_flows_summary = None

        # adding objects 
        self.fin_proj = {}

    def load_dates(self):
        dates = [self._val_date]
        dates.extend(list(pd.date_range(start=self._date_start, end=self._date_end, freq=self._freq)))
        self._proj_t = len(dates)
        self._dates = [dates[i].date() for i in range(self._proj_t)]

    def init_fin_proj(self):        
        for t in range(0, self._proj_t, 1):
            self.fin_proj[t] = {
                'date'    : self._dates[t],
                'Forecast': Corpclass.EBS_Dashboard(self._dates[t], self._actual_estimate, self._date_start), 
                'Econ_Scen' : {}
                }
            

    def set_base_cash_flow(self): 
        self._liab_val_base = Corp.get_liab_cashflow(
                           self._actual_estimate, 
                           self._val_date, 
                           self._input_liab_val_base['CF_Database'], 
                           self._input_liab_val_base['CF_TableName'], 
                           self._input_liab_val_base['Step1_Database'], 
                           self._input_liab_val_base['PVBE_TableName'], 
                           self._input_liab_val_base['bindingScen'],
                           self._input_liab_val_base['numOfLoB'],
                           self._input_liab_val_base['Proj_Year'],
                           self._input_liab_val_base['work_dir'], 
                           self._input_liab_val_base['cash_flow_freq'] )
        
    def set_base_projection(self): 
        self._proj_cash_flows = Corp.get_liab_cashflow(
                           self._actual_estimate, 
                           self._val_date, 
                           self._input_proj_cash_flows['CF_Database'], 
                           self._input_proj_cash_flows['CF_TableName'], 
                           self._input_proj_cash_flows['Step1_Database'], 
                           self._input_proj_cash_flows['PVBE_TableName'], 
                           self._input_proj_cash_flows['projScen'],
                           self._input_proj_cash_flows['numOfLoB'],
                           self._input_proj_cash_flows['Proj_Year'],
                           self._input_proj_cash_flows['work_dir'], 
                           self._input_proj_cash_flows['cash_flow_freq'] )  
        
    def set_forecasting_scalar(self, file_name, work_dir):
        self._scalar = Corp_Proj.load_forecasting_scalar(self.fin_proj, self._val_date, file_name, work_dir)
        
    def set_LOC_Assumption(self, file_name, work_dir):
        self._loc_input = Corp_Proj.load_LOC_Assumption(self.fin_proj, self._val_date, file_name, work_dir)
        
    def set_tarcap_Assumption(self, file_name, work_dir):
        self._tarcap_input = Corp_Proj.load_TarCap_Assumption(self.fin_proj, self._val_date, file_name, work_dir) 
    
    def set_surplus_split(self, file_name, work_dir):
        self._surplus_split = Corp_Proj.load_surplus_split(self.fin_proj, self._val_date, file_name, work_dir)
  
    def set_base_liab_value(self):
        self._liab_val_base = Corp.Set_Liab_Base(self._val_date, self._input_liab_val_base['curve_type'], self._input_liab_val_base['base_GBP'], self._input_liab_val_base['numOfLoB'], self._liab_val_base, self._input_liab_val_base['liab_benchmark'])

    def set_base_liab_summary(self):
        self._liab_summary_base = Corp.summary_liab_analytics(self._liab_val_base, self._input_liab_val_base['numOfLoB'])
        
    def run_TP_forecast(self, input_irCurve_USD = 0, input_irCurve_GBP = 0):
        Corp_Proj.run_TP_forecast(self.fin_proj, self._proj_t, self._val_date, self._liab_val_base, self._liab_summary_base, self._input_liab_val_base['curve_type'], self._input_liab_val_base['numOfLoB'], self._input_liab_val_base['base_GBP'], base_irCurve_USD = input_irCurve_USD, base_irCurve_GBP = input_irCurve_GBP, cf_proj_end_date = self._input_liab_val_base['cf_proj_end_date'], cash_flow_freq = self._input_liab_val_base['cash_flow_freq'], recast_risk_margin = self._input_liab_val_base['recast_risk_margin'])
    
    def run_fin_forecast(self):
        Corp_Proj.run_fin_forecast(self.fin_proj, self._proj_t, self._input_liab_val_base['numOfLoB'], self._proj_cash_flows)        

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
