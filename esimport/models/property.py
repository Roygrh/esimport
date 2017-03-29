import logging

from esimport.models import ESRecord


logger = logging.getLogger(__name__)


class Property:

    cursor = None

    def __init__(self, connection):
        self.cursor = connection.cursor


    _type = "property"
    @staticmethod
    def get_type():
        return Property._type


    def fetch(self, query, column_names):
        for row in self.cursor.execute(query):
            if column_names:
                yield dict([(cn, getattr(row, cn, '')) for cn in column_names])
            else:
                yield row


    def get_properties(self, start, limit):
        logger.debug("Fetching properties from Organization.ID >= {0} (limit: {1})"
                .format(start, limit))

        h1 = ['ID', 'Number', 'Name', 'GuestRooms', 'MeetingRooms',
                'Lite', 'Pan', 'Status', 'Time_Zone']
        q1 = self.query_one(start, limit)
        for rec1 in list(self.fetch(q1, h1)):

            q2 = self.query_two(rec1['ID'])
            for rec2 in list(self.fetch(q2, None)):
                rec1[rec2.Name] = rec2.Value

            q3 = self.query_three(rec1['ID'])
            for rec3 in list(self.fetch(q3, None)):
                rec1['Provider_Display_Name'] = rec3.Provider_Display_Name

            q4 = self.query_four(rec1['ID'])
            for rec4 in list(self.fetch(q4, None)):
                rec1[rec4.Service_Area_Number] = rec4.Service_Area_Display_Name

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
Org_Status.Name as Status,
Time_Zone.Tzid as Time_Zone
From Organization
Left Join Org_Status on Org_Status.ID = Organization.Org_Status_ID
Left Join Time_Zone on Time_Zone.ID = Organization.Time_Zone_ID
Where Organization.Org_Category_Type_ID = 3
    AND Organization.ID >= {1}
ORDER BY Organization.ID ASC"""
        q = q.format(limit, start)
        return q


    @staticmethod
    def query_two(org_id):
        q = """SELECT Name, Value
FROM Org_Value
WHERE Org_Value.Organization_ID = {0}"""
        q = q.format(org_id)
        return q


    @staticmethod
    def query_three(org_id):
        q = """WITH Providers (Parent_Org_ID, Child_Org_ID, Org_Category_Type_ID, Display_Name, DepthNumber)
AS
(
    SELECT Org_Relation.Parent_Org_ID, Org_Relation.Child_Org_ID, Organization.Org_Category_Type_ID, Organization.Display_Name, 0
    FROM Org_Relation, Organization
    WHERE Org_Relation.Child_Org_ID = Organization.ID
        AND Organization.ID = {0}
    UNION ALL
    SELECT Providers.Parent_Org_ID, Providers.Child_Org_ID, Organization.Org_Category_Type_ID, Organization.Display_Name, DepthNumber+1
    FROM Organization
    INNER JOIN Providers ON Providers.Parent_Org_ID = Organization.ID
    WHERE Providers.Org_Category_Type_ID = 1
)
SELECT Providers.Display_Name as Provider_Display_Name
FROM Providers
WHERE Providers.Org_Category_Type_ID = 2;"""
        q = q.format(org_id)
        return q


    @staticmethod
    def query_four(org_id):
        q = """WITH Providers (Org_ID, Parent_Org_ID, Child_Org_ID, Org_Category_Type_ID, Display_Name, DepthNumber)
AS
(
    SELECT Organization.ID, Org_Relation.Parent_Org_ID, Org_Relation.Child_Org_ID, Organization.Org_Category_Type_ID, Organization.Display_Name, 0
    FROM Org_Relation, Organization
    WHERE Org_Relation.Parent_Org_ID = Organization.ID
    UNION ALL
    SELECT Providers.Org_ID, Org_Relation.Parent_Org_ID, Org_Relation.Child_Org_ID, Organization.Org_Category_Type_ID, Organization.Display_Name, DepthNumber + 1
    FROM Org_Relation, Organization, Providers
    WHERE Org_Relation.Parent_Org_ID = Organization.ID
        AND Organization.ID = Providers.Child_Org_ID
)
SELECT Providers.Display_Name as Service_Area_Display_Name, COUNT(*) as Service_Area_Number
FROM Providers
WHERE Providers.Org_ID = {0}
    AND Providers.Org_Category_Type_ID = 4
GROUP BY Providers.Display_Name;"""
        q = q.format(org_id)
        return q
