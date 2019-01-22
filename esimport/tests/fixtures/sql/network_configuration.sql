USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Network_Configuration'))
BEGIN
DROP TABLE [dbo].[Network_Configuration]
END
GO

CREATE TABLE [dbo].[Network_Configuration](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Scheduled_Access_ID] [int] NOT NULL,
	[SsidName] [varchar](32) NULL,
 CONSTRAINT [PK_Network_Configuration] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]
GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Network_Configuration](Scheduled_Access_ID, SsidName)
	VALUES(1, 'SSID1')
INSERT INTO [dbo].[Network_Configuration](Scheduled_Access_ID, SsidName)
	VALUES(2, 'SSID2')
INSERT INTO [dbo].[Network_Configuration](Scheduled_Access_ID, SsidName)
	VALUES(3, 'SSID3')
INSERT INTO [dbo].[Network_Configuration](Scheduled_Access_ID, SsidName)
	VALUES(4, 'SSID4')
