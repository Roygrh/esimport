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

    def setupindex(self):

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
                "UpdateTime": {"type": "date"},
                "Name": {"type": "text"},
                "Number": {"type": "keyword", "ignore_above": 12},
                "GuestRooms": {"type": "integer"},
                "MeetingRooms": {"type": "integer"},
                "Lite": {"type": "boolean"},
                "Pan": {"type": "boolean"},
                "Status": {"type": "keyword", "ignore_above": 16},
                "CreatedUTC": {"type": "date"}, "GoLiveUTC": {"type": "date"},
                "GoLiveUTC": {"type": "date"},
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
                "Name": {"type": "text"},
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
                "ConnectCode": {"type": "text"},
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
                "TaxRate": {"type": "float"}
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
                "ServiceArea": {"type": "keyword", "ignore_above": 12},
                "VLAN": {"type": "integer"},
                "LogoutTime": {"type": "date"},
                "LogoutTimeLocal": {"type": "date"},
                "LoginTime": {"type": "date"},
                "LoginTimeLocal": {"type": "date"},
                "BytesIn": {"type": "long"},
                "MacAddress": {"type": "keyword", "ignore_above": 18},
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
                "MemberNumber": {"type": "keyword", "ignore_above": 32},
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

        conference_mapping = {
            "properties": {
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

        es.indices.create(index=settings.ES_INDEX, body=create_index)
        es.indices.refresh(index=settings.ES_INDEX)
        es.indices.put_mapping(index=settings.ES_INDEX, doc_type="property", body=property_mapping)
        es.indices.put_mapping(index=settings.ES_INDEX, doc_type="device", body=device_mapping)
        es.indices.put_mapping(index=settings.ES_INDEX, doc_type="account", body=account_mapping)
        es.indices.put_mapping(index=settings.ES_INDEX, doc_type="session", body=session_mapping)
        es.indices.put_mapping(index=settings.ES_INDEX, doc_type="conference", body=conference_mapping)
