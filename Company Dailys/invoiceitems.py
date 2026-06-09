#!/usr/bin/env python
# coding: utf-8

import DE_GlobalFunctions_Pkg.db as db
from DE_GlobalFunctions_Pkg.DE_Functions import merge_data

def read_sql(query):
    #read function for pulling data from RetailCompanyDW

    rcursor = db.storis_read_conn.cursor()
    rcursor.execute(query)

    row = rcursor.fetchone()
    values = []

    while row is not None:
        dict_row = {'oorder_id': row[0],
                    'oorder_line_id': row[1],
                    'oproduct_sku': row[2],
                    'oproduct_kit_status': row[3],
                    'oproduct_status': row[4],
                    'oproduct_price': row[5],
                    'oinvoiceitem_comm_cost': row[6],
                    'oinvoiceitem_date_created': row[7],
                    'oinvoiceitem_discnt_flag': row[8],
                    'oinvoiceitem_discnt_pct': row[9],
                    'oinvoiceitem_discnt_amt': row[10],
                    'oinvoiceitem_discnt_endprice': row[11],
                    'oinvoiceitem_eta': row[12],
                    'oinvoiceitem_landed_cost': row[13],
                    'oinvoiceitem_total_cost': row[14],
                    'oinvoiceitem_committed': row[15],
                    'oinvoiceitem_ordered': row[16],
                    'oinvoiceitem_undelivered': row[17],
                    'opo_id': row[18],
                    'opo_line_id': row[19],
                    'opo_received_date': row[20],
                    'oinvoiceitem_ship_from_id': row[21],
                    'oinvoiceitem_ship_weight': row[22],
                    'ostore_id': row[23],
                    'ovendor_id': row[24],
                    'oinvoiceitem_rec_status': row[25]
                    }
        values.append(dict_row)
        #values.append(dict(row))
        row = rcursor.fetchone()
    rcursor.close()
    db.storis_read_conn.close()
    return values

########################################################################################
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

########################################################################################
def write_sql(values):
    #write function for writing data to new db table

    numchunk = 0
    for chunk in chunker(values, 50000):
        try:
            cursor = db.da_prod_conn.cursor()
            cursor.executemany(insert_query, chunk)
            db.da_prod_conn.commit()
            cursor.close()
            numchunk = numchunk + 1
            print("Chunk #" + str(numchunk) + " - Invoice Items Upload")
        except Exception as e:
            print(e)
            print("Chunk #" + str(numchunk) + " - Invoice Items Upload Failed")

    db.da_prod_conn.close()

