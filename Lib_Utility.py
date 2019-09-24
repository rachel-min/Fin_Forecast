# -*- coding: utf-8 -*-
"""
Created on Fri May 17 17:32:57 2019

@author: seongpar
"""

import pandas as pd
import pyodbc
import openpyxl
import os


# SQL function to get data from MS Access Database
def run_SQL(database, sql):

    dbConn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + database + r';')
    data = pd.read_sql(sql, dbConn)

    return data

def wavg(group, avg_name, weight_name):
    d = group[avg_name]
    w = group[weight_name]
    try:
        return (d * w).sum() / w.sum()
    except ZeroDivisionError:
        return 0
    
def append_to_excel_file(work_dir, excel_file_name, data):
    
    os.chdir(work_dir)
    book = openpyxl.load_workbook(excel_file_name)
    sheet = book.active
    
    
    for row in data:
        sheet.append(row)
    
    book.save(excel_file_name)

def output_to_excel_file(work_dir, excel_file_name, data):
    os.chdir(work_dir)
    pd.DataFrame(data).to_excel(excel_file_name, header = False, index = False)
    
def export_class(work_class, colNames):

    output = pd.DataFrame([],columns = colNames)
    

    for key, val in work_class.items():
        each_col_val = []
        
        for each_col_name in colNames:
            each_col_val.append(val[each_col_name])

    output = output.append(pd.DataFrame([each_col_val], columns = colNames), ignore_index = True)
    
    return output
