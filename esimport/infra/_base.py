import logging
from dataclasses import dataclass


class BaseInfra:
    def _log(self, message: str, level: int = logging.INFO):
        if self.logger:
            self.logger.log(level, message)
