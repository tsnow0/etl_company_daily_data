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
        dict_row = {'ocustomer_id': row[0],
                    'ocustomer_type': row[1],
                    'ocustomer_fname': row[2],
                    'ocustomer_lname': row[3],
                    'ocustomer_full_name': row[4],
                    'ocustomer_address1': row[5],
                    'ocustomer_address2': row[6],
                    'ocustomer_city': row[7],
                    'ocustomer_state': row[8],
                    'ocustomer_postcode': row[9],
                    'ocustomer_email_address': row[10],
                    'ocustomer_due_day': row[11],
                    'ocustomer_is_business': row[12],
                    'ocustomer_on_account_cash': row[13],
                    'ocustomer_on_account_deposits': row[14],
                    'ocustomer_open_balance': row[15],
                    'ocustomer_rec_status': row[16],
                    'ocustomer_open_date': row[17],
                    'ocustomer_trade_type': row[18]
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
                SELECT c.CustomerID,
                       c.CustomerType,
                       c.FirstName,
                       c.LastName,
                       c.FullName,
                       c.Address1,
                       c.Address2,
                       c.City,
                       c.State,
                       c.PostalCodeID,
                       c.EmailAddress,
                       c.DueDay,
                       c.IsBusiness,
                       c.OnAcctCash,
                       c.OnAcctDeposits,
                       c.OpenTotBal,
                       c.RecStatus,
                       c.OpenDt,
                       c.TradeTypeID
                FROM DowneastDW.storis.Customer c
                """

    insert_query = """
                    INSERT INTO oCustomers (ocustomer_id,
                                    ocustomer_type,
                                    ocustomer_fname,
                                    ocustomer_lname,
                                    ocustomer_full_name,
                                    ocustomer_address1,
                                    ocustomer_address2,
                                    ocustomer_city,
                                    ocustomer_state,
                                    ocustomer_postcode,
                                    ocustomer_email_address,
                                    ocustomer_due_day,
                                    ocustomer_is_business,
                                    ocustomer_on_account_cash,
                                    ocustomer_on_account_deposits,
                                    ocustomer_open_balance,
                                    ocustomer_rec_status,
                                    ocustomer_open_date,
                                    ocustomer_trade_type
                                    )

                    VALUES( %(ocustomer_id)s, 
                            %(ocustomer_type)s,
                            %(ocustomer_fname)s,
                            %(ocustomer_lname)s,
                            %(ocustomer_full_name)s,
                            %(ocustomer_address1)s, 
                            %(ocustomer_address2)s, 
                            %(ocustomer_city)s,
                            %(ocustomer_state)s,
                            %(ocustomer_postcode)s,
                            %(ocustomer_email_address)s,
                            %(ocustomer_due_day)s,
                            %(ocustomer_is_business)s,
                            %(ocustomer_on_account_cash)s,
                            %(ocustomer_on_account_deposits)s,
                            %(ocustomer_open_balance)s,
                            %(ocustomer_rec_status)s,
                            %(ocustomer_open_date)s,
                            %(ocustomer_trade_type)s
                            )
                    ON DUPLICATE KEY UPDATE
                            ocustomer_type = VALUES(ocustomer_type),
                            ocustomer_fname = VALUES(ocustomer_fname),
                            ocustomer_lname = VALUES(ocustomer_lname),
                            ocustomer_full_name = VALUES(ocustomer_full_name),
                            ocustomer_address1 = VALUES(ocustomer_address1),
                            ocustomer_address2 = VALUES(ocustomer_address2),
                            ocustomer_city = VALUES(ocustomer_city),
                            ocustomer_state = VALUES(ocustomer_state),
                            ocustomer_postcode = VALUES(ocustomer_postcode),
                            ocustomer_email_address = VALUES(ocustomer_email_address),
                            ocustomer_due_day = VALUES(ocustomer_due_day),
                            ocustomer_is_business = VALUES(ocustomer_is_business),
                            ocustomer_on_account_cash = VALUES(ocustomer_on_account_cash),
                            ocustomer_on_account_deposits = VALUES(ocustomer_on_account_deposits),
                            ocustomer_open_balance = VALUES(ocustomer_open_balance),
                            ocustomer_rec_status = VALUES(ocustomer_rec_status),
                            ocustomer_open_date = VALUES(ocustomer_open_date),
                            ocustomer_trade_type = VALUES(ocustomer_trade_type)
                   """

    print('Customer download started')
    customers = read_sql(read_query)

    print('Customer Upload started')
    write_sql(customers)

    print('Customer upload finished')
