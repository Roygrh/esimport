import six
import logging

from datetime import datetime, timedelta

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
            row['UpdateTime'] = datetime.datetime.utcnow().isoformat()
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
Scheduled_Access.Actual_User_Count AS UserCount,
Scheduled_Access.Total_Input_Bytes AS TotalInputBytes,
Scheduled_Access.Total_Output_Bytes AS TotalOutputBytes,
Scheduled_Access.Total_Session_Time AS TotalSessionTime
FROM Scheduled_Access
LEFT JOIN Member WITH (NOLOCK) ON Member.ID = Scheduled_Access.Member_ID
LEFT JOIN Organization WITH (NOLOCK) ON Organization.ID = Scheduled_Access.Organization_ID
WHERE Scheduled_Access.ID >= {0} AND Scheduled_Access.Date_Created_UTC > '{2}'
ORDER BY Scheduled_Access.ID ASC
"""
        q = q.format(start_sa_id, limit, start_date)
        return q
