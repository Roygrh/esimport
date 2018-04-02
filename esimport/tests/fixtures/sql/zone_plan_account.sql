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