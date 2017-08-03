import pprint
import logging

from elasticsearch import Elasticsearch
from esimport import settings


es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)

logger = logging.getLogger(__name__)

class new_index():
    es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)

    def __init__(self):
        super(new_index, self).__init__()
        self.step_size = settings.ES_BULK_LIMIT
        self.pp = pprint.PrettyPrinter(indent=2, depth=10)  # pragma: no cover
        self.db_wait = settings.DATABASE_CALLS_WAIT

    def setup(self):
        logger.debug("Setting up ES connection")
        # defaults to localhost:9200
        self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)

    def setupindex(self):

        request_body = {
            "settings" : {
                    "number_of_shards" : 24,
                    "number_of_replicas" : 1
            }
        }

        property_mapping = {
                    "properties": {
                        "Name": {"type": "text"},
                        "Number": {"type": "keyword", "ignore_above": 12},
                        "GuestRooms": {"type": "integer"},
                        "MeetingRooms": {"type": "integer"},
                        "Lite": {"type": "boolean"},
                        "Pan": {"type": "boolean"},
                        "Status": {"type": "keyword", "ignore_above": 16},
                        "CreatedUTC": {"type": "date"},                    "GoLiveUTC": {"type": "date"},
                        "TimeZone": {"type": "keyword", "ignore_above": 32},
                        "Provider": {"type": "keyword", "ignore_above": 128},
                        "ServiceAreas": {"type": "keyword"},
                        "CorporateBrand": {"type": "keyword", "ignore_above": 128},
                        "Brand": {"type": "keyword", "ignore_above": 64},
                        "OwnershipGroup": {"type": "keyword", "ignore_above": 128},
                        "MARSHA_Code": {"type": "keyword", "ignore_above": 64},
                        "ExtPropId": {"type": "keyword", "ignore_above": 64},
                        "Country": {"type": "keyword", "ignore_above": 64},
                        "Region": {"type": "keyword", "ignore_above": 64},
                        "SubRegion": {"type": "keyword", "ignore_above": 64},
                        "ZoneType": {"type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 128
                                }
                             }
                        },
                        "TaxRate": {"type": "float"}
                     }
        }

        device_mapping = {
                    "properties": {
                      "Browser": {  "type": "keyword",  "ignore_above": 32 } ,
                      "DateLocal": { "type": "date" },
                      "DateUTC": { "type": "date" },
                      "IP": { "type": "keyword", "ignore_above": 56 },
                      "MAC": { "type": "keyword", "ignore_above": 18 },
                      "Platform": { "type": "keyword", "ignore_above": 32 },
                      "ZoneType": {"type": "text",
                        "fields": {
                          "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                          }}},
                      "PropertyName": {"type": "text"},
                      "PropertyNumber": {"type": "keyword", "ignore_above": 12},
                      "CorporateBrand": {"type": "keyword","ignore_above": 128 },
                      "Brand":{ "type": "keyword", "ignore_above": 64},
                      "OwnershipGroup": {"type": "keyword","ignore_above": 128},
                      "Provider": {"type": "keyword", "ignore_above":128},
                      "MARSHA_Code": {"type": "keyword","ignore_above": 64 },
                      "ExtPropId": {"type": "keyword", "ignore_above": 64},
                      "Country": {"type": "keyword", "ignore_above": 64},
                      "Region": {"type": "keyword", "ignore_above": 64},
                      "SubRegion": {"type": "keyword", "ignore_above": 64},
                      "TimeZone": {"type": "keyword", "ignore_above": 32},
                      "TaxRate": {"type":"float"}
                }
        }

        account_mapping = {
                     "properties": {
                          "Name": { "type": "text" },
                          "Status": {"type": "keyword", "ignore_above":16},
                          "ServiceArea": {"type": "keyword", "ignore_above":12},
                          "Price": {"type": "float"},
                          "PurchaseMacAddress": {"type": "keyword", "ignore_above":18 },
                          "Activated": {"type": "date"},
                          "ActivatedLocal": {"type": "date"},
                          "Created": {"type": "date"},
                          "CreatedLocal": { "type": "date" },
                          "ServicePlan": {"type": "text",
                            "fields": {
                              "keyword": {
                                "type": "keyword",
                                "ignore_above": 128
                              }}},
                          "ServicePlanNumber": {"type": "keyword", "ignore_above": 64},
                          "UpCap": {"type": "integer"},
                          "DownCap": {"type": "integer"},
                          "PayMethod": {"type": "keyword"},
                          "Currency": {"type": "keyword", "ignore_above": 8},
                          "CreditCardNumber": {"type": "integer"},
                          "CardType": {"type": "keyword", "ignore_above": 16},
                          "LastName": {"type": "text"},
                          "RoomNumber": {"type": "keyword"},
                          "DiscountCode": {"type": "text",
                            "fields": {
                              "keyword": {
                                "type": "keyword",
                                "ignore_above": 128
                              }}},
                          "ConnectCode": {
                            "type": "text",
                            "fields": {
                              "keyword": {
                                "type": "keyword",
                                "ignore_above": 128
                              } }},
                          "ConsumableTime": {"type": "integer"},
                          "ConsumableUnit": {"type": "keyword", "ignore_above": 16 },
                          "SpanTime": {"type": "integer"},
                          "SpanUnit": {"type": "keyword", "ignore_above": 16},
                          "ConnectCode": {"type": "text"},
                          "ZoneType": {"type": "text",
                            "fields": {
                              "keyword": {
                                "type": "keyword",
                                "ignore_above": 128
                              }}},
                          "PropertyName": {"type": "text"},
                          "PropertyNumber": {"type": "keyword", "ignore_above": 12},
                          "CorporateBrand": {"type": "keyword","ignore_above": 128 },
                          "Brand":{ "type": "keyword", "ignore_above": 64},
                          "OwnershipGroup": {"type": "keyword","ignore_above": 128},
                          "Provider": {"type": "keyword", "ignore_above":128},
                          "MARSHA_Code": {"type": "keyword","ignore_above": 64 },
                          "ExtPropId": {"type": "keyword", "ignore_above": 64},
                          "Country": {"type": "keyword", "ignore_above": 64},
                          "Region": {"type": "keyword", "ignore_above": 64},
                          "SubRegion": {"type": "keyword", "ignore_above": 64},
                          "TimeZone": {"type": "keyword", "ignore_above": 32},
                          "TaxRate": {"type":"float"}
                     }
        }

        session_mapping = {
                     "properties": {
                          "UserName": {"type": "text",
                            "fields": {
                              "keyword": {
                                "type": "keyword",
                                "ignore_above": 128
                              }}},
                          "ServiceArea": {"type": "keyword", "ignore_above":12},
                          "VLAN": {"type": "integer"},
                          "LogoutTime": {"type": "date"},
                          "LogoutTimeLocal": {"type": "date"},
                          "LoginTime": {"type": "date"},
                          "LoginTimeLocal": {"type": "date"},
                          "BytesIn": {"type": "long"},
                          "MacAddress": {"type": "keyword", "ignore_above":18 },
                          "BytesOut": {"type": "long"},
                          "SessionID": {"type": "text",
                            "fields": {
                              "keyword": {
                                "type": "keyword",
                                "ignore_above": 128
                              }}},
                          "CalledStation": {"type": "text",
                            "fields": {
                              "keyword": {
                                "type": "keyword",
                                "ignore_above": 128
                              }}},
                          "Name": {"type": "text",
                            "fields": {
                              "keyword": {
                                "type": "keyword",
                                "ignore_above": 128
                              }}},
                          "TerminationReason": {"type": "text",
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
                          "SessionLength": {"type": "integer"},
                          "ZoneType": {"type": "text",
                            "fields": {
                              "keyword": {
                                "type": "keyword",
                                "ignore_above": 128
                              }}},
                          "PropertyName": {"type": "text"},
                          "PropertyNumber": {"type": "keyword", "ignore_above": 12},
                          "CorporateBrand": {"type": "keyword","ignore_above": 128 },
                          "Brand":{ "type": "keyword", "ignore_above": 64},
                          "OwnershipGroup": {"type": "keyword","ignore_above": 128},
                          "Provider": {"type": "keyword", "ignore_above":128},
                          "MARSHA_Code": {"type": "keyword","ignore_above": 64 },
                          "ExtPropId": {"type": "keyword", "ignore_above": 64},
                          "Country": {"type": "keyword", "ignore_above": 64},
                          "Region": {"type": "keyword", "ignore_above": 64},
                          "SubRegion": {"type": "keyword", "ignore_above": 64},
                          "TimeZone": {"type": "keyword", "ignore_above": 32},
                          "TaxRate": {"type":"float"}
                     }
        }

        es.indices.create(index="elevenos", body=request_body)
        es.indices.refresh(index="elevenos")
        es.indices.put_mapping(index="elevenos", doc_type="property", body=property_mapping)
        es.indices.put_mapping(index="elevenos", doc_type="device", body=device_mapping)
        es.indices.put_mapping(index="elevenos", doc_type="account", body=account_mapping)
        es.indices.put_mapping(index="elevenos", doc_type="session", body=session_mapping)