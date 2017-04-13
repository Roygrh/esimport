#!/bin/bash

driver=$(find /usr -name "libtdsodbc.so" | awk '{print $1}')
cat > /etc/ODBCDataSources/tds.driver.template <<- EOF
[FreeTDS]
Description = FreeTDS v1.12
Driver = $driver
EOF
odbcinst -i -d -f /etc/ODBCDataSources/tds.driver.template

cat > /etc/ODBCDataSources/dsn_esimport <<- EOF
[esimport]
Driver = FreeTDS
TDS_Version = 7.0
Description = ESImport MSSQL Database
Servername = esimport_tunnel
Port = 1433
Database = Eleven_OS
EOF
odbcinst -i -s -l -f /etc/ODBCDataSources/dsn_esimport

cat >> /etc/freetds/freetds.conf <<- EOF

[esimport_tunnel]
    host = 10.10.10.102
    port = 1433
    tds version = 7.0
    timeout = 60
    connect timeout = 60
EOF
