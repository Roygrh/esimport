USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Zone_Plan'))
BEGIN
DROP TABLE [dbo].[Zone_Plan]
END
GO

CREATE TABLE [dbo].[Zone_Plan](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Plan_Number] [varchar](64) NOT NULL,
	[Name] [varchar](64) NOT NULL,
	[Zone_Plan_Status_ID] [int] NOT NULL,
	[Zone_Plan_Type_ID] [int] NOT NULL,
	[Network_Access_Limits_ID] [int] NOT NULL,
	[Price_Currency_ID] [int] NOT NULL,
	[Org_Zone_ID] [int] NOT NULL,
	[Description] [varchar](1024) NOT NULL,
	[Price] [money] NOT NULL,
	[Date_Created_UTC] [datetime] NOT NULL,
 CONSTRAINT [PK_Zone_Plan] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

-- PUT DATA INSERT SCRIPTS BELOW
SET IDENTITY_INSERT Zone_Plan ON
INSERT INTO [dbo].[Zone_Plan](ID, Plan_Number, Name, Zone_Plan_Status_ID, Zone_Plan_Type_ID, Network_Access_Limits_ID, Price_Currency_ID, Org_Zone_ID, Description, Price, Date_Created_UTC)
VALUES
	(1, 'basic_day_01', 'basic day', 1, 1, 1, 1, 1, 'Description 1', 20, '2019-02-05 10:22:24.357'),
	(2, 'prem_day_01', 'premium day', 2, 2, 1, 1, 2, 'Description 2', 15, '2019-02-05 10:30:15.421')
GO