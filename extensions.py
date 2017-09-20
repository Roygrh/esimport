################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

from raven import Client
from esimport import settings
from constants import (PROD_WEST_ENV, PROD_EAST_ENV, STAGING_ENV)

if settings.ENVIRONMENT in [PROD_WEST_ENV, PROD_EAST_ENV, STAGING_ENV]:
    sentry_client = Client(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT)
else:
    sentry_client = Client()
