################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import logging

from datetime import datetime, timezone
from esimport.models import ESRecord
from esimport.models.base import BaseModel
from esimport.utils import set_utc_timezone


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

        q1 = self.query_get_properties()
        for rec in list(self.fetch_dict(q1, limit, start)):

            # All site-level service plans are stored with their org ID as key
            site_level_sps = {}

            q_serviceplans = self.query_get_service_area_serviceplans()
            for service_plan in list(self.fetch(q_serviceplans, rec["ID"])):
                sp_dic = {
                    "Number": service_plan.Number,
                    "Name": service_plan.Name,
                    "Description": service_plan.Description,
                    "Price": service_plan.Price,
                    "UpKbs": service_plan.UpKbs,
                    "DownKbs": service_plan.DownKbs,
                    "IdleTimeout": service_plan.IdleTimeout,
                    "ConnectionLimit": service_plan.ConnectionLimit,
                    "RadiusClass": service_plan.RadiusClass,
                    "GroupBandwidthLimit": service_plan.GroupBandwidthLimit,
                    "Type": service_plan.Type,
                    "PlanTime": service_plan.PlanTime,
                    "PlanUnit": service_plan.PlanUnit,
                    "LifespanTime": service_plan.LifespanTime,
                    "LifespanUnit": service_plan.LifespanUnit,
                    "CurrencyCode": service_plan.CurrencyCode,
                    "Status": service_plan.Status,
                    "OrgCode": service_plan.OrgCode,
                    "DateCreatedUTC": set_utc_timezone(service_plan.DateCreatedUTC)
                }

                if not service_plan.Owner_Org_ID in site_level_sps.keys():
                    site_level_sps[service_plan.Owner_Org_ID] = [sp_dic]
                else:
                    site_level_sps[service_plan.Owner_Org_ID].append(sp_dic)

            q2 = self.query_get_property_org_values()
            for rec2 in self.execute(q2, rec["ID"]):
                if rec2.Name == "TaxRate":
                    rec[rec2.Name] = float(rec2.Value)
                else:
                    rec[rec2.Name] = rec2.Value

            q3 = self.query_get_provider()
            rec["Provider"] = self.execute(q3, rec["ID"]).fetchval()

            sa_list = []

            q4 = self.query_get_service_areas()
            for rec4 in list(self.fetch(q4, rec["ID"])):

                hosts_list = []

                q5 = self.query_get_service_area_devices()
                for rec5 in list(self.fetch(q5, rec4.ID)):
                    host_dic = {
                        "NASID": rec5.NASID,
                        "RadiusNASID": rec5.RadiusNASID,
                        "HostType": rec5.HostType,
                        "VLANRangeStart": rec5.VLANRangeStart,
                        "VLANRangeEnd": rec5.VLANRangeEnd,
                        "NetIP":rec5.NetIP
                    }
                    hosts_list.append(host_dic)

                sa_dic = {
                    "Number": rec4.Number,
                    "Name": rec4.Name,
                    "ZoneType": rec4.ZoneType,
                    "ActiveMembers": rec4.ActiveMembers,
                    "ActiveDevices": rec4.ActiveDevices,
                    "Hosts": hosts_list
                }

                if rec4.ID in site_level_sps.keys():
                    sa_dic["ServicePlans"] = site_level_sps[rec4.ID]
                else:
                    sa_dic["ServicePlans"] = []

                sa_list.append(sa_dic)

            rec["ServiceAreaObjects"] = sa_list

            q6 = self.query_get_org_number_tree()
            org_number_tree_list = []

            for rec6 in list(self.fetch(q6, rec["ID"], rec["ID"])):
                org_number_tree_list.append(rec6[0])

            rec["OrgNumberTree"] = org_number_tree_list

            q7 = self.query_get_active_counts()
            row = self.execute(q7, rec["ID"]).fetchone()

            rec["ActiveMembers"] = row.ActiveMembers if row else 0
            rec["ActiveDevices"] = row.ActiveDevices if row else 0

            rec["Address"] = {
                "AddressLine1": rec.pop("AddressLine1"),
                "AddressLine2": rec.pop("AddressLine2"),
                "City": rec.pop("City"),
                "Area": rec.pop("Area"),
                "PostalCode": rec.pop("PostalCode"),
                "CountryName": rec.pop("CountryName")
            }

            for key, value in rec.items():
                if isinstance(value, datetime):
                    rec[key] = set_utc_timezone(value)

            rec["UpdateTime"] = datetime.now(timezone.utc)

            yield ESRecord(rec, self.get_type())

    @staticmethod
    def query_get_properties():
        return """Select TOP (?) Organization.ID as ID,
Organization.Number as Number,
Organization.Display_Name as Name,
Organization.Guest_Room_Count as GuestRooms,
Organization.Meeting_Room_Count as MeetingRooms,
Organization.Is_Lite as Lite,
Organization.Pan_Enabled as Pan,
Organization.Date_Added_UTC as CreatedUTC,
Org_Billing.Go_Live_Date_UTC as GoLiveUTC,
Org_Status.Name as Status,
Time_Zone.Tzid as TimeZone,
Address.Address_1 as AddressLine1,
Address.Address_2 as AddressLine2,
Address.City,
Address.Area,
Address.Postal_Code as PostalCode,
Country.Name as CountryName
From Organization WITH (NOLOCK)
Left Join Org_Status WITH (NOLOCK) ON Org_Status.ID = Organization.Org_Status_ID
Left Join Time_Zone WITH (NOLOCK) ON Time_Zone.ID = Organization.Time_Zone_ID
Left Join Org_Billing WITH (NOLOCK) ON Organization.ID = Org_Billing.Organization_ID
Left Join Contact_Address WITH (NOLOCK) ON Contact_Address.Contact_ID = Organization.Contact_ID
Left Join Address WITH (NOLOCK) ON Address.ID = Contact_Address.Address_ID
Left Join Country WITH (NOLOCK) ON Country.ID = Address.Country_ID
Where Organization.Org_Category_Type_ID = 3
    AND Organization.ID > ?
ORDER BY Organization.ID ASC"""

    @staticmethod
    def query_get_property_org_values():
        return """SELECT Name, Value
                  FROM Org_Value WITH (NOLOCK)
                  WHERE Org_Value.Organization_ID = ?
                    AND Name NOT IN ('EradApiKey')"""

    """
    Returns the owning service provider for the given org.  If there are multiple
    service providers in the org lineage, then the most distant ancestor will be used.
    """
    @staticmethod
    def query_get_provider():
        return """SELECT TOP 1 Organization.Display_Name as Provider
                  FROM Org_Relation_Cache WITH (NOLOCK)
                  JOIN Organization ON Organization.ID = Org_Relation_Cache.Parent_Org_ID
                  WHERE Org_Relation_Cache.Child_Org_ID = ?
                    AND Organization.Org_Category_Type_ID = 2
                    AND Org_Relation_Cache.Org_Relation_Type_ID = 1
                  ORDER BY Org_Relation_Cache.Depth DESC"""

    @staticmethod
    def query_get_service_areas():
        return """SELECT Organization.ID as ID,
                      Organization.Number as Number,
                      Organization.Display_Name as Name,
                      Org_Value.Value as ZoneType,
                      COUNT(DISTINCT r.Member_ID) as ActiveMembers,
                      COUNT(DISTINCT r.Calling_Station_Id) as ActiveDevices
FROM Org_Relation_Cache WITH (NOLOCK)
JOIN Organization WITH (NOLOCK) ON Organization.ID = Child_Org_ID
LEFT JOIN Org_Value WITH (NOLOCK) ON Org_Value.Organization_ID = Organization.ID AND Org_Value.Name='ZoneType'
LEFT JOIN Radius_Active_Usage r WITH (NOLOCK) ON r.Organization_ID = Child_Org_ID
WHERE Org_Relation_Cache.Parent_Org_ID = ?
    AND Organization.Org_Category_Type_ID = 4
GROUP BY Organization.ID,
         Organization.Number,
         Organization.Display_Name,
         Org_Value.Value"""

    @staticmethod
    def query_get_service_area_devices():
        return """SELECT NAS_Device.NAS_ID as NASID,
                      NAS_Device.Radius_NAS_ID as RadiusNASID,
                      NAS_Device_Type.Name as HostType,
                      NAS_Device.VLAN_Range_Start as VLANRangeStart,
                      NAS_Device.VLAN_Range_End as VLANRangeEnd,
                      NAS_Device.Net_IP as NetIP
FROM NAS_Device WITH (NOLOCK)
LEFT JOIN NAS_Device_Type WITH (NOLOCK) ON NAS_Device_Type.ID = NAS_Device.NAS_Device_Type_ID
WHERE Organization_ID = ?"""

    @staticmethod
    def query_get_org_number_tree():
        return """SELECT o.Number as OrgNumberTree
               FROM Org_Relation_Cache c
               JOIN Organization o on o.ID = c.Parent_Org_ID
               WHERE c.Child_Org_ID = ?
               UNION
               SELECT o.Number as OrgNumberTree
               FROM Org_Relation_Cache c
               JOIN Organization o on o.ID = c.Child_Org_ID
               WHERE c.Parent_Org_ID = ?"""

    @staticmethod
    def query_get_active_counts():
        return """SELECT COUNT(DISTINCT r.Member_ID) as ActiveMembers,
                         COUNT(DISTINCT r.Calling_Station_Id) as ActiveDevices
                  FROM Radius_Active_Usage r
                  INNER JOIN Org_Relation_Cache o ON o.Child_Org_ID = r.Organization_ID
                  WHERE o.Parent_Org_ID = ?"""

    @staticmethod
    def query_get_service_area_serviceplans():
        return """SELECT            
                Organization.ID as Owner_Org_ID,
                Zone_Plan.Plan_Number AS Number,
                Zone_Plan.Name AS Name, 
                Zone_Plan.Description AS Description,
                Zone_Plan.Price AS Price,
                Network_Access_Limits.Up_kbs AS UpKbs,
                Network_Access_Limits.Down_kbs AS DownKbs,
                Network_Access_Limits.Idle_Timeout AS IdleTimeout,
                Network_Access_Limits.Connection_Limit AS ConnectionLimit,
                Network_Access_Limits.Radius_Class AS RadiusClass,
                Network_Access_Limits.Group_Bandwidth_Limit AS GroupBandwidthLimit,
                Zone_Plan_Type.Name AS Type,
                Prepaid_Zone_Plan.Consumable_Time AS PlanTime,
                Time_Unit.Name AS PlanUnit,
                Prepaid_Zone_Plan.Lifespan_Time AS LifespanTime,
                Lifespan_Time_Unit.Name AS LifespanUnit,
                Currency.Code AS CurrencyCode,
                Zone_Plan_Status.Name AS Status,
                Organization.Property_Code AS OrgCode,
                Zone_Plan.Date_Created_UTC AS DateCreatedUTC
            FROM
                Zone_Plan
                JOIN Network_Access_Limits ON Network_Access_Limits.ID = Zone_Plan.Network_Access_Limits_ID
                JOIN Zone_Plan_Type ON Zone_Plan_Type.ID = Zone_Plan.Zone_Plan_Type_ID
                LEFT JOIN Prepaid_Zone_Plan ON Prepaid_Zone_Plan.Zone_Plan_ID = Zone_Plan.ID
                LEFT JOIN Time_Unit ON Time_Unit.ID = Prepaid_Zone_Plan.Consumable_Time_Unit_ID
                LEFT JOIN Time_Unit AS Lifespan_Time_Unit ON Lifespan_Time_Unit.ID = Prepaid_Zone_Plan.Lifespan_Time_Unit_ID
                JOIN Currency ON Currency.ID = Zone_Plan.Price_Currency_ID
                JOIN Zone_Plan_Status ON Zone_Plan_Status.ID = Zone_Plan.Zone_Plan_Status_ID
                JOIN Org_Zone ON Org_Zone.ID = Zone_Plan.Org_Zone_ID
                JOIN Organization ON Organization.ID = Org_Zone.Organization_ID
                JOIN Org_Relation_Cache ON Org_Relation_Cache.Child_Org_ID = Organization.ID
            WHERE 
                Org_Relation_Cache.Parent_Org_ID = ?"""

