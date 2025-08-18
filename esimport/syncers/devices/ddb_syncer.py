import os
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Attr
from ._schema import DeviceSchema
#from esimport.config import Config


class DeviceDdbSyncer:
    """
    Fetch device records from DynamoDB by scanning and filtering on DateUTC.
    """
    def __init__(self, *, region: str, table_name: str, query_limit: int = 1000):

        dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = dynamodb.Table(table_name)
        self.query_limit = int(query_limit)

    def fetch_from_ddb(self, start_dt: datetime, end_dt: datetime):
        """
        Scan the DynamoDB table for items where DateUTC is between start_dt and end_dt.
        Paginates automatically using LastEvaluatedKey.
        """
        # Convert datetimes to ISO strings
        start_iso = start_dt.isoformat()
        end_iso = end_dt.isoformat()

        scan_kwargs = {
            'FilterExpression': Attr('DateTime').between(start_iso, end_iso),
            'Limit': self.query_limit
        }
        response = self.table.scan(**scan_kwargs)

        while True:
            for raw in response.get("Items", []):
                model = self._map_item(raw)                         # -> DeviceSchema
                doc = {k: v for k, v in model.dict().items() if v is not None}
                # The test expects a string; we guarantee ISO-8601:
                if isinstance(doc.get("DateUTC"), datetime):
                    doc["DateUTC"] = doc["DateUTC"].isoformat()
                yield doc
                #yield self._map_item(raw)

            # Continue scanning if there are more pages
            if 'LastEvaluatedKey' in response:
                scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
                response = self.table.scan(**scan_kwargs)
            else:
                break

    def _map_item(self, item: dict) -> DeviceSchema:
        """
        Convert a DynamoDB item to a Device model instance.
        """
        return DeviceSchema(
            DateUTC = item.get("DateTime"),             # renamed
            IP      = item.get("IpAddress"),
            MAC     = item.get("MacAddress"),
            UserAgentRaw = item.get("UserAgentRaw"),

            DeviceId   = item.get("ClientDeviceTypeId"),
            PlatformId = item.get("PlatformTypeId"),
            BrowserId  = item.get("BrowserTypeId"),

            # Optional if you can resolve names:
            # Device   = item.get("")
            # Platform = item.get("")
            # Browser  = item.get("")

            Username     = item.get("MemberName"),
            MemberID     = item.get("MemberId"),
            MemberNumber = item.get("MemberNumber"),
            ServiceArea  = item.get("OrgNumber"),
            ZoneType     = item.get("ZoneType"),

            # Event extras (pass-through)
            Origin        = item.get("Origin"),
            Scope         = item.get("Scope"),
            GpnsEnabled   = item.get("GpnsEnabled"),
            SchemaName    = item.get("SchemaName"),
            SchemaVersion = item.get("SchemaVersion"),
            Subject       = item.get("Subject"),
            ChangeType    = item.get("ChangeType"),
            AuthMethod    = item.get("AuthMethod"),
            ZonePlanName  = item.get("ZonePlanName"),
            CurrencyCode  = item.get("CurrencyCode"),
            Price         = item.get("Price"),
            TimeZoneId    = item.get("TimeZoneId"),
        )
