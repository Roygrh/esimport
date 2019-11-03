GET_CONFERENCES_QUERY = """
SELECT TOP (?)
    Scheduled_Access.ID AS ID,
    Scheduled_Access.Event_Name AS Name,
    Scheduled_Access.Date_Created_UTC AS DateCreatedUTC,
    Organization.Number AS ServiceArea,
    Member.Display_Name AS Code,
    Member.ID AS MemberID,
    Member.Number AS MemberNumber,
    Member_Status.Name AS MemberStatus,
    Network_Configuration.SsidName AS SSID,
    Network_Access_Limits.Start_Date_UTC AS StartDateUTC,
    Network_Access_Limits.End_Date_UTC AS EndDateUTC,
    Network_Access_Limits.Connection_Limit AS ConnectionLimit,
    Network_Access_Limits.Down_kbs AS DownKbs,
    Network_Access_Limits.Up_kbs AS UpKbs,
    Network_Access_Limits.Group_Bandwidth_Limit as GroupBandwidthLimit,
    Scheduled_Access.Actual_User_Count AS UserCount,
    Scheduled_Access.Total_Input_Bytes AS TotalInputBytes,
    Scheduled_Access.Total_Output_Bytes AS TotalOutputBytes,
    Scheduled_Access.Total_Session_Time AS TotalSessionTime
FROM Scheduled_Access
    LEFT JOIN Member WITH (NOLOCK) ON Member.ID = Scheduled_Access.Member_ID
    LEFT JOIN Member_Status WITH (NOLOCK) ON Member_Status.ID = Member.Member_Status_ID
    LEFT JOIN Organization WITH (NOLOCK) ON Organization.ID = Scheduled_Access.Organization_ID
    LEFT JOIN Network_Configuration WITH (NOLOCK) ON Network_Configuration.Scheduled_Access_ID = Scheduled_Access.ID
    LEFT JOIN Network_Access WITH (NOLOCK) ON Network_Access.ID = Scheduled_Access.Network_Access_ID
    LEFT JOIN Network_Access_Limits WITH (NOLOCK) ON Network_Access_Limits.ID = Network_Access.Network_Access_Limits_ID
WHERE Scheduled_Access.ID >= ? AND Scheduled_Access.Date_Created_UTC > ?
ORDER BY Scheduled_Access.ID ASC"""

GET_CONFERENCE_ADDITIONAL_ACCESS_CODES = """
SELECT Display_Name AS Code,
        Member.Number AS MemberNumber,
        Member.ID AS MemberID
FROM Member WITH (NOLOCK)
    JOIN Scheduled_Access_Member ON Scheduled_Access_Member.Member_ID = Member.ID
WHERE Scheduled_Access_Member.Scheduled_Access_ID = ?"""
