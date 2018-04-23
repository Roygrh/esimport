-- DROP TABLE [dbo].[Network_Access_Limits]
-- GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Network_Access_Limits'))
BEGIN
DROP TABLE [dbo].[Network_Access_Limits]
END
GO

CREATE TABLE [dbo].[Network_Access_Limits](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Up_kbs] [int] NULL,
	[Down_kbs] [int] NULL,
 CONSTRAINT [PK_Network_Access_Limits] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 100) ON [PRIMARY]
) ON [PRIMARY]

GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Network_Access_Limits](Up_kbs, Down_kbs)
	VALUES(4096, 4096)
INSERT INTO [dbo].[Network_Access_Limits](Up_kbs, Down_kbs)
	VALUES(12288, 12288)
INSERT INTO [dbo].[Network_Access_Limits](Up_kbs, Down_kbs)
	VALUES(4096, 4096)
INSERT INTO [dbo].[Network_Access_Limits](Up_kbs, Down_kbs)
	VALUES(12288, 12288)		
INSERT INTO [dbo].[Network_Access_Limits](Up_kbs, Down_kbs)
	VALUES(4096, 4096)
INSERT INTO [dbo].[Network_Access_Limits](Up_kbs, Down_kbs)
	VALUES(12288, 12288)
INSERT INTO [dbo].[Network_Access_Limits](Up_kbs, Down_kbs)
	VALUES(2304, 2304)
INSERT INTO [dbo].[Network_Access_Limits](Up_kbs, Down_kbs)
	VALUES(6096, 6096)
GO