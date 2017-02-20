# ######################################################################################################################
#
# Python2.7 Script: account.py
#
# Purpose: Account Index
#
# Author: Sean P. Parker
# Created: October 2016
# Updated: January 2017
#
# Copyright @ 2017 Eleven Wireless Inc.
#
# ######################################################################################################################
import json


class Account:
    # Initialize from MsSql row
    def __init__(self, row):
        self.Name = row.Name
        self.Timestamp = row.Timestamp.isoformat()
        self.Property = row.Property
        self.Price = str(row.Price) + str(row.Currency)
        self.PurchaseMacAddress = row.PurchaseMacAddress
        self.UpCap = row.UpCap
        self.DownCap = row.DownCap
        self.CreditCardNumber = row.CreditCardNumber
        self.CardType = row.CardType
        self.LastName = row.LastName
        self.RoomNumber = row.RoomNumber
        self.AccessCodeUsed = row.AccessCodeUsed
        self.PayMethod = self.find_pay_method()
        self.Tax = self.Tax()
        self.LoyaltyTier = self.LoyaltyTier()
        self.LoyaltyNumber = self.LoyaltyNumber()

    def __str__(self):
        return "{0} at {1} created {2}. Purchased via {3} for {4}. {5}up/{6}down".format(self.Name, self.Property,
                                                                                         self.Timestamp,
                                                                                         self.pay_details(), self.Price,
                                                                                         self.UpCap,
                                                                                         self.DownCap)

    def action(self):
        action = {
                "_index": "elevenos",
                "_type": "account",
                "_source":
                    {
                        "Name": self.Name,
                        "Timestamp": self.Timestamp,
                        "Property": self.Property,
                        "Price": self.Price,
                        "PurchaseMacAddress": self.PurchaseMacAddress,  # PII
                        "UpCap": self.UpCap,
                        "DownCap": self.DownCap,
                        "CreditCardNumber": self.CreditCardNumber,
                        "CardType": self.CardType,
                        "LastName": self.LastName,
                        "RoomNumber": self.RoomNumber,
                        "AccessCodeUsed": self.AccessCodeUsed,
                        "PayMethod": self.PayMethod,
                        "Tax": self.Tax,
                        "LoyaltyTier": self.LoyaltyTier,
                        "LoyaltyNumber": self.LoyaltyNumber
                    }
            }
        return action

    def find_pay_method(self):
        if self.CreditCardNumber is not None:
            return "Credit Card"
        if self.LastName is not None:
            return "PMS"
        if self.AccessCodeUsed is not None:
            return "Access Code"
        else:
            return "Free"

    def pay_details(self):
        if self.PayMethod is "Credit Card":
            return "{0}{1}".format(self.CardType, self.CreditCardNumber)
        if self.PayMethod is "PMS":
            return "PMS {0}/{1}".format(self.LastName, self.RoomNumber)
        if self.PayMethod is "Access Code":
            return "Access Code: {0}".format(self.AccessCodeUsed)
        if self.PayMethod is "Free":
            return "FREE"

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4, encoding='latin1')

    @staticmethod
    def eleven_query(lower, upper):
        q = """Select Zone_Plan_Account.ID as ID,
Member.Name as Name,
Organization.Number as Property,
Zone_Plan_Account.Purchase_Price as Price,
Zone_Plan_Account.Purchase_MAC_Address as PurchaseMacAddress,
Zone_Plan_Account.Activation_Date_UTC Activated,
Zone_Plan_Account.Date_Created_UTC Created,
Network_Access_Limits.Up_kbs as UpCap,
Network_Access_Limits.Down_kbs as DownCap,
Currency.Code as Currency,
Credit_Card.Masked_Number as CreditCardNumber,
Credit_Card_Type.Name as CardType,
PMS_Charge.Last_Name as LastName,
PMS_Charge.Room_Number as RoomNumber,
Access_Code.Access_Code_String as AccessCodeUsed
From Member
Left Join Organization on Organization.ID = Member.Organization_ID
Left Join Zone_Plan_Account on Zone_Plan_Account.Member_ID = Member.ID
Left Join Zone_Plan on Zone_Plan.ID = Zone_Plan_Account.Zone_Plan_ID
Left Join Network_Access_Limits on Network_Access_Limits.ID = Zone_Plan.Network_Access_Limits_ID
Left Join Currency on Currency.ID = Zone_Plan_Account.Purchase_Price_Currency_ID
Left Join Credit_Card on Credit_Card.ID = Zone_Plan_Account.Credit_Card_ID
Left Join Credit_Card_Type on Credit_Card_Type.ID = Credit_Card.Credit_Card_Type_ID
Left Join PMS_Charge on PMS_Charge.ID = Zone_Plan_Account.PMS_Charge_ID
Left Join Access_Code on Access_Code.ID = Zone_Plan_Account.Access_Code_ID
Where Member.ID >= {0} and Member.ID <= {1}"""
        q = q.format(lower, upper)
        return q
