import os

# Are we inside Docker?
INSIDE_DOCKER = os.getenv("INSIDE_DOCKER") in ["1", "y", "yes", "true", "t"]

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
    # Note that 'DRIVER' and 'DSN' might be optional if they're already specified system-wide using the 'odbcinst' tool
    # See: `ESImport/docker/setup_db.bash` for an example.
    MSSQL_DSN = "DRIVER={ODBC Driver 17 for SQL Server};server=%(HOST)s;DSN=%(DSN)s;UID=%(USER)s;PWD=%(PASSWORD)s;Database=%(NAME)s;trusted_connection=no"
    # If you're using FreeTDS driver, you may want to use the following connection string instead:
    # MSSQL_DSN = "Driver={FreeTDS};Server=%(HOST)s;UID=%(USER)s;PWD=%(PASSWORD)s;Database=%(NAME)s"

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
