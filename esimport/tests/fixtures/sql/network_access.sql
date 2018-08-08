USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Network_Access'))
BEGIN
DROP TABLE [dbo].[Network_Access]
END
GO

CREATE TABLE [dbo].[Network_Access](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Network_Access_Limits_ID] [int] NOT NULL,
 CONSTRAINT [PK_Network_Access] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Network_Access](Network_Access_Limits_ID)
        VALUES(1)
INSERT INTO [dbo].[Network_Access](Network_Access_Limits_ID)
        VALUES(2)
INSERT INTO [dbo].[Network_Access](Network_Access_Limits_ID)
        VALUES(3)
INSERT INTO [dbo].[Network_Access](Network_Access_Limits_ID)
        VALUES(4)
