#!/usr/bin/env python
# coding: utf-8

import DE_GlobalFunctions_Pkg.db as db
from DE_GlobalFunctions_Pkg.DE_Functions import merge_data

# sales with order ids

def read_sql(query):
    # read function for pulling data from STORIS
    rcursor = db.storis_read_conn.cursor()
    rcursor.execute(query)

    row = rcursor.fetchone()
    values = []
    while row is not None:
        dict_row = {'oorder_id': row[0],
                    'oorder_item_id': row[1],
                    'oproduct_sku': row[2],
                    'okit_status':row[3],
                    'osales_date': row[4],
                    'osales_fis_year': row[5],
                    'osales_fis_month': row[6],
                    'osales_fis_week': row[7],
                    'ocustomer_id': row[8],
                    'osalesperson_id': row[9],
                    'ostore_id': row[10],
                    'osales_trans_code': row[11],
                    'osales_units': row[12],
                    'osales_amount': row[13],
                    'osales_cost': row[14]
                    }
        values.append(dict_row)
        row = rcursor.fetchone()
    rcursor.close()
    db.storis_read_conn.close()
    return values


########################################################################################
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

########################################################################################
def write_sql(values):
    # write function for writing data to Downeast_analytics
    numchunk = 0
    for chunk in chunker(values, 48000):
        try:
            cursor = db.da_prod_conn.cursor()
            cursor.executemany(insert_query, chunk)
            db.da_prod_conn.commit()
            cursor.close()
            numchunk = numchunk + 1
            print("Chunk #" + str(numchunk) + " - oSaleOrders Upload")
        except Exception as e:
            print(e)
            print("Chunk #" + str(numchunk) + " - oSaleOrders Upload Failed")

    db.da_prod_conn.close()

########################################################################################
if __name__ == "__main__":
    # select statement for STORIS
    read_query = """
                    SELECT bta.OrderID as oorder_id,
                           bta.OrderItemID as oorder_item_id,
                           bta.ProductID as oproduct_sku, 
                           bta.KitStatus as okit_status,
                           bta.TransDate as osales_date, 
                           bta.FisYear as osales_fis_year, 
                           bta.FisPeriod as osales_fis_month, 
                           bta.FisWeek as osales_fis_week, 
                           bta.CustomerID as ocustomer_id, 
                           bta.SalesPersonID as osalesperson_id,
                           bta.StoreID as ostore_id,
                           bta.TransCodeID as osales_trans_code,
                           SUM(bta.NetUnits) as osales_units, 
                           SUM(bta.NetSales) as osales_amount,
                           SUM(bta.NetCost) as osales_cost
                    FROM DowneastDW.storis.BtaData bta
                    WHERE bta.WrittenFlag = 1
                    AND bta.KitStatus <> 'c'
                    AND bta.RtnPrice = 0
                    AND bta.TransDate > '2022-12-31'
                    GROUP BY bta.OrderID, bta.OrderItemID, bta.ProductID, bta.KitStatus, bta.TransDate, bta.FisYear, 
                            bta.FisPeriod, bta.FisWeek, bta.CustomerID, bta.SalesPersonID, bta.StoreID, bta.TransCodeID
                 """

    # insert statement for downeast_analytics
    insert_query = """
                    INSERT INTO oSaleOrders (oorder_id,
                                    oorder_item_id,
                                    oproduct_id,
                                    okit_status,
                                    osales_date, 
                                    osales_fis_year,
                                    osales_fis_month,
                                    osales_fis_week, 
                                    ocustomer_id, 
                                    osalesperson_id,
                                    ostore_id,
                                    osales_trans_code,
                                    osales_units,
                                    osales_amount,
                                    osales_cost
                                    )
                    VALUES( %(oorder_id)s,
                            %(oorder_item_id)s,
                            %(oproduct_id)s,
                            %(okit_status)s,
                            %(osales_date)s,
                            %(osales_fis_year)s,
                            %(osales_fis_month)s,
                            %(osales_fis_week)s, 
                            %(ocustomer_id)s, 
                            %(osalesperson_id)s,
                            %(ostore_id)s,
                            %(osales_trans_code)s,
                            %(osales_units)s,
                            %(osales_amount)s,
                            %(osales_cost)s
                            )
                    ON DUPLICATE KEY UPDATE
                            osales_units = VALUES(osales_units),
                            osales_amount = VALUES(osales_amount),
                            osales_cost = VALUES(osales_cost)
                    """

    # read in sales orders
    print('SalesOrders download')
    orders = read_sql(read_query)
    print('SalesOrders download successful')

    # read in product ids and update components variable
    print('ProductID query download')
    orders = merge_data(orders)
    print('ProductID added to download')


    print('SalesOrders upload start')
    write_sql(orders)

    print('SalesOrders upload finished')
