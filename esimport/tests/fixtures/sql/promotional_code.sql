USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Promotional_Code'))
BEGIN
DROP TABLE [dbo].[Promotional_Code]
END
GO


CREATE TABLE [dbo].[Promotional_Code](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Code] [varchar](128) NOT NULL,
 CONSTRAINT [PK_Promotional_Code] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]

GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Promotional_Code](Code)
	VALUES('DC03')
INSERT INTO [dbo].[Promotional_Code](Code)
	VALUES('HALFOFF')
INSERT INTO [dbo].[Promotional_Code](Code)
	VALUES('INTEL')
GO