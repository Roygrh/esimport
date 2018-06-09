import os
import subprocess
from esimport import settings

test_dir = os.getcwd()
host = settings.DATABASES['default']['HOST']
uid = settings.DATABASES['default']['USER']
pwd = settings.DATABASES['default']['PASSWORD']
db = settings.DATABASES['default']['NAME']

for sql in os.listdir(test_dir+'/esimport/tests/fixtures/sql/'):
    script = test_dir + "/esimport/tests/fixtures/sql/"+sql
    subprocess.check_call(["sqlcmd", "-S", host, "-i", script, "-U", uid, "-P", pwd, "-d", db], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    # with open(script, 'r') as inp:
    #     sqlQuery = ''
    #     for line in inp:
    #         if 'GO' not in line:
    #             sqlQuery = sqlQuery + line
    #     self.am.model.execute(sqlQuery).commit()
    # inp.close()
print("Done!")