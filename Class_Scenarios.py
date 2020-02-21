import Lib_Market_Akit   as IAL_App

class Scenario():
    def __init__(self, val_date, scen_date, config_scen):
        self._val_date                = val_date
        self._scen_date               = scen_date
        self._config_scen             = config_scen
        self._scen_name               = config_scen['Scen_Name']
        self._IR_Curve_USD            = None
        self._IR_Curve_GBP            = None

    def setup_scen(self):
        self._IR_Curve_USD = IAL_App.load_BMA_Std_Curves(self._val_date, 'USD', self._scen_date, IR_shift = self._config_scen['IR_Parallel_Shift_bps'])       
        self._IR_Curve_GBP = IAL_App.load_BMA_Std_Curves(self._val_date, 'GBP', self._scen_date, IR_shift = self._config_scen['IR_Parallel_Shift_bps'])



"""
Scenarios Naming convension 

In BondEdge / Redshift DB:
    
    BMA Scenarios:
        Baseline: BMABASELINETERASPAR
        Scenario 1-8: BMASCENxTERASPAR
        
    NY Scenarios:
        NY1-7: NYx
        LRT: LRT
        
    ALBA: ALBA
        
    Sensitive Scenarios:
        UP: BMAUPxBPS
        DOWN: BMADOWNxBPS
        COMP: COMP
        SFP: SFP



"""