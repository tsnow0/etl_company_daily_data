#!/usr/bin/env python
# coding: utf-8

import DE_GlobalFunctions_Pkg.db as db
from DE_GlobalFunctions_Pkg.DE_Functions import merge_data

# pulling delivered sales rather than all written sales and pulling the transacion code so you can filter out returns/sales/etc...

def read_sql(query):
    # read function for pulling data from STORIS
    rcursor = db.storis_read_conn.cursor()
    rcursor.execute(query)

    row = rcursor.fetchone()
    values = []
    while row is not None:
        dict_row = {'oproduct_sku': row[0],
                    'oorder_id': row[1],
                    'osales_date': row[2],
                    'osales_fis_year': row[3],
                    'osales_fis_month': row[4],
                    'osales_fis_week': row[5],
                    'ocustomer_id': row[6],
                    'ostore_id': row[7],
                    'osalesperson_id': row[8],
                    'osales_trans_code': row[9],
                    'osales_units': row[10],
                    'osales_amount': row[11]
                    }
        values.append(dict_row)
        row = rcursor.fetchone()
    rcursor.close()
    db.storis_read_conn.close()
    return values

########################################################################################
def write_sql(values):
    # write function for writing data to Downeast_analytics
    try:
        cursor = db.da_prod_conn.cursor()
        cursor.executemany(insert_query, values)
        db.da_prod_conn.commit()
        cursor.close()
    except Exception as e:
        print(e)
    db.da_prod_conn.close()

########################################################################################
if __name__ == "__main__":

    # select statement for STORIS
    read_query = """
                SELECT  bta.ProductID as oproduct_sku, 
                        bta.OrderID as oorder_id,
                        bta.TransDate as osales_date, 
                        bta.FisYear as osales_fis_year, 
                        bta.FisPeriod as osales_fis_month, 
                        bta.FisWeek as osales_fis_week, 
                        bta.CustomerID as ocustomer_id, 
                        bta.StoreID as ostore_id,
                        bta.SalespersonID as osalesperson_id,
                        bta.TransCodeID as osales_trans_code,
                        SUM(bta.NetUnits) as osales_units, 
                        SUM(bta.NetSales) as osales_amount
                FROM DowneastDW.storis.BtaData bta 
                WHERE bta.WrittenFlag = 0
                AND bta.KitStatus <> 'c' 
                AND bta.FisYear > 2022
                GROUP BY bta.ProductID,bta.OrderID, bta.TransDate, bta.FisYear, bta.FisPeriod, 
                         bta.FisWeek, bta.CustomerID, bta.StoreID, bta.SalespersonID, bta.TransCodeID
                ORDER BY bta.ProductID
                """

    # insert statement for downeast_analytics
    insert_query = """
                    INSERT INTO oSalesDelivered (oproduct_id,
                                    oorder_id,
                                    osales_date, 
                                    osales_fis_year,
                                    osales_fis_month,
                                    osales_fis_week, 
                                    ocustomer_id, 
                                    ostore_id,
                                    osalesperson_id,
                                    osales_trans_code,
                                    osales_units,
                                    osales_amount
                                    )
                    VALUES( %(oproduct_id)s,
                            %(oorder_id)s,
                            %(osales_date)s,
                            %(osales_fis_year)s,
                            %(osales_fis_month)s,
                            %(osales_fis_week)s, 
                            %(ocustomer_id)s, 
                            %(ostore_id)s,
                            %(osalesperson_id)s,
                            %(osales_trans_code)s,
                            %(osales_units)s,
                            %(osales_amount)s
                            )
                    ON DUPLICATE KEY UPDATE
                            osales_units = VALUES(osales_units),
                            osales_amount = VALUES(osales_amount)
                    """

    # read in delivered sales
    print('Delivered Sales download')
    delivered = read_sql(read_query)
    print('Delivered Sales download successful')

    # read in product ids and update components variable
    print('ProductID query download')
    delivered = merge_data(delivered)
    print('ProductID added to download')

    print('Delivered Sales upload')
    write_sql(delivered)

    print('Delivered Sales upload finished')
