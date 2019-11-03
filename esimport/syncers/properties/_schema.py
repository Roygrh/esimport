import datetime
from dataclasses import dataclass
from typing import List, Union

from esimport.core import BaseSchema


class Host(BaseSchema):
    NASID: str
    HostType: str
    VLANRangeStart: int
    VLANRangeEnd: int

    RadiusNASID: Union[str, None]
    NetIP: Union[str, None]


class ServicePlan(BaseSchema):
    Number: str
    Name: str
    Description: str
    Price: float
    UpKbs: int
    DownKbs: int
    IdleTimeout: int
    ConnectionLimit: int
    RadiusClass: str
    GroupBandwidthLimit: bool
    Type: str
    PlanTime: str
    PlanUnit: str
    LifespanTime: int
    LifespanUnit: str
    CurrencyCode: str
    Status: str
    OrgCode: Union[str, None]
    DateCreatedUTC: datetime.datetime


class ServiceArea(BaseSchema):
    Number: str
    Name: str
    ZoneType: str
    ActiveMembers: int
    ActiveDevices: int
    Hosts: List[Host]
    ServicePlans: List[ServicePlan]


class Address(BaseSchema):
    AddressLine2: str
    Area: str
    AddressLine1: str
    CountryName: str
    PostalCode: str
    City: str


class Property(BaseSchema):

    ID: int

    CreatedUTC: datetime.datetime
    UpdateTime: datetime.datetime

    CorporateBrand: str
    Provider: str
    Lite: bool
    Pan: Union[str, None]
    Status: str
    Ctyhocn: str
    TaxRate: float
    GoLiveUTC: datetime.datetime
    ExtPropId: str
    Brand: str
    OwnershipGroup: str
    Region: str
    Name: str
    Country: str
    CurrencyCode: str
    TimeZone: str
    SubRegion: str
    Number: str
    BandwidthMarker: str
    SingleCredential: str

    MeetingRooms: int
    GuestRooms: int  #  101
    ActiveDevices: int
    ActiveMembers: int

    ServiceAreaObjects: List[ServiceArea]

    Address: Address
    OrgNumberTree: List[str]
