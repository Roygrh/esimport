USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Client_Device_Type'))
BEGIN
DROP TABLE [dbo].[Client_Device_Type]
END
GO

/****** Object:  Table [dbo].[Client_Device_Type]    Script Date: 4/26/2018 12:32:14 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Client_Device_Type](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Name] [varchar](64) NOT NULL,
 CONSTRAINT [PK_Client_Device_Type] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

SET IDENTITY_INSERT [dbo].[Client_Device_Type] ON;

INSERT INTO [dbo].[Client_Device_Type] (ID, Name)
VALUES 
	(1, 'Client Device Type 1'),
	(2, 'Client Device Type 2')
GO

--  CONSTRAINT [UQ_Client_Device_Type_Name] UNIQUE NONCLUSTERED 
-- (
-- 	[Name] ASC
-- )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
-- ) ON [PRIMARY]
-- GO
