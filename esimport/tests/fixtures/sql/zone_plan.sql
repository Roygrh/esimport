-- DROP TABLE [dbo].[Zone_Plan]
-- GO

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
 CONSTRAINT [PK_Zone_Plan] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Zone_Plan](Plan_Number, Name)
	VALUES('basic_day_01', 'basic day')
INSERT INTO [dbo].[Zone_Plan](Plan_Number, Name)
	VALUES('prem_day_01', 'premium day')
GO