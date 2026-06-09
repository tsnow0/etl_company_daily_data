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
                    'ocollection_id': row[1],
                    'ocollection_description': row[2]
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
        # empty table first because the records can be removed from STORIS altogether but will stay in our system if we don't empty it every time
        cursor = db.da_prod_conn.cursor()
        # cursor.execute("TRUNCATE TABLE oProductCollections")
        # print('Collections emptied')

        cursor.executemany(insert_query, values)
        db.da_prod_conn.commit()
        cursor.close()
    except Exception as e:
        print(e)
    db.hq_prod_conn.close()


########################################################################################
if __name__ == "__main__":
    # select statement for STORIS
    read_query = """
                SELECT 
                    pc.ProductID as oproduct_sku,
                    pc.CollectionID as ocollection_id,
                    c.Description as ocollection_description
                FROM DowneastDW.storis.Product_Collection pc
                JOIN DowneastDW.storis.Collection c on pc.CollectionID = c.CollectionID
                """

    # insert statement for downeast_analytics
    insert_query = """
                    INSERT INTO oProductCollections (oproduct_id,
                                    ocollection_id, 
                                    ocollection_description
                                    )
                    VALUES( %(oproduct_id)s,
                            %(ocollection_id)s,
                            %(ocollection_description)s
                            )
                    ON DUPLICATE KEY UPDATE
                            ocollection_id = VALUES(ocollection_id),
                            ocollection_description = VALUES(ocollection_description)
                    """

    # read in product collections
    print('Collections download')
    collections = read_sql(read_query)
    print('Collections download successful')

    # read in product ids and update components variable
    print('ProductID query download')
    collections = merge_data(collections)
    print('ProductID added to download')

    print('Collections Upload')
    write_sql(collections)

    print('Collections upload finished')
