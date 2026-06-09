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
                    'oproduct_width': row[1],
                    'oproduct_length': row[2],
                    'oproduct_height': row[3],
                    'oproduct_cubic_feet': row[4],
                    'oproduct_case_weight': row[5],
                    'oproduct_storage_width': row[6],
                    'oproduct_storage_length': row[7],
                    'oproduct_storage_height': row[8],
                    'oproduct_storage_weight': row[9]
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
        cursor.execute("TRUNCATE TABLE oProductDims")
        print('ProductDims emptied')

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
                SELECT p.ProductID as oproduct_sku, 
                       p.WidthDimension as oproduct_width, 
                       p.DepthDimension as oproduct_length, 
                       p.HeightDimension as oproduct_height,
                       p.CubicFeet as oproduct_cubic_feet,
                       p.CaseWeight as oproduct_case_weight,
                       p.StorageWidth as oproduct_storage_width,
                       p.StorageDepth as oproduct_storage_length,
                       p.StorageHeight as oproduct_storage_height,
                       p.StorageWeight as oproduct_storage_weight
                FROM DowneastDW.storis.Product p
                WHERE p.ProductID NOT IN ('PART1176001')
                """

    # insert statement for downeast_analytics
    insert_query = """
                INSERT INTO oProductDims (oproduct_id,
                                oproduct_width, 
                                oproduct_length, 
                                oproduct_height,
                                oproduct_cubic_feet,
                                oproduct_case_weight,
                                oproduct_storage_width,
                                oproduct_storage_length,
                                oproduct_storage_height,
                                oproduct_storage_weight
                                )
                VALUES( %(oproduct_id)s,
                        %(oproduct_width)s,
                        %(oproduct_length)s,
                        %(oproduct_height)s,
                        %(oproduct_cubic_feet)s,
                        %(oproduct_case_weight)s,
                        %(oproduct_storage_width)s,
                        %(oproduct_storage_length)s,
                        %(oproduct_storage_height)s,
                        %(oproduct_storage_weight)s
                        )
                ON DUPLICATE KEY UPDATE
                        oproduct_width = VALUES(oproduct_width),
                        oproduct_length = VALUES(oproduct_length),
                        oproduct_height = VALUES(oproduct_height),
                        oproduct_cubic_feet = VALUES(oproduct_cubic_feet),
                        oproduct_case_weight = VALUES(oproduct_case_weight),
                        oproduct_storage_width = VALUES(oproduct_storage_width),
                        oproduct_storage_length = VALUES(oproduct_storage_length),
                        oproduct_storage_height = VALUES(oproduct_storage_height),
                        oproduct_storage_weight = VALUES(oproduct_storage_weight)
                """

    # read in product dims
    print('Product Dims download')
    dims = read_sql(read_query)
    print('Product Dims download successful')

    # read in product ids and update components variable
    print('ProductID query download')
    dims = merge_data(dims)
    print('ProductID added to download')

    print('Product Dims Upload')
    write_sql(dims)

    print('Product Dims upload finished')