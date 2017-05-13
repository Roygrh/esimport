from raven import Client
from esimport import settings
from constants import (PROD_ENV, STAGING_ENV)

if settings.ENVIRONMENT in [PROD_ENV, STAGING_ENV]:
    sentry_client = Client(settings.SENTRY_DSN)
else:
    sentry_client = Client()
