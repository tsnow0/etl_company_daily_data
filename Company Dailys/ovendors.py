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
        dict_row = {'ovendor_id':row[0],
                    'ovendor_name':row[1],
                    'ovendor_city':row[2],
                    'ovendor_state':row[3],
                    'ovendor_country':row[4],
                    'ovendor_apterms':row[5],
                    'ovendor_total_bal':row[6],
                    'ovendor_lead_days': row[7],
                    'ovendor_freight_factor': row[8]
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
        cursor.execute("TRUNCATE TABLE oVendors")
        print('Vendors emptied')

        cursor.executemany(insert_query, values)
        db.da_prod_conn.commit()
        cursor.close()
    except Exception as e:
        print(e)
    db.da_prod_conn.close()
    print("Vendors Upload")

########################################################################################
if __name__ == "__main__":
    read_query = """
                SELECT
                    v.VendorID as ovendor_id,
                    v.Name as ovendor_name,
                    v.City as ovendor_city,
                    CASE WHEN v.CountryID = 'USA' THEN v.State ELSE NULL END as ovendor_state,
                    v.CountryID as ovendor_country,
                    v.APTermsCode as ovendor_apterms,
                    v.APTotalBal as ovendor_total_bal,
                    b.LeadDays as ovendor_lead_days,
                    v.FreightFactor as ovendor_freight_factor
                FROM [DowneastDW].[storis].[Vendor] v
                LEFT JOIN [DowneastDW].[storis].[Budget] b on v.VendorID = b.VendorID
                WHERE v.RecStatus <> 'D'
                """

    insert_query = """
                    INSERT INTO oVendors (ovendor_id,
                                    ovendor_name,
                                    ovendor_city,
                                    ovendor_state,
                                    ovendor_country,
                                    ovendor_apterms,
                                    ovendor_total_bal,
                                    ovendor_lead_days,
                                    ovendor_freight_factor
                                    )
                    VALUES( %(ovendor_id)s,
                            %(ovendor_name)s,
                            %(ovendor_city)s,
                            %(ovendor_state)s,
                            %(ovendor_country)s,
                            %(ovendor_apterms)s,
                            %(ovendor_total_bal)s,
                            %(ovendor_lead_days)s,
                            %(ovendor_freight_factor)s
                            )
                    ON DUPLICATE KEY UPDATE
                            ovendor_name = VALUES(ovendor_name),
                            ovendor_city = VALUES(ovendor_city),
                            ovendor_state = VALUES(ovendor_state),
                            ovendor_country = VALUES(ovendor_country),
                            ovendor_apterms = VALUES(ovendor_apterms),
                            ovendor_total_bal = VALUES(ovendor_total_bal),
                            ovendor_lead_days = VALUES(ovendor_lead_days),
                            ovendor_freight_factor = VALUES(ovendor_freight_factor)
                    """
    print('Vendors download')
    vendors = read_sql(read_query)
    print('Vendors upload')
    write_sql(vendors)

    print('Vendors upload finished')


