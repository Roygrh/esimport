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


def create_session_sql(n, start_date):
    def get_last_id(table_name):
        (last_id,) = mssql_con.execute(
            f"Select IDENT_CURRENT('{table_name}')"
        ).fetchone()
        return last_id

    # SQL queries for inserting session related demo data
    radius_acct_event_sql = """INSERT INTO Radius.dbo.Radius_Accounting_Event
                        (Session_ID, Radius_Accounting_Event_ID)
                        VALUES"""
    radius_acct_event_column = """('{session_id}', '{radius_event_id}')"""

    radius_stop_event_sql = """INSERT INTO Radius.dbo.Radius_Accounting_Stop_Event
                            ( Radius_Accounting_Event_ID, Acct_Terminate_Cause, 
                            Acct_Session_Time, Acct_Output_Octets, 
                            Acct_Input_Octets)
                            VALUES"""
    radius_stop_event_column = (
        """('{radius_act_event_id}', 1, 9354, 43787611, 24313077)"""
    )

    radius_event_history_sql = """INSERT INTO Radius.dbo.Radius_Accounting_Event_History (User_Name, 
                                Organization_ID, Member_ID, NAS_Identifier, Called_Station_Id, 
                                VLAN, Calling_Station_Id, Date_UTC)
                                VALUES"""
    radius_event_history_column = """('username{user_id}', 1, 1, 'E8-1D-A8-20-1B-88', 
                                'E8-1D-A8-20-1B-88:WOODSPRING_GUEST', 95, 
                                '5C-52-1E-60-6A-17', cast(N'{date_utc}' AS DateTime2) )"""

    radius_event_sql = """INSERT INTO Radius.dbo.Radius_Accounting_Event ( User_Name, 
                        Member_ID, Organization_ID, Date_UTC, NAS_Identifier, 
                        Called_Station_Id, VLAN, Calling_Station_Id)
                        VALUES"""
    radius_event_column = """('username{user_id}', 1, 1, 
                        cast(N'{date_utc}' AS DateTime2),  
                        'E8-1D-A8-20-1B-88', 'E8-1D-A8-20-1B-88:WOODSPRING_GUEST', 
                        95, '5C-52-1E-60-6A-17')"""

    records_radius_acct = []
    records_radius_stop = []
    records_radius_history = []
    records_radius_events = []

    next_radius_event_id = get_last_id("Radius.dbo.Radius_Accounting_Event")
    next_radius_act_event_id = get_last_id("Radius.dbo.Radius_Accounting_Event")
    next_radius_stop_event_id = get_last_id("Radius.dbo.Radius_Accounting_Stop_Event")

    id = 0
    for i in range(n):
        for x in range(2):
            session_id = f"{id:010d}"
            records_radius_acct.append(
                radius_acct_event_column.format(
                    id=id, session_id=session_id, radius_event_id=next_radius_event_id
                )
            )
            records_radius_stop.append(
                radius_stop_event_column.format(
                    radius_act_event_id=next_radius_act_event_id
                )
            )
            records_radius_history.append(
                radius_event_history_column.format(user_id=id, date_utc=start_date)
            )
            records_radius_events.append(
                radius_event_column.format(user_id=id, date_utc=start_date)
            )
            id += 1
            next_radius_act_event_id += 1

            next_radius_stop_event_id += 1
            next_radius_event_id += 1
        start_date += timedelta(days=1)

    mssql_con.execute(" ".join([radius_acct_event_sql, ",".join(records_radius_acct)]))
    mssql_con.execute(" ".join([radius_stop_event_sql, ",".join(records_radius_stop)]))
    mssql_con.execute(
        " ".join([radius_event_history_sql, ",".join(records_radius_history)])
    )
    mssql_con.execute(" ".join([radius_event_sql, ",".join(records_radius_events)]))


def create_device_sql(n, start_date):
    # SQL query for inserting device related demo data
    client_tracking_sql = """
INSERT INTO [dbo].[Client_Tracking] (
Date, 
Organization_ID, 
IP_Address, 
MAC_Address, 
Platform_Type_ID, 
Browser_Type_ID, 
Member_ID, 
Client_Device_Type_ID, 
User_Agent_Raw)
VALUES"""
    client_tracking_column = """(
cast(N'{date_utc}' AS DateTime2), 
1, 
'172.168.1.11', 
'62:8D:2F:6A:F0:78', 
1, 
1, 
1, 
1, 
'Chrome/60.0.3112.113')"""

    records = []
    id = 0
    for i in range(n):
        for x in range(2):
            records.append(client_tracking_column.format(date_utc=start_date))
            id += 1
        start_date += timedelta(days=1)

    final_sql = " ".join([client_tracking_sql, ",".join(records)])
    return final_sql


def create_account_sql(n, start_date):
    # SQL query for inserting account related demo data

    account_sql = """
INSERT INTO [dbo].[Zone_Plan_Account] (
Member_ID, 
Zone_Plan_ID, 
Purchase_Price, 
Purchase_Price_Currency_ID, 
Network_Access_Limits_ID, 
Payment_Method_ID, 
Purchase_MAC_Address, 
Activation_Date_UTC, 
Date_Created_UTC,
Date_Modified_UTC, 
PMS_Charge_ID, 
Zone_Plan_Account_Status_ID, 
Upsell_Zone_Plan_Account_ID, 
Purchase_Org_ID
)
VALUES"""
    column = """(
1, 
1, 
12.95, 
1, 
1, 
1, 
'34-C0-59-D8-31-08', 
cast(N'{date_activated_utc}' AS DateTime2),
cast(N'{date_created_utc}' AS DateTime2),
cast(N'{date_modified_utc}' AS DateTime2), 
1, 
1, 
NULL, 
1
)"""

    records = []
    id = 0
    for i in range(n):
        for x in range(2):
            records.append(
                column.format(
                    date_activated_utc=start_date,
                    date_created_utc=start_date,
                    date_modified_utc=start_date,
                )
            )
            id += 1
        start_date += timedelta(days=1)

    final_sql = " ".join([account_sql, ",".join(records)])
    return final_sql


mssql_con = MSSQLConnection()

start_date = datetime(2019, 1, 1, 1, 1, 1, 123456)

mssql_con.execute(create_conference_sql(10, start_date))
mssql_con.execute(create_property_sql(10, start_date))
create_session_sql(10, start_date)  # execute many sql statement inside
mssql_con.execute(create_device_sql(10, start_date))
mssql_con.execute(create_account_sql(10, start_date))
