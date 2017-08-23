import six
import logging

from datetime import datetime

from esimport.models import ESRecord
from esimport.models.base import BaseModel


logger = logging.getLogger(__name__)


class Conference(BaseModel):


    _type = "conference"
    @staticmethod
    def get_type():
        return Conference._type


    def get_conferences(self, start, limit, start_date='1900-01-01'):
        dt_columns = ['DateCreatedUTC']
        q = self.query_one(start_date, start, limit)
        for row in self.fetch_dict(q):
            row['ID'] = long(row.get('ID')) if six.PY2 else int(row.get('ID'))
            # convert datetime to string
            for dt_column in dt_columns:
                if dt_column in row and isinstance(row[dt_column], datetime):
                    row[dt_column] = row[dt_column].isoformat()
            row['UpdateTime'] = datetime.utcnow().isoformat()

            q2 = self.query_two(row['ID'])
            code_list = []
            member_number_list = []
            for rec2 in list(self.fetch(q2, None)):
                code_list.append(rec2.Name)
                member_number_list.append(rec2.Number)

            row['CodeList'] = code_list
            row['MemberNumberList'] = member_number_list

            yield ESRecord(row, self.get_type())


    @staticmethod
    def query_one(start_date, start_sa_id, limit):
        q = """SELECT TOP ({1})
Scheduled_Access.ID AS ID,
Scheduled_Access.Event_Name AS Name,
Scheduled_Access.Date_Created_UTC AS DateCreatedUTC,
Organization.Number AS ServiceArea,
Member.Display_Name AS Code,
Member.ID AS MemberID,
Network_Configuration.SsidName AS SSID,
Network_Access_Limits.Start_Date_UTC AS StartDateUTC,
Network_Access_Limits.End_Date_UTC AS EndDateUTC,
Scheduled_Access.Actual_User_Count AS UserCount,
Scheduled_Access.Total_Input_Bytes AS TotalInputBytes,
Scheduled_Access.Total_Output_Bytes AS TotalOutputBytes,
Scheduled_Access.Total_Session_Time AS TotalSessionTime
FROM Scheduled_Access
LEFT JOIN Member WITH (NOLOCK) ON Member.ID = Scheduled_Access.Member_ID
LEFT JOIN Organization WITH (NOLOCK) ON Organization.ID = Scheduled_Access.Organization_ID
LEFT JOIN Network_Configuration WITH (NOLOCK) ON Network_Configuration.Scheduled_Access_ID = Scheduled_Access.ID
WHERE Scheduled_Access.ID >= {0} AND Scheduled_Access.Date_Created_UTC > '{2}'
ORDER BY Scheduled_Access.ID ASC
"""
        q = q.format(start_sa_id, limit, start_date)
        return q


    @staticmethod
    def query_two(sa_id):
        q = """SELECT Display_Name AS Name,
Number AS MemberNumber
FROM Member WITH (NOLOCK)
JOIN Scheduled_Access_Member ON Scheduled_Access_Member.Member_ID = Member.ID
WHERE Scheduled_Access_Member.Scheduled_Access_ID = {0}
"""
        q = q.format(sa_id)
        return q
