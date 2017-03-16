# ElasticSearch Import Project

The overall task is to move data from our T-SQL database into ElasticSearch for reporting and dashboard use.

## Create config files

```bash
cat <<< '
# Environment
OS: 'linux'

# ElevenOS MSSQL Server (either DSN or HOST depending on OS)
ELEVEN_DSN: ''
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

## HOW TO USE?

```bash
$ pip install ssh://git@bitbucket.org/distrodev/esimport.git
$ export ESIMPORT_CONFIG=/path/to/config.yml
$ esimport sync
```

#### Update existing records in ElasticSearch

```bash
$ esimport update account
```

## HOW TO RUN TESTS?

```bash
$ export ES_HOME=/path/to/elasticsearch-5.1.1/
$ tox
```
