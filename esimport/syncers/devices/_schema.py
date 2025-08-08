from datetime import datetime
from dataclasses import dataclass
from esimport.core import BaseSchema


class DeviceSchema(BaseSchema):

    DateUTC: datetime
    IP: str
    MAC: str
    UserAgentRaw: str

    DeviceId: str | None = None
    PlatformId: str | None = None
    BrowserId: str | None = None

    # (Optional) names if you choose to resolve them:
    #Device: str | None = None
    #Platform: str | None = None
    #Browser: str | None = None
    #MemberName: str | None = None

    Username: str | None = None
    MemberID: int | str | None = None
    MemberNumber: str | None = None
    ServiceArea: str | None = None
    ZoneType: str | None = None

    # Extra event fields:
    Origin: str | None = None
    Scope: str | None = None
    GpnsEnabled: bool | None = None
    SchemaName: str | None = None
    SchemaVersion: str | None = None
    Subject: str | None = None
    ChangeType: str | None = None
    AuthMethod: str | None = None
    ZonePlanName: str | None = None
    CurrencyCode: str | None = None
    Price: float | None = None
    TimeZoneId: str | None = None
