SESSIONS_QUERY = """
    SELECT TOP (?) 
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
        dateadd(s, (0-stop.Acct_Session_Time), hist.Date_UTC) AS LoginTime,
        hist.Date_UTC AS LogoutTime,
        acct.Session_ID AS SessionID,
        stop.Acct_Session_Time AS SessionLength,
        stop.Acct_Output_Octets AS BytesOut,
        stop.Acct_Input_Octets AS BytesIn,
        term.Name AS TerminationReason,
        zp.Name AS ServicePlan,
        zp.Zone_Plan_Tag_ID AS ServicePlanTier
    FROM
        Radius.dbo.Radius_Stop_Event stop
        JOIN Radius.dbo.Radius_Acct_Event acct ON acct.ID = stop.Radius_Acct_Event_ID
        JOIN Radius.dbo.{0} hist ON hist.{1} = acct.Radius_Event_ID
        LEFT JOIN Radius.dbo.Radius_Terminate_Cause term ON term.ID = stop.Acct_Terminate_Cause
        JOIN Organization org ON org.ID = hist.Organization_ID
        LEFT JOIN Org_Value val ON val.Organization_ID = org.ID AND val.Name='ZoneType'
        LEFT JOIN Member mem ON mem.ID = hist.Member_ID
        OUTER APPLY (
            SELECT TOP 1 Zone_Plan_ID
            FROM Zone_Plan_Account 
            WHERE Zone_Plan_Account.Activation_Date_UTC <= dateadd(s, (0-stop.Acct_Session_Time), hist.Date_UTC) AND Zone_Plan_Account.Member_ID = mem.ID
            ORDER BY Zone_Plan_Account.Activation_Date_UTC DESC
        ) zpa
        LEFT JOIN Zone_Plan zp ON zp.ID = zpa.Zone_Plan_ID
    WHERE
        stop.ID >= ? AND stop.ID < (? + ?) AND hist.Date_UTC > ?
    ORDER BY
        stop.ID ASC
"""
