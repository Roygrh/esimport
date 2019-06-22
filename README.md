# ElasticSearch Import Project

The overall task is to move data from our T-SQL database into ElasticSearch.

## Create settings file

```bash
cat <<EOF > local_settings.py
import os

# Are we inside Docker?
INSIDE_DOCKER = os.getenv("INSIDE_DOCKER") in ["1", "y", "yes", "true"]

# General
ENVIRONMENT = "dev"

DATABASES = {
    "default": {
        "DSN": "Eleven_OS" if not INSIDE_DOCKER else "Eleven_OS",  # either DSN or HOST
        "HOST": "localhost" if not INSIDE_DOCKER else "mssql",
        "PORT": "1433",
        "NAME": "Eleven_OS",
        "USER": "sa",
        "PASSWORD": "DistroDev@11",  # you probably have something else as a password
    }
}

if INSIDE_DOCKER:
    # No need to specify a driver
    MSSQL_DSN = "DSN=%(DSN)s;UID=%(USER)s;PWD=%(PASSWORD)s;Database=%(NAME)s;trusted_connection=no"
else:
    # MSSQL_DSN = "Driver={FreeTDS};Server=%(HOST)s;UID=%(USER)s;PWD=%(PASSWORD)s;Database=%(NAME)s"
    MSSQL_DSN = "DSN=%(DSN)s;UID=%(USER)s;PWD=%(PASSWORD)s;Database=%(NAME)s;trusted_connection=no"

# MSSQL_DSN = "DSN=%(DSN)s;UID=%(USER)s;PWD=%(PASSWORD)s;trusted_connection=no"
ES_HOST = "localhost" if not INSIDE_DOCKER else "elasticsearch"
ES_INDEX = "elevenos"
ES_TIMEOUT = 1
ES_RETRIES = 1
ES_RETRIES_WAIT = 1
ES_BULK_LIMIT = 10

REDIS_HOST = "localhost" if not INSIDE_DOCKER else "redis"

# Wait between database queries execution (seconds)
DATABASE_CALLS_WAIT = 1

# Reset database connection (seconds) giving esimport a chance to
# pickup any DNS changes that have propagated since the last connection
DATABASE_CONNECTION_RESET_LIMIT = 300

DATABASE_CALLS_RETRIES = 1
DATABASE_CALLS_RETRIES_WAIT = 1
DATABASE_CALLS_RETRIES_WAIT_INCREMENTAL = False
ES_CALLS_RETRIES = 1
ES_CALLS_RETRIES_WAIT = 1
ES_CALLS_RETRIES_WAIT_INCREMENTAL = False
EOF
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

```bash
$ esimport update conference --start-date 2018-05-01
```

## HOW TO RUN TESTS?

Start an ElasticSearch server and then run following commands.

```bash
$ export PYTHONPATH=/path/to/local_settings.py
$ tox
```

```bash
$ export PYTHONPATH=/path/to/local_settings.py
$ pytest esimport/tests/test_conferencemapping_es.py
```

## Using docker-compose

Docker-compose can be used to spin up SQLServer, Redis and ElasticSearch.
You can start these services with `make start-environment` or `docker-compose up redis mssql elasticsearch`.

Once these services are up, you can access them like so:
- ElasticSearch: `localhost:9200`
- MSSQL Server: `localhost:1433`, user: `sa`, password: `DistroDev@11` (You have to create the databases: Eleven_OS, Radius)
- Redis: `localhost:6379`

If you want to run ESImport from inside a docker container as well, issue `make shell` inside the project root directory.
It will set up the whole dev-stack from docker-compose.yml and leave you in a shell from where you can run the unit tests
and esimport update/sync (see section above).

If you set up the stack with `make start-environment` or `docker-compose up redis mssql elasticsearch` you can still add the
esimport or kibana container afterwards with `docker-compose run --rm --service-ports <service-name>`.
