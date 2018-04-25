################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import six
import logging

from datetime import datetime

from esimport.models import ESRecord
from esimport.models.base import BaseModel

logger = logging.getLogger(__name__)

class Account(BaseModel):

    _type = "account"
    @staticmethod
    def get_type():
        return Account._type

    def get_accounts_by_created_date(self, start, limit, start_date='1900-01-01'):
        q = self.eleven_query(start_date, start, limit)
        return self.get_accounts(q)

    def get_accounts_by_id(self, id):
        q = self.query_records_by_zpa_id(id)
        return self.get_accounts(q)

    def get_records_by_zpa_id(self, ids):
        q = self.query_records_by_zpa_id(ids)
        return self.fetch_dict(q)

    def get_updated_accounts(self, start_date, end_date):
        q = self.updated_accounts_query()        
        return self.get_accounts(q, start_date, end_date)

    def get_accounts(self, query, *args):
        dt_columns = ['Created', 'Activated', 'DateModifiedUTC']
        for row in self.fetch_dict(query, *args):
            row['ID'] = long(row.get('ID')) if six.PY2 else int(row.get('ID'))
            row['Duration'] = self.find_duration(row)
            # convert datetime to string
            for dt_column in dt_columns:
                if dt_column in row and isinstance(row[dt_column], datetime):
                    row[dt_column] = row[dt_column].isoformat()
            yield ESRecord(row, self.get_type())

    def find_duration(self, row):
        if row.get('ConsumableTime') is not None:
            return "{0} {1} {2}".format(row.get('ConsumableTime'), row.get('ConsumableUnit'), "consumable")
        if row.get('SpanTime') is not None:
            return "{0} {1}".format(row.get('SpanTime'), row.get('SpanUnit'))
        else:
            return None

    @staticmethod
    def updated_accounts_query():
        return """
SELECT
    Zone_Plan_Account.ID as ID,
    Member.Display_Name AS Name,
    Member.Number AS MemberNumber,
    Member_Status.Name AS Status,
    Organization.Number AS ServiceArea,
    Zone_Plan_Account.Purchase_Price AS Price,
    Zone_Plan_Account.Purchase_MAC_Address AS PurchaseMacAddress,
    Zone_Plan_Account.Activation_Date_UTC AS Activated,
    Zone_Plan_Account.Date_Created_UTC AS Created,
    Zone_Plan_Account.Date_Modified_UTC AS DateModifiedUTC,
    Zone_Plan.Name AS ServicePlan,
    Zone_Plan.Plan_Number AS ServicePlanNumber,
    Network_Access_Limits.Up_kbs AS UpCap,
    Network_Access_Limits.Down_kbs AS DownCap,
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
    Org_Value.Value AS ZoneType
FROM
    Zone_Plan_Account WITH (NOLOCK)
    JOIN Member WITH (NOLOCK) ON Member.ID = Zone_Plan_Account.Member_ID
    JOIN Member_Status WITH (NOLOCK) ON Member_Status.ID = Member.Member_Status_ID
    JOIN Organization WITH (NOLOCK) ON Organization.ID = Member.Organization_ID
    JOIN Zone_Plan WITH (NOLOCK) ON Zone_Plan.ID = Zone_Plan_Account.Zone_Plan_ID
    JOIN Network_Access_Limits WITH (NOLOCK) ON Network_Access_Limits.ID = Zone_Plan_Account.Network_Access_Limits_ID
    JOIN Payment_Method WITH (NOLOCK) ON Payment_Method.ID = Zone_Plan_Account.Payment_Method_ID
    JOIN Currency WITH (NOLOCK) ON Currency.ID = Zone_Plan_Account.Purchase_Price_Currency_ID
    JOIN Prepaid_Zone_Plan WITH (NOLOCK) ON Prepaid_Zone_Plan.Zone_Plan_ID = Zone_Plan.ID
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
    Zone_Plan_Account.Date_Modified_UTC > ? AND Zone_Plan_Account.Date_Modified_UTC <= ?
ORDER BY 
	Zone_Plan_Account.Date_Modified_UTC ASC"""


    @staticmethod
    def eleven_query(start_date, start_zpa_id, limit):
        q = """Select TOP {1} Zone_Plan_Account.ID as ID,
Member.Display_Name AS Name,
Member.Number AS MemberNumber,
Member_Status.Name AS Status,
Organization.Number AS ServiceArea,
Zone_Plan_Account.Purchase_Price AS Price,
Zone_Plan_Account.Purchase_MAC_Address AS PurchaseMacAddress,
Zone_Plan_Account.Activation_Date_UTC AS Activated,
Zone_Plan_Account.Date_Created_UTC AS Created,
Zone_Plan.Name AS ServicePlan,
Zone_Plan.Plan_Number AS ServicePlanNumber,
Network_Access_Limits.Up_kbs AS UpCap,
Network_Access_Limits.Down_kbs AS DownCap,
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
Org_Value.Value AS ZoneType
FROM Zone_Plan_Account WITH (NOLOCK)
JOIN Member WITH (NOLOCK) ON Member.ID = Zone_Plan_Account.Member_ID
JOIN Member_Status WITH (NOLOCK) ON Member_Status.ID = Member.Member_Status_ID
JOIN Organization WITH (NOLOCK) ON Organization.ID = Member.Organization_ID
JOIN Zone_Plan WITH (NOLOCK) ON Zone_Plan.ID = Zone_Plan_Account.Zone_Plan_ID
JOIN Network_Access_Limits WITH (NOLOCK) ON Network_Access_Limits.ID = Zone_Plan_Account.Network_Access_Limits_ID
JOIN Payment_Method WITH (NOLOCK) ON Payment_Method.ID = Zone_Plan_Account.Payment_Method_ID
JOIN Currency WITH (NOLOCK) ON Currency.ID = Zone_Plan_Account.Purchase_Price_Currency_ID
JOIN Prepaid_Zone_Plan WITH (NOLOCK) ON Prepaid_Zone_Plan.Zone_Plan_ID = Zone_Plan.ID
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
WHERE Zone_Plan_Account.ID >= {0} AND Zone_Plan_Account.Date_Created_UTC >= '{2}'
ORDER BY Zone_Plan_Account.ID ASC"""
        q = q.format(start_zpa_id, limit, start_date)
        return q

    @staticmethod
    def query_records_by_zpa_id(ids):
        q = """Select Zone_Plan_Account.ID as ID,
Member.Display_Name AS Name,
Member.Number AS MemberNumber,
Member_Status.Name AS Status,
Organization.Number AS ServiceArea,
Zone_Plan_Account.Purchase_Price AS Price,
Zone_Plan_Account.Purchase_MAC_Address AS PurchaseMacAddress,
Zone_Plan_Account.Activation_Date_UTC AS Activated,
Zone_Plan_Account.Date_Created_UTC AS Created,
Zone_Plan.Name AS ServicePlan,
Zone_Plan.Plan_Number AS ServicePlanNumber,
Network_Access_Limits.Up_kbs AS UpCap,
Network_Access_Limits.Down_kbs AS DownCap,
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
Org_Value.Value AS ZoneType
FROM Zone_Plan_Account WITH (NOLOCK)
JOIN Member WITH (NOLOCK) ON Member.ID = Zone_Plan_Account.Member_ID
JOIN Member_Status WITH (NOLOCK) ON Member_Status.ID = Member.Member_Status_ID
JOIN Organization WITH (NOLOCK) ON Organization.ID = Member.Organization_ID
JOIN Zone_Plan WITH (NOLOCK) ON Zone_Plan.ID = Zone_Plan_Account.Zone_Plan_ID
JOIN Network_Access_Limits WITH (NOLOCK) ON Network_Access_Limits.ID = Zone_Plan_Account.Network_Access_Limits_ID
JOIN Payment_Method WITH (NOLOCK) ON Payment_Method.ID = Zone_Plan_Account.Payment_Method_ID
JOIN Currency WITH (NOLOCK) ON Currency.ID = Zone_Plan_Account.Purchase_Price_Currency_ID
JOIN Prepaid_Zone_Plan WITH (NOLOCK) ON Prepaid_Zone_Plan.Zone_Plan_ID = Zone_Plan.ID
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
WHERE Zone_Plan_Account.ID IS NOT NULL and Zone_Plan_Account.ID IN ({0})
ORDER BY Zone_Plan_Account.ID ASC"""
        q = q.format(','.join(ids))
        return q
