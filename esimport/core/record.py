from datetime import datetime, timezone
from dataclasses import dataclass


# This how the record to be sent to the SNS topic looks like:
@dataclass
class Record:

    _op_type: str = "index"
    _index: str  # the name of the target Elasticsearch index
    _type: str  # the record type for Elasticsearch
    _version_type: str = "external"
    _source: dict  # the actual record content itself, as json (dict)
    _date: datetime

    @property
    def id(self) -> int:
        # The ID of the document for Elasticsearch (same as its MSSQL ID)
        return self._source["ID"]

    @property
    def version(self) -> int:
        # The document version
        # if `self._date` does not have timezone information then `timestamp()` method will treat datetime
        # object as if it's in local timezone. If OS timezone will not be set to UTC it may lead to unexpected
        # results. It is an edge case, but explicitly configuring timezone will give stable results.
        # If timezone info does not get parsed then we assume date is in UTC.
        if self._date.tzinfo is None:
            self._date.replace(tzinfo=timezone.utc)

        # We need microsecond precision because documents can be changed many times during one second period
        # and for each change we need a new version number
        return int(self._date.timestamp() * 1000000)

    @property
    def raw(self):
        """
        The raw record to be stored in Elasticsearch, without the metadata.
        """
        return self._source

    def as_dict(self):
        """
        Only the fields needed later by Elasticsearch bulk index are included
        As we need to optimize the messages size when they're sent over SNS.
        """
        return {
            "_op_type": self._op_type,
            "_index": self._index,
            "_id": self.id,
            "_version": self.version,
            "_version_type": self._version_type,
            "_source": self._source,
        }
