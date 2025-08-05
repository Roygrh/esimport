import os
import boto3
from boto3.dynamodb.conditions import Attr
from esimport.config import DYNAMODB_TABLE_NAME, AWS_REGION
from ._schema import Device


class DeviceDdbSyncer:
    """
    Fetch device records from DynamoDB by scanning and filtering on DateUTC.
    """
    def __init__(self):
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
        self.table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    def fetch(self, start_dt: str, end_dt: str, limit: int = 1000):
        """
        Scan the DynamoDB table for items where DateUTC is between start_dt and end_dt.
        Paginates automatically using LastEvaluatedKey.
        """
        scan_kwargs = {
            "FilterExpression": Attr("DateUTC").between(start_dt, end_dt),
            "Limit": limit
        }
        response = self.table.scan(**scan_kwargs)

        for item in response.get("Items", []):
            yield self._map_item(item)

        # Continue scanning if there are more items
        while "LastEvaluatedKey" in response:
            scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
            response = self.table.scan(**scan_kwargs)
            for item in response.get("Items", []):
                yield self._map_item(item)

    def _map_item(self, item: dict) -> Device:
        """
        Convert a DynamoDB item to a Device model instance.
        """
        return Device(
            id=None,                    # Let Elasticsearch generate its own ID
            Date=item.get("DateUTC"),
            IP=item.get("IP"),
            MAC=item.get("MAC"),
            UserAgentRaw=item.get("UserAgentRaw"),
            Device=item.get("Device"),
            Platform=item.get("Platform"),
            Browser=item.get("Browser"),
            Username=item.get("Username"),
            MemberID=item.get("MemberID"),
            MemberNumber=item.get("MemberNumber"),
            ServiceArea=item.get("ServiceArea"),
            ZoneType=item.get("ZoneType")
        )
