#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from calendar import monthrange
import mysql.connector
import DE_GlobalFunctions_Pkg.db as db
from DE_GlobalFunctions_Pkg.DE_Functions import merge_data
import numpy as np


def read_sql(sqlstr):

    try:
        cursor = db.da_report_conn.cursor()
        cursor.execute(sqlstr)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        print(e)
    db.da_report_conn.close()


########################################################################################
def write_sql(strSQL, values):

    try:
        cursor = db.da_prod_conn.cursor()
        cursor.execute("TRUNCATE TABLE oForecast_Daily")
        print('Daily Forecast emptied')

        cursor.executemany(strSQL, values)
        db.da_prod_conn.commit()
        cursor.close()
    except Exception as e:
        print(e)
    db.da_prod_conn.close()


########################################################################################
def days_in_months(year, month):
    return monthrange(year, month)[1]


########################################################################################
if __name__ == "__main__":
    forecastSQL = """SELECT IF(k.oproduct_sku IS NULL, f.oproduct_sku, k.oproduct_sku),
                            f.oforecast_year,
                            f.oforecast_month,
                            SUM(f.oforecast_units) * IF(k.oproduct_sku IS NULL, 1, k.okit_component_qty)
                        FROM downeast_analytics.oForecasts f
                        LEFT JOIN (SELECT p.oproduct_sku,
                                     kitmaster.oproduct_sku as okit_sku,
                                     kc.okit_component_qty
                              FROM downeast_analytics.oKitComponents kc
                              JOIN downeast_analytics.oProducts p on kc.oproduct_id = p.oproduct_id
                              JOIN downeast_analytics.oProducts kitmaster on kc.okit_product_id = p.oproduct_id
                            ) k on f.oproduct_sku = k.okit_sku
                        GROUP BY f.oproduct_sku,IF(k.oproduct_sku IS NULL, f.oproduct_sku, k.oproduct_sku), f.oforecast_year, f.oforecast_month
                   """


    forecast_insert_query = """
                    INSERT INTO oForecast_Daily (oforecast_daily_date,
                                oproduct_sku,
                                oforecast_daily_units
                                )
    
                    VALUES( %(oforecast_daily_date)s,
                        %(oproduct_sku)s,
                        %(oforecast_daily_units)s
                        )
                    ON DUPLICATE KEY UPDATE
                    oforecast_daily_units = VALUES(oforecast_daily_units)
                   """

    print('Forecast download')
    forecasts = read_sql(forecastSQL)
    print('Forecast download successful')

    leaddays = 80
    targetdays = leaddays + 30
    column_names = ['oproduct_sku', 'year', 'month', 'units']

    #create dataframes
    print('create dataframe')
    forecasts = pd.DataFrame(forecasts)
    forecasts.columns = column_names

    #add new columns and format
    print('add daily_forecast and year_month columns')

    forecasts['daily_forecast'] = forecasts.apply(lambda x: x['units'] / days_in_months(x['year'], x['month']),
                                                  axis=1).astype(float)
    forecasts['daily_forecast'].round(5)
    forecasts['year-month'] = forecasts.apply(lambda x: str(x['year']) + "-" + str(x['month']) + '-01', axis=1)
    forecasts['year-month'] = pd.to_datetime(forecasts['year-month'])


    #create pivot table from dataframe
    daily_forecast = forecasts.pivot_table(index='year-month', columns='oproduct_sku', values='daily_forecast',aggfunc=np.sum)


    #reindex pivot table
    start_date = daily_forecast.index.min() - pd.DateOffset(day=1)
    end_date = daily_forecast.index.max() + pd.DateOffset(day=31)

    dates = pd.date_range(start_date, end_date, freq='D')
    dates.name = 'oforecast_daily_date'

    daily_forecast = daily_forecast.reindex(dates, method='ffill')

    daily_forecast = daily_forecast.stack('oproduct_sku')
    daily_forecast = daily_forecast.reset_index()

    daily_forecast.columns = ['oforecast_daily_date', 'oproduct_sku', 'oforecast_daily_units']
    daily_forecast['oforecast_daily_date'] = daily_forecast['oforecast_daily_date'].astype(str)

    print('Daily Forecasts upload')
    values = daily_forecast.to_dict('records')
    write_sql(forecast_insert_query, values)

    print('Daily Forecasts upload finished')
