import raven
from .config import Config

SentryClient = raven.Client(Config().sentry_dsn)
