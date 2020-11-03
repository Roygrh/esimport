GET_PROPERTIES_QUERY = """
Select TOP (?) Organization.ID as ID,
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
Where 
    Organization.Org_Category_Type_ID = 3
    AND Organization.ID > ?
ORDER BY Organization.ID ASC"""
