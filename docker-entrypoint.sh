#!/bin/bash

if [ ! -z "$DEV" ]; then
    # dev
    pip install -r dev-requirements.txt
fi

cat >odbc.driver.template <<-EOF
[Eleven_OS]
Driver      = ODBC Driver 17 for SQL Server
Description = ODBC connection
Trace       = No
Server      = $MSSQL_HOST
EOF
odbcinst -i -s -f odbc.driver.template -l
echo $@
$@
