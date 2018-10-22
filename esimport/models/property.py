################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import logging

from datetime import datetime
from esimport.models import ESRecord
from esimport.models.base import BaseModel


logger = logging.getLogger(__name__)


class Property(BaseModel):

    _type = "property"
    _date_field = "UpdateTime"

    @staticmethod
    def get_type():
        return Property._type

    @staticmethod
    def get_key_date_field():
        return Property._date_field


    def get_properties(self, start, limit):
        logger.debug("Fetching properties from Organization.ID >= {0} (limit: {1})"
                .format(start, limit))

        h1 = ['ID', 'Number', 'Name', 'GuestRooms', 'MeetingRooms', 'Lite',
              'Pan', 'CreatedUTC', 'GoLiveUTC', 'Status', 'TimeZone']

        q1 = self.query_one(start, limit)
        for rec1 in list(self.fetch(q1, h1)):

            q2 = self.query_two(rec1['ID'])
            for rec2 in list(self.fetch(q2, None)):
                if rec2.Name == "TaxRate":
                    rec1[rec2.Name] = float(rec2.Value)
                else:
                    rec1[rec2.Name] = rec2.Value

            q3 = self.query_three(rec1['ID'])
            for rec3 in list(self.fetch(q3, None)):
                rec1['Provider'] = rec3.Provider

            q4 = self.query_four(rec1['ID'])

            sa_list = []
            for rec4 in list(self.fetch(q4, None)):

                q5 = self.query_five(rec4.ID)

                hosts_list = []
                for rec5 in list(self.fetch(q5, None)):
                    host_dic = {"NASID":rec5.NASID, "RadiusNASID":rec5.RadiusNASID, "HostType":rec5.HostType, "VLANRangeStart":rec5.VLANRangeStart, "VLANRangeEnd":rec5.VLANRangeEnd, "NetIP":rec5.NetIP}
                    hosts_list.append(host_dic)

                sa_dic = {"Number":rec4.Number, "Name":rec4.Name, "ZoneType":rec4.ZoneType, "Hosts":hosts_list}
                sa_list.append(sa_dic)

            rec1['ServiceAreas'] = sa_list

            q = self.query_get_active_counts()
            row = self.execute(q, rec1['ID']).fetchone()

            rec1['ActiveMembers'] = row.ActiveMembers if row else 0
            rec1['ActiveDevices'] = row.ActiveDevices if row else 0

            rec1['UpdateTime'] = datetime.utcnow().isoformat()

            yield ESRecord(rec1, self.get_type())


    @staticmethod
    def query_one(start, limit):
        q = """Select TOP {0} Organization.ID as ID,
Organization.Number as Number,
Organization.Display_Name as Name,
Organization.Guest_Room_Count as GuestRooms,
Organization.Meeting_Room_Count as MeetingRooms,
Organization.Is_Lite as Lite,
Organization.Pan_Enabled as Pan,
Organization.Date_Added_UTC as CreatedUTC,
Org_Billing.Go_Live_Date_UTC as GoLiveUTC,
Org_Status.Name as Status,
Time_Zone.Tzid as TimeZone
From Organization WITH (NOLOCK)
Left Join Org_Status WITH (NOLOCK) ON Org_Status.ID = Organization.Org_Status_ID
Left Join Time_Zone WITH (NOLOCK) ON Time_Zone.ID = Organization.Time_Zone_ID
Left Join Org_Billing WITH (NOLOCK) ON Organization.ID = Org_Billing.Organization_ID
Where Organization.Org_Category_Type_ID = 3
    AND Organization.ID > {1}
ORDER BY Organization.ID ASC"""
        q = q.format(limit, start)
        return q


    @staticmethod
    def query_two(org_id):
        q = """SELECT Name, Value
FROM Org_Value WITH (NOLOCK)
WHERE Org_Value.Organization_ID = {0}
    AND Name NOT IN ('EradApiKey')"""
        q = q.format(org_id)
        return q


    @staticmethod
    def query_three(org_id):
        q = """SELECT Organization.Display_Name as Provider
FROM Org_Relation_Cache WITH (NOLOCK)
JOIN Organization ON Organization.ID = Parent_Org_ID
WHERE Child_Org_ID = {0}
    AND Organization.Org_Category_Type_ID = 2"""
        q = q.format(org_id)
        return q


    @staticmethod
    def query_four(org_id):
        q = """SELECT Organization.ID as ID,
                      Organization.Number as Number,
                      Organization.Display_Name as Name,
                      Org_Value.Value as ZoneType
FROM Org_Relation_Cache WITH (NOLOCK)
JOIN Organization WITH (NOLOCK) ON Organization.ID = Child_Org_ID
LEFT JOIN Org_Value WITH (NOLOCK) ON Org_Value.Name='ZoneType'
WHERE Org_Relation_Cache.Parent_Org_ID = {0}
AND Organization.Org_Category_Type_ID = 4"""
        q = q.format(org_id)
        return q

    @staticmethod
    def query_five(org_id):
        q = """SELECT NAS_Device.NASID as NASID,
                      NAS_Device.RadiusNASID as RadiusNASID,
                      NAS_Device_Type.Name as HostType,
                      NAS_Device.VLAN_Range_Start as VLANRangeStart,
                      NAS_Device.VLAN_Range_End as VLANRangeEnd,
                      NAS_Device.Net_IP as NetIP
FROM NAS_Device WITH (NOLOCK)
LEFT JOIN NAS_Device_Type WITH (NOLOCK) ON NAS_Device_Type.ID = NAS_Device.NAS_Device_Type_ID
WHERE Organization_ID = {0}"""
        q = q.format(org_id)
        return q



    @staticmethod
    def query_get_active_counts():
        return """SELECT COUNT(DISTINCT r.Member_ID) as ActiveMembers,
                         COUNT(DISTINCT r.Calling_Station_Id) as ActiveDevices
                  FROM Radius_Active_Usage r
                  INNER JOIN Org_Relation_Cache o ON o.Child_Org_ID = r.Organization_ID
                  WHERE o.Parent_Org_ID = ?"""
