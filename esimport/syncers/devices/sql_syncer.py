import os
import pyodbc
from ._queries import GET_ALL_DEVICES, GET_DEVICES_UPDATED_AFTER
from ._schema import DeviceSchema as Device

class DeviceSqlSyncer:
    """
    Fetch device records from SQL Server.
    """
    def __init__(self):
        connection_string = os.getenv("SQL_CONNECTION_STRING")
        self.connection = pyodbc.connect(connection_string)

    def fetch(self, start_dt: str, end_dt: str, limit: int = 1000):
        """
        Execute SQL query to retrieve device data.
        """
        cursor = self.connection.cursor()
        # Example: fetch top N records
        cursor.execute(GET_ALL_DEVICES, limit)
        for row in cursor.fetchall():
            yield Device(
                id=row.ID,
                Date=row.Date,
                IP=row.IP,
                MAC=row.MAC,
                UserAgentRaw=row.UserAgentRaw,
                Device=row.Device,
                Platform=row.Platform,
                Browser=row.Browser,
                Username=row.Username,
                MemberID=row.MemberID,
                MemberNumber=row.MemberNumber,
                ServiceArea=row.ServiceArea,
                ZoneType=row.ZoneType
            )
        # Optionally fetch by date range:
        # cursor.execute(GET_DEVICES_UPDATED_AFTER, start_dt)