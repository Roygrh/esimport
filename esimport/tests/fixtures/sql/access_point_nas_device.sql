USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Access_Point_Nas_Device'))
BEGIN
DROP TABLE [dbo].[Access_Point_Nas_Device]
END
GO

/****** Object:  Table [dbo].[Access_Point_Nas_Device]    Script Date: 4/26/2018 12:32:14 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Access_Point_Nas_Device](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Net_MAC_Address] [varchar](64) NOT NULL,
	[Nas_Device_ID] [int] NOT NULL,
 CONSTRAINT [PK_Access_Point_Nas_Device] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]
GO

SET IDENTITY_INSERT Access_Point_Nas_Device ON
INSERT INTO [dbo].[Access_Point_Nas_Device] (ID, Net_MAC_Address, Nas_Device_ID) 
VALUES 
	(1, 'd2:90:1d:d0:0f:24', 7),
	(2, '69:15:8f:8f:2e:5d', 8),
	(3, 'fe:7a:82:14:59:95', 9),
	(4, 'e0:57:cd:2d:83:b5', 10)
GO

-- ALTER TABLE [dbo].[Access_Point_Nas_Device] ADD  CONSTRAINT [DF_Access_Point_Nas_Device_Erad_Dirty]  DEFAULT ((1)) FOR [Erad_Dirty]
-- GO
-- ALTER TABLE [dbo].[Access_Point_Nas_Device]  WITH CHECK ADD  CONSTRAINT [FK_Access_Point_Nas_Device_Nas_Device] FOREIGN KEY([Nas_Device_ID])
-- REFERENCES [dbo].[NAS_Device] ([ID])
-- GO
-- ALTER TABLE [dbo].[Access_Point_Nas_Device] CHECK CONSTRAINT [FK_Access_Point_Nas_Device_Nas_Device]
-- GO
