#!/bin/sh

for i in `/bin/ls -1 esimport/tests/fixtures/sql/*.sql`; do
   sqlcmd -S localhost -U sa -P DistroDev@11 -d Eleven_OS -i $i
done