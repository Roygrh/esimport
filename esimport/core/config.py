import os
from typing import Union

from pydantic import BaseModel, BaseSettings, Field, Schema


class Config(BaseSettings):
    """
    This how the config object should look like.
    This is using Pydantic's `BaseSettings`. 

    INSTANTIATING THIS CLASS WILL AUTO FILL ITS FIELDS FROM YOUR ENVIRONMENT VARIABLES.
    
    For more info, see: https://pydantic-docs.helpmanual.io/usage/settings/
    """

    # The MSSQL DB credentials, host, port ..etc as a dictionnary.

    mssql_host: str
    mssql_port: int = 1433
    mssql_password: str = ""
    mssql_user: str = ""
    mssql_db_mame: str = "Eleven_OS"

    # How the connection string should look like?
    # This differ depending the driver being used, and the operating system.
    # this default DSN presented here is for *nix operating systems, with the official driver we're using
    # for prod as well. You'd better seek to use this combination.
    # If you're under Windows, this would like something like:
    # mssql_dsn = "Driver={SQL Server};Server=.;Trusted_Connection=yes;"
    mssql_dsn: str = "DSN=%(DSN)s;UID=%(USER)s;PWD=%(PASSWORD)s;trusted_connection=no;MARS_Connection=yes"
    # DSN config name if a dsn file is configured
    dsn: str = "localhost"

    # Redis (for caching)
    redis_host: str = "localhost"
    redis_port: int = 6379

    # The hard limit of the number of records to return from sql queries where TOP X is used in SQL queries.
    database_max_records_limit: int = 10_000

    # Database timeouts (seconds)
    # How many seconds before we consider the connection to the DB as timing out.
    database_connection_timeout: int = 60

    # How many seconds before we consider a query to the DB as timing out.
    database_query_timeout: int = 60

    # Wait between database queries execution (seconds)
    database_calls_wait_in_seconds: int = 1

    # TODO: Since we now connect to SQL via the SQL Listener High Availability Group,
    # we no longer need to account for any DNS propagation changes.  We should remove this.
    # Reset database connection (seconds) giving esimport a chance to
    # pickup any DNS changes that have propagated since the last connection
    database_connection_reset_limit: int = 300

    # AWS
    # This endpoint can be set in case we're mocking AWS service. e.g. via localstack: https://github.com/localstack/localstack
    aws_endpoint_url: Union[str, None] = None

    aws_access_key_id: str = "foo"
    aws_secret_access_key: str = "bar"
    aws_default_region: Union[str, None] = None

    # SNS
    # Custom SNS Port, in case we're using a mock SNS service (e.g. with LocalStack)
    sns_port: Union[int, None] = None
    sns_topic_arn: str  # required
    max_sns_bulk_send_size_in_bytes: int = 255_000

    sns_calls_wait_in_seconds: int = 1

    # Dynamodb
    # Custom DynamoDB Port, in case we're using a mock DynamoDB service (e.g. with LocalStack)
    dynamodb_port: Union[int, None] = None
    dynamodb_table: str = "esimport_cursor"

    # S3
    # Custom S3 Port, in case we're using a mock S3 service (e.g. with LocalStack)
    s3_port: Union[int, None] = None

    # SQS
    sqs_port: Union[int, None] = None
    sqs_queue_url: str = None

    # Sentry/Error Reporting
    sentry_dsn: str = ""

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    pkg_dir: str = os.path.dirname(os.path.abspath(__file__))
    root_dir: str = os.path.abspath(os.path.join(pkg_dir, ".."))

    test_fixtures_dir: str = os.path.join(root_dir, "tests/fixtures")

    # Are we inside a docker container?
    inside_docker: bool = False

    @property
    def database_info(self):
        return {
            "DSN": "Eleven_OS" if self.inside_docker else self.dsn,
            "HOST": self.mssql_host,
            "PORT": self.mssql_port,
            "NAME": self.mssql_db_mame,
            "USER": self.mssql_user,
            "PASSWORD": self.mssql_password,
        }

    class Config:
        case_sensitive = False
