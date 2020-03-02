import datetime
from dataclasses import dataclass
from esimport.core import BaseSchema


class DPSKSessionSchema(BaseSchema):
    ID: int
    ServiceArea: str
    UserName: str
    NasIdentifier: str
    CalledStation: str
    VLAN: str
    MacAddress: str

    LoginTime: datetime.datetime
    LogoutTime: datetime.datetime

    ResidentID: str
    SessionID: str
    SessionLength: str

    BytesOut: int
    BytesIn: int

    TerminationReason: str
