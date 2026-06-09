import DE_GlobalFunctions_Pkg.db as db
from DE_GlobalFunctions_Pkg.DE_Functions import merge_data


def read_sql(query):
    rcursor = db.storis_read_conn.cursor()
    rcursor.execute(query)

    row = rcursor.fetchone()
    values = []
    while row is not None:
        dict_row = {'obrand_id':row[0],
                    'obrand_name':row[1]
                   }
        values.append(dict_row)
        # values.append(dict(row))
        row = rcursor.fetchone()
    rcursor.close()
    db.storis_read_conn.close()
    return values


########################################################################################
def fix_brand_id(brands):
    for brand_dicts in brands:
        brand_dicts.update((key, "9999") for key, value in brand_dicts.items() if value == "BeckyOwens")

    return brands


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
                    b.BrandID as obrand_id,
                    b.Name as obrand_name
                FROM DowneastDW.storis.Brand b
                WHERE b.BrandID NOT IN ('<COGID>','<No Value>')
                """

    insert_query = """
                    INSERT INTO oBrands (obrand_id,
                                obrand_name
                                )

                    VALUES( %(obrand_id)s, 
                            %(obrand_name)s
                          )
                    ON DUPLICATE KEY UPDATE
                        obrand_name = VALUES (obrand_name),
                        OMDT = VALUES(OMDT)
                    """

    print('Brands download')
    brands = read_sql(read_query)

    # # fix becky owens brand because some idiot decided to make the Brand ID text instead of a number
    # print('fix becky owens brand')
    # brands = fix_brand_id(brands)

    print('Brands upload')
    write_sql(brands)

    print('Brands upload finished')
