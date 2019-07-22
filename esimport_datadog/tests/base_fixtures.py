from datetime import datetime
from datetime import timezone

import pytest
from elasticsearch import Elasticsearch


@pytest.fixture()
def local_es():
    return Elasticsearch("localhost:9200")


@pytest.fixture()
def empty_es_indexes(local_es):
    indexes_names = local_es.indices.get_settings(index="*").keys()
    for index_name in indexes_names:
        local_es.indices.delete(index=index_name)

    yield

    indexes_names = local_es.indices.get_settings(index="*").keys()
    for index_name in indexes_names:
        local_es.indices.delete(index=index_name)


@pytest.fixture
def sample_record(local_es):
    # local_es.indices.put_mapping(
    #     index="test-index",
    #     doc_type="accounts-current",
    #     body=indicides_definition.account_mapping,
    # )

    record_datetime = datetime.now(tz=timezone.utc)

    doc = {
        "ID": 1,
        "Name": "cc-9886_79C66442-7E37-4B0D-B512-E7D1C9EDFC11",
        "MemberNumber": "1",
        "Status": "Status",
        "ServiceArea": "FF-471-20",
        "Price": 1,
        "PurchaseMacAddress": "AA-BB-CC-DD-EE-FF",
        "Activated": record_datetime,
        "Created": record_datetime,
        "DateModifiedUTC": record_datetime,
        "ServicePlan": "basic day",
        "ServicePlanNumber": "basic_day_01",
        "UpCap": 1236,
        "DownCap": 4196,
        "NetworkAccessStartDateUTC": record_datetime,
        "NetworkAccessEndDateUTC": record_datetime,
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
    }
    local_es.index(index="test-index", doc_type="accounts-current", id=1, body=doc)

    yield

    local_es.delete(index="test-index", doc_type="accounts-current", id=1)
