import datetime
from decimal import Decimal

import pytest


@pytest.fixture()
def sample_account():
    return {
        "expected_index": "accounts",
        "expected_alias": "accounts-current",
        "doc": {
            "ID": 1,
            "Name": "cc-9886_79C66442-7E37-4B0D-B512-E7D1C9EDFC11",
            "MemberNumber": "1",
            "Status": "Status",
            "ServiceArea": "FF-471-20",
            "Price": Decimal(12.9500),
            "PurchaseMacAddress": "AA-BB-CC-DD-EE-FF",
            "Activated": datetime.datetime(
                2019, 1, 1, 1, 23, 46, 000000, tzinfo=datetime.timezone.utc
            ),
            "Created": datetime.datetime(
                2019, 1, 1, 1, 23, 45, 000000, tzinfo=datetime.timezone.utc
            ),
            "DateModifiedUTC": datetime.datetime(
                2019, 1, 2, 1, 23, 45, 000000, tzinfo=datetime.timezone.utc
            ),
            "ServicePlan": "basic day",
            "ServicePlanNumber": "basic_day_01",
            "UpCap": 1236,
            "DownCap": 4196,
            "NetworkAccessStartDateUTC": datetime.datetime(
                2019, 1, 1, 1, 24, 46, 000000, tzinfo=datetime.timezone.utc
            ),
            "NetworkAccessEndDateUTC": datetime.datetime(
                2019, 1, 3, 1, 24, 46, 000000, tzinfo=datetime.timezone.utc
            ),
            "PayMethod": "CC",
            "Currency": "AFA",
            "CreditCardNumber": None,
            "CardType": None,
            "LastName": "trava",
            "RoomNumber": "4051",
            "DiscountCode": "DC03",
            "ConsumableTime": None,
            "ConsumableUnit": None,
            "SpanTime": 1,
            "SpanUnit": "Seconds",
            "ConnectCode": None,
            "MarketingContact": None,
            "ZoneType": None,
            "VLAN": 1,
        },
    }


@pytest.fixture()
def sample_device():
    return {
        "expected_index": "devices-2019-01",
        "expected_alias": "devices-current",
        "doc": {
            "ID": 1,
            "DateUTC": datetime.datetime(
                2019, 1, 2, 3, 45, 00, 000000, tzinfo=datetime.timezone.utc
            ),
            "IP": "172.168.1.11",
            "MAC": "62:8D:2F:6A:F0:78",
            "UserAgentRaw": "Chrome/60.0.3112.113",
            "Device": "Client Device Type 1",
            "Platform": "Platform 1",
            "Browser": "Chrome",
            "Username": "cc-9886_79C66442-7E37-4B0D-B512-E7D1C9EDFC11",
            "MemberID": 1,
            "MemberNumber": "1",
            "ServiceArea": "FF-471-20",
            "ZoneType": None,
        },
    }


@pytest.fixture()
def sample_session():
    return {
        "expected_index": "sessions-2019-01",
        "expected_alias": "sessions-current",
        "doc": {
            "ID": 1,
            "ServiceArea": "FF-471-20",
            "ZoneType": None,
            "UserName": "username1",
            "Name": "cc-9886_79C66442-7E37-4B0D-B512-E7D1C9EDFC11",
            "MemberNumber": "1",
            "NasIdentifier": "E8-1D-A8-20-1B-88",
            "CalledStation": "E8-1D-A8-20-1B-88:WOODSPRING_GUEST",
            "VLAN": 95,
            "MacAddress": "5C-52-1E-60-6A-17",
            "LoginTime": datetime.datetime(
                2019, 1, 1, 3, 45, 00, 000000, tzinfo=datetime.timezone.utc
            ),
            "LogoutTime": datetime.datetime(
                2019, 1, 2, 3, 45, 00, 000000, tzinfo=datetime.timezone.utc
            ),
            "SessionID": "5B3657A7-331D8000",
            "SessionLength": 9354,
            "BytesOut": 43787611,
            "BytesIn": 24313077,
            "TerminationReason": "User-Request",
            "ServicePlan": "basic day",
        },
    }


@pytest.fixture()
def sample_property():
    return {
        "expected_index": "properties",
        "doc": {
            "ID": 1,
            "Owner_Org_ID": 1,
            "Number": "basic_day_01",
            "Name": "basic day",
            "Description": "Description 1",
            "Price": Decimal(5.0000),
            "UpKbs": 1236,
            "DownKbs": 4196,
            "IdleTimeout": 10,
            "ConnectionLimit": 5,
            "RadiusClass": "Rad class 1",
            "GroupBandwidthLimit": "1",
            "Type": "Prepaid",
            "PlanTime": None,
            "PlanUnit": None,
            "LifespanTime": 1,
            "LifespanUnit": "Seconds",
            "CurrencyCode": "AFA",
            "Status": "Testing",
            "OrgCode": "PropertyCode1",
            "DateCreatedUTC": datetime.datetime(
                2019, 1, 2, 3, 45, 00, 000000, tzinfo=datetime.timezone.utc
            ),
            "UpdateTime": datetime.datetime(
                2019, 1, 2, 3, 45, 00, 1, tzinfo=datetime.timezone.utc
            ),
        },
    }


@pytest.fixture()
def sample_conference():
    return {
        "expected_index": "conferences",
        "doc": {
            "ID": 1,
            "Name": "Event_Name1",
            "DateCreatedUTC": datetime.datetime(
                2019, 1, 2, 3, 45, 00, 000000, tzinfo=datetime.timezone.utc
            ),
            "UpdateTime": datetime.datetime(
                2019, 1, 2, 3, 45, 00, 1, tzinfo=datetime.timezone.utc
            ),
            "ServiceArea": "FF-471-20",
            "Code": "cc-9886_79C66442-7E37-4B0D-B512-E7D1C9EDFC11",
            "MemberID": 1,
            "MemberNumber": "1",
            "MemberStatus": "Active",
            "SSID": "SSID1",
            "StartDateUTC": datetime.datetime(
                2019, 1, 2, 3, 50, 00, 000000, tzinfo=datetime.timezone.utc
            ),
            "EndDateUTC": datetime.datetime(
                2019, 1, 3, 4, 50, 00, 000000, tzinfo=datetime.timezone.utc
            ),
            "ConnectionLimit": 5,
            "DownKbs": 4196,
            "UpKbs": 1236,
            "GroupBandwidthLimit": "1",
            "UserCount": 12,
            "TotalInputBytes": 128369818,
            "TotalOutputBytes": 91276953,
            "TotalSessionTime": 1213,
        },
    }
