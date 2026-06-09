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
        dict_row = {'ogroup_abbrv': row[0],
                    'ogroup_description': row[1],
                    'ocategory_abbrv': row[2],
                    'ogroup_inv_type': row[3],
                    'ogroup_is_active': row[4],
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
    print('Groups Upload')

########################################################################################
if __name__ == "__main__":
    read_query = """
                SELECT 
                    g.GroupID as ogroup_abbrv,
                    g.Description as ogroup_name,
                    g.CategoryID as ocategory_abbrv,
                    g.InvType as ogroup_inv_type,
                    g.IsActive as ogroup_is_active
                FROM DowneastDW.storis.Groups g
                WHERE g.GroupID NOT IN ('<COGID>','<No Value>')
               """

    insert_query = """
                    INSERT INTO oGroups (ogroup_abbrv, 
                                    ogroup_description, 
                                    ocategory_abbrv,
                                    ogroup_inv_type,
                                    ogroup_is_active
                                    )
                
                    VALUES( %(ogroup_abbrv)s, 
                            %(ogroup_description)s,
                            %(ocategory_abbrv)s,
                            %(ogroup_inv_type)s,
                            %(ogroup_is_active)s
                            )
                    ON DUPLICATE KEY UPDATE
                        ogroup_description = VALUES(ogroup_description),
                        ocategory_abbrv = VALUES(ocategory_abbrv),
                        ogroup_inv_type = VALUES(ogroup_inv_type),
                        ogroup_is_active = VALUES(ogroup_is_active)
                    """
    print('Groups download')
    groups = read_sql(read_query)

    print('Groups Upload')
    write_sql(groups)

    print('Groups upload finished')