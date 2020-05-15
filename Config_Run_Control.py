# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 01:07:39 2019

@author: seongpar
"""

#import datetime       as dt
# import Lib_Corp_Model as Corp
import Lib_BSCR_Calc  as BSCR_calc
import Config_BSCR    as BSCR_Config
import pandas as pd

def update_runControl(run_control):
    
    if run_control._run_control_ver == '2018Q4_Base':
        ### Hard-coded inputs from I_Control
        run_control.time0_LTIC = 97633492
        run_control.surplus_life_0 = 1498468068.62392
        run_control.surplus_PC_0 = 1541220172.25324
        run_control.I_SFSLiqSurplus = 1809687680.14178

        run_control.GAAP_Reserve_method     = 'Roll-forward'  #### 'Product_Level" or 'Roll-forward'
        ### Update assumptions as needed #####
        # Load ModCo Asset Projection
        BSCR_mapping = run_control.modco_BSCR_mapping
        BSCR_charge  = BSCR_Config.BSCR_Asset_Risk_Charge_v1
        
        run_control.asset_proj_modco           = pd.read_csv("L:\Global Profitability Standards and ALM\Legacy Portfolio\SAM RE\Fortitude-Re Asset Model Team\___Ad-Hoc___\Asset Category projection\cm_input_asset_category_proj_annual_20200515.csv")
        # run_control.asset_proj_modco           = pd.read_csv("### Please fill file path here ###")
        run_control.asset_proj_modco.columns   = ['val_date', 'proj_time', 'rowNo', 'LOB', 'asset_class', 'MV', 'BV', 'Dur', 'run_id']
        # run_control.asset_proj_modco           = Corp.get_asset_category_proj(run_control._val_date, 'alm', freq = run_control._freq)
        run_control.asset_proj_modco['MV_Dur'] = run_control.asset_proj_modco['MV'] * run_control.asset_proj_modco['Dur']
        run_control.asset_proj_modco['FI_Alts'] =  run_control.asset_proj_modco.apply(lambda x: 'Alts' if x['asset_class'] == 'Alts' else 'FI', axis=1)
        run_control.asset_proj_modco['risk_charge_factor'] \
        =  run_control.asset_proj_modco.apply(lambda \
               x: BSCR_calc.proj_BSCR_asset_risk_charge(BSCR_mapping[x['asset_class']], BMA_asset_risk_charge = BSCR_charge), axis=1)
        
        run_control.asset_proj_modco['asset_risk_charge']  = run_control.asset_proj_modco['MV'] * run_control.asset_proj_modco['risk_charge_factor']
        
        run_control.asset_proj_modco_agg                       = run_control.asset_proj_modco.groupby(['val_date', 'rowNo', 'proj_time', 'FI_Alts']).sum().reset_index()    
        run_control.asset_proj_modco_agg['Dur']                = run_control.asset_proj_modco_agg['MV_Dur'] / run_control.asset_proj_modco_agg['MV']
        run_control.asset_proj_modco_agg['risk_charge_factor'] = run_control.asset_proj_modco_agg['asset_risk_charge'] / run_control.asset_proj_modco_agg['MV']
        run_control.asset_proj_modco_agg.fillna(0, inplace=True)
        
        # Dividend Schedule
        run_control.proj_schedule[1]['dividend_schedule']     = 'Y'
        run_control.proj_schedule[1]['dividend_schedule_amt'] = 500000000
        run_control.proj_schedule[2]['dividend_schedule']     = 'Y'
        run_control.proj_schedule[2]['dividend_schedule_amt'] = 1000000000
        run_control.proj_schedule[3]['dividend_schedule']     = 'Y'
        run_control.proj_schedule[3]['dividend_schedule_amt'] = 1000000000
        
        # LOC SFS Limit
        SFS_limit = [ 0.25,
                     0.248285375,
                     0.252029898,
                     0.285955276,
                     0.38330347,
                     0.441096663,
                     0.460419183,
                     0.470052356,
                     0.462474131,
                     0.448079715,
                     0.42905067,
                     0.401161493,
                     0.374517694,
                     0.354974144,
                     0.312988995,
                     0.298355834,
                     0.301492895,
                     0.294050736,
                     0.284305953,
                     0.274386361,
                     0.264800284,
                     0.257449286,
                     0.253203818,
                     0.248658944,
                     0.240894683,
                     0.235788524,
                     0.224783331,
                     0.218340687,
                     0.214482419,
                     0.209553337,
                     0.208785641,
                     0.211190424,
                     0.210920573,
                     0.216687659,
                     0.222172075,
                     0.227580018,
                     0.232088173,
                     0.236832925,
                     0.241751243,
                     0.245726161,
                     0.248599255,
                     0.248058163,
                     0.246790226,
                     0.24740993,
                     0.247595613,
                     0.247582842,
                     0.244536254,
                     0.254065247,
                     0.246678196,
                     0.242226328,
                     0.25,
                     0.242866482,
                     0.244004135,
                     0.301949013,
                     0.244575476,
                     0.244081956,
                     0.243021021,
                     0.250817216,
                     0.252697673,
                     0.200005319,
                     0.200005319,
                     0.200005319,
                     0.200005319,
                     0.200005319,
                     0.200005319,
                     0.200005319,
                     0.200005319,
                     0.200005319,
                     0.200005319,
                     0.200005319,
                     0.200005319,
                     0.200005319,
                     0.200005319,
                     0.200005319,
                     0.200006653,
                     0.200011781,
                     0.2,
                     0.2,
                     0.2,
                     0.2]
        
        for i in range(min(len(run_control._dates), len(SFS_limit))):
            run_control.proj_schedule[i]['LOC_SFS_Limit'] = SFS_limit[i]
        
        # Initial and Ultimate Spread
        run_control.initial_spread = {
            'Term' : [1,	2,	3,	5,	7,	10,	20,	30 ],
            'AAA'  : [ 0.0016,	0.0028,	0.0035,	0.0037,	0.0042,	0.0054,	0.0069,	0.0084 ],
            'AA'   : [ 0.0019,	0.0034,	0.0042,	0.0048,	0.0055,	0.007,	0.0085,	0.0099 ],
            'A'	   : [ 0.0023,	0.0042,	0.0052,	0.0062,	0.0095,	0.0109,	0.0105,	0.0127 ],
            'BBB'  : [ 0.0044,	0.0082,	0.0092,	0.0114,	0.0156,	0.0162,	0.0161,	0.0183 ],
            'BB'   : [ 0.012,	0.0162,	0.0193,	0.0234,	0.0267,	0.0306,	0.0337,	0.0368 ],
            'B'	   : [ 0.0183,	0.0237,	0.0277,	0.0331,	0.0373,	0.0421,	0.046,	0.0499 ],
            'CCC'  : [ 0.0546,	0.0579,	0.0602,	0.0631,	0.0655,	0.0684,	0.0705,	0.0726 ]
        }
        
        run_control.ultimate_spread = {
            'Term' : [1,	2,	3,	5,	7,	10,	20,	30 ],
            'AAA'  : [ 0.0049,	0.0053,	0.0058,	0.0065,	0.0066,	0.0062,	0.0065,	0.008],
            'AA'   : [ 0.0053,	0.0059,	0.0066,	0.0076,	0.0081,	0.0081,	0.0091,	0.0107 ],
            'A'	   : [ 0.0073,	0.0081,	0.009,	0.0106,	0.0114,	0.0117,	0.0134,	0.0154 ],
            'BBB'  : [ 0.0123,	0.0136,	0.0149,	0.0173,	0.0187,	0.0196,	0.0219,	0.0238 ],
            'BB'   : [ 0.0295,	0.0311,	0.0328,	0.0357,	0.0375,	0.0386,	0.0407,	0.0421 ],
            'B'	   : [ 0.0492,	0.0569,	0.059,	0.0626,	0.0647,	0.0661,	0.068,	0.0681 ],
            'CCC'  : [ 0.1221,	0.1255,	0.1269,	0.1288,	0.1287,	0.1263,	0.1196,	0.1129 ]
        }
