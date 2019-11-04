# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 18:06:54 2019

@author: seongpar
"""

SP_Rating = {   'AAA' : 1 ,
                'AA+' : 2 ,
                'AA' : 2 ,
                'AA-' : 2 ,
                'A+' : 3 ,
                'A' : 3 ,
                'A-' : 3 ,
                'BBB+' : 4 ,
                'BBB' : 4 ,
                'BBB-' : 4 ,
                'BB+' : 5 ,
                'BB' : 5 ,
                'BB-' : 5 ,
                'B+' : 6 ,
                'B' : 6 ,
                'B-' : 6 ,
                'CCC+' : 7 ,
                'CCC' : 7 ,
                'CCC-' : 7 ,
                'CC' : 8 ,
                'D' : 8 ,
                'NR' : 0 
                }


Moodys_Rating = {   'Aaa' : 1 ,
                    'Aa1' : 2 ,
                    'Aa2' : 2 ,
                    'Aa3' : 2 ,
                    'A1' : 3 ,
                    'A2' : 3 ,
                    'A3' : 3 ,
                    'Baa1' : 4 ,
                    'Baa2' : 4 ,
                    'Baa3' : 4 ,
                    'Ba1' : 5 ,
                    'Ba2' : 5 ,
                    'Ba3' : 5 ,
                    'B1' : 6 ,
                    'B2' : 6 ,
                    'B3' : 6 ,
                    'Caa1' : 7 ,
                    'Caa2' : 7 ,
                    'Caa3' : 7 ,
                    'Ca' : 8 ,
                    'C' : 8 ,
                    'WR' : 0 ,
                    'NR' : 0 
                    }

Fitch_Rating = {    'AAA' : 1 ,
                    'AA+' : 2 ,
                    'AA' : 2 ,
                    'AA-' : 2 ,
                    'A+' : 3 ,
                    'A' : 3 ,
                    'A-' : 3 ,
                    'BBB+' : 4 ,
                    'BBB' : 4 ,
                    'BBB-' : 4 ,
                    'BB+' : 5 ,
                    'BB' : 5 ,
                    'BB-' : 5 ,
                    'B+' : 6 ,
                    'B' : 6 ,
                    'B-' : 6 ,
                    'CCC+' : 7 ,
                    'CCC' : 7 ,
                    'CCC-' : 7 ,
                    'C' : 8 ,
                    'D' : 8 ,
                    'CC' : 8 ,
                    'WD' : 0 ,
                    'NR' : 0 
        }

AIG_Rating = {  'AAA' : 1 ,
                'AA' : 2 ,
                'A' : 3 ,
                'BBB' : 4 ,
                'BB' : 5 ,
                'B' : 6 ,
                'CCC' : 7 ,
                'CC' : 8 ,
                'C' : 8 ,
                'D' : 8 ,
                'NR' : 8 ,
                'NA' : 8 
        }

AC_Mapping_to_BMA = {   'ABS'                       : 'CMBS' ,
                        'CDO'                       : 'Bonds' ,
                        'CMBS Agency'               : 'CMBS' ,
                        'CMBS Non-Agency'           : 'CMBS' ,
                        'Cash'                      : 'Bonds Cash and Govt' ,
                        'Cash Fund'                 : 'Bonds Cash and Govt' ,
                        'Short Term Securities'     : 'Bonds Cash and Govt' ,
                        'Collateral Loan'           : 'Other Commercial and Farm Mortgages' ,
                        'Commercial Mortgage Loan'  : 'Other Commercial and Farm Mortgages' ,
                        'Common Equity'             : 'Alternatives' ,
                        'Corporate Bond'            : 'Bonds' ,
                        'Credit Loan'               : 'Bonds' ,
                        'Derivative'                : 'Derivative' ,
                        'Hedge Fund'                : 'Alternatives' ,
                        'Mezzanine Mortgage Loan'   : 'Other Commercial and Farm Mortgages' ,
                        'National Govt'             : 'Bonds Cash and Govt' ,
                        'Other Invested Assets'     : 'Alternatives' ,
                        'Private Equity Fund'       : 'Alternatives' ,
                        'RMBS Agency'               : 'RMBS' ,
                        'RMBS Non-Agency'           : 'RMBS' ,
                        'Regional Govt'             : 'Bonds' ,
                        'Supranational'             : 'Bonds Cash and Govt' ,
                        'Residential Mortgage Loan' : 'Other Residential Mortgages' ,
                        'Consumer Loan'             : 'Policy Loan' ,
                        'ALBA_Hedge'                : 'Derivative' 
        }
