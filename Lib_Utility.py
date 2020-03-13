# -*- coding: utf-8 -*-
"""
Created on Fri May 17 17:32:57 2019

@author: seongpar
"""

import pandas as pd
import pyodbc
import openpyxl
import os
import json
import psycopg2
#from psycopg2 import pool

#%% Ad-hoc
_saveData = False ## Default False
_tempWorkSpace = os.getcwd()
_csvIdWrite = 0
_csvIdRead = -1
_readFromLocalCSV = False ## Default False

#%%

def run_SQL(database, sql, conn_pool = None, with_header = False):
    
    if _readFromLocalCSV:
        global _csvIdRead
        _csvIdRead += 1
        print("Reading from cached CSV " + str(_csvIdRead))
        return pd.read_csv(_tempWorkSpace + "/_CacheDataNo" + str(_csvIdRead) + ".csv")
    if database.lower() == 'redshift':
        out = run_SQL_redshift(sql, conn_pool, with_header)
        disconnect_redshift(conn_pool)
        return out
    else:
        # Read from Microsoft Access DB
        dbConn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};' \
                                r'DBQ=' + database + ';', autocommit = True)
        data = pd.read_sql(sql, dbConn)
        dbConn.close() 
        if _saveData:
            global _csvIdWrite
            print("Writing results as CSV " + str(_csvIdWrite))
            data.to_csv(_tempWorkSpace + "/_CacheDataNo" + str(_csvIdWrite) + ".csv")
            _csvIdWrite += 1
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


#%% 
'''
Functions to get data from AWS Redshift Database
'''

# load the database config file and prepare the credentials
def db_connection_string(config_file_name):
    try:
        Status_Message = 'Open Config file. Local'
        with open(config_file_name, 'r') as fp:
            database = json.load(fp)

        # print(str(database["cm_database"]['dbname']))
        # print(str(database["cm_database"]['schema']))
        # print(str(database["cm_database"]['host']))
        # print(str(database["cm_database"]['port']))
        # print(str(database["cm_database"]['user']))
        # print(str(database["cm_database"]['credentials']))

    except:
        print(Status_Message + ' Error')
    return database

# connect to redshift and create connection pool
def connect_redshift(connection_string):
    try:
        print('Creating redshift database connection pool with max 20 threads...')
        # conn = psycopg2.connect("dbname = " + str(connection_string["cm_database"]['dbname'])
        #                         + " user=" + str(connection_string["cm_database"]['user'])
        #                         + " password=" + str(connection_string["cm_database"]['password'])
        #                         + " port=" + str(connection_string["cm_database"]['port'])
        #                         + " host=" + str(connection_string["cm_database"]['host'])
        #                         )

        conn_pool = psycopg2.pool.SimpleConnectionPool(1, 20,
                                                       "dbname = " + str(connection_string["cm_database"]['dbname'])
                                                       + " user=" + str(connection_string["cm_database"]['user'])
                                                       + " password=" + str(
                                                           connection_string["cm_database"]['password'])
                                                       + " port=" + str(connection_string["cm_database"]['port'])
                                                       + " host=" + str(connection_string["cm_database"]['host']))
        if (conn_pool):
            print("Redshift connection pool created successfully")
            return conn_pool

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while connecting to Redshift database ", error)
    # finally:
    #     # closing database connection.
    #     # use closeall method to close all the active connection if you want to turn of the application
    #     if (conn_pool):
    #         conn_pool.closeall
    #     print("PostgreSQL connection pool is closed")


def disconnect_redshift(conn_pool):
    if (conn_pool):
        print("Redshift connection pool closed...")
        conn_pool.closeall

def run_SQL_redshift(sql, conn_pool, with_header = False):
    try:
        db_conn = conn_pool.getconn()
        if (db_conn):
            print("successfully received 1 connection from connection pool ")
            ps_cursor = db_conn.cursor()
            ps_cursor.execute(sql)
            results = ps_cursor.fetchall()
            
            if with_header:
                header = ps_cursor.description
                if (ps_cursor):
                    ps_cursor.close()
                # Use this method to release the connection object and send back to connection pool
                conn_pool.putconn(db_conn)
                print("return 1 connection to the pool")
                return header, results
            
            else:
                if (ps_cursor):
                    ps_cursor.close()
                # Use this method to release the connection object and send back to connection pool
                conn_pool.putconn(db_conn)
                print("return 1 connection to the pool")
                return results
    except Exception as error:
        print("Error while running SQL: ", error)