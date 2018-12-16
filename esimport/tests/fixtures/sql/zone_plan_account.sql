USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Zone_Plan_Account'))
BEGIN
DROP TABLE [dbo].[Zone_Plan_Account]
END
GO

CREATE TABLE [dbo].[Zone_Plan_Account](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Member_ID] [int] NOT NULL,
	[Zone_Plan_ID] [int] NOT NULL,
	[Purchase_Price] [money] NOT NULL,
	[Purchase_Price_Currency_ID] [int] NOT NULL,
	[Network_Access_Limits_ID] [int] NOT NULL,
	[Payment_Method_ID] [int] NOT NULL,
	[Purchase_MAC_Address] [varchar](64) NULL,
	[Credit_Card_ID] [int] NULL,
	[PMS_Charge_ID] [int] NULL,
	[Date_Created_UTC] [datetime] NULL,
	[Activation_Date_UTC] [datetime] NULL,
	[Code_ID] [int] NULL,
	[Date_Modified_UTC] [datetime] NULL,
	[Zone_Plan_Account_Status_ID] [int] NOT NULL,
 CONSTRAINT [PK_Zone_Plan_Account] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 100) ON [PRIMARY]
) ON [PRIMARY]

GO

-- Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, 
-- Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC, Date_Modified_UTC

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC, Date_Modified_UTC, PMS_Charge_ID, Zone_Plan_Account_Status_ID)
VALUES
	(1, 1, 12.95, 1, 1, 1, '34-C0-59-D8-31-08', '2014-01-04 07:38:24.370', '2014-01-04 07:38:24.357', '2018-04-05 10:31:46.768', 1, 1),
	(2, 1, 12.95, 1, 5, 1, '4C-B1-99-0A-4A-96', '2014-01-04 07:38:52.080', '2014-01-04 07:38:52.070', '2018-04-05 10:32:45.537', 2, 1),
	(3, 2, 5, 1, 8, 1, '14-10-9F-DF-53-83', '2018-06-27 22:24:11:147', '2014-01-04 07:48:47.143', '2018-04-05 10:33:19.594', 3, 1)
GO

-- INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC, Date_Modified_UTC, PMS_Charge_ID, Zone_Plan_Account_Status_ID)
-- 	VALUES(1, 2, 4, 1, 2, 1, '34-C0-59-D8-31-08', '2014-01-04 07:38:26.620', '2014-01-04 07:38:26.607', '2018-04-05 10:31:58.679', 1, 1)
-- INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC, Date_Modified_UTC, PMS_Charge_ID, Zone_Plan_Account_Status_ID)
-- 	VALUES(1, 1, 12.95, 1, 3, 1, '34-C0-59-D8-31-08', '2014-01-05 07:43:03.940', '2014-01-05 07:43:03.933', '2018-04-05 10:32:14.551', 1, 1)
-- INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC, Date_Modified_UTC, PMS_Charge_ID, Zone_Plan_Account_Status_ID)
-- 	VALUES(1, 2, 4, 1, 4, 1, '34-C0-59-D8-31-08', '2014-01-05 07:43:06.507', '2014-01-05 07:43:06.490', '2018-04-05 10:32:28.728', 1, 1)
-- INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC, Date_Modified_UTC, PMS_Charge_ID, Zone_Plan_Account_Status_ID)
-- 	VALUES(2, 1, 12.95, 1, 5, 1, '4C-B1-99-0A-4A-96', '2014-01-04 07:38:52.080', '2014-01-04 07:38:52.070', '2018-04-05 10:32:45.537', 2, 1)
-- INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC, Date_Modified_UTC, PMS_Charge_ID, Zone_Plan_Account_Status_ID)
-- 	VALUES(2, 2, 4, 1, 6, 1, '4C-B1-99-0A-4A-96', '2014-01-04 07:38:54.323', '2014-01-04 07:38:54.320', '2018-04-05 10:32:56.841', 2, 1)
-- INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC, Date_Modified_UTC, PMS_Charge_ID, Zone_Plan_Account_Status_ID)
-- 	VALUES(3, 1, 9.95, 1, 7, 1, '14-10-9F-DF-53-83', '2014-01-04 07:48:44.467', '2014-01-04 07:48:44.450', '2018-04-05 10:33:09.034', 3, 1)
-- INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC, Date_Modified_UTC, PMS_Charge_ID, Zone_Plan_Account_Status_ID)
-- 	VALUES(3, 2, 5, 1, 8, 1, '14-10-9F-DF-53-83', '2014-01-04 07:48:47.147', '2014-01-04 07:48:47.143', '2018-04-05 10:33:19.594', 3, 1)
-- GO