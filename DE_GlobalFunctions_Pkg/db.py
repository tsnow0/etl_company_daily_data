import DE_GlobalFunctions_Pkg.creds as c
import pymysql as py
import pyodbc


hq_report_conn = py.connect(host=c.m_report, user=c.m_user, password=c.m_password, db=c.db_hq, charset='utf8mb4', cursorclass=py.cursors.DictCursor)
hq_prod_conn = py.connect(host=c.m_prod, user=c.m_user, password=c.m_password, db=c.db_hq,  charset='utf8mb4', cursorclass=py.cursors.DictCursor)


da_report_conn = py.connect(host=c.m_report, user=c.m_user, password=c.m_password, db=c.db_da, charset='utf8mb4', cursorclass=py.cursors.DictCursor)
da_prod_conn = py.connect(host=c.m_prod, user=c.m_user, password=c.m_password, db=c.db_da,  charset='utf8mb4', cursorclass=py.cursors.DictCursor)


storis_read_conn = pyodbc.connect("Driver={SQL Server}; Server=" + c.de_server + ";Database=" + c.de_db + ";uid=" + c.de_user + ";pwd=" + c.de_password + ";")