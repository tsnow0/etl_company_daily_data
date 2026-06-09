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
        dict_row = {'oorder_id': row[0],
                    'oorderitem_line_id': row[1],
                    'oproduct_sku': row[2],
                    'opo_id': row[3],
                    'ostore_id': row[4],
                    'oorderitem_cost_source': row[5],
                    'oorderitem_discount_flag': row[6],
                    'oorderitem_dlvy_status': row[7],
                    'oorderitem_dlvy_type': row[8],
                    'oorderitem_landed_freight': row[9],
                    'oorderitem_line_cost': row[10],
                    'oorderitem_product_case_price': row[11],
                    'oorderitem_committed_qty': row[12],
                    'oorderitem_ordered_qty': row[13],
                    'oorderitem_undelivered_qty': row[14],
                    'oorderitem_rcvd_po_id': row[15],
                    'oorderitem_rcvd_po_line_id': row[16],
                    'oorderitem_rec_status': row[17],
                    'oorderitem_ship_location_id': row[18],
                    'oorderitem_spec_order_flag': row[19],
                    'oorderitem_total_cost': row[20],
                    'oorderitem_written_date': row[21]}
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
    for chunk in chunker(values, 5000):
        try:
            cursor = db.da_prod_conn.cursor()
            cursor.executemany(insert_query, chunk)
            db.da_prod_conn.commit()
            cursor.close()
            numchunk = numchunk + 1
            print("Chunk #" + str(numchunk) + " - OrderItems Upload")
        except Exception as e:
            print(e)
            print("Chunk #" + str(numchunk) + " - OrderItems Upload Failed")

    db.da_prod_conn.close()

########################################################################################
if __name__ == "__main__":
    read_query = """
                 SELECT 
                    oi.OrderID,
                    oi.ItemID,
                    oi.ProductID,
                    oi.PurchaseOrderID,
                    oi.StoreID,
                    oi.CostSource,
                    oi.DiscntFlg,
                    oi.DlvyStatus,
                    oi.DlvyTypeCodeID,
                    oi.LandedFreight,
                    oi.LineCost,
                    oi.CaseSellingPrice,
                    oi.QtyCommitted,
                    oi.QtyOrdered,
                    oi.QtyUndelivered,
                    oi.RcvdPurchaseOrderID,
                    oi.RcvdPOLineID,
                    oi.RecStatus,
                    oi.ShipLocnID,
                    oi.SpecOrderFlg,
                    oi.TotCost,
                    oi.WrittenDate
                 FROM DowneastDW.storis.OrderItem oi
                 WHERE YEAR(oi.WrittenDate) > 2022
                 AND oi.TransCodeID NOT IN (60,61,66);
                """

    insert_query = """
                    INSERT INTO oOrderItems (oorder_id, 
                                    oorderitem_line_id,
                                    oproduct_id,
                                    opo_id,
                                    ostore_id,
                                    oorderitem_cost_source,
                                    oorderitem_discount_flag,
                                    oorderitem_dlvy_status,
                                    oorderitem_dlvy_type,
                                    oorderitem_landed_freight,
                                    oorderitem_line_cost,
                                    oorderitem_product_case_price,
                                    oorderitem_committed_qty,
                                    oorderitem_ordered_qty,
                                    oorderitem_undelivered_qty,
                                    oorderitem_rcvd_po_id,
                                    oorderitem_rcvd_po_line_id,
                                    oorderitem_rec_status,
                                    oorderitem_ship_location_id,
                                    oorderitem_spec_order_flag,
                                    oorderitem_total_cost,
                                    oorderitem_written_date
                                    )
                
                    VALUES( %(oorder_id)s, 
                            %(oorderitem_line_id)s,
                            %(oproduct_id)s,
                            %(opo_id)s,
                            %(ostore_id)s,
                            %(oorderitem_cost_source)s,
                            %(oorderitem_discount_flag)s,
                            %(oorderitem_dlvy_status)s,
                            %(oorderitem_dlvy_type)s,
                            %(oorderitem_landed_freight)s,
                            %(oorderitem_line_cost)s,
                            %(oorderitem_product_case_price)s, 
                            %(oorderitem_committed_qty)s,
                            %(oorderitem_ordered_qty)s,
                            %(oorderitem_undelivered_qty)s,
                            %(oorderitem_rcvd_po_id)s,
                            %(oorderitem_rcvd_po_line_id)s,
                            %(oorderitem_rec_status)s,
                            %(oorderitem_ship_location_id)s,
                            %(oorderitem_spec_order_flag)s,
                            %(oorderitem_total_cost)s,
                            %(oorderitem_written_date)s
                            )
                    ON DUPLICATE KEY UPDATE
                        opo_id = VALUES(opo_id),
                        ostore_id = VALUES(ostore_id),
                        oorderitem_cost_source = VALUES(oorderitem_cost_source),
                        oorderitem_discount_flag = VALUES(oorderitem_discount_flag),
                        oorderitem_dlvy_status = VALUES(oorderitem_dlvy_status),
                        oorderitem_dlvy_type = VALUES(oorderitem_dlvy_type),
                        oorderitem_landed_freight = VALUES(oorderitem_landed_freight),
                        oorderitem_line_cost = VALUES(oorderitem_line_cost),
                        oorderitem_product_case_price = VALUES(oorderitem_product_case_price),
                        oorderitem_committed_qty = VALUES(oorderitem_committed_qty),
                        oorderitem_ordered_qty = VALUES(oorderitem_ordered_qty),
                        oorderitem_undelivered_qty = VALUES(oorderitem_undelivered_qty),
                        oorderitem_rcvd_po_id = VALUES(oorderitem_rcvd_po_id),
                        oorderitem_rcvd_po_line_id = VALUES(oorderitem_rcvd_po_line_id),
                        oorderitem_rec_status = VALUES(oorderitem_rec_status),
                        oorderitem_ship_location_id = VALUES(oorderitem_ship_location_id),
                        oorderitem_spec_order_flag = VALUES(oorderitem_spec_order_flag),
                        oorderitem_total_cost = VALUES(oorderitem_total_cost),
                        oorderitem_written_date = VALUES(oorderitem_written_date)
                    """

    #read in order items
    print('OrderItems download')
    orderitems = read_sql(read_query)
    print('OrderItems download successful')

    #read in product ids and update orderitems variable
    print('Order Item ProductID query download')
    orderitems = merge_data(orderitems)
    print('Order Item product id added to download')

    #upload orderitems into database
    print('OrderItems Upload')
    write_sql(orderitems)

    print('OrderItems upload successful')
