import argparse
import random
import signal
import string
import time
from datetime import datetime, timedelta

import click

from esimport.mappings.account import AccountMapping

state = {'counter': 0}  # placed a dict here instead of a gloabl int variable, since dict are mutable while ints are not
start_time = time.time()


def exit_():
    count = state.get('counter')
    click.secho(f"\nDone! fed the DB with {count} records", fg="green")
    end_time = time.time() - start_time
    click.secho(f"\nTime took {end_time:.2f} sec", fg="green")
    exit(0)


signal.signal(signal.SIGINT, lambda sig, frame: exit_())

am = AccountMapping()
am.setup()

# A list of dates spread out in past 10 months from now
dt = datetime.now()
dt_list = []
for _ in range(10):
    dt = dt - timedelta(days=31)
    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    dt_list.append(dt_str)
dt_list = list(reversed(dt_list))

letters = string.ascii_uppercase


def random_org_number():
    digits = string.digits
    x = ''.join(random.choice(letters) for _ in range(2))
    x += '-' + ''.join(random.choice(digits) for _ in range(3))
    x += '-' + ''.join(random.choice(digits) for _ in range(2))
    return x


def create_account_sql(n, dt):
    # SQL query for inserting account related demo data
    column = """(1, 1, 12.95, 1, 1, 1, '34-C0-59-D8-31-08', '2014-01-04 07:38:24.370', 
            '{}', '2018-04-05 10:31:46.768', 1, 1, NULL, 1)"""

    account_sql = """INSERT INTO [dbo].[Zone_Plan_Account]
            (Member_ID, Zone_Plan_ID, Purchase_Price, 
            Purchase_Price_Currency_ID, Network_Access_Limits_ID, 
            Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, 
            Date_Created_UTC,Date_Modified_UTC, PMS_Charge_ID, 
            Zone_Plan_Account_Status_ID, Upsell_Zone_Plan_Account_ID, Purchase_Org_ID)
            VALUES"""

    for i in range(n, n+10):
        account_sql += column.format(dt)
        if i < n+9:
            account_sql += ','

    return [account_sql]


def create_session_sql(n, dt):
    # SQL queries for inserting session related demo data
    radius_acct_event_sql = """INSERT INTO Radius.dbo.Radius_Accounting_Event
                        (Session_ID, Radius_Accounting_Event_ID)
                        VALUES"""
    radius_acct_event_column = """('{session_id}', '{radius_event_id}')"""

    radius_stop_event_sql = """INSERT INTO Radius.dbo.Radius_Accounting_Stop_Event
                            (Radius_Accounting_Event_ID, Acct_Terminate_Cause, 
                            Acct_Session_Time, Acct_Output_Octets, 
                            Acct_Input_Octets)
                            VALUES"""
    radius_stop_event_column = """('{radius_event_id}', 1, 9354, 43787611, 24313077)"""

    radius_event_history_sql = """INSERT INTO Radius.dbo.Radius_Accounting_Event_History(User_Name, 
                                Organization_ID, Member_ID, NAS_Identifier, Called_Station_Id, 
                                VLAN, Calling_Station_Id, Date_UTC)
                                VALUES"""
    radius_event_history_column = """('username{user_id}', 1, 1, 'E8-1D-A8-20-1B-88', 
                                'E8-1D-A8-20-1B-88:WOODSPRING_GUEST', 95, 
                                '5C-52-1E-60-6A-17', '{date_utc}')"""

    radius_event_sql = """INSERT INTO Radius.dbo.Radius_Accounting_Event (User_Name, 
                        Member_ID, Organization_ID, Date_UTC, NAS_Identifier, 
                        Called_Station_Id, VLAN, Calling_Station_Id)
                        VALUES"""
    radius_event_column = """('username{user_id}', 1, 1, 
                        '{date_utc}', 
                        'E8-1D-A8-20-1B-88', 'E8-1D-A8-20-1B-88:WOODSPRING_GUEST', 
                        95, '5C-52-1E-60-6A-17')"""

    for i in range(n, n+10):
        random_str = ''.join(random.choice(letters) for _ in range(10))
        radius_acct_event_sql += radius_acct_event_column.format(session_id=random_str, radius_event_id=i)
        radius_stop_event_sql += radius_stop_event_column.format(radius_event_id=i)
        radius_event_history_sql += radius_event_history_column.format(user_id=i, date_utc=dt)
        radius_event_sql += radius_event_column.format(user_id=i, date_utc=dt)
        if i < n+9:
            radius_acct_event_sql += ','
            radius_stop_event_sql += ','
            radius_event_history_sql += ','
            radius_event_sql += ','

    return [radius_acct_event_sql, radius_stop_event_sql,
            radius_event_history_sql, radius_event_sql]


