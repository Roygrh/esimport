################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import logging

from datetime import datetime, timedelta, timezone
from dateutil import tz

from esimport.models import ESRecord
from esimport.models.base import BaseModel
from esimport.utils import convert_pacific_to_utc, convert_utc_to_local_time, \
    set_pacific_timezone, set_utc_timezone

logger = logging.getLogger(__name__)


class Device(BaseModel):
    _type = "device"
    _date_field = "DateUTC"
    _index_name_date_field = "DateUTC"
    _index = "devices"

    # These dates are in 'America/Los_Angeles' format
    dates_from_pacific = {"Date": "DateUTC"}

    @staticmethod
    def get_type():
        return Device._type

    @staticmethod
    def get_key_date_field():
        return Device._date_field

    @staticmethod
    def get_index():
        return Device._index

    def get_devices(self, start, limit, start_date='1900-01-01'):
        q = self.query_one()

        for row in list(self.fetch_dict(q, limit, start, start_date)):
            for key, value in row.items():
                if isinstance(value, datetime):
                    if key in self.dates_from_pacific:
                        row[self.dates_from_pacific[key]] = convert_pacific_to_utc(set_pacific_timezone(row[key]))
                        del row[key]  # As there's no `Date` field in ElevenAPI's Device model
                    else:
                        row[key] = set_utc_timezone(row[key])

            org_number_tree = []
            
            # FIXME: this is very slow, causing the devices records to stay way behind on PROD
            # find a better way to attach the org_number tree for devices. this must NOT be done for EACH device!
            # org_number_tree_query = self.query_get_org_number_tree()
            # for org in list(self.fetch(org_number_tree_query, row['ID'])):
            #     org_number_tree.append(org[0])
            row['AncestorOrgNumberTree'] = org_number_tree

            yield ESRecord(row, self.get_type(), self.get_index(), index_date=row[self._index_name_date_field])

    @staticmethod
    def query_one():
        return """SELECT TOP (?)
Client_Tracking.ID AS ID,
Client_Tracking.Date AS Date,
Client_Tracking.IP_Address AS IP,
Client_Tracking.MAC_Address AS MAC,
Client_Tracking.User_Agent_Raw AS UserAgentRaw,
Client_Device_Type.Name AS Device,
Platform_Type.Name AS Platform,
Browser_Type.Name AS Browser,
Member.Display_Name AS Username,
Member.ID as MemberID,
Member.Number as MemberNumber,
Organization.Number AS ServiceArea,
Org_Value.Value AS ZoneType
FROM Client_Tracking WITH (NOLOCK)
LEFT JOIN Client_Device_Type WITH (NOLOCK) ON Client_Device_Type.ID = Client_Tracking.Client_Device_Type_ID
LEFT JOIN Platform_Type WITH (NOLOCK) ON Platform_Type.ID = Client_Tracking.Platform_Type_ID
LEFT JOIN Browser_Type WITH (NOLOCK) ON Browser_Type.ID = Client_Tracking.Browser_Type_ID
LEFT JOIN Member WITH (NOLOCK) ON Member.ID = Client_Tracking.Member_ID
LEFT JOIN Organization WITH (NOLOCK) ON Organization.ID = Client_Tracking.Organization_ID
LEFT JOIN Org_Value WITH (NOLOCK) ON Org_Value.Organization_ID = Organization.ID AND Org_Value.Name='ZoneType'
WHERE Client_Tracking.ID >= ? AND Client_Tracking.Date > ?
ORDER BY Client_Tracking.ID ASC"""

    @staticmethod
    def query_get_org_number_tree():
        return """SELECT o.Number AS AncestorOrgNumberTree
                      FROM Org_Relation_Cache c
                      JOIN Organization o ON o.ID = c.Parent_Org_ID
                      WHERE c.Child_Org_ID = ?"""