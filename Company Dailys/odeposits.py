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
        dict_row = {'oorder_id': row[0],
                    'odeposits_id': row[1],
                    'odeposits_is_history': row[2],
                    'ocustomer_id': row[3],
                    'odeposits_date_created': row[4],
                    'odeposits_date': row[5],
                    'odeposits_payment_NSF_reference': row[6],
                    'odeposits_is_financed': row[7],
                    'odeposits_payment_type_id': row[8],
                    'odeposits_payment_nbr': row[9],
                    'odeposits_payment_amt': row[10],
                    'odeposits_auth_nbr': row[11],
                    'odeposits_payment_exp_date': row[12],
                    'odeposits_work_status': row[13],
                    'odeposits_sequence': row[14],
                    'odeposits_reference_nbr': row[15],
                    'odeposits_rec_status': row[16]
                    }
        values.append(dict_row)
        row = rcursor.fetchone()
    rcursor.close()
    db.storis_read_conn.close()
    return values

########################################################################################
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))
########################################################################################
def write_sql(values):
    numchunk = 0

    cursor = db.da_prod_conn.cursor()
    cursor.execute("TRUNCATE TABLE oDeposits")
    print('Deposits emptied')
    cursor.close()

    for chunk in chunker(values, 50000):
        try:
            cursor = db.da_prod_conn.cursor()
            cursor.executemany(insert_query, chunk)
            db.da_prod_conn.commit()
            cursor.close()
            numchunk = numchunk + 1
            print("Chunk #" + str(numchunk) + " - Deposits Upload")
        except Exception as e:
            print(e)
            print("Chunk #" + str(numchunk) + " - Deposits Upload Failed")

    db.da_prod_conn.close()

########################################################################################
if __name__ == "__main__":
    read_query = """
                 SELECT
                    OrderID,
                    DepositsID,
                    IsHistory,
                    CustomerID,
                    DateCreated,
                    DepositDate,
                    PaymentNSFReference,
                    IsFinanced,
                    PaymentTypeID,
                    PaymentNbr,
                    PaymentAmt,
                    PaymentAuthNbr,
                    PaymentExpDate,
                    WorkStatus,
                    Sequence,
                    ReferenceNbr,
                    RecStatus
                  FROM [DowneastDW].[storis].[Deposits];
               """

    insert_query = """
                    INSERT INTO oDeposits (oorder_id,
                                    odeposits_id,
                                    odeposits_is_history,
                                    ocustomer_id,
                                    odeposits_date_created,
                                    odeposits_date,
                                    odeposits_payment_NSF_reference,
                                    odeposits_is_financed,
                                    odeposits_payment_type_id,
                                    odeposits_payment_nbr,
                                    odeposits_payment_amt,
                                    odeposits_auth_nbr,
                                    odeposits_payment_exp_date,
                                    odeposits_work_status,
                                    odeposits_sequence,
                                    odeposits_reference_nbr,
                                    odeposits_rec_status
                                    )
                
                    VALUES( %(oorder_id)s,
                            %(odeposits_id)s,
                            %(odeposits_is_history)s,
                            %(ocustomer_id)s,
                            %(odeposits_date_created)s,
                            %(odeposits_date)s,
                            %(odeposits_payment_NSF_reference)s,
                            %(odeposits_is_financed)s,
                            %(odeposits_payment_type_id)s,
                            %(odeposits_payment_nbr)s,
                            %(odeposits_payment_amt)s,
                            %(odeposits_auth_nbr)s,
                            %(odeposits_payment_exp_date)s,
                            %(odeposits_work_status)s,
                            %(odeposits_sequence)s,
                            %(odeposits_reference_nbr)s,
                            %(odeposits_rec_status)s
                            )
                
                    """

    print('Deposits download')
    deposits = read_sql(read_query)

    print('Deposits Upload')
    write_sql(deposits)

    print('Deposits upload finished')