def create_device_sql(n, dt):
    # SQL query for inserting device related demo data
    client_tracking_sql = """INSERT INTO [dbo].[Client_Tracking] 
                            (Date, Organization_ID, IP_Address, 
                            MAC_Address, Platform_Type_ID, Browser_Type_ID, 
                            Member_ID, Client_Device_Type_ID, User_Agent_Raw)
                            VALUES"""
    client_tracking_column = """('{date_utc}', 1, '172.168.1.11', 
                            '62:8D:2F:6A:F0:78', 1, 1, 1, 1, 
                            'Chrome/60.0.3112.113')"""

    for i in range(n, n+10):
        client_tracking_sql += client_tracking_column.format(date_utc=dt)
        if i < n+9:
            client_tracking_sql += ','

    return [client_tracking_sql]


def create_property_sql(n, dt):
    property_sql = """INSERT INTO [dbo].[Organization] (Number, Name, Display_Name, Guest_Room_Count, Meeting_Room_Count, 
                    Is_Lite, Pan_Enabled,Date_Added_UTC, Org_Status_ID, Time_Zone_ID, Org_Category_Type_ID, 
                    Contact_ID, Property_Code) VALUES"""
    column = """('{org_num}', 'organization{org_id}', 'some display name 1', 1, 1, 0, 0, 
                '{date_utc}', 1, 1, 4, 1, 'PropertyCode1')"""
    for i in range(n, n+10):
        org_num = random_org_number()
        property_sql += column.format(org_num=org_num, org_id=i, date_utc=dt)
        if i < n+9:
            property_sql += ','

    return [property_sql]


def create_conference_sql(n, dt):
    conference_sql = """INSERT INTO [dbo].[Scheduled_Access](Event_Name, 
                        Date_Created_UTC, Actual_User_Count, Total_Input_Bytes, 
                        Total_Output_Bytes, Total_Session_Time, Member_ID, 
                        Organization_ID, Network_Access_ID) VALUES"""
    column = """('Event_Name{id}', '{date_utc}', '12', 
                '128369818', '91276953', '1213', 1, 1, 1)"""
    for i in range(n, n+10):
        conference_sql += column.format(id=i, date_utc=dt)
        if i < n+9:
            conference_sql += ','

    return [conference_sql]


@click.command()
@click.option('-n', '--number', type=int, help='Number of records to feed the DB with.')
@click.option('-t', '--doc_type', type=click.Choice(['account', 'session',
                                                     'device', 'property',
                                                     'conference']), help='Name of the doc type')
@click.option('--nostop', is_flag=True, help='Continuously feed the DB.')
def feed(number, doc_type, nostop):

    if number and nostop:
        click.secho("-n and --nostop are mutually exclusive.", fg="red", err=True)
        exit(1)

    if not number and not nostop or not doc_type:
        click.secho("Either -n or --nostop and --doc_type option has to be given.", fg="red", err=True)
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        exit(1)

    click.echo("Inserting demo data...")
    n = 0
    while True:
        for dt in dt_list:
            # Zone_Plan_Account sql
            if doc_type == 'account':
                account_sql_list = create_account_sql(n, dt)
                for account_sql in account_sql_list:
                    am.model.execute(account_sql).commit()
            elif doc_type == 'session':
                session_sql_list = create_session_sql(n, dt)
                for session_sql in session_sql_list:
                    am.model.execute(session_sql).commit()
            elif doc_type == 'device':
                device_sql_list = create_device_sql(n, dt)
                for device_sql in device_sql_list:
                    am.model.execute(device_sql).commit()
            elif doc_type == 'property':
                property_sql_list = create_property_sql(n, dt)
                for property_sql in property_sql_list:
                    am.model.execute(property_sql).commit()
            elif doc_type == 'conference':
                conference_sql_list = create_conference_sql(n, dt)
                for conference_sql in conference_sql_list:
                    am.model.execute(conference_sql).commit()

            state['counter'] += 10
            n += 10

            if number and state['counter'] >= number:
                break

        if not nostop and state['counter'] >= number:
            break
        
        time.sleep(1)
        
    exit_()


if __name__ == "__main__":
    feed()
