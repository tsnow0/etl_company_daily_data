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
                    'obase_order_id': row[1],
                    'ocustomer_id': row[2],
                    'oinvoice_date_created': row[3],
                    'oinvoice_date_changed': row[4],
                    'oinvoice_eta': row[5],
                    'oinvoice_date': row[6],
                    'oinvoice_nbr_invoices': row[7],
                    'oinvoice_TotAddTaxAmt': row[8],
                    'oinvoice_TotCommissionableAmt': row[9],
                    'oinvoice_TotCustDiscAmt': row[10],
                    'oinvoice_TotInvoiceAmt': row[11],
                    'oinvoice_TotMerchCost': row[12],
                    'oinvoice_TotSaleAmt': row[13],
                    'oinvoice_TotSpecOrderAmt': row[14],
                    'oinvoice_voided_date': row[15],
                    'oinvoice_voided_reason_code': row[16]
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
        print("Invoices Uploaded")
    except Exception as e:
        print(e)
    db.da_prod_conn.close()

########################################################################################
if __name__ == '__main__':
    read_query = """
                SELECT
                i.OrderID,
                i.Base_OrderID, 
                i.CustomerID,
                i.DateCreated,
                i.DateChanged,
                i.DlvyDate,
                i.InvoiceDate,
                i.NbrOfInvoices,
                i.TotAddlTaxAmt,
                i.TotCommissionableAmt,
                i.TotCustDiscntAmt,
                i.TotInvcAmt,
                i.MerchSubTot,
                i.TotSaleAmt,
                i.TotSpecOrderAmt,
                i.VoidedDate,
                i.VoidedOrderReasonCodeID
                FROM RetailCompanyDW.storis.Invoice i
                WHERE YEAR(i.DateCreated) >= 2023
                """

    insert_query = """
                    INSERT INTO oInvoices (oorder_id, 
                                    obase_order_id,
                                    ocustomer_id, 
                                    oinvoice_date_created,
                                    oinvoice_date_changed,
                                    oinvoice_eta, 
                                    oinvoice_date, 
                                    oinvoice_nbr_invoices,
                                    oinvoice_TotAddTaxAmt,
                                    oinvoice_TotCommissionableAmt,
                                    oinvoice_TotCustDiscAmt,
                                    oinvoice_TotInvoiceAmt,
                                    oinvoice_TotMerchCost,
                                    oinvoice_TotSaleAmt,
                                    oinvoice_TotSpecOrderAmt,
                                    oinvoice_voided_date,
                                    oinvoice_voided_reason_code
                                    )
                    VALUES( %(oorder_id)s, 
                            %(obase_order_id)s,
                            %(ocustomer_id)s,
                            %(oinvoice_date_created)s,
                            %(oinvoice_date_changed)s,
                            %(oinvoice_eta)s, 
                            %(oinvoice_date)s, 
                            %(oinvoice_nbr_invoices)s,
                            %(oinvoice_TotAddTaxAmt)s,
                            %(oinvoice_TotCommissionableAmt)s,
                            %(oinvoice_TotCustDiscAmt)s,
                            %(oinvoice_TotInvoiceAmt)s,
                            %(oinvoice_TotMerchCost)s,
                            %(oinvoice_TotSaleAmt)s,
                            %(oinvoice_TotSpecOrderAmt)s,
                            %(oinvoice_voided_date)s,
                            %(oinvoice_voided_reason_code)s
                            )
                    ON DUPLICATE KEY UPDATE
                            obase_order_id = VALUES(obase_order_id),
                            ocustomer_id = VALUES(ocustomer_id),
                            oinvoice_date_created = VALUES(oinvoice_date_created),
                            oinvoice_date_changed = VALUES(oinvoice_date_changed),
                            oinvoice_eta = VALUES(oinvoice_eta),
                            oinvoice_date = VALUES(oinvoice_date),
                            oinvoice_nbr_invoices = VALUES(oinvoice_nbr_invoices),
                            oinvoice_TotAddTaxAmt = VALUES(oinvoice_TotAddTaxAmt),
                            oinvoice_TotCommissionableAmt = VALUES(oinvoice_TotCommissionableAmt),
                            oinvoice_TotCustDiscAmt = VALUES(oinvoice_TotCustDiscAmt),
                            oinvoice_TotInvoiceAmt = VALUES(oinvoice_TotInvoiceAmt),
                            oinvoice_TotMerchCost = VALUES(oinvoice_TotMerchCost),
                            oinvoice_TotSaleAmt = VALUES(oinvoice_TotSaleAmt),
                            oinvoice_TotSpecOrderAmt = VALUES(oinvoice_TotSpecOrderAmt),
                            oinvoice_voided_date = VALUES(oinvoice_voided_date),
                            oinvoice_voided_reason_code = VALUES(oinvoice_voided_reason_code)
                    """


    print('Invoices download')
    invoices = read_sql(read_query)

    print('Invoices upload')
    write_sql(invoices)

    print('Invoices upload finished')