########################################################################################
if __name__ == "__main__":

    # select statement from company's db
    read_query = """
                SELECT ii.OrderID as 'oorder_id',
                       ii.ItemID as 'oorder_line_id',
                       ii.ProductID as 'oproduct_sku',
                       ii.OrderItemType as 'oproduct_kit_status',
                       ii.PurchaseStatusCodeID as 'oproduct_status',
                       ii.CasePriceOverride as 'oproduct_price',
                       ii.CommCost as 'oinvoiceitem_comm_cost',
                       ii.DateCreated as 'oinvoiceitem_date_created',
                       ii.DiscntFlg as 'oinvoiceitem_discnt_flag',
                       ii.DiscntPct as 'oinvoiceitem_discnt_pct',
                       ii.DiscountAmt as 'oinvoiceitem_discnt_amt',
                       ii.DiscountEndPrice as 'oinvoiceitem_discnt_endprice',
                       ii.DlvyDate as 'oinvoiceitem_eta',
                       ii.LandedFreight as 'oinvoiceitem_landed_cost',
                       ii.TotCost as 'oinvoiceitem_total_cost',
                       ii.QtyCommitted as 'oinvoiceitem_committed',
                       ii.QtyOrdered as 'oinvoiceitem_ordered',
                       ii.QtyUndelivered as 'oinvoiceitem_undelivered',
                       ii.RcvdPONbr as 'opo_id',
                       ii.RcvdPOLineID as 'opo_line_id',
                       ii.RcvdPODate as 'opo_received_date',
                       ii.RecStatus as 'oinvoiceitem_status',
                       ii.ShipLocnID as 'oinvoiceitem_ship_from_id',
                       ii.TotShipWeight as 'oinvoiceitem_ship_weight',
                       ii.StoreID as 'ostore_id',
                       ii.VendorID as 'ovendor_id'
                FROM RetailCompanyDW.storis.InvoiceItem ii
                WHERE YEAR(ii.DateCreated) >= 2023
                """

    # insert statement for new db tables
    insert_query = """
                    INSERT INTO oInvoiceItems (oorder_id, 
                                    oorder_line_id,
                                    oproduct_id, 
                                    oproduct_kit_status,
                                    oproduct_status,
                                    oproduct_price, 
                                    oinvoiceitem_comm_cost, 
                                    oinvoiceitem_date_created,
                                    oinvoiceitem_discnt_flag,
                                    oinvoiceitem_discnt_pct,
                                    oinvoiceitem_discnt_amt,
                                    oinvoiceitem_discnt_endprice,
                                    oinvoiceitem_eta,
                                    oinvoiceitem_landed_cost,
                                    oinvoiceitem_total_cost,
                                    oinvoiceitem_committed,
                                    oinvoiceitem_ordered,
                                    oinvoiceitem_undelivered,
                                    opo_id,
                                    opo_line_id,
                                    opo_received_date,
                                    oinvoiceitem_ship_from_id,
                                    oinvoiceitem_ship_weight,
                                    ostore_id,
                                    ovendor_id,
                                    oinvoiceitem_rec_status
                                    )

                    VALUES( %(oorder_id)s, 
                            %(oorder_line_id)s,
                            %(oproduct_id)s,
                            %(oproduct_kit_status)s,
                            %(oproduct_status)s,
                            %(oproduct_price)s, 
                            %(oinvoiceitem_comm_cost)s, 
                            %(oinvoiceitem_date_created)s,
                            %(oinvoiceitem_discnt_flag)s,
                            %(oinvoiceitem_discnt_pct)s,
                            %(oinvoiceitem_discnt_amt)s,
                            %(oinvoiceitem_discnt_endprice)s,
                            %(oinvoiceitem_eta)s,
                            %(oinvoiceitem_landed_cost)s,
                            %(oinvoiceitem_total_cost)s,
                            %(oinvoiceitem_committed)s,
                            %(oinvoiceitem_ordered)s,
                            %(oinvoiceitem_undelivered)s,
                            %(opo_id)s,
                            %(opo_line_id)s,
                            %(opo_received_date)s,
                            %(oinvoiceitem_ship_from_id)s,
                            %(oinvoiceitem_ship_weight)s,
                            %(ostore_id)s,
                            %(ovendor_id)s,
                            %(oinvoiceitem_rec_status)s        
                            )
                            
                    ON DUPLICATE KEY UPDATE
                            oproduct_kit_status = VALUES(oproduct_kit_status),
                            oproduct_status = VALUES(oproduct_status),
                            oproduct_price = VALUES(oproduct_price),
                            oinvoiceitem_comm_cost = VALUES(oinvoiceitem_comm_cost),
                            oinvoiceitem_date_created = VALUES(oinvoiceitem_date_created),
                            oinvoiceitem_discnt_flag = VALUES(oinvoiceitem_discnt_flag),
                            oinvoiceitem_discnt_pct = VALUES(oinvoiceitem_discnt_pct),
                            oinvoiceitem_discnt_amt = VALUES(oinvoiceitem_discnt_amt),
                            oinvoiceitem_discnt_endprice = VALUES(oinvoiceitem_discnt_endprice),
                            oinvoiceitem_eta = VALUES(oinvoiceitem_eta),
                            oinvoiceitem_landed_cost = VALUES(oinvoiceitem_landed_cost),
                            oinvoiceitem_total_cost = VALUES(oinvoiceitem_total_cost),
                            oinvoiceitem_committed = VALUES(oinvoiceitem_committed),
                            oinvoiceitem_ordered = VALUES(oinvoiceitem_ordered),
                            oinvoiceitem_undelivered = VALUES(oinvoiceitem_undelivered),
                            opo_id = VALUES(opo_id),
                            opo_line_id = VALUES(opo_line_id),
                            opo_received_date = VALUES(opo_received_date),
                            oinvoiceitem_ship_from_id = VALUES(oinvoiceitem_ship_from_id),
                            oinvoiceitem_ship_weight = VALUES(oinvoiceitem_ship_weight),
                            ostore_id = VALUES(ostore_id),
                            ovendor_id = VALUES(ovendor_id),
                            oinvoiceitem_rec_status = VALUES(oinvoiceitem_rec_status)
                   """


    print('InvoiceItems download')
    invoiceitems = read_sql(read_query)
    print('Kit Components download successful')

    print('ProductID query download')
    invoiceitems = merge_data(invoiceitems)
    print('ProductID added to download')

    print('InvoiceItems Upload')
    write_sql(invoiceitems)

    print('InvoiceItems upload finished')
