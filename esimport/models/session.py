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


    def get_sessions(self, start, limit, start_date='1900-01-01'):
        dt_columns = ['LogoutTime', 'LoginTime']
        q = self.query_one(start_date, start, limit)
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
    def query_one(start_date, start_rad_id, limit):
        q = """
SELECT DISTINCT TOP ({1}) 
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
	term.Name AS TerminationReason,
    zp.Name as ServicePlan
FROM 
	Radius.dbo.Radius_Stop_Event stop WITH (NOLOCK)
	JOIN Radius.dbo.Radius_Acct_Event acct WITH (NOLOCK) ON acct.ID = stop.Radius_Acct_Event_ID
	JOIN Radius.dbo.Radius_Event_History hist WITH (NOLOCK) ON hist.Radius_Event_ID = acct.Radius_Event_ID
	LEFT JOIN Radius.dbo.Radius_Terminate_Cause term WITH (NOLOCK) ON term.ID = stop.Acct_Terminate_Cause
	JOIN Organization org WITH (NOLOCK) ON org.ID = hist.Organization_ID
	LEFT JOIN Org_Value val WITH (NOLOCK) ON val.Organization_ID = org.ID AND val.Name='ZoneType'
	LEFT JOIN Member mem WITH (NOLOCK) ON mem.ID = hist.Member_ID
    LEFT JOIN Zone_Plan_Account zpa WITH (NOLOCK) ON zpa.Member_ID = hist.Member_ID
    LEFT JOIN Zone_Plan zp WITH (NOLOCK) ON zp.ID = zpa.Zone_Plan_ID
	-- if Radius_Event_History.NAS_Identifier is a MAC address, use Access_Point_NAS_Device.Net_MAC_Address to get a NAS_Device
	LEFT JOIN Access_Point_Nas_Device ap_nas WITH (NOLOCK) ON ap_nas.Net_MAC_Address = hist.NAS_Identifier
	LEFT JOIN NAS_Device ap_nas_device WITH (NOLOCK) ON 
		ap_nas_device.Organization_ID = hist.Organization_ID AND
		ap_nas_device.ID = ap_nas.Nas_Device_ID AND
		ap_nas_device.VLAN_Range_Start <= hist.VLAN AND 
		ap_nas_device.VLAN_Range_End >= hist.VLAN
	-- if Radius_Event_History.NAS_Identifier is NOT a MAC address, go straight to NAS_Device.Radius_NAS_ID (see COALESCE below)
	LEFT JOIN NAS_Device nas_device WITH (NOLOCK) ON 
		nas_device.Organization_ID = hist.Organization_ID AND
		nas_device.Radius_NAS_ID = hist.NAS_Identifier AND
		nas_device.VLAN_Range_Start <= hist.VLAN AND 
		nas_device.VLAN_Range_End >= hist.VLAN
	-- alternative approach of using Radius_Event_History.Called_Station_Id to get a NAS_Device
	LEFT JOIN NAS_Device nas_device_alt WITH (NOLOCK) ON 
		nas_device_alt.Organization_ID = hist.Organization_ID AND
		nas_device_alt.Net_MAC_Address = CASE WHEN CHARINDEX(':', hist.Called_Station_Id) = 0 THEN hist.Called_Station_Id ELSE SUBSTRING(hist.Called_Station_Id, 1, CHARINDEX(':', hist.Called_Station_Id)-1) END AND
		nas_device_alt.VLAN_Range_Start <= hist.VLAN AND 
		nas_device_alt.VLAN_Range_End >= hist.VLAN
	-- then take the first valid NAS_Device and lookup its type
	LEFT JOIN NAS_Device_Type nas_type WITH (NOLOCK) ON nas_type.ID = COALESCE(ap_nas_device.NAS_Device_Type_ID, nas_device.NAS_Device_Type_ID, nas_device_alt.NAS_Device_Type_ID)
WHERE 
	stop.ID >= {0} AND hist.Date_UTC > '{2}'
ORDER BY 
	stop.ID ASC
"""
        q = q.format(start_rad_id, limit, start_date)
        return q
