################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import six
import logging

from datetime import datetime, timedelta, timezone
from dateutil import tz

from esimport.models import ESRecord
from esimport.models.base import BaseModel
from esimport.utils import convert_pacific_to_utc, convert_utc_to_local_time


logger = logging.getLogger(__name__)


class Device(BaseModel):

    _type = "device"
    _date_field = "DateUTC"

    # These dates are in 'PST8PDT' format
    dates_from_pacific = {"Date": "DateUTC"}

    @staticmethod
    def get_type():
        return Device._type


    @staticmethod
    def get_key_date_field():
        return Device._date_field


    def get_devices(self, start, limit, start_date='1900-01-01'):
        # REVIEW: dt_columns seems redundant now.  It looks like dates_from_pacific holds the date columns to convert to Pacific time.
        dt_columns = ['Date']
        q = self.query_one(start_date, start, limit)

        # REVIEW: I think I told you do it this way ... to set the correct timezone on the datetime before passing it into convert_pacific_to_utc(),
        # but in the long run, I think we'll want to change how this works.  Maybe there'll be other mappings that have pacific dates and we'll
        # have copy this code to those mapping files and I don't want to copy the "tz.gettz('PST8PDT')" logic everywhere ... I'd rather have it
        # in one location.  I'm thinking to create another function in the utils class like, set_pacific_timezone() and pass the naive date to it
        # and let it set the PST8PDT timezone on it and then return it.  Then we can pass that timezone aware date to convert_pacific_to_utc()
        pacific_timezone = tz.gettz('PST8PDT')

        for row in self.fetch_dict(q):
            row['ID'] = long(row.get('ID')) if six.PY2 else int(row.get('ID'))

            # REVIEW: Let's rework this logic.  The code in (esimport\models\account.py lines 58-60) looks like a good
            # model to follow.  I think should just loop through all of the fields in the row.  If the field is a datetime, 
            # then it would check to see if it's in the dates_from_pacific dict.  If so, then call convert_pacific_to_utc(),
            # otherwise just set the timezone to UTC.
            for dt_column in dt_columns:
                if dt_column in row and isinstance(row[dt_column], datetime):
                    if dt_column in self.dates_from_pacific:
                        row[self.dates_from_pacific[dt_column]] = convert_pacific_to_utc(row[dt_column].replace(tzinfo=pacific_timezone))
                        del row[dt_column]
                    else:
                        row[dt_column] = convert_pacific_to_utc(row[dt_column].replace(tzinfo=timezone.utc))

            yield ESRecord(row, self.get_type())


    @staticmethod
    def query_one(start_date, start_ct_id, limit):
        q = """SELECT TOP({1})
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
WHERE Client_Tracking.ID >= {0} AND Client_Tracking.Date > '{2}'
ORDER BY Client_Tracking.ID ASC
"""
        q = q.format(start_ct_id, limit, start_date)
        return q
