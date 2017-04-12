import six
import json
import logging

from esimport import settings
from esimport.models import ESRecord
from esimport.models.base import BaseModel


logger = logging.getLogger(__name__)


class Account(BaseModel):


    _type = "account"
    @staticmethod
    def get_type():
        return Account._type


    def get_accounts(self, start, limit, start_date='1900-01-01'):
        q = self.eleven_query(start_date, start, limit)
        for row in self.fetch(q):
            rec = {
                "ID": long(row.ID) if six.PY2 else int(row.ID),
                "Name": row.Name,
                "Created": row.Created,
                "Activated": row.Activated,
                "ServiceArea": row.ServiceArea,
                "Price": str(row.Price) + str(row.Currency),
                "PurchaseMacAddress": row.PurchaseMacAddress,  # PII
                "ServicePlan" : row.ServicePlan,
                "ServicePlanNumber": row.ServicePlanNumber,
                "UpCap": row.UpCap,
                "DownCap": row.DownCap,
                "CreditCardNumber": row.CreditCardNumber,
                "CardType": row.CardType,
                "LastName": row.LastName,
                "RoomNumber": row.RoomNumber,
                "AccessCodeUsed": row.AccessCodeUsed,
                "PayMethod": row.PayMethod,
                "ZoneType": row.ZoneType,
                "DiscountCode": row.DiscountCode,
                "ConsumableTime": row.ConsumableTime,
                "ConsumableUnit": row.ConsumableUnit,
                "SpanTime": row.SpanTime,
                "SpanUnit": row.SpanUnit,
                "Duration": self.find_duration(row)
            }
            yield ESRecord(rec, self.get_type())


    @property
    def action(self):
        action = {
            "_op_type": "update",
            "_index": settings.ES_INDEX,
            "_type": self.get_type(),
            "_id": self.ID,
            "doc_as_upsert": True
        }
        return action

    @staticmethod
    def make_json(unique_id, doc):
        _json_ = {
            "_op_type": "update",
            "_index": settings.ES_INDEX,
            "_type": Account.get_type(),
            "_id": unique_id,
            "doc_as_upsert": True,
            "doc": doc
        }
        return _json_

    def find_duration(self, row):
        if row.ConsumableTime is not None:
            return "{0} {1} {2}".format(row.ConsumableTime, row.ConsumableUnit, "consumable")
        if row.SpanTime is not None:
            return "{0} {1}".format(row.SpanTime, row.SpanUnit)
        else:
            return None

    def pay_details(self):
        if self.PayMethod is "CC":
            return "{0}{1}".format(self.CardType, self.CreditCardNumber)
        if self.PayMethod is "PMS":
            return "PMS {0}/{1}".format(self.LastName, self.RoomNumber)
        if self.PayMethod is "AC":
            return "Access Code: {0}".format(self.AccessCodeUsed)
        if self.PayMethod is "FREE":
            return "FREE"
        else:
            return self.PayMethod

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4, encoding='latin1')

    @staticmethod
    def eleven_query(start_date, start_zpa_id, limit):
        q = """Select TOP {1} Zone_Plan_Account.ID as ID,
Member.Display_Name AS Name,
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
Access_Code.Access_Code_String AS AccessCodeUsed,
Promotional_Code.Code AS DiscountCode,
Prepaid_Zone_Plan.Consumable_Time AS ConsumableTime,
CTU.Name AS ConsumableUnit,
Prepaid_Zone_Plan.Lifespan_Time AS SpanTime,
STU.Name AS SpanUnit,
Org_Value.Value AS ZoneType
FROM Zone_Plan_Account
JOIN Member ON Member.ID = Zone_Plan_Account.Member_ID
JOIN Organization ON Organization.ID = Zone_Plan_Account.Purchase_Org_ID
JOIN Zone_Plan ON Zone_Plan.ID = Zone_Plan_Account.Zone_Plan_ID
JOIN Network_Access_Limits ON Network_Access_Limits.ID = Zone_Plan_Account.Network_Access_Limits_ID
JOIN Payment_Method ON Payment_Method.ID = Zone_Plan_Account.Payment_Method_ID
JOIN Currency ON Currency.ID = Zone_Plan_Account.Purchase_Price_Currency_ID
JOIN Prepaid_Zone_Plan ON Prepaid_Zone_Plan.Zone_Plan_ID = Zone_Plan.ID
LEFT JOIN Credit_Card ON Credit_Card.ID = Zone_Plan_Account.Credit_Card_ID
LEFT JOIN Credit_Card_Type ON Credit_Card_Type.ID = Credit_Card.Credit_Card_Type_ID
LEFT JOIN PMS_Charge ON PMS_Charge.ID = Zone_Plan_Account.PMS_Charge_ID
LEFT JOIN Access_Code ON Access_Code.ID = Zone_Plan_Account.Access_Code_ID
LEFT JOIN Zone_Plan_Account_Promotional_Code ON Zone_Plan_Account_Promotional_Code.Zone_Plan_Account_ID = Zone_Plan_Account.ID
LEFT JOIN Promotional_Code ON Promotional_Code.ID = Zone_Plan_Account_Promotional_Code.Promotional_Code_ID
LEFT JOIN Time_Unit AS CTU ON CTU.ID = Prepaid_Zone_Plan.Consumable_Time_Unit_ID
LEFT JOIN Time_Unit AS STU ON STU.ID = Prepaid_Zone_Plan.Lifespan_Time_Unit_ID
LEFT JOIN Org_Value ON Org_Value.Organization_ID = Organization.ID AND Org_Value.Name='ZoneType'
WHERE Zone_Plan_Account.ID >= {0} AND Zone_Plan_Account.Date_Created_UTC >= '{2}'
ORDER BY Zone_Plan_Account.ID ASC"""
        q = q.format(start_zpa_id, limit, start_date)
        return q


    @staticmethod
    def query_records_by_zpa_id(ids):
        q = """Select Zone_Plan_Account.ID as ID,
Member.Display_Name AS Name,
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
Access_Code.Access_Code_String AS AccessCodeUsed,
Promotional_Code.Code AS DiscountCode,
Prepaid_Zone_Plan.Consumable_Time AS ConsumableTime,
CTU.Name AS ConsumableUnit,
Prepaid_Zone_Plan.Lifespan_Time AS SpanTime,
STU.Name AS SpanUnit,
Org_Value.Value AS ZoneType
FROM Zone_Plan_Account
JOIN Member ON Member.ID = Zone_Plan_Account.Member_ID
JOIN Organization ON Organization.ID = Zone_Plan_Account.Purchase_Org_ID
JOIN Zone_Plan ON Zone_Plan.ID = Zone_Plan_Account.Zone_Plan_ID
JOIN Network_Access_Limits ON Network_Access_Limits.ID = Zone_Plan_Account.Network_Access_Limits_ID
JOIN Payment_Method ON Payment_Method.ID = Zone_Plan_Account.Payment_Method_ID
JOIN Currency ON Currency.ID = Zone_Plan_Account.Purchase_Price_Currency_ID
JOIN Prepaid_Zone_Plan ON Prepaid_Zone_Plan.Zone_Plan_ID = Zone_Plan.ID
LEFT JOIN Credit_Card ON Credit_Card.ID = Zone_Plan_Account.Credit_Card_ID
LEFT JOIN Credit_Card_Type ON Credit_Card_Type.ID = Credit_Card.Credit_Card_Type_ID
LEFT JOIN PMS_Charge ON PMS_Charge.ID = Zone_Plan_Account.PMS_Charge_ID
LEFT JOIN Access_Code ON Access_Code.ID = Zone_Plan_Account.Access_Code_ID
LEFT JOIN Zone_Plan_Account_Promotional_Code ON Zone_Plan_Account_Promotional_Code.Zone_Plan_Account_ID = Zone_Plan_Account.ID
LEFT JOIN Promotional_Code ON Promotional_Code.ID = Zone_Plan_Account_Promotional_Code.Promotional_Code_ID
LEFT JOIN Time_Unit AS CTU ON CTU.ID = Prepaid_Zone_Plan.Consumable_Time_Unit_ID
LEFT JOIN Time_Unit AS STU ON STU.ID = Prepaid_Zone_Plan.Lifespan_Time_Unit_ID
LEFT JOIN Org_Value ON Org_Value.Organization_ID = Organization.ID AND Org_Value.Name='ZoneType'
WHERE Zone_Plan_Account.ID IS NOT NULL and Zone_Plan_Account.ID IN ({0})
ORDER BY Zone_Plan_Account.ID ASC"""
        q = q.format(','.join(ids))
        return q
