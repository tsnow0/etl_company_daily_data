#!/usr/bin/env python
# coding: utf-8

import DE_GlobalFunctions_Pkg.db as db
from DE_GlobalFunctions_Pkg.DE_Functions import merge_data



def read_sql(query):
    # read function for pulling data from STORIS
    rcursor = db.storis_read_conn.cursor()
    rcursor.execute(query)

    row = rcursor.fetchone()
    values = []
    while row is not None:
        dict_row = {'oproduct_sku': row[0],
                    'okit_status': row[1],
                    'oSalesByCustomer_date': row[2],
                    'oSalesByCustomer_fis_year': row[3],
                    'oSalesByCustomer_fis_month': row[4],
                    'oSalesByCustomer_fis_week': row[5],
                    'ocustomer_id': row[6],
                    'osalesperson_id': row[7],
                    'ostore_id': row[8],
                    'oSalesByCustomer_units': row[9],
                    'oSalesByCustomer_amount': row[10],
                    'oSalesByCustomer_cost': row[11]
                    }
        values.append(dict_row)
        row = rcursor.fetchone()
    rcursor.close()
    db.storis_read_conn.close()
    return values


########################################################################################
def chunker(seq, size):
    # break up data into uploadable chunks
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


########################################################################################
def write_sql(values):
    # write function for writing data to Downeast_analytics
    numchunk = 0
    for chunk in chunker(values, 10000):
        try:
            cursor = db.da_prod_conn.cursor()
            cursor.executemany(insert_query, chunk)
            db.da_prod_conn.commit()
            cursor.close()
            numchunk = numchunk + 1
            print("Chunk #" + str(numchunk) + " - Sales Upload")
        except Exception as e:
            print(e)
            print("Chunk #" + str(numchunk) + " - Sales Upload Failed")

    db.da_prod_conn.close()


########################################################################################
if __name__ == "__main__":
    # select statement for STORIS
    read_query = """
                SELECT 
                       bta.ProductID as oproduct_sku, 
                       bta.KitStatus as okit_status,
                       bta.TransDate as oSalesByCustomer_date, 
                       bta.FisYear as oSalesByCustomer_fis_year, 
                       bta.FisPeriod as oSalesByCustomer_fis_month, 
                       bta.FisWeek as oSalesByCustomer_fis_week, 
                       bta.CustomerID as ocustomer_id, 
                       bta.SalesPersonID as osalesperson_id,
                       bta.StoreID as ostore_id,
                       SUM(bta.NetUnits) as oSalesByCustomer_units, 
                       SUM(bta.NetSales) as oSalesByCustomer_amount,
                       SUM(bta.NetCost) as oSalesByCustomer_cost
                FROM DowneastDW.storis.BtaData bta
                WHERE bta.WrittenFlag = 1
                AND bta.RtnPrice = 0
                AND bta.KitStatus <> 'c'
                AND bta.TransDate > '2022-12-31'
                AND bta.TransDate < CAST( GETDATE() AS Date )
                GROUP BY bta.ProductID, bta.KitStatus, bta.TransDate, bta.FisYear, bta.FisPeriod, 
                         bta.FisWeek, bta.CustomerID, bta.SalesPersonID, bta.StoreID
                """

    # insert statement for downeast_analytics
    insert_query = """
                    INSERT INTO oSalesByCustomer (   
                                    oproduct_id,
                                    okit_status,
                                    oSalesByCustomer_date, 
                                    oSalesByCustomer_fis_year,
                                    oSalesByCustomer_fis_month,
                                    oSalesByCustomer_fis_week, 
                                    ocustomer_id, 
                                    osalesperson_id,
                                    ostore_id,
                                    oSalesByCustomer_units,
                                    oSalesByCustomer_amount,
                                    oSalesByCustomer_cost
                                    )
                
                
                    VALUES( %(oproduct_id)s,
                            %(okit_status)s,
                            %(oSalesByCustomer_date)s,
                            %(oSalesByCustomer_fis_year)s,
                            %(oSalesByCustomer_fis_month)s,
                            %(oSalesByCustomer_fis_week)s, 
                            %(ocustomer_id)s, 
                            %(osalesperson_id)s,
                            %(ostore_id)s,
                            %(oSalesByCustomer_units)s,
                            %(oSalesByCustomer_amount)s,
                            %(oSalesByCustomer_cost)s
                            )
                    ON DUPLICATE KEY UPDATE
                            oSalesByCustomer_units = VALUES(oSalesByCustomer_units),
                            oSalesByCustomer_amount = VALUES(oSalesByCustomer_amount),
                            oSalesByCustomer_cost = VALUES(oSalesByCustomer_cost)
                    """

    # read in written sales
    print('SalesByCustomer download')
    sales = read_sql(read_query)
    print('SalesByCustomer download successful')

    # read in product ids and update components variable
    print('ProductID query download')
    sales = merge_data(sales)
    # merge_data(sales,product)
    print('ProductID added to download')

    # upload sales data into database
    print('SalesByCustomer upload')
    write_sql(sales)

    print('SalesByCustomer upload finished')
