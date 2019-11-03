import logging
from dataclasses import dataclass


@dataclass
class BaseInfra:
    logger: logging.Logger = None

    def _log(self, message: str, level: int = logging.INFO):
        if self.logger:
            self.logger.log(level, message)
