from faker import Faker
import random
import string
from elasticsearch import Elasticsearch, NotFoundError

faker = Faker()
es = Elasticsearch('https://search-esimport-test-7t44eh5b3x5x7a63eqkrtw7vfy.us-west-2.es.amazonaws.com/')

try:
    es.indices.delete(index=dev.ELASTICSEARCH_INDEX)
except NotFoundError:
    pass

create_index = {
    "settings": {
        "number_of_shards": 24,
        "number_of_replicas": 1
    }
}

session_mapping = {
    "properties": {
        "Brand": {"type": "keyword", "ignore_above": 64},
        "BytesIn": {"type": "long"},
        "BytesOut": {"type": "long"},
        "CalledStation": {"type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 128
                                }}},
        "CorporateBrand": {"type": "keyword", "ignore_above": 128},
        "Country": {"type": "keyword", "ignore_above": 64},
        "ExtPropId": {"type": "keyword", "ignore_above": 64},
        "LoginTime": {"type": "date"},
        "LoginTimeLocal": {"type": "date"},
        "LogoutTime": {"type": "date"},
        "LogoutTimeLocal": {"type": "date"},
        "MARSHA_Code": {"type": "keyword", "ignore_above": 64},
        "MacAddress": {"type": "keyword", "ignore_above": 18},
        "MemberNumber": {"type": "keyword", "ignore_above": 32},
        "Name": {"type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }}},
        "NasIdentifier": {"type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }}},
        "NetworkDeviceType": {"type": "keyword"},
        "OwnershipGroup": {"type": "keyword", "ignore_above": 128},
        "PropertyName": {"type": "text"},
        "PropertyNumber": {"type": "keyword", "ignore_above": 12},
        "Provider": {"type": "keyword", "ignore_above": 128},
        "Region": {"type": "keyword", "ignore_above": 64},
        "ServiceArea": {"type": "keyword", "ignore_above": 12},
        "SessionID": {"type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 128
                            }}},
        "SessionLength": {"type": "integer"},
        "SubRegion": {"type": "keyword", "ignore_above": 64},
        "TaxRate": {"type": "float"},
        "TerminationReason": {"type": "text",
                                "fields": {
                                    "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 128
                                    }}},
        "TimeZone": {"type": "keyword", "ignore_above": 32},
        "UserName": {"type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 128
                            }}},
        "VLAN": {"type": "integer"},
        "ZoneType": {"type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 128
                        }}}
    }
}

es.indices.create(index=dev.ELASTICSEARCH_INDEX, body=create_index)
es.indices.refresh(index=dev.ELASTICSEARCH_INDEX)
es.indices.put_mapping(index=dev.ELASTICSEARCH_INDEX, doc_type="session", body=session_mapping)

# Generate random station ID
def stationID():
    return '-'.join((random.choice(string.ascii_uppercase + string.digits)+random.choice(string.ascii_uppercase + string.digits)) for _ in range(6))


# Generate some random session records
rand_dict = []
for i in range(10000):
    rand_d = {
        'Brand': faker.company(),
        'BytesIn': random.randint(10000, 100000),
        'BytesOut': random.randint(10000, 100000),
        'CalledStation': stationID(),
        'CorporateBrand': '',
        'Country': faker.country(),
        'ExtPropId': '',
        'ID': i+1,
        'LoginTime': faker.past_datetime(start_date="-30d", tzinfo=None),
        'LoginTimeLocal': faker.past_datetime(start_date="-30d", tzinfo=None),
        'LogoutTime': faker.past_datetime(start_date="-30d", tzinfo=None),
        'LogoutTimeLocal': faker.past_datetime(start_date="-30d", tzinfo=None),
        'MARSHA_Code': ''.join(random.choices(string.ascii_uppercase, k=5)),
        'MacAddress': faker.mac_address(),
        'Name': 'em-' + ''.join(random.choices(string.ascii_lowercase, k=4)),
        'NasIdentifier': ''.join(random.choices(string.ascii_uppercase, k=5)),
        'MemberNumber': ''.join(random.choices(string.digits, k=4)) + '-' + 
                        ''.join(random.choices(string.ascii_uppercase, k=2)) + '-' + 
                        ''.join(random.choices(string.digits, k=2)),
        'OwnershipGroup': '',
        'PropertyName': faker.company(),
        'PropertyNumber': ''.join(random.choices(string.ascii_uppercase, k=2)) + '-' +  
                          ''.join(random.choices(string.digits, k=3)) + '-' +
                          ''.join(random.choices(string.digits, k=2)),
        'Provider': faker.company(),
        'Provider_Display_Name': '',
        'Region': '',
        'ServiceArea': ''.join(random.choices(string.ascii_uppercase, k=2)) + '-' +
                       ''.join(random.choices(string.digits, k=3)) + '-' + 
                       ''.join(random.choices(string.digits, k=2)),
        'SessionID': ''.join(random.choices(string.ascii_uppercase+string.digits, k=8)),
        'SessionLength': str(random.randint(500, 2000)),
        'SubRegion': '',
        'TaxRate': '',
        'TerminationReason': '',
        'TimeZone': faker.timezone(),
        'UserName': faker.user_name(),
        'VLAN': str(random.randint(1000, 5000)),
        'ZoneType': "GuestRoom"
    }
    rand_dict.append(rand_d)

for r in rand_dict:
    es.create(index='esrecord', doc_type='session', id=r['ID'], body=r)

print('done!')