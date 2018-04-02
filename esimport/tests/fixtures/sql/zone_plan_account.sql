DROP TABLE [dbo].[Zone_Plan_Account]
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
 CONSTRAINT [PK_Zone_Plan_Account] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 100) ON [PRIMARY]
) ON [PRIMARY]

GO


-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC)
	VALUES(1, 1, 12.95, 1, 1, 1, '34-C0-59-D8-31-08', '2014-01-04 07:38:24.370', '2014-01-04 07:38:24.357')
INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC)
	VALUES(1, 1, 4, 1, 2, 1, '34-C0-59-D8-31-08', '2014-01-04 07:38:26.620',	'2014-01-04 07:38:26.607')
INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC)
	VALUES(1, 1, 12.95, 1, 3, 1, '34-C0-59-D8-31-08', '2014-01-05 07:43:03.940', '2014-01-05 07:43:03.933')
INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC)
	VALUES(1, 1, 12.95, 1, 4, 1, '4C-B1-99-0A-4A-96', '2014-01-04 07:38:52.080',	'2014-01-04 07:38:52.070')
INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC)
	VALUES(1, 1, 4, 1, 5, 1, '4C-B1-99-0A-4A-96', '2014-01-04 07:38:54.323', '2014-01-04 07:38:54.320')
INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC)
	VALUES(1, 1, 9.95, 1, 6, 1, '14-10-9F-DF-53-83', '2014-01-04 07:48:44.467', '2014-01-04 07:48:44.450')
INSERT INTO [dbo].[Zone_Plan_Account](Member_ID, Zone_Plan_ID, Purchase_Price, Purchase_Price_Currency_ID, Network_Access_Limits_ID, Payment_Method_ID, Purchase_MAC_Address, Activation_Date_UTC, Date_Created_UTC)
	VALUES(1, 1, 5, 1, 7, 1, '14-10-9F-DF-53-83', '2014-01-04 07:48:47.147', '2014-01-04 07:48:47.143')
GO