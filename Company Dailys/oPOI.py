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
        dict_row = {'opo_id':row[0],
                    'opoi_line_id':row[1],
                    'oproduct_sku':row[2],
                    'obrand_id':row[3],
                    'ostore_id':row[4],
                    'opoi_inv_cost':row[5],
                    'opoi_qty_in_transit':row[6],
                    'opoi_qty_ordered':row[7],
                    'opoi_qty_received':row[8],
                    'ovendor_id':row[9],
                    'opoi_vendor_model_nbr':row[10],
                    'opoi_is_special_order':row[11],
                    'opoi_date_created':row[12],
                    'opoi_est_delivery_date':row[13],
                    'opoi_original_est_dlvy_date':row[14],
                    'opoi_status': row[15]
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
    except Exception as e:
        print(e)
    db.da_prod_conn.close()

########################################################################################
if __name__ == "__main__":
    read_query = """
                SELECT 
                    p.PurchaseOrderID as opo_id,
                    p.LineID as opoi_line_id,
                    p.ProductID as oproduct_sku,
                    p.BrandID as obrand_id,
                    p.StoreID as ostore_id,
                    p.InvCost as opoi_inv_cost,
                    p.QtyInTransit as opoi_qty_in_transit,
                    p.QtyOrdered as opoi_qty_ordered,
                    p.QtyReceived as opoi_qty_received,
                    p.VendorID as ovendor_id,
                    p.VendorModelNbr as opoi_vendor_model_nbr,
                    p.SpecOrderFlg as opoi_is_special_order,
                    p.DateCreated as opoi_date_created,
                    p.DlvyDate as opoi_est_delivery_date,
                    p.EDIOriginalExpectedDeliveryDate as opoi_original_est_dlvy_date,
                    p.RecStatus as opoi_status
                  FROM [DowneastDW].[storis].[PurchaseOrderItem] p
                  WHERE p.DateCreated > '2022-12-31'
                """

    insert_query = """
                INSERT INTO oPOI (opo_id, 
                                opoi_line_id,
                                oproduct_id,
                                obrand_id,
                                ostore_id, 
                                opoi_inv_cost, 
                                opoi_qty_in_transit,
                                opoi_qty_ordered,
                                opoi_qty_received,
                                ovendor_id,
                                opoi_vendor_model_nbr,
                                opoi_is_special_order,
                                opoi_date_created,
                                opoi_est_delivery_date,
                                opoi_original_est_dlvy_date,
                                opoi_status
                                )
                VALUES( %(opo_id)s, 
                        %(opoi_line_id)s,
                        %(oproduct_id)s,
                        %(obrand_id)s,
                        %(ostore_id)s, 
                        %(opoi_inv_cost)s, 
                        %(opoi_qty_in_transit)s,
                        %(opoi_qty_ordered)s,
                        %(opoi_qty_received)s,
                        %(ovendor_id)s,
                        %(opoi_vendor_model_nbr)s,
                        %(opoi_is_special_order)s,
                        %(opoi_date_created)s,
                        %(opoi_est_delivery_date)s,
                        %(opoi_original_est_dlvy_date)s,
                        %(opoi_status)s
                        )   
                ON DUPLICATE KEY UPDATE
                        obrand_id = VALUES(obrand_id),
                        ostore_id = VALUES(ostore_id),
                        opoi_inv_cost = VALUES(opoi_inv_cost),
                        opoi_qty_in_transit = VALUES(opoi_qty_in_transit),
                        opoi_qty_ordered = VALUES(opoi_qty_ordered),
                        opoi_qty_received = VALUES(opoi_qty_received),
                        ovendor_id = VALUES(ovendor_id),
                        opoi_vendor_model_nbr = VALUES(opoi_vendor_model_nbr),
                        opoi_date_created = VALUES(opoi_date_created),
                        opoi_est_delivery_date = VALUES(opoi_est_delivery_date),
                        opoi_original_est_dlvy_date = VALUES(opoi_original_est_dlvy_date),
                        opoi_status = VALUES(opoi_status),
                        OMDT = VALUES(OMDT)
                """

    #read in poi
    print('POI download')
    poi = read_sql(read_query)
    print('POI download successful')

    print('ProductID query download')
    poi = merge_data(poi)
    print('product id added to download')

    print('POI Upload')
    write_sql(poi)

    print('POI upload finished')