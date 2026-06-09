import DE_GlobalFunctions_Pkg.db as db
from DE_GlobalFunctions_Pkg.DE_Functions import merge_data

def read_sql(query):
    rcursor = db.storis_read_conn.cursor()
    rcursor.execute(query)

    row = rcursor.fetchone()
    values = []
    while row is not None:
        dict_row = {'oinventory_status_id': row[0],
                    'ostatus_description': row[1],
                    }
        values.append(dict_row)
        row = rcursor.fetchone()
    rcursor.close()
    db.storis_read_conn.close()
    return  values

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
                SELECT PieceStatusID,
                       Description
                    FROM [DowneastDW].[storis].[PieceStatus]
                """

    insert_query = """
                    INSERT INTO oInventoryStatus (oinventory_status_id, 
                                ostatus_description
                                )

                    VALUES( %(oinventory_status_id)s, 
                            %(ostatus_description)s
                          )
                    ON DUPLICATE KEY UPDATE
                        ostatus_description = VALUES (ostatus_description)
                    """

    print('Inventory Statuses download')
    status = read_sql(read_query)

    print('Inventory Statuses Upload')
    write_sql(status)

    print('Inventory Statuses upload finished')
