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
        dict_row = {'ocategory_abbrv': row[0],
                    'ocategory_name': row[1],
                    'ocategory_inv_type': row[2],
                    'ocategory_is_active': row[3],
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
                    c.CategoryID as ocategory_abbrv,
                    c.Description as ocategory_name,
                    c.InvType as ocategory_inv_type,
                    c.IsActive as ocategory_is_active
               FROM RetailCompanyDW.storis.Category c
               """

    insert_query = """
                    INSERT INTO oCategories (ocategory_abbrv, 
                                    ocategory_name, 
                                    ocategory_inv_type,
                                    ocategory_is_active
                                    )
                
                    VALUES( %(ocategory_abbrv)s, 
                            %(ocategory_name)s,
                            %(ocategory_inv_type)s,
                            %(ocategory_is_active)s
                            )
                    ON DUPLICATE KEY UPDATE
                        ocategory_name = VALUES(ocategory_name),
                        ocategory_inv_type = VALUES(ocategory_inv_type),
                        ocategory_is_active = VALUES(ocategory_is_active)
                    """

    print('Categories download')
    categories = read_sql(read_query)

    print('Categories Upload')
    write_sql(categories)

    print('Categories upload finished')
