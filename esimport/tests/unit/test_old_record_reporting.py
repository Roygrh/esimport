from datetime import datetime, timedelta
from esimport.core import Record
from esimport.syncers import SessionsSyncer

# We're choosing SessionsSyncer on random.
# as the function we're going to test
# is independent of any type of specific syncer

def test_report_old_record():
    ss = SessionsSyncer()
    ss.setup()

    # Check if it reports old records
    record_date = datetime(2000,1,2)
    record = Record(
                    ss.get_target_elasticsearch_index(record_date),
                    ss.record_type,
                    {
                        "ID": "1",
                        "Radius_Accounting_Event_ID": "2652371592",
                        "Acct_Terminate_Cause": 1,
                        "Acct_Session_Time": 9354,
                        "Acct_Output_Octets": "43787611",
                        "Acct_Input_Octets": "24313077"
                    },
                    record_date
                    )
    assert ss.report_old_record(record) == True

    # Check no reports on record for current month
    record_date = datetime.utcnow()
    record = Record(
                    ss.get_target_elasticsearch_index(record_date),
                    ss.record_type,
                    {
                        "ID": "1",
                        "Radius_Accounting_Event_ID": "2652371592",
                        "Acct_Terminate_Cause": 1,
                        "Acct_Session_Time": 9354,
                        "Acct_Output_Octets": "43787611",
                        "Acct_Input_Octets": "24313077"
                    },
                    record_date
                    )
    assert ss.report_old_record(record) == None

    # Edge case test.
    # Checks taht syncert class that stores in variable current_date value for pervious month
    # will not report record once date and therefore index name will change name to new month
    # Example: end of months i.e 2022-01-30:23:59:59
    # I.e. it expectedt that class will detect that `current_date` should be updated, and condition will not trigger
    # report
    now = datetime.utcnow()
    record_date = datetime(now.year,now.month,1) # record date first day of current month

    # Syncer class store current_date stores outdated date (previous day)
    ss.current_date = (record_date - timedelta(days=1)).strftime("%Y-%m")
    record = Record(
                    ss.get_target_elasticsearch_index(record_date),
                    ss.record_type,
                    {
                        "ID": "1",
                        "Radius_Accounting_Event_ID": "2652371592",
                        "Acct_Terminate_Cause": 1,
                        "Acct_Session_Time": 9354,
                        "Acct_Output_Octets": "43787611",
                        "Acct_Input_Octets": "24313077"
                    },
                    record_date
                    )
    assert ss.report_old_record(record) == None
