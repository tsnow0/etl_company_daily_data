import pickle
import os
import multiprocessing
import DE_GlobalFunctions_Pkg.db as db


def merge_data(values):
    # load product list from pickle file
    infile = open(r'../product list', "rb")
    prod_ids = pickle.load(infile)

    # add product_id to Values variable (list of dictionaries from STORIS query)
    for item in values:
        # lookup = {x['oproduct_sku']: x['oproduct_id'] for x in prod_ids}
        item['oproduct_id'] = prod_ids[item['oproduct_sku']]
    return values


########################################################################################
def kit_merge_data(values):
    # load product list from pickle file
    infile = open(r'../product list', "rb")
    prod_ids = pickle.load(infile)

    # add product_id to Values variable (list of dictionaries from STORIS query)
    for item in values:
        # lookup = {x['oproduct_sku']: x['oproduct_id'] for x in prod_ids}
        item['oproduct_id'] = prod_ids[item['oproduct_sku']]
        item['okit_product_id'] = prod_ids[item['okit_sku']]
    return values


########################################################################################
##add first sale date column to products table
def add_first_sale_date(sqlstr):
    try:
        cursor = db.da_report_conn.cursor()
        cursor.execute(sqlstr)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        print(e)
    db.da_prod_conn.close()


########################################################################################
# This block of code enables us to call the script from command line.
def execute(process):
    os.system(f'python {process}')


########################################################################################
# create tuple of all processes
def dailyrun():
    # path of daily scripts
    mypath = r'C:\Users\tori.snow\Documents\Python\Downeast Dailys'
    os.chdir(mypath)

    # tuple of script files to run
    files = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
    # print(files)
    try:
        process_pool = multiprocessing.Pool(processes=3)
        process_pool.map(execute, files)
        print('All files have been executed')
    finally:
        process_pool.close()
        process_pool.join()

