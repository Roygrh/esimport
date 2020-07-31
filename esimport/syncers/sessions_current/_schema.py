import datetime
from dataclasses import dataclass
from esimport.core import BaseSchema


class SessionSchema(BaseSchema):
    ID: int

    ServiceArea: str
    ZoneType: str
    UserName: str
    Name: str
    MemberNumber: str
    NasIdentifier: str
    CalledStation: str
    VLAN: str
    MacAddress: str

    LoginTime: datetime.datetime
    LogoutTime: datetime.datetime

    SessionID: str
    SessionLength: str

    BytesOut: int
    BytesIn: int

    TerminationReason: str
    ServicePlan: str
