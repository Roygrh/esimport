USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Time_Unit'))
BEGIN
DROP TABLE [dbo].[Time_Unit]
END
GO

CREATE TABLE [dbo].[Time_Unit](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Name] [varchar](64) NOT NULL,
 CONSTRAINT [PK_Time_Unit] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO


-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Time_Unit](Name)
	VALUES('Days')
INSERT INTO [dbo].[Time_Unit](Name)
	VALUES('Minutes')
INSERT INTO [dbo].[Time_Unit](Name)
	VALUES('Hours')
INSERT INTO [dbo].[Time_Unit](Name)
	VALUES('Weeks')
GO