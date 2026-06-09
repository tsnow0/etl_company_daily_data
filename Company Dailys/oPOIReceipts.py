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
        dict_row = {'opo_id': row[0],
                    'oproduct_sku': row[1],
                    'opoi_line_id': row[2],
                    'opoi_received_position': row[3],
                    'opoi_qty_received': row[4],
                    'opoi_receipt_date_created': row[5],
                    'opoi_date_received': row[6],
                    'opoi_receipt_status': row[7]
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
        cursor.execute("TRUNCATE TABLE oPOIReceipts")
        print('oPOIReceipts Emptied')

        cursor.executemany(insert_query, values)
        db.da_prod_conn.commit()
        cursor.close()
    except Exception as e:
        print(e)
        cursor.close()
    db.da_prod_conn.close()


########################################################################################
if __name__ == "__main__":
    # select statement for STORIS
    read_query = """
                SELECT 
                    p.PurchaseOrderID as opo_id,
                    p.ProductID as oproduct_sku,
                    p.PurchaseOrderItemLineID as opoi_line_id,
                    p.Position as opoi_received_position,
                    p.Quantity as opoi_qty_received,
                    p.DateCreated as opoi_receipt_date_created,
                    p.DateReceived as opoi_date_received,
                    p.RecStatus as opoi_receipt_status
                  FROM [DowneastDW].[storis].[PurchaseOrderItem_Receipts] p
               """

    # insert statement for downeast_analytics
    insert_query = """
                    INSERT INTO oPOIReceipts (opo_id, 
                                    oproduct_id,
                                    opoi_line_id,
                                    opoi_received_position,
                                    opoi_qty_received,
                                    opoi_receipt_date_created,
                                    opoi_date_received,
                                    opoi_receipt_status
                                    )
                
                    VALUES( %(opo_id)s, 
                            %(oproduct_id)s,
                            %(opoi_line_id)s,
                            %(opoi_received_position)s,
                            %(opoi_qty_received)s,
                            %(opoi_receipt_date_created)s,
                            %(opoi_date_received)s,
                            %(opoi_receipt_status)s
                            )
                    ON DUPLICATE KEY UPDATE
                            opoi_qty_received = VALUES(opoi_qty_received),
                            opoi_receipt_date_created = VALUES(opoi_receipt_date_created),
                            opoi_receipt_status = VALUES(opoi_receipt_status)
                    """

    # read in POI receipts
    print('POI Receipts download')
    receipts = read_sql(read_query)
    print('POI Receipts download successful')

    # read in product ids and update components variable
    print('ProductID query download')
    receipts = merge_data(receipts)
    print('ProductID added to download')

    # upload kit components into database
    print('POI Receipts Upload')
    write_sql(receipts)

    print('POI Receipts upload finished')
