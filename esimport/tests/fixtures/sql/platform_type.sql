USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Platform_Type'))
BEGIN
DROP TABLE [dbo].[Platform_Type]
END
GO

/****** Object:  Table [dbo].[Platform_Type]    Script Date: 4/26/2018 12:32:22 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Platform_Type](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Name] [varchar](64) NOT NULL,
 CONSTRAINT [PK_Platform_Type] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

SET IDENTITY_INSERT [dbo].[Platform_Type] ON;

INSERT INTO [dbo].[Platform_Type] (ID, Name)
VALUES 
	(1, 'Platform 1'),
	(2, 'Platform 2')
GO
--  CONSTRAINT [UQ_Platform_Type_Name] UNIQUE NONCLUSTERED 
-- (
-- 	[Name] ASC
-- )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
-- ) ON [PRIMARY]
-- GO
