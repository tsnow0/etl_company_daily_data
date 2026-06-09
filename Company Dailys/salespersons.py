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
        dict_row = {'ostaff_id': row[0],
                    'osalesperson_id': row[1],
                    'oemployee_nbr': row[2],
                    'ostaff_name': row[3],
                    'ostaff_store_id': row[4]
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
                 SELECT StaffID,
                 SalesPersonID, 
                 EmployeeNbr,
                 Name,
                 Default_StoreID
                 FROM DowneastDW.storis.Staff;
                """

    insert_query = """
                    INSERT INTO oStaff (ostaff_id,
                                    osalesperson_id,
                                    oemployee_nbr,
                                    ostaff_name,
                                    ostaff_store_id
                                    )
                
                    VALUES( %(ostaff_id)s,
                            %(osalesperson_id)s,
                            %(oemployee_nbr)s,
                            %(ostaff_name)s,
                            %(ostaff_store_id)s
                            )
                    ON DUPLICATE KEY UPDATE
                        oemployee_nbr = VALUES(oemployee_nbr),
                        ostaff_name = VALUES(ostaff_name),
                        ostaff_store_id = VALUES(ostaff_store_id)
                    """
    print('SalesPersons download')
    salespersons = read_sql(read_query)

    print('SalesPersons upload')
    write_sql(salespersons)

    print('SalesPersons upload finished')