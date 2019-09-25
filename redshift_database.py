# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 17:18:58 2019

@author: xiagao
"""

import json
import os

import psycopg2
#from psycopg2 import pool

#redshift_connection_pool = None


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

def runSQL(sql, conn_pool, with_header = False):
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


if __name__ == '__main__':
    workDir = r'L:\Global Profitability Standards and ALM\Legacy Portfolio\SAM RE\FRL Investment ALM\AWS Corp Migration\FortitudeRe'
    os.chdir(workDir)
    configFile = r'.\redshift_alm.config'
    db_conn_str = db_connection_string(configFile)
    redshift_connection_pool = connect_redshift(db_conn_str)
    sql = "select * from public.ggy_input_mappings_all"
    records = runSQL(sql, redshift_connection_pool)
    disconnect_redshift(redshift_connection_pool)
    print(records)
    debugX = 1