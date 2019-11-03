GET_DEVICES_QUERY = """
SELECT TOP (?)
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

GET_DEVICES_ANCESTOR_ORG_NUMBER_TREE_QUERY = """
SELECT o.Number AS AncestorOrgNumberTree
FROM Org_Relation_Cache c
    JOIN Organization o ON o.ID = c.Parent_Org_ID
WHERE c.Child_Org_ID = ?"""
