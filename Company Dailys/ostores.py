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
        dict_row = {'ostore_id':row[0],
                    'ostore_name':row[1],
                    'ostore_address1':row[2],
                    'ostore_address2':row[3],
                    'ostore_city':row[4],
                    'ostore_state':row[5],
                    'ostore_postcode':row[6],
                    'ostore_district_id':row[7],
                    'ostore_location_type':row[8],
                    'ostore_date_created':row[9]
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
    print("Stores Upload")

########################################################################################
if __name__ == "__main__":
    read_query = """
                SELECT
                    s.StoreID as ostore_id,
                    s.Name as ostore_name,
                    s.Address1 as ostore_address1,
                    s.Address2 as ostore_address2,
                    s.City as ostore_city,
                    s.State as ostore_state,
                    s.PostalCodeID as ostore_postcode,
                    s.DistrictID as ostore_district_id,
                    s.LocnType as ostore_location_type,
                    s.DateCreated as ostore_date_created
                FROM [DowneastDW].[storis].[Store] s
                WHERE s.Name != '<Unknown>'
                """

    insert_query = """
                    INSERT INTO oStores (ostore_id,
                                    ostore_name,
                                    ostore_address1,
                                    ostore_address2,
                                    ostore_city,
                                    ostore_state,
                                    ostore_postcode,
                                    ostore_district_id,
                                    ostore_location_type,
                                    ostore_date_created
                                    )
                    VALUES( %(ostore_id)s,
                            %(ostore_name)s,
                            %(ostore_address1)s,
                            %(ostore_address2)s,
                            %(ostore_city)s,
                            %(ostore_state)s,
                            %(ostore_postcode)s,
                            %(ostore_district_id)s,
                            %(ostore_location_type)s,
                            %(ostore_date_created)s
                            )
                    ON DUPLICATE KEY UPDATE
                            ostore_name = VALUES(ostore_name),
                            ostore_address1 = VALUES(ostore_address1),
                            ostore_address2 = VALUES(ostore_address2),
                            ostore_city = VALUES(ostore_city),
                            ostore_state = VALUES(ostore_state),
                            ostore_postcode = VALUES(ostore_postcode),
                            ostore_district_id = VALUES(ostore_district_id),
                            ostore_location_type = VALUES(ostore_location_type),
                            OMDT = VALUES(OMDT)
                    """
    print('Stores download')
    stores = read_sql(read_query)

    print('Stores upload')
    write_sql(stores)

    print('Stores upload finished')



