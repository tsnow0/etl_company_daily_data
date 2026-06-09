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
                    'ocustomer_id': row[1],
                    'oorder_date': row[2],
                    'oorder_rec_status': row[3],
                    'oorder_nbr_of_invoices': row[4],
                    'oorder_terms_id': row[5],
                    'oorder_customer_type': row[6],
                    'oorder_delivery_date': row[7],
                    'oorder_delivery_status': row[8],
                    'oorder_delivery_items': row[9],
                    'oorder_delivery_sub_total': row[10],
                    'oorder_invoice_date': row[11],
                    'oorder_landed_freight': row[12],
                    'oorder_manifest_number': row[13],
                    'oorder_merch_sub_total': row[14],
                    'oorder_total_addl_tax_amt': row[15],
                    'oorder_total_discount_amt': row[16],
                    'oorder_total_invoice_amt': row[17],
                    'oorder_total_merch_cost': row[18],
                    'oorder_total_order_value': row[19],
                    'oorder_total_payment_amt': row[20],
                    'oorder_total_sales_amt': row[21],
                    'oorder_total_state_tax_amt': row[22],
                    'oorder_voided_date': row[23],
                    'oorder_voided_order_code': row[24]}
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
            print("Chunk #" + str(numchunk) + " - Orders Upload")
        except Exception as e:
            print(e)
            print("Chunk #" + str(numchunk) + " - Orders Upload Failed")

    db.da_prod_conn.close()

########################################################################################
if __name__ == "__main__":
    read_query = """
                 SELECT o.OrderID,
                        o.CustomerID,
                        o.OrderDate,
                        o.RecStatus,
                        o.NbrOfInvoices,
                        o.TermsID,
                        o.CustType,
                        o.DlvyDate,
                        o.DlvyStatus,
                        o.DlvyItems,
                        o.DlvySubTot,
                        o.InvoiceDate,
                        o.LandedFreight,
                        o.ManifestNbr,
                        o.MerchSubTot,
                        o.TotAddlTaxAmt,
                        o.TotCustDiscntAmt,
                        o.TotInvcAmt,
                        o.TotMerchCost,
                        o.TotOrderValue,
                        o.TotPaymentAmt,
                        o.TotSaleAmt,
                        o.TotStateTaxAmt,
                        o.VoidedDate,
                        o.VoidedOrderReasonCodeID
                 FROM DowneastDW.storis.orders o
                 WHERE o.OrderDate > '2022-12-31'
                 AND o.OrderID NOT LIKE 'T%';
                """

    insert_query = """
                    INSERT INTO oOrders (oorder_id, 
                                    ocustomer_id,
                                    oorder_date,
                                    oorder_rec_status,
                                    oorder_nbr_of_invoices,
                                    oorder_terms_id,
                                    oorder_customer_type,
                                    oorder_delivery_date,
                                    oorder_delivery_status,
                                    oorder_delivery_items,
                                    oorder_delivery_sub_total,
                                    oorder_invoice_date,
                                    oorder_landed_freight,
                                    oorder_manifest_number,
                                    oorder_merch_sub_total,
                                    oorder_total_addl_tax_amt,
                                    oorder_total_discount_amt,
                                    oorder_total_invoice_amt,
                                    oorder_total_merch_cost,
                                    oorder_total_order_value,
                                    oorder_total_payment_amt,
                                    oorder_total_sales_amt,
                                    oorder_total_state_tax_amt,
                                    oorder_voided_date,
                                    oorder_voided_order_code
                                    )
                
                    VALUES( %(oorder_id)s, 
                            %(ocustomer_id)s,
                            %(oorder_date)s,
                            %(oorder_rec_status)s,
                            %(oorder_nbr_of_invoices)s,
                            %(oorder_terms_id)s,
                            %(oorder_customer_type)s,
                            %(oorder_delivery_date)s,
                            %(oorder_delivery_status)s,
                            %(oorder_delivery_items)s,
                            %(oorder_delivery_sub_total)s,
                            %(oorder_invoice_date)s, 
                            %(oorder_landed_freight)s,
                            %(oorder_manifest_number)s,
                            %(oorder_merch_sub_total)s,
                            %(oorder_total_addl_tax_amt)s,
                            %(oorder_total_discount_amt)s,
                            %(oorder_total_invoice_amt)s,
                            %(oorder_total_merch_cost)s,
                            %(oorder_total_order_value)s,
                            %(oorder_total_payment_amt)s,
                            %(oorder_total_sales_amt)s,
                            %(oorder_total_state_tax_amt)s,
                            %(oorder_voided_date)s,
                            %(oorder_voided_order_code)s
                            )   
                    ON DUPLICATE KEY UPDATE
                        oorder_rec_status = VALUES(oorder_rec_status),
                        oorder_nbr_of_invoices = VALUES(oorder_nbr_of_invoices),
                        oorder_terms_id = VALUES(oorder_terms_id),
                        oorder_customer_type = VALUES(oorder_customer_type),
                        oorder_delivery_date = VALUES(oorder_delivery_date),
                        oorder_delivery_status = VALUES(oorder_delivery_status),
                        oorder_delivery_items = VALUES(oorder_delivery_items),
                        oorder_delivery_sub_total = VALUES(oorder_delivery_sub_total),
                        oorder_invoice_date = VALUES(oorder_invoice_date),
                        oorder_landed_freight = VALUES(oorder_landed_freight),
                        oorder_manifest_number = VALUES(oorder_manifest_number),
                        oorder_merch_sub_total = VALUES(oorder_merch_sub_total),
                        oorder_total_addl_tax_amt = VALUES(oorder_total_addl_tax_amt),
                        oorder_total_discount_amt = VALUES(oorder_total_discount_amt),
                        oorder_total_invoice_amt = VALUES(oorder_total_invoice_amt),
                        oorder_total_merch_cost = VALUES(oorder_total_merch_cost),
                        oorder_total_order_value = VALUES(oorder_total_order_value),
                        oorder_total_payment_amt = VALUES(oorder_total_payment_amt),
                        oorder_total_sales_amt = VALUES(oorder_total_sales_amt),
                        oorder_total_state_tax_amt = VALUES(oorder_total_state_tax_amt),
                        oorder_voided_date = VALUES(oorder_voided_date),
                        oorder_voided_order_code = VALUES(oorder_voided_order_code)
                    """
    print('Orders download')
    orders = read_sql(read_query)

    print('Orders Upload')
    write_sql(orders)

    print('Orders upload finished')