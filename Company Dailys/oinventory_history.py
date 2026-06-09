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
                    'oproduct_inv_status': row[1],
                    'okit_status': row[2],
                    'ostore_id': row[3],
                    'ovendor_id': row[4],
                    'oinv_selling_price': row[5],
                    'oinv_on_hand': row[6],
                    'oinv_on_order': row[7],
                    'oinv_committed': row[8],
                    'oinv_soft_committed': row[9],
                    'oinv_non_saleable': row[10],
                    'oinv_back_ordered': row[11],
                    'oinv_date': row[12],
                    'oinv_rec_status': row[13]
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
    numchunk = 0
    for chunk in chunker(values, 100000):
        try:
            cursor = db.da_prod_conn.cursor()
            cursor.executemany(insert_query, chunk)
            db.da_prod_conn.commit()
            cursor.close()
            numchunk = numchunk + 1
            print("Chunk #" + str(numchunk) + " - Inventory History Upload")
        except Exception as e:
            print(e)
            print("Chunk #" + str(numchunk) + " - Inventory History Upload Failed")
    db.da_prod_conn.close()

########################################################################################
if __name__ == "__main__":
    read_query = """
                SELECT
                    i.ProductID as oproduct_sku,
                    i.PieceStatusID as oproduct_inv_status,
                    i.KitStatus as okit_status,
                    i.StoreID as ostore_id,
                    i.VendorID as ovendor_id,
                    i.SellingPrice as oinv_selling_price,
                    i.QtyOnHand as oinv_on_hand,
                    i.QtyOnOrder as oinv_on_order,
                    i.QtyCommitted as oinv_committed,
                    i.QtySoftCommitted as oinv_soft_committed,
                    i.QtyNonSale as oinv_non_saleable,
                    i.QtyBackOrdered as oinv_back_ordered,
                    i.TransDate as oinv_date,
                    i.RecStatus as oinv_rec_status
                FROM DowneastDW.storis.ProductInventory i
                JOIN DowneastDW.storis.Product p on i.ProductID = p.ProductID
                WHERE i.TransDate > '2022-12-31'
                AND p.PurchaseStatusCodeID NOT IN ('T', 'P', 'D')
                """

    insert_query = """
                    INSERT INTO oInventoryHistory (oproduct_sku,
                                    oproduct_inv_status,
                                    okit_status,
                                    ostore_id,
                                    ovendor_id,
                                    oinv_selling_price,
                                    oinv_on_hand,
                                    oinv_on_order,
                                    oinv_committed,
                                    oinv_soft_committed,
                                    oinv_non_saleable,
                                    oinv_back_ordered,
                                    oinv_date,
                                    oinv_rec_status
                                    )
                
                    VALUES( %(oproduct_sku)s,
                            %(oproduct_inv_status)s,
                            %(okit_status)s,
                            %(ostore_id)s,
                            %(ovendor_id)s,
                            %(oinv_selling_price)s,
                            %(oinv_on_hand)s,
                            %(oinv_on_order)s,
                            %(oinv_committed)s,
                            %(oinv_soft_committed)s,
                            %(oinv_non_saleable)s,
                            %(oinv_back_ordered)s,
                            %(oinv_date)s,
                            %(oinv_rec_status)s
                            )
                    ON DUPLICATE KEY UPDATE
                            oinv_selling_price = VALUES(oinv_selling_price),
                            oinv_on_hand = VALUES(oinv_on_hand),
                            oinv_on_order = VALUES(oinv_on_order),
                            oinv_committed = VALUES(oinv_committed),
                            oinv_soft_committed = VALUES(oinv_soft_committed),
                            oinv_non_saleable = VALUES(oinv_non_saleable),
                            oinv_back_ordered = VALUES(oinv_back_ordered) 
                    """

    print('Inventory History download')
    inventory_history = read_sql(read_query)

    # read in product ids and update inventory variable
    print('ProductID query download')
    inventory_history = merge_data(inventory_history)
    print('ProductID added to download')

    print('Inventory History Upload')
    write_sql(inventory_history)

    print('Inventory History upload finished')

