import pickle
import sys

import DW_GlobalFunctions_Pkg.db as db
from pathlib import Path
import subprocess


def get_ProductID():
    # read function for pulling product data from downeast_analytics and updating the data from STORIS with the correct Product ID
    prod_ids = []
    try:
        # pulling data from downeast_analytics
        cursor = db.da_report_conn.cursor()
        cursor.execute(productID_query)
        print('ProductID query download successful')

        row = cursor.fetchone()

        # put query into a new list of dictionaries
        while row is not None:
            prod_ids.append(dict(row))
            row = cursor.fetchone()
    except Exception as e:
        print(e + ' - ProductID upload failed')
    db.da_report_conn.close()

    # convert list of dictionaries to dictionary (key = SKU and value = product_id) so we can look up id in the other scripts
    prod_ids = {x['oproduct_sku']: x['oproduct_id'] for x in prod_ids}

    return prod_ids


########################################################################################
if __name__ == "__main__":
    cur_dir = Path(__file__).parent
    # first, run oproducts script to update downeast_analytics.oProducts table
    # exec(open(str(cur_dir / 'oproducts.py')).read())

    # pull data from downeast_analytics.oProducts
    # query string
    productID_query = """
                        SELECT DISTINCT p.oproduct_sku,
                               p.oproduct_id
                        FROM downeast_analytics.oProducts p
                        """

    # load query results into variable
    products = get_ProductID()

    # open pickle file
    outfile = open(r'C:/Users/tori.snow/Documents/Python/product list', "wb")

    # dump query results into file
    pickle.dump(products, outfile)

    # close file
    outfile.close()

    print('Pickle file updated')
