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
        dict_row = {'opoi_order_date_change': row[0],
                    'opoi_order_date_created': row[1],
                    'oorder_id': row[2],
                    'oorder_position': row[3],
                    'opo_id': row[4],
                    'opoi_line_id': row[5],
                    'opoi_order_qty': row[6],
                    'opoi_order_qty_commited': row[7],
                    'opoi_order_rec_status': row[8]
                    }
        values.append(dict_row)
        row = rcursor.fetchone()
    rcursor.close()
    db.storis_read_conn.close()
    return values


########################################################################################
def write_sql(values):
    try:
        cursor = db.da_prod_conn.cursor()
        cursor.execute("TRUNCATE TABLE oPOI_Orders")
        print('POI_Orders Emptied')

        cursor.executemany(insert_query, values)
        db.da_prod_conn.commit()
        cursor.close()
    except Exception as e:
        print(e)

    db.da_prod_conn.close()


########################################################################################
if __name__ == "__main__":
    read_query = """
                SELECT *
                  FROM [DowneastDW].[storis].[PurchaseOrderItem_Orders] p
               """

    insert_query = """
                    INSERT INTO oPOI_Orders (opoi_order_date_change, 
                                    opoi_order_date_created,
                                    oorder_id,
                                    oorder_position,
                                    opo_id,
                                    opoi_line_id,
                                    opoi_order_qty,
                                    opoi_order_qty_commited,
                                    opoi_order_rec_status
                                    )
                
                    VALUES( %(opoi_order_date_change)s, 
                            %(opoi_order_date_created)s,
                            %(oorder_id)s,
                            %(oorder_position)s,
                            %(opo_id)s,
                            %(opoi_line_id)s,
                            %(opoi_order_qty)s,
                            %(opoi_order_qty_commited)s,
                            %(opoi_order_rec_status)s
                            )
                    ON DUPLICATE KEY UPDATE
                            opoi_order_date_change = VALUES(opoi_order_date_change),
                            opoi_order_date_created = VALUES(opoi_order_date_created),
                            oorder_id = VALUES(oorder_id),
                            opoi_order_qty = VALUES(opoi_order_qty),
                            opoi_order_qty_commited = VALUES(opoi_order_qty_commited),
                            opoi_order_rec_status = VALUES(opoi_order_rec_status)
                    """

    print('POI Orders Download')
    orders = read_sql(read_query)

    print('POI Orders Upload')
    write_sql(orders)

    print('POI Orders Upload Finished')
