################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import six
import logging

from datetime import datetime

from esimport.models import ESRecord
from esimport.models.base import BaseModel

logger = logging.getLogger(__name__)


class Conference(BaseModel):
    _type = "conference"
    _date_field = "UpdateTime"

    @staticmethod
    def get_type():
        return Conference._type

    @staticmethod
    def get_key_date_field():
        return Conference._date_field

    def get_conferences(self, start, limit, start_date='1900-01-01'):
        logger.debug("Fetching conferences from Scheduled_Access.ID >= {0} AND Scheduled_Access.Date_Created_UTC > {1} (limit: {2})"
                     .format(start, start_date, limit))

        dt_columns = ['DateCreatedUTC', 'StartDateUTC', 'EndDateUTC']
        q1 = self.query_one(start_date, start, limit)

        h1 = ['ID', 'Name', 'DateCreatedUTC', 'ServiceArea',
              'Code', 'MemberID', 'MemberNumber', 'SSID', 'StartDateUTC', 'EndDateUTC',
	          'ConnectionLimit', 'DownKbs', 'UpKbs', 'UserCount', 'TotalInputBytes',
              'TotalOutputBytes', 'TotalSessionTime']

        for rec1 in list(self.fetch(q1, h1)):

            rec1['ID'] = long(rec1.get('ID')) if six.PY2 else int(rec1.get('ID'))
            # convert datetime to string
            for dt_column in dt_columns:
                if dt_column in rec1 and isinstance(rec1[dt_column], datetime):
                    rec1[dt_column] = rec1[dt_column].isoformat()

            rec1['UpdateTime'] = datetime.utcnow().isoformat()

            q2 = self.query_two(rec1['ID'])

            # Update the CodeList with the main Code first
            code_list = [rec1.get('Code')]
            
            # Update the MemberNumberList with the main MemberNumber first
            member_number_list = [rec1.get('MemberNumber')]

            for rec2 in list(self.fetch(q2, None)):
                code_list.append(rec2.Name)
                member_number_list.append(rec2.MemberNumber)

            rec1['CodeList'] = code_list
            rec1['MemberNumberList'] = member_number_list

            yield ESRecord(rec1, self.get_type())

    @staticmethod
    def query_one(start_date, start_sa_id, limit):
        q = """SELECT TOP ({1})
Scheduled_Access.ID AS ID,
Scheduled_Access.Event_Name AS Name,
Scheduled_Access.Date_Created_UTC AS DateCreatedUTC,
Organization.Number AS ServiceArea,
Member.Display_Name AS Code,
Member.ID AS MemberID,
Member.Number AS MemberNumber,
Network_Configuration.SsidName AS SSID,
Network_Access_Limits.Start_Date_UTC AS StartDateUTC,
Network_Access_Limits.End_Date_UTC AS EndDateUTC,
Network_Access_Limits.Connection_Limit AS ConnectionLimit,
Network_Access_Limits.Down_kbs AS DownKbs,
Network_Access_Limits.Up_kbs AS UpKbs,
Scheduled_Access.Actual_User_Count AS UserCount,
Scheduled_Access.Total_Input_Bytes AS TotalInputBytes,
Scheduled_Access.Total_Output_Bytes AS TotalOutputBytes,
Scheduled_Access.Total_Session_Time AS TotalSessionTime
FROM Scheduled_Access
LEFT JOIN Member WITH (NOLOCK) ON Member.ID = Scheduled_Access.Member_ID
LEFT JOIN Organization WITH (NOLOCK) ON Organization.ID = Scheduled_Access.Organization_ID
LEFT JOIN Network_Configuration WITH (NOLOCK) ON Network_Configuration.Scheduled_Access_ID = Scheduled_Access.ID
LEFT JOIN Network_Access WITH (NOLOCK) ON Network_Access.ID = Scheduled_Access.Network_Access_ID
LEFT JOIN Network_Access_Limits WITH (NOLOCK) ON Network_Access_Limits.ID = Network_Access.Network_Access_Limits_ID
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
