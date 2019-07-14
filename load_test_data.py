import glob
import os

from esimport import settings
from esimport.mappings.account import AccountMapping

test_dir = os.getcwd()
host = settings.DATABASES["default"]["HOST"]
uid = settings.DATABASES["default"]["USER"]
pwd = settings.DATABASES["default"]["PASSWORD"]
db = settings.DATABASES["default"]["NAME"]

am = AccountMapping()
am.setup()

# for sql in os.listdir(test_dir+'/esimport/tests/fixtures/sql/'):
#     if '.sql' in sql:
#         script = test_dir + "/esimport/tests/fixtures/sql/"+sql
#         subprocess.check_call(["sqlcmd", "-S", host, "-i", script, "-U", uid, "-P", pwd, "-d", db],
#                                 stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

for sql in glob.glob(test_dir + "/esimport/tests/fixtures/sql/*.sql"):
    with open(sql, "r") as inp:
        sqlQuery = ""
        for line in inp:
            if "GO" not in line:
                sqlQuery = sqlQuery + line
        r = am.model.execute(sqlQuery).commit()
        am.model.conn.reset()
    inp.close()

print("Done!")
