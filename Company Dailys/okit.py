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
        dict_row = {'oproduct_sku': row[0],
                    'okit_number': row[1],
                    'okit_description': row[2],
                    'okit_type': row[3],
                    'okit_status': row[4],
                    'okit_record_status': row[5],
                    'okit_reason_code': row[6],
                    'okit_created_date': row[7]
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
        cursor.execute("TRUNCATE TABLE oKits")
        print('Kits emptied')

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
                    k.ProductID,
                    k.IDNumber,
                    p.Description,
                    k.KitStatusID,
                    k.KitStatusCodeID,
                    k.RecStatus,
                    k.ReasonCodeID,
                    k.StorisCreateDate
                  FROM [DowneastDW].[storis].[Kit] k
                  JOIN [DowneastDW].[storis].[Product] p ON k.ProductID = p.ProductID
                  WHERE k.RecStatus <> 'D';
               """

    insert_query = """
                    INSERT INTO oKits (oproduct_id,
                                    okit_number,
                                    okit_description,
                                    okit_type,
                                    okit_status,
                                    okit_record_status,
                                    okit_reason_code,
                                    okit_created_date
                                    )
                
                    VALUES( %(oproduct_id)s,
                            %(okit_number)s,
                            %(okit_description)s,
                            %(okit_type)s,
                            %(okit_status)s,
                            %(okit_record_status)s,
                            %(okit_reason_code)s,
                            %(okit_created_date)s
                            )
                    ON DUPLICATE KEY UPDATE
                        okit_description = VALUES(okit_description),
                        okit_type = VALUES(okit_type),
                        okit_status = VALUES(okit_status),
                        okit_record_status = VALUES(okit_record_status),
                        okit_reason_code = VALUES(okit_reason_code),
                        okit_created_date = VALUES(okit_created_date),
                        OMDT = VALUES(OMDT)
                    """

    print('Kits download')
    kits = read_sql(read_query)

    # read in product ids and update components variable
    print('ProductID query download')
    kits = merge_data(kits)
    # merge_data(components, prod_ids)
    print('ProductID added to download')

    print('Kits Upload')
    write_sql(kits)

    print('Kits upload finished')
