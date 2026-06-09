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
        dict_row = {'opo_id': row[0],
                    'ovendor_id': row[1],
                    'opo_container_number': row[2],
                    'opo_open_amount': row[3],
                    'opo_subtotal_amount': row[4],
                    'opo_total_amount': row[5],
                    'opo_date': row[6],
                    'opo_request_date': row[7],
                    'opo_est_delivery_date': row[8],
                    'opo_closed_date': row[9],
                    'opo_status': row[10],
                    'opo_is_special_order': row[11]
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
        cursor.executemany(insert_query, values)
        db.da_prod_conn.commit()
        cursor.close()
        print('PO Upload')
    except Exception as e:
        print(e)
    db.da_prod_conn.close()

########################################################################################
if __name__ == "__main__":
    read_query = """
                SELECT 
                    p.PurchaseOrderID as opo_id,
                    p.VendorID as ovendor_id,
                    p.ContainerNumber as opo_container_number,
                    p.OpenAmt as opo_open_amount,
                    p.SubTotAmt as opo_subtotal_amount,
                    p.TotAmt as opo_total_amount,
                    p.DateCreated as opo_date,
                    p.RequestDate as opo_request_date,
                    p.DlvyDate as opo_est_delivery_date,
                    p.DateClosed as opo_closed_date,
                    p.RecStatus as opo_status,
                    CASE WHEN p.SpecOrdFlg = 1 THEN 1 ELSE 0 END AS opo_is_special_order
                  FROM [DowneastDW].[storis].[PurchaseOrder] p
                  WHERE p.DateCreated > '2022-12-31'
               """

    insert_query = """
                    INSERT INTO oPO (opo_id, 
                                    ovendor_id,
                                    opo_container_number,
                                    opo_open_amount,
                                    opo_subtotal_amount,
                                    opo_total_amount,
                                    opo_date,
                                    opo_request_date,
                                    opo_est_delivery_date,
                                    opo_closed_date,
                                    opo_status,
                                    opo_is_special_order
                                    )
                
                    VALUES( %(opo_id)s, 
                            %(ovendor_id)s,
                            %(opo_container_number)s,
                            %(opo_open_amount)s,
                            %(opo_subtotal_amount)s,
                            %(opo_total_amount)s,
                            %(opo_date)s,
                            %(opo_request_date)s,
                            %(opo_est_delivery_date)s,
                            %(opo_closed_date)s,
                            %(opo_status)s,
                            %(opo_is_special_order)s
                            )
                    ON DUPLICATE KEY UPDATE
                            ovendor_id = VALUES(ovendor_id),
                            opo_container_number = VALUES(opo_container_number),
                            opo_open_amount = VALUES(opo_open_amount),
                            opo_subtotal_amount = VALUES(opo_subtotal_amount),
                            opo_total_amount = VALUES(opo_total_amount),
                            opo_date = VALUES(opo_date),
                            opo_request_date = VALUES(opo_request_date),
                            opo_est_delivery_date = VALUES(opo_est_delivery_date),
                            opo_closed_date = VALUES(opo_closed_date),
                            opo_status = VALUES(opo_status),
                            OMDT = VALUES(OMDT),
                            opo_is_special_order = VALUES(opo_is_special_order)
                    """

    print('PO download')
    po = read_sql(read_query)

    print('PO Upload')
    write_sql(po)

    print('PO upload finished')