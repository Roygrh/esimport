################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import logging

from datetime import datetime, timedelta, timezone

from esimport.models import ESRecord
from esimport.models.base import BaseModel
from esimport.utils import set_utc_timezone


logger = logging.getLogger(__name__)


class Session(BaseModel):


    _type = "session"
    _date_field = "LogoutTime"

    @staticmethod
    def get_type():
        return Session._type

    @staticmethod
    def get_key_date_field():
        return Session._date_field


    def get_sessions(self, start_id, limit, start_date='1900-01-01'):
        q = self.query_one(start_id, start_date, limit)
        for row in self.fetch_dict(q):
            row['ID'] = int(row.get('ID'))
            if 'LogoutTime' in row and 'SessionLength' in row:
                row['LoginTime'] = row['LogoutTime'] - timedelta(seconds=row['SessionLength'])

            for key, value in row.items():
                if isinstance(value, datetime):
                    row[key] = set_utc_timezone(value)

            yield ESRecord(row, self.get_type())


    @staticmethod
    def query_one(start_id, start_date, limit):
        q = """
SELECT TOP ({2}) 
	stop.ID AS ID,
	org.Number AS ServiceArea,
	val.Value AS ZoneType,
	hist.User_Name AS UserName,
	mem.Display_Name AS Name,
	mem.Number AS MemberNumber,
	hist.NAS_Identifier AS NasIdentifier,
	hist.Called_Station_Id AS CalledStation,
	hist.VLAN AS VLAN,
	hist.Calling_Station_Id AS MacAddress,
	hist.Date_UTC AS LogoutTime,
	acct.Session_ID AS SessionID,
	stop.Acct_Session_Time AS SessionLength,
	stop.Acct_Output_Octets AS BytesOut,
	stop.Acct_Input_Octets AS BytesIn,
	term.Name AS TerminationReason
FROM 
	Radius.dbo.Radius_Stop_Event stop
	JOIN Radius.dbo.Radius_Acct_Event acct ON acct.ID = stop.Radius_Acct_Event_ID
	JOIN Radius.dbo.Radius_Event_History hist ON hist.Radius_Event_ID = acct.Radius_Event_ID
	LEFT JOIN Radius.dbo.Radius_Terminate_Cause term ON term.ID = stop.Acct_Terminate_Cause
	JOIN Organization org ON org.ID = hist.Organization_ID
	LEFT JOIN Org_Value val ON val.Organization_ID = org.ID AND val.Name='ZoneType'
	LEFT JOIN Member mem ON mem.ID = hist.Member_ID
WHERE 
    stop.ID >= {0} AND stop.ID < ({0} + {2}) AND hist.Date_UTC > '{1}'
ORDER BY 
    stop.ID ASC
"""
        q = q.format(start_id, start_date, limit)
        return q
