#!/usr/bin/env python
# coding: utf-8

import DE_GlobalFunctions_Pkg.db as db
from DE_GlobalFunctions_Pkg.DE_Functions import merge_data

def read_sql(query):
    rcursor = db.storis_read_conn.cursor()
    rcursor.execute(query)

    row = rcursor.fetchone()
    values = []
    while row is not None:
        dict_row = {'oproduct_sku': row[0],
                    'oapply_to_order_id': row[1],
                    'oorder_id': row[2],
                    'okit_status': row[3],
                    'oreturns_date': row[4],
                    'ocustomer_id': row[5],
                    'oreturn_reason_code': row[6],
                    'ostore_id': row[7],
                    'oreturn_trans_code': row[8],
                    'oreturn_cost': row[9],
                    'oreturn_units': row[10],
                    'oreturn_price': row[11]}
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
    numchunk = 0
    for chunk in chunker(values, 10000):
        try:
            cursor = db.da_prod_conn.cursor()
            cursor.executemany(insert_query, chunk)
            db.da_prod_conn.commit()
            cursor.close()
            numchunk = numchunk + 1
            print("Chunk #" + str(numchunk) + " - Returns Upload")
        except Exception as e:
            print(e)
            print("Chunk #" + str(numchunk) + " - Returns Upload Failed")

    db.da_prod_conn.close()

########################################################################################
if __name__ == "__main__":
    read_query = """
                 SELECT  bta.ProductID as oproduct_sku,
                        bta.ApplyTo_OrderID as oapply_to_order_id,
                        bta.OrderID as oorder_id,
                        bta.KitStatus as okit_status,
                        bta.TransDate as oreturns_date, 
                        bta.CustomerID as ocustomer_id, 
                        CASE WHEN bta.RtnReasonCodeID IS NULL THEN '0'
                           ELSE bta.RtnReasonCodeID END AS oreturn_reason_code,
                        bta.StoreID as ostore_id,
                        bta.TransCodeID as oreturn_trans_code,
                        SUM(bta.RtnCost) as oreturn_cost,
                        SUM(bta.RtnUnits) as oreturn_units, 
                        SUM(bta.RtnPrice) as oreturn_price
                FROM DowneastDW.storis.BtaData bta
                WHERE bta.WrittenFlag = 1
                AND bta.KitStatus <> 'c'
                AND bta.FisYear > '2021'
                AND bta.RtnPrice != 0
                GROUP BY bta.ProductID, bta.ApplyTo_OrderID, bta.OrderID, bta.KitStatus, bta.TransDate, bta.CustomerID, 
                            bta.RtnReasonCodeID, bta.StoreID, bta.TransCodeID;
                """

    insert_query = """
                    INSERT INTO oReturns (oapply_to_order_id,
                                    oorder_id,
                                    oproduct_id,
                                    okit_status,
                                    oreturns_date,
                                    ocustomer_id,
                                    oreturn_reason_code,
                                    ostore_id,
                                    oreturn_trans_code,
                                    oreturn_cost,
                                    oreturn_units,
                                    oreturn_price
                                    )
                
                    VALUES( %(oapply_to_order_id)s,
                            %(oorder_id)s,
                            %(oproduct_id)s,
                            %(okit_status)s,
                            %(oreturns_date)s,
                            %(ocustomer_id)s,
                            %(oreturn_reason_code)s,
                            %(ostore_id)s,
                            %(oreturn_trans_code)s,
                            %(oreturn_cost)s,
                            %(oreturn_units)s,
                            %(oreturn_price)s
                            )
                    ON DUPLICATE KEY UPDATE
                        oreturn_cost = VALUES(oreturn_cost),
                        oreturn_units = VALUES(oreturn_units),
                        oreturn_price = VALUES(oreturn_price)
                    """

    #read in order items
    print('Returns download')
    returns = read_sql(read_query)
    print('Returns download successful')

    #read in product ids and update orderitems variable
    print('Returns ProductID query download')
    returns = merge_data(returns)
    print('Returns product id added to download')

    #upload orderitems into database
    print('Returns Upload')
    write_sql(returns)

    print('Returns upload successful')
