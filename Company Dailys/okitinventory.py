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
                    'ostatus_id': row[1],
                    'ostore_id': row[2],
                    'okit_inv_on_hand': row[3],
                    'okit_inv_net_available': row[4]}
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
        cursor.execute("TRUNCATE TABLE oKitInventory")
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
                    i.KitMaster_ProductID as okit_product_sku,
                    i.KitStatusID as okit_status_id,
                    i.StoreID as ostore_id,
                    i.QtyOnHand as okit_inv_on_hand,
                    i.NetAvailable as okit_inv_net_available
                FROM fn_GetKitNetAvailable(null) i;
                """

    #insert statement for downeast_analytics
    insert_query = """
                    INSERT INTO oKitInventory (okit_product_sku,
                                    okit_status_id,
                                    okit_store_id,
                                    okit_inv_on_hand,
                                    okit_inv_net_available
                                    )
                    VALUES( %(oproduct_sku)s,
                            %(ostatus_id)s,
                            %(ostore_id)s,
                            %(okit_inv_on_hand)s,
                            %(okit_inv_net_available)s
                            )
                    ON DUPLICATE KEY UPDATE
                        okit_inv_on_hand = VALUES(okit_inv_on_hand),
                        okit_inv_net_available = VALUES(okit_inv_net_available),
                        OMDT = VALUES(OMDT)
                    """

    #read in inventory
    print('KitInv download')
    inventory = read_sql(read_query)
    print('KitInv download successful')

    #read in product ids and update inventory variable
    print('ProductID query download')
    inventory = merge_data(inventory)
    print('ProductID added to download')

    #upload inventory into database
    print('KitInv Upload')
    write_sql(inventory)

    print('KitInv upload finished')