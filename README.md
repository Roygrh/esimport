# ElasticSearch Import Project

The overall task is to move data from our T-SQL database into ElasticSearch for reporting and dashboard use.

## Create settings file

```bash
cat <<< '
# ElevenOS MSSQL Server (either DSN or HOST depending on OS)
DATABASES = {
    'default': {
        'DSN': '', # either DSN or HOST
        'HOST': '',
        'PORT': None,
        'NAME': 'Eleven_OS',
        'USER': '',
        'PASSWORD': '',
    }
}

# ElasticSearch
ES_HOST = ''
ES_PORT = '9200'
ES_INDEX = ''
ES_TIMEOUT = 30
ES_RETRIES = 5
ES_BULK_LIMIT = 500
' > local_settings.py
```

## HOW TO USE?

```bash
$ pip install ssh://git@bitbucket.org/distrodev/esimport.git
$ export PYTHONPATH=/path/to/local_settings.py
$ esimport sync
```

```bash
$ esimport sync --start-date 2014-01-01
```

#### Update existing records in ElasticSearch

```bash
$ esimport update account
```

## HOW TO RUN TESTS?

Start an ElasticSearch server and then run following commands.

```bash
$ export PYTHONPATH=/path/to/local_settings.py
$ tox
```
