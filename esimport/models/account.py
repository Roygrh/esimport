################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import logging
from datetime import datetime

from esimport.models import ESRecord
from esimport.models.base import BaseModel
from esimport.utils import set_utc_timezone

logger = logging.getLogger(__name__)


class Account(BaseModel):
    _type = "account"
    _date_field = "DateModifiedUTC"
    _index = "accounts"
    _version_date_fieldname = "DateModifiedUTC"

    @staticmethod
    def get_type():
        return Account._type

    @staticmethod
    def get_index():
        return Account._index

    def get_accounts_by_created_date(self, start, limit, start_date="1900-01-01"):
        q = self.query_records_by_account_id()
        return self.get_accounts(q, limit, start, start_date)

    def get_accounts_by_modified_date(self, start_date, end_date):
        q = self.query_records_by_modified_date()
        return self.get_accounts(q, start_date, end_date, start_date, end_date)

    def get_accounts(self, query, *args):
        for row in self.fetch_dict(query, *args):
            row["Duration"] = self.find_duration(row)

            # Set all datetime objects to utc timezone
            for key, value in row.items():
                if isinstance(value, datetime):
                    row[key] = set_utc_timezone(value)

            yield ESRecord(
                row, self.get_type(), self.get_index(), row[self._version_date_fieldname]
            )

    @staticmethod
    def find_duration(row):
        if row.get("ConsumableTime") is not None:
            return "{0} {1} {2}".format(
                row.get("ConsumableTime"), row.get("ConsumableUnit"), "consumable"
            )
        if row.get("SpanTime") is not None:
            return "{0} {1}".format(row.get("SpanTime"), row.get("SpanUnit"))
        else:
            return None

    @staticmethod
    def query_records_by_account_id():
        return """Select TOP (?) Zone_Plan_Account.ID as ID,
Member.Display_Name AS Name,
Member.Number AS MemberNumber,
Zone_Plan_Account_Status.Name AS Status,
Organization.Number AS ServiceArea,
Zone_Plan_Account.Purchase_Price AS Price,
Zone_Plan_Account.Purchase_MAC_Address AS PurchaseMacAddress,
Zone_Plan_Account.Activation_Date_UTC AS Activated,
Zone_Plan_Account.Date_Created_UTC AS Created,
CASE 
	WHEN COALESCE(Zone_Plan_Account.Date_Modified_UTC, Zone_Plan_Account.Date_Created_UTC) > COALESCE(Network_Access_Limits.Date_Modified_UTC, Zone_Plan_Account.Date_Created_UTC)
    THEN COALESCE(Zone_Plan_Account.Date_Modified_UTC, Zone_Plan_Account.Date_Created_UTC)
    ELSE COALESCE(Network_Access_Limits.Date_Modified_UTC, Zone_Plan_Account.Date_Created_UTC)
END AS DateModifiedUTC,
Zone_Plan.Name AS ServicePlan,
Zone_Plan.Plan_Number AS ServicePlanNumber,
Network_Access_Limits.Up_kbs AS UpCap,
Network_Access_Limits.Down_kbs AS DownCap,
Network_Access_Limits.Start_Date_UTC AS NetworkAccessStartDateUTC,
Network_Access_Limits.End_Date_UTC AS NetworkAccessEndDateUTC,
Payment_Method.Code AS PayMethod,
Currency.Code AS Currency,
Credit_Card.Masked_Number AS CreditCardNumber,
Credit_Card_Type.Name AS CardType,
PMS_Charge.Last_Name AS LastName,
PMS_Charge.Room_Number AS RoomNumber,
Promotional_Code.Code AS DiscountCode,
Prepaid_Zone_Plan.Consumable_Time AS ConsumableTime,
CTU.Name AS ConsumableUnit,
Prepaid_Zone_Plan.Lifespan_Time AS SpanTime,
STU.Name AS SpanUnit,
Code.Code AS ConnectCode,
Member_Marketing_Opt_In.Marketing_Contact_Info AS MarketingContact,
Org_Value.Value AS ZoneType,
Member_Vlan.Vlan as VLAN
FROM Zone_Plan_Account WITH (NOLOCK)
JOIN Member WITH (NOLOCK) ON Member.ID = Zone_Plan_Account.Member_ID
JOIN Zone_Plan_Account_Status WITH (NOLOCK) ON Zone_Plan_Account.Zone_Plan_Account_Status_ID = Zone_Plan_Account_Status.ID
JOIN Organization WITH (NOLOCK) ON Organization.ID = Zone_Plan_Account.Purchase_Org_ID
JOIN Zone_Plan WITH (NOLOCK) ON Zone_Plan.ID = Zone_Plan_Account.Zone_Plan_ID
JOIN Network_Access_Limits WITH (NOLOCK) ON Network_Access_Limits.ID = Zone_Plan_Account.Network_Access_Limits_ID
JOIN Payment_Method WITH (NOLOCK) ON Payment_Method.ID = Zone_Plan_Account.Payment_Method_ID
JOIN Currency WITH (NOLOCK) ON Currency.ID = Zone_Plan_Account.Purchase_Price_Currency_ID
JOIN Prepaid_Zone_Plan WITH (NOLOCK) ON Prepaid_Zone_Plan.Zone_Plan_ID = Zone_Plan.ID
LEFT JOIN Member_Vlan WITH (NOLOCK) ON Member_Vlan.Member_ID = Zone_Plan_Account.Member_ID
LEFT JOIN Credit_Card WITH (NOLOCK) ON Credit_Card.ID = Zone_Plan_Account.Credit_Card_ID
LEFT JOIN Credit_Card_Type WITH (NOLOCK) ON Credit_Card_Type.ID = Credit_Card.Credit_Card_Type_ID
LEFT JOIN PMS_Charge WITH (NOLOCK) ON PMS_Charge.ID = Zone_Plan_Account.PMS_Charge_ID
LEFT JOIN Zone_Plan_Account_Promotional_Code WITH (NOLOCK) ON Zone_Plan_Account_Promotional_Code.Zone_Plan_Account_ID = Zone_Plan_Account.ID
LEFT JOIN Promotional_Code WITH (NOLOCK) ON Promotional_Code.ID = Zone_Plan_Account_Promotional_Code.Promotional_Code_ID
LEFT JOIN Time_Unit AS CTU WITH (NOLOCK) ON CTU.ID = Prepaid_Zone_Plan.Consumable_Time_Unit_ID
LEFT JOIN Time_Unit AS STU WITH (NOLOCK) ON STU.ID = Prepaid_Zone_Plan.Lifespan_Time_Unit_ID
LEFT JOIN Code WITH (NOLOCK) ON Code.ID = Zone_Plan_Account.Code_ID
LEFT JOIN Member_Marketing_Opt_In WITH (NOLOCK) ON Member_Marketing_Opt_In.Member_ID = Member.ID
LEFT JOIN Org_Value WITH (NOLOCK) ON Org_Value.Organization_ID = Organization.ID AND Org_Value.Name='ZoneType'
WHERE Zone_Plan_Account.ID >= ? AND Zone_Plan_Account.Date_Created_UTC >= ?
ORDER BY Zone_Plan_Account.ID ASC"""

    @staticmethod
    def query_records_by_modified_date():
        return """
SELECT
    Zone_Plan_Account.ID as ID,
    Member.Display_Name AS Name,
    Member.Number AS MemberNumber,
    Zone_Plan_Account_Status.Name AS Status,
    Organization.Number AS ServiceArea,
    Zone_Plan_Account.Purchase_Price AS Price,
    Zone_Plan_Account.Purchase_MAC_Address AS PurchaseMacAddress,
    Zone_Plan_Account.Activation_Date_UTC AS Activated,
    Zone_Plan_Account.Date_Created_UTC AS Created,
    Zone_Plan_Account.Upsell_Zone_Plan_Account_ID AS UpsellAccountID,
    CASE 
        WHEN COALESCE(Zone_Plan_Account.Date_Modified_UTC, Zone_Plan_Account.Date_Created_UTC) > COALESCE(Network_Access_Limits.Date_Modified_UTC, Zone_Plan_Account.Date_Created_UTC)
        THEN COALESCE(Zone_Plan_Account.Date_Modified_UTC, Zone_Plan_Account.Date_Created_UTC)
        ELSE COALESCE(Network_Access_Limits.Date_Modified_UTC, Zone_Plan_Account.Date_Created_UTC)
    END AS DateModifiedUTC,
    Zone_Plan.Name AS ServicePlan,
    Zone_Plan.Plan_Number AS ServicePlanNumber,
    Network_Access_Limits.Up_kbs AS UpCap,
    Network_Access_Limits.Down_kbs AS DownCap,
    Network_Access_Limits.Start_Date_UTC AS NetworkAccessStartDateUTC,
    Network_Access_Limits.End_Date_UTC AS NetworkAccessEndDateUTC,
    Payment_Method.Code AS PayMethod,
    Currency.Code AS Currency,
    Credit_Card.Masked_Number AS CreditCardNumber,
    Credit_Card_Type.Name AS CardType,
    PMS_Charge.Last_Name AS LastName,
    PMS_Charge.Room_Number AS RoomNumber,
    Promotional_Code.Code AS DiscountCode,
    Prepaid_Zone_Plan.Consumable_Time AS ConsumableTime,
    CTU.Name AS ConsumableUnit,
    Prepaid_Zone_Plan.Lifespan_Time AS SpanTime,
    STU.Name AS SpanUnit,
    Code.Code AS ConnectCode,
    Member_Marketing_Opt_In.Marketing_Contact_Info AS MarketingContact,
    Org_Value.Value AS ZoneType,
    Member_Vlan.Vlan as VLAN
FROM
    Zone_Plan_Account WITH (NOLOCK)
    JOIN Member WITH (NOLOCK) ON Member.ID = Zone_Plan_Account.Member_ID
    JOIN Zone_Plan_Account_Status WITH (NOLOCK) ON Zone_Plan_Account.Zone_Plan_Account_Status_ID = Zone_Plan_Account_Status.ID
    JOIN Organization WITH (NOLOCK) ON Organization.ID = Zone_Plan_Account.Purchase_Org_ID
    JOIN Zone_Plan WITH (NOLOCK) ON Zone_Plan.ID = Zone_Plan_Account.Zone_Plan_ID
    JOIN Network_Access_Limits WITH (NOLOCK) ON Network_Access_Limits.ID = Zone_Plan_Account.Network_Access_Limits_ID
    JOIN Payment_Method WITH (NOLOCK) ON Payment_Method.ID = Zone_Plan_Account.Payment_Method_ID
    JOIN Currency WITH (NOLOCK) ON Currency.ID = Zone_Plan_Account.Purchase_Price_Currency_ID
    JOIN Prepaid_Zone_Plan WITH (NOLOCK) ON Prepaid_Zone_Plan.Zone_Plan_ID = Zone_Plan.ID
    LEFT JOIN Member_Vlan WITH (NOLOCK) ON Member_Vlan.Member_ID = Zone_Plan_Account.Member_ID
    LEFT JOIN Credit_Card WITH (NOLOCK) ON Credit_Card.ID = Zone_Plan_Account.Credit_Card_ID
    LEFT JOIN Credit_Card_Type WITH (NOLOCK) ON Credit_Card_Type.ID = Credit_Card.Credit_Card_Type_ID
    LEFT JOIN PMS_Charge WITH (NOLOCK) ON PMS_Charge.ID = Zone_Plan_Account.PMS_Charge_ID
    LEFT JOIN Zone_Plan_Account_Promotional_Code WITH (NOLOCK) ON Zone_Plan_Account_Promotional_Code.Zone_Plan_Account_ID = Zone_Plan_Account.ID
    LEFT JOIN Promotional_Code WITH (NOLOCK) ON Promotional_Code.ID = Zone_Plan_Account_Promotional_Code.Promotional_Code_ID
    LEFT JOIN Time_Unit AS CTU WITH (NOLOCK) ON CTU.ID = Prepaid_Zone_Plan.Consumable_Time_Unit_ID
    LEFT JOIN Time_Unit AS STU WITH (NOLOCK) ON STU.ID = Prepaid_Zone_Plan.Lifespan_Time_Unit_ID
    LEFT JOIN Code WITH (NOLOCK) ON Code.ID = Zone_Plan_Account.Code_ID
    LEFT JOIN Member_Marketing_Opt_In WITH (NOLOCK) ON Member_Marketing_Opt_In.Member_ID = Member.ID
    LEFT JOIN Org_Value WITH (NOLOCK) ON Org_Value.Organization_ID = Organization.ID AND Org_Value.Name='ZoneType'
WHERE 
    Zone_Plan_Account.ID IN (
        SELECT Zone_Plan_Account.ID
        FROM Zone_Plan_Account WITH (NOLOCK)
        WHERE Zone_Plan_Account.Date_Modified_UTC > ? AND Zone_Plan_Account.Date_Modified_UTC <= ?
            UNION
        SELECT Zone_Plan_Account.ID
        FROM Zone_Plan_Account WITH (NOLOCK)
        JOIN Network_Access_Limits WITH (NOLOCK) ON Network_Access_Limits.ID = Zone_Plan_Account.Network_Access_Limits_ID 
        WHERE Network_Access_Limits.Date_Modified_UTC > ? AND Network_Access_Limits.Date_Modified_UTC <= ?    
    )
ORDER BY
    CASE 
        WHEN COALESCE(Zone_Plan_Account.Date_Modified_UTC, Zone_Plan_Account.Date_Created_UTC) > COALESCE(Network_Access_Limits.Date_Modified_UTC, Zone_Plan_Account.Date_Created_UTC)
        THEN COALESCE(Zone_Plan_Account.Date_Modified_UTC, Zone_Plan_Account.Date_Created_UTC)
        ELSE COALESCE(Network_Access_Limits.Date_Modified_UTC, Zone_Plan_Account.Date_Created_UTC)
    END"""
