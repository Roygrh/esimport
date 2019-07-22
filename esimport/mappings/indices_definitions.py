# fmt: off
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

accounts_template_body = {
    "template": "accounts*",
    "settings": None,
    "aliases": {
        "accounts-current": {
            "filter": {
                "type": {"value": "account"}
            },
        },
    },
    "mappings": {
        "account": {
            "properties": account_mapping["properties"]
        }
    }
}

sessions_template_body = {
    "template": "sessions*",
    "settings": None,
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
    "settings": None,
    "aliases": {
        "devices-current": {
            "filter": {
                "type": {"value": "device"}
            },
        }
    },
    "mappings": {
        "device": {
            "properties": device_mapping["properties"]
        }
    }
}
elevenos_aliases_config= {
    "account": "accounts-current",
    "device": "devices-current",
    "session": "sessions-current"
}

index_templates = {
    'accounts': accounts_template_body,
    'sessions': sessions_template_body,
    'devices': devices_template_body
}
# fmt: on
