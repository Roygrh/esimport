USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Zone_Plan_Account_Promotional_Code'))
BEGIN
DROP TABLE [dbo].[Zone_Plan_Account_Promotional_Code]
END
GO

CREATE TABLE [dbo].[Zone_Plan_Account_Promotional_Code](
	[Zone_Plan_Account_ID] [int] NOT NULL,
	[Promotional_Code_ID] [int] NOT NULL,
 CONSTRAINT [PK_Zone_Plan_Account_Promotional_Code] PRIMARY KEY CLUSTERED 
(
	[Zone_Plan_Account_ID] ASC,
	[Promotional_Code_ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Zone_Plan_Account_Promotional_Code](Zone_Plan_Account_ID, Promotional_Code_ID)
	VALUES(1, 1)
INSERT INTO [dbo].[Zone_Plan_Account_Promotional_Code](Zone_Plan_Account_ID, Promotional_Code_ID)
	VALUES(2, 1)
INSERT INTO [dbo].[Zone_Plan_Account_Promotional_Code](Zone_Plan_Account_ID, Promotional_Code_ID)
	VALUES(3, 2)
INSERT INTO [dbo].[Zone_Plan_Account_Promotional_Code](Zone_Plan_Account_ID, Promotional_Code_ID)
	VALUES(4, 2)
INSERT INTO [dbo].[Zone_Plan_Account_Promotional_Code](Zone_Plan_Account_ID, Promotional_Code_ID)
	VALUES(7, 3)
INSERT INTO [dbo].[Zone_Plan_Account_Promotional_Code](Zone_Plan_Account_ID, Promotional_Code_ID)
	VALUES(8, 3)
GO