from datetime import datetime, timezone
from dataclasses import dataclass
import uuid

# This how the record to be sent to the SNS topic looks like:
@dataclass
class Record:

    _index: str  # the name of the target Elasticsearch index
    _type: str  # the record type for Elasticsearch
    _source: dict  # the actual record content itself, as json (dict)
    _date: datetime
    _op_type: str = "index"
    _version_type: str = "external"

    @property
    def id(self) -> int:
        # The ID of the document for Elasticsearch (same as its MSSQL ID)
        # for DPSK (PPK) records, they have a non-integer ID, stored in RECORD_ID field instead.
        # for RADIUS_EVENT_HISTORY records, the ID is stored in RADIUS_EVENT_ID field.
        # for RADUIS_EVENT records, the ID is stored in ID field.
        if self._source.get("ID", None):
            return int(self._source["ID"])
        if self._source.get("Radius_Event_ID")
            return int(self._source["Radius_Event_ID"])
        return self._source.get("RECORD_ID")

    @property
    def version(self) -> int:
        # The document version

        # We need microsecond precision because documents can be changed many times during one second period
        # and for each change we need a new version number
        # document _date(LogoutTime) is DATETIME, so only has 3.33ms precision. microsecond will be 0 for most of the cases. 
        # using the date timestamp will not give us the microsecond precision we need. So we need to use the current 
        # timestamp instead. It has higher precision, and is  guaranteed to increase for each new record, as long as 
        # the records are not created in the same microsecond.
        #return int(self._date.timestamp() * 1000000)
        return int(datetime.now(timezone.utc).timestamp() * 1000000)

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
            "_type": self._type,
            "_version": self.version,
            "_version_type": self._version_type,
            "_source": self._source,
        }
