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
        dict_row = {'oproduct_sku': row[0],
                    'ovendor_id': row[1],
                    'oproduct_lead_days': row[2]
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
        cursor.executemany(insert_query, values)
        db.da_prod_conn.commit()
        cursor.close()
    except Exception as e:
        print(e)
    db.da_prod_conn.close()

########################################################################################
if __name__ == "__main__":

    # select statement for STORIS
    read_query = """
                 SELECT
                    p.ProductID,
                    p.VendorID,
                    p.PurchaseLeadDays
                  FROM [DowneastDW].[storis].[Product] p;
               """

    # insert statement for downeast_analytics
    insert_query = """
                    INSERT INTO oProductLeadDays (oproduct_id,
                                    ovendor_id,
                                    oproduct_lead_days
                                    )
                
                    VALUES( %(oproduct_id)s,
                            %(ovendor_id)s,
                            %(oproduct_lead_days)s
                            )
                    ON DUPLICATE KEY UPDATE
                        oproduct_lead_days = VALUES(oproduct_lead_days),
                        OMDT = VALUES(OMDT)
    """

    # read in lead days
    print('Lead Days download')
    lead_days = read_sql(read_query)
    print('Lead Days download successful')

    #read in product ids and update components variable
    print('ProductID query download')
    lead_days = merge_data(lead_days)
    print('ProductID added to download')

    # upload kit components into database
    print('Lead Days Upload')
    write_sql(lead_days)

    print('Lead Days upload finished')