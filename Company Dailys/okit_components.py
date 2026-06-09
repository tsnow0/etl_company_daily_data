#!/usr/bin/env python
# coding: utf-8

import DE_GlobalFunctions_Pkg.db as db
from DE_GlobalFunctions_Pkg.DE_Functions import kit_merge_data

def read_sql(query):
    #read function for pulling data from STORIS
    rcursor = db.storis_read_conn.cursor()
    rcursor.execute(query)

    row = rcursor.fetchone()
    values = []
    while row is not None:
        dict_row = {'oproduct_sku': row[0],
                    'okit_sku': row[1],
                    'okit_component_id_number': row[2],
                    'okit_id_number': row[3],
                    'okit_component_qty': row[4],
                    'okit_component_recstatus': row[5],
                    'okit_component_date_created': row[6],
                    'okit_component_serial_nbr': row[7]
                    }
        values.append(dict_row)
        row = rcursor.fetchone()
    rcursor.close()
    db.storis_read_conn.close()
    return values

########################################################################################
def write_sql(values):
    #write function for writing data to Downeast_analytics
    try:
        #empty table first because the records can be removed from STORIS altogether but will stay in our system if we don't empty it every time
        cursor = db.da_prod_conn.cursor()
        cursor.execute("TRUNCATE TABLE oKitComponents")
        print('KitComponents emptied')


        cursor.executemany(insert_query, values)
        db.da_prod_conn.commit()
        cursor.close()
    except Exception as e:
        print(e)
    db.da_prod_conn.close()

########################################################################################
if __name__ == "__main__":

    #select statement for STORIS
    read_query = """
                 SELECT
                    k.ProductID as oproduct_sku,
                    k.Kit_ProductID as okit_sku,
                    k.IDNumber as okit_component_id_number,
                    k.Kit_IDNumber as okit_id_number,
                    k.Qty as okit_component_qty,
                    k.RecStatus as okit_component_recstatus,
                    k.DateCreated as okit_component_date_created,
                    k.SerialNbrID as okit_component_serial_nbr
                  FROM [DowneastDW].[storis].[KitComponents] k
                  WHERE Kit_IDNumber = 0;
                 """

    #insert statement for downeast_analytics
    insert_query = """
                    INSERT INTO oKitComponents (oproduct_id,
                                    okit_product_id,
                                    okit_component_id_number,
                                    okit_id_number,
                                    okit_component_qty,
                                    okit_component_recstatus,
                                    okit_component_date_created,
                                    okit_component_serial_nbr
                                    )
                
                    VALUES( %(oproduct_id)s,
                            %(okit_product_id)s,
                            %(okit_component_id_number)s,
                            %(okit_id_number)s,
                            %(okit_component_qty)s,
                            %(okit_component_recstatus)s,
                            %(okit_component_date_created)s,
                            %(okit_component_serial_nbr)s
                            )
                    ON DUPLICATE KEY UPDATE
                            okit_component_qty = VALUES(okit_component_qty),
                            okit_component_recstatus = VALUES(okit_component_recstatus),
                            # okit_component_date_created = VALUES(okit_component_date_created),
                            okit_component_serial_nbr = VALUES(okit_component_serial_nbr)
                    """

    #read in kit components
    print('Kit Components download')
    components = read_sql(read_query)
    print('Kit Components download successful')

    #read in product ids and update components variable
    print('ProductID query download')
    components = kit_merge_data(components)
    #merge_data(components, prod_ids)
    print('ProductID added to download')

    #upload kit components into database
    print('Kit Components Upload')
    write_sql(components)

    print('Kit Components upload finished')