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
        dict_row = {'odistrict_id': row[0],
                    'odistrict_name': row[1],
                    'odistrict_city': row[2],
                    'odistrict_state': row[3],
                    'odistrict_zip': row[4]
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
                    d.DistrictID as odistrict_id,
                    d.Name as odistrict_name,
                    d.City as odistrict_city, 
                    d.State as odistrict_state,
                    d.PostalCodeID as odistrict_zip
                FROM DowneastDW.storis.District d
               """

    insert_query = """
                    INSERT INTO oDistricts (odistrict_id, 
                                    odistrict_name, 
                                    odistrict_city,
                                    odistrict_state,
                                    odistrict_zip
                                    )
                
                    VALUES( %(odistrict_id)s, 
                            %(odistrict_name)s,
                            %(odistrict_city)s,
                            %(odistrict_state)s,
                            %(odistrict_zip)s
                            )
                    ON DUPLICATE KEY UPDATE
                        odistrict_name = VALUES(odistrict_name),
                        odistrict_city = VALUES(odistrict_city),
                        odistrict_state = VALUES(odistrict_state),
                        odistrict_zip = VALUES(odistrict_zip)
                    """


    print('Districts download')
    districts = read_sql(read_query)

    print('Districts Upload')
    write_sql(districts)

    print('Districts upload finished')
