import argparse
import random
import string
from datetime import datetime, timedelta
from esimport.mappings.account import AccountMapping

parser = argparse.ArgumentParser()
parser.add_argument('-n', help='Number of demo data')
args = parser.parse_args()
number = int(args.n)

am = AccountMapping()
am.setup()

# A list of dates spread out in past 10 months from now
dt = datetime.now()
dt_list = []
for i in range(10):
    dt = dt - timedelta(days=31)
    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    dt_list.append(dt_str)
dt_list = list(reversed(dt_list))

# SQL query for inserting account related demo data
account_sql = """INSERT INTO [dbo].[Zone_Plan_Account]
        (Member_ID, Zone_Plan_ID, Purchase_Price, 
        Purchase_Price_Currency_ID, Network_Access_Limits_ID, 
        Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, 
        Date_Created_UTC,Date_Modified_UTC, PMS_Charge_ID, 
        Zone_Plan_Account_Status_ID, Upsell_Zone_Plan_Account_ID, Purchase_Org_ID)
        VALUES 
        (1, 1, 12.95, 1, 1, 1, '34-C0-59-D8-31-08', '2014-01-04 07:38:24.370', 
        '{}', '2018-04-05 10:31:46.768',
        1, 1, NULL, 1)"""

# SQL queries for inserting session related demo data
radius_acct_event_sql = """INSERT INTO Radius.dbo.Radius_Acct_Event
                    (Session_ID, Radius_Event_ID)
                    VALUES
                    ('{session_id}', '{radius_event_id}')"""
radius_stop_event_sql = """INSERT INTO Radius.dbo.Radius_Stop_Event
                        (Radius_Acct_Event_ID, Acct_Terminate_Cause, 
                        Acct_Session_Time, Acct_Output_Octets, 
                        Acct_Input_Octets)
                        VALUES
                        ('{radius_event_id}', 1, 9354, 43787611, 24313077)"""
radius_event_history_sql = """INSERT INTO Radius.dbo.Radius_Event_History(User_Name, 
                            Organization_ID, Member_ID, NAS_Identifier, Called_Station_Id, 
                            VLAN, Calling_Station_Id, Date_UTC)
                            VALUES
                            ('username{user_id}', 1, 1, 'E8-1D-A8-20-1B-88', 
                            'E8-1D-A8-20-1B-88:WOODSPRING_GUEST', 95, 
                            '5C-52-1E-60-6A-17', '{date_utc}')"""
radius_event_sql = """INSERT INTO Radius.dbo.Radius_Event (User_Name, 
                    Member_ID, Organization_ID, Date_UTC, NAS_Identifier, 
                    Called_Station_Id, VLAN, Calling_Station_Id)
                    VALUES
                    ('username{user_id}', 1, 1, 
                    '{date_utc}', 
                    'E8-1D-A8-20-1B-88', 'E8-1D-A8-20-1B-88:WOODSPRING_GUEST', 
                    95, '5C-52-1E-60-6A-17')"""

# SQL query for inserting device related demo data
client_tracking_sql = """INSERT INTO [dbo].[Client_Tracking] 
                        (Date, Organization_ID, IP_Address, 
                        MAC_Address, Platform_Type_ID, Browser_Type_ID, 
                        Member_ID, Client_Device_Type_ID, User_Agent_Raw)
                        VALUES
                        ('{date_utc}', 1, '172.168.1.11', 
                        '62:8D:2F:6A:F0:78', 1, 1, 1, 1, 
                        'Chrome/60.0.3112.113')"""

letters = string.ascii_uppercase
dt_now = datetime.now()

counter = 1

for dt in dt_list:
    for i in range(number//10):
        # Zone_Plan_Account sql
        am.model.execute(account_sql.format(dt)).commit()
        # Radius_Acct_Event sql
        random_str = ''.join(random.choice(letters) for _ in range(10))
        sql = radius_acct_event_sql.format(session_id=random_str, radius_event_id=counter)
        am.model.execute(sql).commit()
        # Radius_Stop_Event sql
        sql = radius_stop_event_sql.format(radius_event_id=counter)
        am.model.execute(sql).commit()
        # Radius_Event_History sql
        sql = radius_event_history_sql.format(user_id=counter, date_utc=dt)
        am.model.execute(sql).commit()
        # Radius_Event sql
        sql = radius_event_sql.format(user_id=counter, date_utc=dt)
        am.model.execute(sql).commit()
        # Client_Tracking sql
        sql = client_tracking_sql.format(date_utc=dt)
        am.model.execute(sql).commit()
        counter += 1

print("Done!")
