################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import pprint
import logging

from elasticsearch import Elasticsearch
from esimport import settings
from constants import (PROD_WEST_ENV, PROD_EAST_ENV)

es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)

logger = logging.getLogger(__name__)


class new_index(object):
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

    def create_index(self, index_name=settings.ES_INDEX):

        if settings.ENVIRONMENT in [PROD_WEST_ENV, PROD_EAST_ENV]:
            create_index = {
                "settings": {
                    "number_of_shards": 24,
                    "number_of_replicas": 1
                }
            }
        else:
            create_index = {
                "settings": {
                    "number_of_shards": 9,
                    "number_of_replicas": 1
                }
            }

        property_mapping = {
            "properties": {
                "ActiveDevices": {"type": "integer"},
                "ActiveMembers": {"type": "integer"},
                "Address": {
                    "type": "nested",
                    "properties": {
                        "AddressLine1": {"type": "text"},
                        "AddressLine2": {"type": "text"},
                        "City": {"type": "keyword"},
                        "Area": {"type": "keyword"},
                        "PostalCode": {"type": "keyword"},
                        "CountryName": {"type": "text"}
                    }
                },
                "Brand": {"type": "keyword", "ignore_above": 64},
                "CorporateBrand": {"type": "keyword", "ignore_above": 128},
                "Country": {"type": "keyword", "ignore_above": 64},
                "CreatedUTC": {"type": "date"},
                "ExtPropId": {"type": "keyword", "ignore_above": 64},
                "GoLiveUTC": {"type": "date"},
                "GuestRooms": {"type": "integer"},
                "Lite": {"type": "boolean"},
                "MARSHA_Code": {"type": "keyword", "ignore_above": 64},
                "MeetingRooms": {"type": "integer"},
                "Name": {"type": "text"},
                "Number": {"type": "keyword", "ignore_above": 12},
                "OwnershipGroup": {"type": "keyword", "ignore_above": 128},
                "Pan": {"type": "boolean"},
                "Provider": {"type": "keyword", "ignore_above": 128},
                "Region": {"type": "keyword", "ignore_above": 64},
                "ServiceAreas": {"type": "keyword"},
                "ServiceAreaObjects": {"type": "nested",
                            "properties": {
                                    "Number": {"type": "keyword" },
                                    "Name": {"type": "text" },
                                    "ZoneType": {"type": "keyword" },
                                    "Hosts": {"type": "nested",
                                           "properties": {
                                                  "NASID": {"type": "keyword" },
                                                  "RadiusNASID": {"type": "text" },
                                                  "HostType": {"type": "text" },
                                                  "VLANRangeStart": {"type": "integer" },
                                                  "VLANRangeEnd": {"type": "integer" },
                                                  "NetIP": {"type": "keyword" }
                                           }
                                    }
                            }
                },
                "Status": {"type": "keyword", "ignore_above": 16},
                "SubRegion": {"type": "keyword", "ignore_above": 64},
                "TaxRate": {"type": "float"},
                "TimeZone": {"type": "keyword", "ignore_above": 32},
                "UpdateTime": {"type": "date"},
                "ZoneType": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                },
            }
        }

        device_mapping = {
            "properties": {
                "Browser": {"type": "keyword", "ignore_above": 32},
                "DateLocal": {"type": "date"},
                "DateUTC": {"type": "date"},
                "IP": {"type": "keyword", "ignore_above": 56},
                "MAC": {"type": "keyword", "ignore_above": 18},
                "Platform": {"type": "keyword", "ignore_above": 32},
                "ZoneType": {"type": "text",
                             "fields": {
                                 "keyword": {
                                     "type": "keyword",
                                     "ignore_above": 128
                                 }}},
                "PropertyName": {"type": "text"},
                "PropertyNumber": {"type": "keyword", "ignore_above": 12},
                "CorporateBrand": {"type": "keyword", "ignore_above": 128},
                "Brand": {"type": "keyword", "ignore_above": 64},
                "OwnershipGroup": {"type": "keyword", "ignore_above": 128},
                "Provider": {"type": "keyword", "ignore_above": 128},
                "MARSHA_Code": {"type": "keyword", "ignore_above": 64},
                "MemberID": {"type": "long"},
                "MemberNumber": {"type": "keyword"},
                "ExtPropId": {"type": "keyword", "ignore_above": 64},
                "Country": {"type": "keyword", "ignore_above": 64},
                "Region": {"type": "keyword", "ignore_above": 64},
                "SubRegion": {"type": "keyword", "ignore_above": 64},
                "TimeZone": {"type": "keyword", "ignore_above": 32},
                "TaxRate": {"type": "float"}
            }
        }

        account_mapping = {
            "properties": {
                "Name": { "type": "text", 
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 128
                            }}},
                "MemberNumber": {"type": "keyword", "ignore_above": 32},
                "Status": {"type": "keyword", "ignore_above": 16},
                "ServiceArea": {"type": "keyword", "ignore_above": 12},
                "Price": {"type": "float"},
                "PurchaseMacAddress": {"type": "keyword", "ignore_above": 18},
                "Activated": {"type": "date"},
                "ActivatedLocal": {"type": "date"},
                "Created": {"type": "date"},
                "CreatedLocal": {"type": "date"},
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
                        }}},
                "MarketingContact": {"type": "text"},
                "ConsumableTime": {"type": "integer"},
                "ConsumableUnit": {"type": "keyword", "ignore_above": 16},
                "SpanTime": {"type": "integer"},
                "SpanUnit": {"type": "keyword", "ignore_above": 16},
                "ZoneType": {"type": "text",
                             "fields": {
                                 "keyword": {
                                     "type": "keyword",
                                     "ignore_above": 128
                                 }}},
                "PropertyName": {"type": "text"},
                "PropertyNumber": {"type": "keyword", "ignore_above": 12},
                "CorporateBrand": {"type": "keyword", "ignore_above": 128},
                "Brand": {"type": "keyword", "ignore_above": 64},
                "OwnershipGroup": {"type": "keyword", "ignore_above": 128},
                "Provider": {"type": "keyword", "ignore_above": 128},
                "MARSHA_Code": {"type": "keyword", "ignore_above": 64},
                "ExtPropId": {"type": "keyword", "ignore_above": 64},
                "Country": {"type": "keyword", "ignore_above": 64},
                "Region": {"type": "keyword", "ignore_above": 64},
                "SubRegion": {"type": "keyword", "ignore_above": 64},
                "TimeZone": {"type": "keyword", "ignore_above": 32},
                "TaxRate": {"type": "float"},
                "DateModifiedUTC": {"type": "date"}
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
                "ID": {"type": "long"},
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
                "OwnershipGroup": {"type": "keyword", "ignore_above": 128},
                "PropertyName": {"type": "text"},
                "PropertyNumber": {"type": "keyword", "ignore_above": 12},
                "Provider": {"type": "keyword", "ignore_above": 128},
                "Region": {"type": "keyword", "ignore_above": 64},
                "ServiceArea": {"type": "keyword", "ignore_above": 12},
                "ServicePlan": {"type": "text",
                                "fields": {
                                    "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 128
                                    }}},
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

        conference_mapping = {
            "properties": {
                "AccessCodes": {
                    "type": "nested", 
                    "properties": {
                        "Code": {"type": "keyword"},
                        "MemberNumber": {"type": "keyword"},
                        "MemberID": {"type": "long"}
                    }
                },
                "UpdateTime": {"type": "date"},
                "Name": {"type": "text"},
                "DateCreatedLocal": {"type": "date"},
                "DateCreatedUTC": {"type": "date"},
                "StartDateLocal": {"type": "date"},
                "StartDateUTC": {"type": "date"},
                "EndDateLocal": {"type": "date"},
                "EndDateUTC": {"type": "date"},
                "ServiceArea": {"type": "keyword", "ignore_above": 12},
                "Code":
                    {"type": "text",
                     "fields": {
                         "keyword": {
                             "type": "keyword",
                             "ignore_above": 128
                         }}},
                "CodeList":
                    {"type": "text",
                     "fields": {
                         "keyword": {
                             "type": "keyword",
                             "ignore_above": 128
                         }}},
                "MemberNumberList": {"type": "keyword"},
                "MemberID": {"type": "long"},
                "MemberNumber": {"type": "keyword"},
                "SSID":
                    {"type": "text",
                     "fields": {
                         "keyword": {
                             "type": "keyword",
                             "ignore_above": 64
                         }}},
                "ConnectionLimit": {"type": "integer"},
                "DownKbs": {"type": "integer"},
                "UpKbs": {"type": "integer"},
                "UserCount": {"type": "integer"},
                "TotalInputBytes": {"type": "long"},
                "TotalOutputBytes": {"type": "long"},
                "TotalSessionTime": {"type": "long"},
                "PropertyName": {"type": "text"},
                "PropertyNumber": {"type": "keyword", "ignore_above": 12},
                "CorporateBrand": {"type": "keyword", "ignore_above": 128},
                "Brand": {"type": "keyword", "ignore_above": 64},
                "OwnershipGroup": {"type": "keyword", "ignore_above": 128},
                "Provider": {"type": "keyword", "ignore_above": 128},
                "MARSHA_Code": {"type": "keyword", "ignore_above": 64},
                "ExtPropId": {"type": "keyword", "ignore_above": 64},
                "Country": {"type": "keyword", "ignore_above": 64},
                "Region": {"type": "keyword", "ignore_above": 64},
                "SubRegion": {"type": "keyword", "ignore_above": 64},
                "TimeZone": {"type": "keyword", "ignore_above": 32},
                "TaxRate": {"type": "float"}
            }

        }

        es.indices.create(index=index_name, body=create_index)
        es.indices.refresh(index=index_name)
        es.indices.put_mapping(index=index_name, doc_type="property", body=property_mapping)
        es.indices.put_mapping(index=index_name, doc_type="device", body=device_mapping)
        es.indices.put_mapping(index=index_name, doc_type="account", body=account_mapping)
        es.indices.put_mapping(index=index_name, doc_type="session", body=session_mapping)
        es.indices.put_mapping(index=index_name, doc_type="conference", body=conference_mapping)
