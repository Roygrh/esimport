# ElasticSearch Import Project

The overall task is to move data from our T-SQL database into ElasticSearch for reporting and dashboard use.

## Create config files

```bash
cat <<< '
# Environment
OS: 'linux'

# ElevenOS MsSQL Server
ELEVEN_HOST: ''
ELEVEN_DB: 'Eleven_OS'
ELEVEN_USER: ''
ELEVEN_PASSWORD: ''

# ElasticSearch
ES_HOST: ''
ES_PORT: '80'
ES_INDEX: ''
ES_TIMEOUT: 30
ES_RETRIES: 5
ES_BULK_LIMIT: 500
' > config.yml
```

```bash
cat <<< '
[sqlserverdatasource]
Driver = FreeTDS
Description = ODBC connection via FreeTDS
Trace = No
Servername = elevenos
Database = Eleven_OS
Port = 1433
' > odbc.ini
```

## Run tests with coverage

```bash
$ pytest --cov=esimport --cov-report=html
```
