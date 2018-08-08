################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import six
import logging

from datetime import datetime, timedelta

from esimport.models import ESRecord
from esimport.models.base import BaseModel


logger = logging.getLogger(__name__)


class Session(BaseModel):


    _type = "session"
    @staticmethod
    def get_type():
        return Session._type


    def get_sessions(self, start_id, limit, start_date='1900-01-01'):
        dt_columns = ['LogoutTime', 'LoginTime']
        q = self.query_one(start_id, start_date, limit)
        for row in self.fetch_dict(q):
            row['ID'] = long(row.get('ID')) if six.PY2 else int(row.get('ID'))
            if 'LogoutTime' in row and 'SessionLength' in row:
                row['LoginTime'] = row['LogoutTime'] - timedelta(seconds=row['SessionLength'])
            # convert datetime to string
            for dt_column in dt_columns:
                if dt_column in row and isinstance(row[dt_column], datetime):
                    row[dt_column] = row[dt_column].isoformat()
            yield ESRecord(row, self.get_type())


    @staticmethod
    def query_one(start_id, start_date, limit):
        q = """
SELECT DISTINCT TOP ({2}) 
	stop.ID AS ID,
	org.Number AS ServiceArea,
	val.Value AS ZoneType,
	hist.User_Name AS UserName,
	mem.Display_Name AS Name,
	mem.Number AS MemberNumber,
	hist.NAS_Identifier AS NasIdentifier,
	hist.Called_Station_Id AS CalledStation,
	nas_type.Name AS NetworkDeviceType,
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
	LEFT JOIN Access_Point_Nas_Device ap_nas ON ap_nas.Net_MAC_Address = hist.NAS_Identifier
	LEFT JOIN NAS_Device nas ON 
		nas.Organization_ID = hist.Organization_ID AND
		nas.VLAN_Range_Start <= hist.VLAN AND 
		nas.VLAN_Range_End >= hist.VLAN AND
		(nas.ID = ap_nas.Nas_Device_ID OR
		 nas.Radius_NAS_ID = hist.NAS_Identifier OR
		 nas.Net_MAC_Address = CASE WHEN CHARINDEX(':', hist.Called_Station_Id) = 0 THEN hist.Called_Station_Id ELSE SUBSTRING(hist.Called_Station_Id, 1, CHARINDEX(':', hist.Called_Station_Id)-1) END)
	LEFT JOIN NAS_Device_Type nas_type ON nas_type.ID = nas.NAS_Device_Type_ID
WHERE 
	stop.ID >= {0} AND stop.ID < ({0} + {2}) AND hist.Date_UTC > '{1}'
ORDER BY 
	stop.ID ASC
"""
        q = q.format(start_id, start_date, limit)
        return q
