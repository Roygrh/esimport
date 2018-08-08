USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Scheduled_Access_Member'))
BEGIN
DROP TABLE [dbo].[Scheduled_Access_Member]
END
GO

CREATE TABLE [dbo].[Scheduled_Access_Member](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Scheduled_Access_ID] [int] NOT NULL,
	[Member_ID] [int] NOT NULL,
 CONSTRAINT [PK_Scheduled_Access_Member] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]
GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Scheduled_Access_Member](Scheduled_Access_ID, Member_ID)
	VALUES(1, 1)
INSERT INTO [dbo].[Scheduled_Access_Member](Scheduled_Access_ID, Member_ID)
	VALUES(2, 2)
INSERT INTO [dbo].[Scheduled_Access_Member](Scheduled_Access_ID, Member_ID)
	VALUES(3, 3)
INSERT INTO [dbo].[Scheduled_Access_Member](Scheduled_Access_ID, Member_ID)
	VALUES(4, 4)
