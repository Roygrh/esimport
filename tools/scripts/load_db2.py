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


mssql_con = MSSQLConnection()

start_date = datetime(2019, 1, 1, 1, 1, 1, 123456)


mssql_con.execute(create_conference_sql(10, start_date))
