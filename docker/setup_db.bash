#!/bin/bash

ip_address=$(/sbin/ip route|awk '/default/ { print $3 }')
cat > odbc.driver.template <<- EOF
[Eleven_OS]
Driver      = ODBC Driver 17 for SQL Server
Description = My MS SQL Server
Trace       = No
Server      = $ip_address
DATABASE    = Eleven_OS
EOF
odbcinst -i -s -f odbc.driver.template -l