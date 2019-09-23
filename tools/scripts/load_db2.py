from esimport import settings
from esimport.connectors.mssql import MsSQLConnector
from datetime import datetime
from datetime import timedelta


class MSSQLConnection:
    def __init__(self):
        self.db_wait = settings.DATABASE_CALLS_WAIT
        self.db_conn_reset_limit = settings.DATABASE_CONNECTION_RESET_LIMIT
        self.db_record_limit = settings.DATABASE_RECORD_LIMIT
        self.conn = MsSQLConnector()

    def execute(self, query, *args):
        # As Eleven uses availability groups, we can't specify db name in DSN string. Rather we have
        # to send an USE command. The API in the pyodbc connector doesn't allow multiple statements
        # in a SQL call. As it remembers context, it's used before every transaction.
        self.conn.cursor.execute("USE Eleven_OS")
        return self.conn.cursor.execute(query, list(args))


def create_conference_sql(n, start_date):
    conference_sql = """
INSERT INTO [dbo].[Scheduled_Access](
    Event_Name, 
    Date_Created_UTC,
    Actual_User_Count,
    Total_Input_Bytes,
    Total_Output_Bytes,
    Total_Session_Time,
    Member_ID,
    Organization_ID,
    Network_Access_ID) 
VALUES"""
    column = """('Event_Name{id}', cast(N'{date_utc}' AS DateTime2), '12', '128369818', '91276953', '1213', 1, 1, 1)"""

    records = []
    id = 0
    for i in range(n):
        for x in range(2):
            records.append(column.format(id=id, date_utc=start_date))
            id += 1
        start_date += timedelta(days=1)

    final_sql = " ".join([conference_sql, ",".join(records)])
    return final_sql


def create_property_sql(n, start_date):
    property_sql = """
INSERT INTO [dbo].[Organization] (
Number, 
Name, 
Display_Name, 
Guest_Room_Count, 
Meeting_Room_Count, 
Is_Lite, 
Pan_Enabled,
Date_Added_UTC, 
Org_Status_ID, 
Time_Zone_ID, 
Org_Category_Type_ID, 
Contact_ID, 
Property_Code) VALUES"""
    column = """(
'FF-471-{org_num:02d}', 
'organization{id}', 
'some display name 1', 
1, 
1, 
0, 
0, 
cast(N'{date_utc}' AS DateTime2), 
1, 
1, 
3, 
1, 
'PropertyCode1'
)"""

    records = []
    id = 0
    for i in range(n):
        for x in range(2):
            records.append(column.format(id=id, date_utc=start_date, org_num=id))
            id += 1
        start_date += timedelta(days=1)

    final_sql = " ".join([property_sql, ",".join(records)])
    return final_sql


mssql_con = MSSQLConnection()

start_date = datetime(2019, 1, 1, 1, 1, 1, 123456)


mssql_con.execute(create_conference_sql(10, start_date))
mssql_con.execute(create_property_sql(10, start_date))
