#!/bin/sh
MSSQL_SERVER_CONTAINER_NAME=$(docker ps | grep "mssql.*esimport"| awk '{print $1}')

if  [ -z "$MSSQL_SERVER_CONTAINER_NAME" ]
then
    echo "MSSQL Server docker container not running, please run it first using the docker-compose.yml file" >&2
    exit 1
fi

SQLCMD_EXEC="/opt/mssql-tools/bin/sqlcmd"

DB_USER="sa"
DB_PASSWORD="DistroDev@11"


sqlcmd="docker exec $MSSQL_SERVER_CONTAINER_NAME $SQLCMD_EXEC -U $DB_USER -P $DB_PASSWORD"

# Make sure required DBs are created
echo "Creating databases"
$sqlcmd -Q "CREATE DATABASE Eleven_OS" #&> /dev/null || true
$sqlcmd -Q "CREATE DATABASE Radius" #&> /dev/null || true

sleep 2
echo "Creating tables"
# loop over the result of 'ls -1 *.sql'
#     'ls -1' sorts the file names based on the current locale 
#     and presents them in a single column
for i in `ls -1 esimport/tests/fixtures/sql/*.sql`; do 
    $sqlcmd -d Eleven_OS -i "${i/esimport\/tests\/fixtures/\/esimport}"
done
