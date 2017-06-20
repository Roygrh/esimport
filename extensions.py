from raven import Client
from esimport import settings
from constants import (PROD_WEST_ENV, PROD_EAST_ENV, STAGING_ENV)

if settings.ENVIRONMENT in [PROD_WEST_ENV, PROD_EAST_ENV, STAGING_ENV]:
    sentry_client = Client(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT)
else:
    sentry_client = Client()
