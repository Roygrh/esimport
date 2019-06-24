import os
import glob
import subprocess
import pyodbc
from esimport import settings
from datetime import datetime, timedelta
from esimport.mappings.account import AccountMapping

test_dir = os.getcwd()
# host = settings.DATABASES['default']['HOST']
am = AccountMapping()
am.setup()

account_sql = """INSERT INTO [dbo].[Zone_Plan_Account]
        (Member_ID, Zone_Plan_ID, Purchase_Price, 
        Purchase_Price_Currency_ID, Network_Access_Limits_ID, 
        Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, 
        Date_Created_UTC,Date_Modified_UTC, PMS_Charge_ID, 
        Zone_Plan_Account_Status_ID, Upsell_Zone_Plan_Account_ID, Purchase_Org_ID)
        VALUES 
        (1, 1, 12.95, 1, 1, 1, '34-C0-59-D8-31-08', '2014-01-04 07:38:24.370', 
        '{}', '2018-04-05 10:31:46.768',
        1, 1, NULL, 1)"""

dt_now = datetime.now()
for _ in range(10):
    dt_str = dt_now.strftime('%Y-%m-%d %H:%M:%S')
    am.model.execute(account_sql.format(dt_str)).commit()
    dt_now = dt_now - timedelta(days=31)

# for sql in os.listdir(test_dir+'/esimport/tests/fixtures/sql/'):
#     if '.sql' in sql:
#         script = test_dir + "/esimport/tests/fixtures/sql/"+sql
#         subprocess.check_call(["sqlcmd", "-S", host, "-i", script, "-U", uid, "-P", pwd, "-d", db],
#                                 stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

# for sql in glob.glob(test_dir + '/esimport/tests/fixtures/sql/*.sql'):
#     with open(sql, 'r') as inp:
#         sqlQuery = ''
#         for line in inp:
#             if 'GO' not in line:
#                 sqlQuery = sqlQuery + line
#         r = am.model.execute(sqlQuery).commit()
#         am.model.conn.reset()
#     inp.close()

print("Done!")
