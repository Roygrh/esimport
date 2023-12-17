from .config import Config

sentry_sdk.init(dsn=Config().sentry_dsn)
