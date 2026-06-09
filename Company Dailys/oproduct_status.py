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
        dict_row = {'oproductstatus_code': row[0],
                    'oproductstatus_description': row[1],
                    'oproductstatus_recstatus': row[2]
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
                    p.PurchaseStatusCodeID as oproductstatus_code,
                    p.Description as oproductstatus_description,
                    p.RecStatus as oproductstatus_recstatus
                  FROM [DowneastDW].[storis].[PurchaseStatusCode] p
                  WHERE p.PurchaseStatusCodeID <> '9';
               """

    insert_query = """
                INSERT INTO oProductStatuses (oproductstatus_code,
                                oproductstatus_description,
                                oproductstatus_recstatus
                                )
            
                VALUES( %(oproductstatus_code)s,
                        %(oproductstatus_description)s,
                        %(oproductstatus_recstatus)s
                        )
                ON DUPLICATE KEY UPDATE
                    oproductstatus_recstatus = VALUES(oproductstatus_recstatus),
                    OMDT = VALUES(OMDT)
                """
    print('Product Statuses download')
    status = read_sql(read_query)

    print('Product Statuses Upload')
    write_sql(status)

    print('Product Statuses upload finished')
