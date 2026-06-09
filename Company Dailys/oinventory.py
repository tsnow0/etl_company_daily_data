#!/usr/bin/env python
# coding: utf-8

import DE_GlobalFunctions_Pkg.db as db
from DE_GlobalFunctions_Pkg.DE_Functions import merge_data

def read_sql(query):
    #read function for pulling data from STORIS

    rcursor = db.storis_read_conn.cursor()
    rcursor.execute(query)

    row = rcursor.fetchone()
    values = []
    while row is not None:
        dict_row = {'oproduct_sku': row[0],
                    'ostore_id': row[1],
                    'oinv_on_hand': row[2],
                    'oinv_committed': row[3],
                    'oinv_net_available': row[4],
                    'oinv_soft_committed': row[5],
                    'oinv_hard_committed': row[6],
                    'oinv_asis_on_hand': row[7]}
        values.append(dict_row)
        row = rcursor.fetchone()
    rcursor.close()
    db.storis_read_conn.close()
    return values

########################################################################################
def write_sql(values):
    #write function for writing data to Downeast_analytics
    try:
        # empty table first because the records can be removed from STORIS altogether but will stay in our system if we don't empty it every time
        cursor = db.da_prod_conn.cursor()
        cursor.execute("TRUNCATE TABLE oInventory")
        print('Inventory emptied')

        cursor.executemany(insert_query, values)
        db.da_prod_conn.commit()
        cursor.close()
    except Exception as e:
        print(e)
    db.da_prod_conn.close()

########################################################################################
if __name__ == "__main__":

    #select statement for STORIS
    read_query = """
                SELECT
                    i.ProductID as oproduct_sku,
                    i.StoreID as ostore_id,
                    i.QtyOnHand as oinv_on_hand,
                    i.QtyCommitted as oinv_committed,
                    i.NetAvailable as oinv_net_available,
                    i.QtySoftCommitted as oinv_soft_committed,
                    i.QtyHardCommitted as oinv_hard_committed,
                    i.AsIsQTYOnHand as oinv_asis_on_hand
                FROM fn_GetProductNetAvailable(null) i;
                """

    #insert statement for downeast_analytics
    insert_query = """
                    INSERT INTO oInventory (oproduct_sku,
                                    ostore_id,
                                    oinv_on_hand,
                                    oinv_committed,
                                    oinv_net_available,
                                    oinv_soft_committed,
                                    oinv_hard_committed,
                                    oinv_asis_on_hand
                                    )
                
                    VALUES( %(oproduct_sku)s,
                            %(ostore_id)s,
                            %(oinv_on_hand)s,
                            %(oinv_committed)s,
                            %(oinv_net_available)s,
                            %(oinv_soft_committed)s,
                            %(oinv_hard_committed)s,
                            %(oinv_asis_on_hand)s
                            )
                    ON DUPLICATE KEY UPDATE
                        oinv_on_hand = VALUES(oinv_on_hand),
                        oinv_committed = VALUES(oinv_committed),
                        oinv_net_available = VALUES(oinv_net_available),
                        oinv_soft_committed = VALUES(oinv_soft_committed),
                        oinv_hard_committed = VALUES(oinv_hard_committed),
                        oinv_asis_on_hand = VALUES(oinv_asis_on_hand),
                        OMDT = VALUES(OMDT)
                    """

    #read in inventory
    print('Inventory download')
    inventory = read_sql(read_query)
    print('Inventory download successful')

    #read in product ids and update inventory variable
    print('ProductID query download')
    inventory = merge_data(inventory)
    print('ProductID added to download')

    #upload inventory into database
    print('Inventory Upload')
    write_sql(inventory)

    print('Inventory upload finished')