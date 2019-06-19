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

    def create_index(self):

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
                "ActiveDevices": {
                    "type": "long"
                },
                "ActiveMembers": {
                    "type": "long"
                },
                "Address": {
                    "type": "nested",
                    "properties": {
                        "AddressLine1": {
                            "type": "text"
                        },
                        "AddressLine2": {
                            "type": "text"
                        },
                        "Area": {
                            "type": "keyword"
                        },
                        "City": {
                            "type": "keyword"
                        },
                        "CountryName": {
                            "type": "text"
                        },
                        "PostalCode": {
                            "type": "keyword"
                        }
                    }
                },
                "Brand": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "CorporateBrand": {
                    "type": "keyword",
                    "ignore_above": 128
                },
                "Country": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "CreatedUTC": {
                    "type": "date"
                },
                "CurrencyCode": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "ExtPropId": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "GoLiveUTC": {
                    "type": "date"
                },
                "GuestRooms": {
                    "type": "integer"
                },
                "ID": {
                    "type": "long"
                },
                "Lite": {
                    "type": "boolean"
                },
                "MARSHA_Code": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "MeetingRooms": {
                    "type": "integer"
                },
                "Name": {
                    "type": "text"
                },
                "Number": {
                    "type": "keyword",
                    "ignore_above": 12
                },
                "OrgNumberTree": {
                    "type": "keyword"
                },
                "OwnershipGroup": {
                    "type": "keyword",
                    "ignore_above": 128
                },
                "Pan": {
                    "type": "boolean"
                },
                "Provider": {
                    "type": "keyword",
                    "ignore_above": 128
                },
                "Region": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "ServiceAreaObjects": {
                    "type": "nested",
                    "properties": {
                        "ActiveDevices": {
                            "type": "integer"
                        },
                        "ActiveMembers": {
                            "type": "integer"
                        },
                        "Hosts": {
                            "type": "nested",
                            "properties": {
                                "HostType": {
                                    "type": "text"
                                },
                                "NASID": {
                                    "type": "keyword"
                                },
                                "NetIP": {
                                    "type": "keyword"
                                },
                                "RadiusNASID": {
                                    "type": "text"
                                },
                                "VLANRangeEnd": {
                                    "type": "integer"
                                },
                                "VLANRangeStart": {
                                    "type": "integer"
                                }
                            }
                        },
                        "Name": {
                            "type": "text"
                        },
                        "Number": {
                            "type": "keyword"
                        },
                        "ServicePlans": {
                            "type": "nested",
                            "properties": {
                                "ConnectionLimit": {
                                    "type": "integer"
                                },
                                "CurrencyCode": {
                                    "type": "keyword"
                                },
                                "DateCreatedUTC": {
                                    "type": "date"
                                },
                                "Description": {
                                    "type": "text"
                                },
                                "DownKbs": {
                                    "type": "integer"
                                },
                                "GroupBandwidthLimit": {
                                    "type": "boolean"
                                },
                                "IdleTimeout": {
                                    "type": "integer"
                                },
                                "LifespanTime": {
                                    "type": "integer"
                                },
                                "LifespanUnit": {
                                    "type": "keyword"
                                },
                                "Name": {
                                    "type": "keyword"
                                },
                                "Number": {
                                    "type": "keyword"
                                },
                                "OrgCode": {
                                    "type": "keyword"
                                },
                                "PlanTime": {
                                    "type": "integer"
                                },
                                "PlanUnit": {
                                    "type": "keyword"
                                },
                                "Price": {
                                    "type": "float"
                                },
                                "RadiusClass": {
                                    "type": "keyword"
                                },
                                "Status": {
                                    "type": "keyword"
                                },
                                "Type": {
                                    "type": "keyword"
                                },
                                "UpKbs": {
                                    "type": "integer"
                                }
                            }
                        },
                        "ZoneType": {
                            "type": "keyword"
                        }
                    }
                },
                "ServiceAreas": {
                    "type": "keyword"
                },
                "Status": {
                    "type": "keyword",
                    "ignore_above": 16
                },
                "SubRegion": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "TaxRate": {
                    "type": "float"
                },
                "TimeZone": {
                    "type": "keyword",
                    "ignore_above": 32
                },
                "UpdateTime": {
                    "type": "date"
                },
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
                "AncestorOrgNumberTree": {"type": "keyword"},
                "Brand": {"type": "keyword", "ignore_above": 64},
                "Browser": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "CorporateBrand": {"type": "keyword", "ignore_above": 128},
                "Country": {"type": "keyword", "ignore_above": 64},
                "DateLocal": {"type": "date"},
                "DateUTC": {"type": "date"},
                "Device": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "ExtPropId": {"type": "keyword", "ignore_above": 64},
                "ID": {"type": "long"},
                "IP": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "MAC": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "MARSHA_Code": {"type": "keyword", "ignore_above": 64},
                "MemberID": {"type": "long"},
                "MemberNumber": {"type": "keyword"},
                "OwnershipGroup": {"type": "keyword", "ignore_above": 128},
                "Platform": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "PropertyName": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "PropertyNumber": {"type": "keyword", "ignore_above": 12},
                "Provider": {"type": "keyword", "ignore_above": 128},
                "Region": {"type": "keyword", "ignore_above": 64},
                "ServiceArea": {"type": "keyword"},
                "SubRegion": {"type": "keyword", "ignore_above": 64},
                "TaxRate": {"type": "float"},
                "TimeZone": {"type": "keyword", "ignore_above": 32},
                "UserAgentRaw": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "Username": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "ZoneType": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                }
            }
        }

        account_mapping = {
            "properties": {
                "Activated": {
                    "type": "date"
                },
                "ActivatedLocal": {
                    "type": "date"
                },
                "Brand": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "CardType": {
                    "type": "keyword",
                    "ignore_above": 16
                },
                "ConnectCode": {
                    "type": "text"
                },
                "ConsumableTime": {
                    "type": "integer"
                },
                "ConsumableUnit": {
                    "type": "keyword",
                    "ignore_above": 16
                },
                "CorporateBrand": {
                    "type": "keyword",
                    "ignore_above": 128
                },
                "Country": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "Created": {
                    "type": "date"
                },
                "CreatedLocal": {
                    "type": "date"
                },
                "CreditCardNumber": {
                    "type": "integer"
                },
                "Currency": {
                    "type": "keyword",
                    "ignore_above": 8
                },
                "DateModifiedUTC": {
                    "type": "date"
                },
                "DiscountCode": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                },
                "DownCap": {
                    "type": "integer"
                },
                "ExtPropId": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "ID": {
                    "type": "long"
                },
                "LastName": {
                    "type": "text"
                },
                "MARSHA_Code": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "MarketingContact": {
                    "type": "text"
                },
                "MemberNumber": {
                    "type": "keyword",
                    "ignore_above": 32
                },
                "Name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                },
                "NetworkAccessEndDateUTC": {
                    "type": "date"
                },
                "NetworkAccessStartDateUTC": {
                    "type": "date"
                },
                "OwnershipGroup": {
                    "type": "keyword",
                    "ignore_above": 128
                },
                "PayMethod": {
                    "type": "keyword"
                },
                "Price": {
                    "type": "float"
                },
                "PropertyName": {
                    "type": "text"
                },
                "PropertyNumber": {
                    "type": "keyword",
                    "ignore_above": 12
                },
                "Provider": {
                    "type": "keyword",
                    "ignore_above": 128
                },
                "PurchaseMacAddress": {
                    "type": "keyword",
                    "ignore_above": 18
                },
                "Region": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "RoomNumber": {
                    "type": "keyword"
                },
                "ServiceArea": {
                    "type": "keyword",
                    "ignore_above": 12
                },
                "ServicePlan": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                },
                "ServicePlanNumber": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "SpanTime": {
                    "type": "integer"
                },
                "SpanUnit": {
                    "type": "keyword",
                    "ignore_above": 16
                },
                "Status": {
                    "type": "keyword",
                    "ignore_above": 16
                },
                "SubRegion": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "TaxRate": {
                    "type": "float"
                },
                "TimeZone": {
                    "type": "keyword",
                    "ignore_above": 32
                },
                "UpCap": {
                    "type": "integer"
                },
                "UpsellAccountID": {
                    "type": "long"
                },
                "VLAN": {
                    "type": "integer"
                },
                "ZoneType": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                }
            }
        }

        session_mapping = {
            "properties": {
                "Brand": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "BytesIn": {
                    "type": "long"
                },
                "BytesOut": {
                    "type": "long"
                },
                "CalledStation": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                },
                "CorporateBrand": {
                    "type": "keyword",
                    "ignore_above": 128
                },
                "Country": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "ExtPropId": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "ID": {
                    "type": "long"
                },
                "LoginTime": {
                    "type": "date"
                },
                "LoginTimeLocal": {
                    "type": "date"
                },
                "LogoutTime": {
                    "type": "date"
                },
                "LogoutTimeLocal": {
                    "type": "date"
                },
                "MARSHA_Code": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "MacAddress": {
                    "type": "keyword",
                    "ignore_above": 18
                },
                "MemberNumber": {
                    "type": "keyword",
                    "ignore_above": 32
                },
                "Name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                },
                "NasIdentifier": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "OwnershipGroup": {
                    "type": "keyword",
                    "ignore_above": 128
                },
                "PropertyName": {
                    "type": "text"
                },
                "PropertyNumber": {
                    "type": "keyword",
                    "ignore_above": 12
                },
                "Provider": {
                    "type": "keyword",
                    "ignore_above": 128
                },
                "Region": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "ServiceArea": {
                    "type": "keyword",
                    "ignore_above": 12
                },
                "ServicePlan": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                },
                "SessionID": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                },
                "SessionLength": {
                    "type": "integer"
                },
                "SubRegion": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "TaxRate": {
                    "type": "float"
                },
                "TerminationReason": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                },
                "TimeZone": {
                    "type": "keyword",
                    "ignore_above": 32
                },
                "UserName": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                },
                "VLAN": {
                    "type": "integer"
                },
                "ZoneType": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                }
            }
        }

        conference_mapping = {
            "properties": {
                "AccessCodes": {
                    "type": "nested",
                    "properties": {
                        "Code": {
                            "type": "keyword"
                        },
                        "MemberID": {
                            "type": "long"
                        },
                        "MemberNumber": {
                            "type": "keyword"
                        }
                    }
                },
                "Brand": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "Code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                },
                "CodeList": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 128
                        }
                    }
                },
                "ConnectionLimit": {
                    "type": "long"
                },
                "CorporateBrand": {
                    "type": "keyword",
                    "ignore_above": 128
                },
                "Country": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "DateCreatedLocal": {
                    "type": "date"
                },
                "DateCreatedUTC": {
                    "type": "date"
                },
                "DownKbs": {
                    "type": "long"
                },
                "EndDateLocal": {
                    "type": "date"
                },
                "EndDateUTC": {
                    "type": "date"
                },
                "ExtPropId": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "GroupBandwidthLimit": {
                    "type": "boolean"
                },
                "ID": {
                    "type": "long"
                },
                "MARSHA_Code": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "MemberID": {
                    "type": "long"
                },
                "MemberNumber": {
                    "type": "keyword"
                },
                "MemberNumberList": {
                    "type": "keyword"
                },
                "MemberStatus": {
                    "type": "keyword"
                },
                "Name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "OwnershipGroup": {
                    "type": "keyword",
                    "ignore_above": 128
                },
                "PropertyName": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "PropertyNumber": {
                    "type": "keyword",
                    "ignore_above": 12
                },
                "Provider": {
                    "type": "keyword",
                    "ignore_above": 128
                },
                "Region": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "SSID": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 64
                        }
                    }
                },
                "ServiceArea": {
                    "type": "keyword",
                    "ignore_above": 12
                },
                "StartDateLocal": {
                    "type": "date"
                },
                "StartDateUTC": {
                    "type": "date"
                },
                "SubRegion": {
                    "type": "keyword",
                    "ignore_above": 64
                },
                "TaxRate": {
                    "type": "float"
                },
                "TimeZone": {
                    "type": "keyword",
                    "ignore_above": 32
                },
                "TotalInputBytes": {
                    "type": "float"
                },
                "TotalOutputBytes": {
                    "type": "float"
                },
                "TotalSessionTime": {
                    "type": "float"
                },
                "UpKbs": {
                    "type": "long"
                },
                "UpdateTime": {
                    "type": "date"
                },
                "UserCount": {
                    "type": "long"
                }
            }
        }

        accounts_template_body = {
            "template": "accounts*",
            "settings": create_index["settings"],
            "aliases": {
                "accounts-current": {}
            },
            "mappings": {
                "account": {
                    "properties": account_mapping["properties"]
                }
            }
        }

        sessions_template_body = {
            "template": "sessions*",
            "settings": create_index["settings"],
            "aliases": {
                "sessions-current": {}
            },
            "mappings": {
                "session": {
                    "properties": session_mapping["properties"]
                }
            }
        }

        devices_template_body = {
            "template": "devices*",
            "settings": create_index["settings"],
            "aliases": {
                "devices-current": {}
            },
            "mappings": {
                "device": {
                    "properties": device_mapping["properties"]
                }
            }
        }

        # property index
        es.indices.create(index="properties", body=create_index)
        es.indices.refresh(index="properties")
        es.indices.put_mapping(index="properties", doc_type="property", body=property_mapping)
        # conference index
        es.indices.create(index="conferences", body=create_index)
        es.indices.refresh(index="conferences")
        es.indices.put_mapping(index="conferences", doc_type="conference", body=conference_mapping)
        # es.indices.put_mapping(index=index_name, doc_type="device", body=device_mapping)
        # es.indices.put_mapping(index=index_name, doc_type="account", body=account_mapping)
        # es.indices.put_mapping(index=index_name, doc_type="session", body=session_mapping)
        # es.indices.put_mapping(index=index_name, doc_type="conference", body=conference_mapping)
        es.indices.put_template(name="accounts", body=accounts_template_body)
        es.indices.put_template(name="sessions", body=sessions_template_body)
        es.indices.put_template(name="devices", body=devices_template_body)
