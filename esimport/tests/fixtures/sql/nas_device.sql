USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'NAS_Device'))
BEGIN
DROP TABLE [dbo].[NAS_Device]
END
GO

/****** Object:  Table [dbo].[NAS_Device]    Script Date: 4/26/2018 12:32:19 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[NAS_Device](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Net_MAC_Address] [varchar](64) NOT NULL,
    [NAS_Device_Type_ID] [int] NOT NULL,
    [NAS_ID] [varchar](64) NOT NULL,
    [Radius_NAS_ID] [varchar](128) NULL,
    [VLAN_Range_Start] [int] NOT NULL,
    [VLAN_Range_End] [int] NOT NULL,
    [Net_IP] [varchar](64) NULL,
    [Net_Hostname] [varchar](64) NULL,
    [Organization_ID] [int] NOT NULL
 CONSTRAINT [PK_NAS_Device] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]
--  CONSTRAINT [UQ_NAS_Device] UNIQUE NONCLUSTERED 
-- (
-- 	[UID] ASC
-- )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
-- ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

-- PUT DATA INSERT SCRIPTS BELOW
SET IDENTITY_INSERT NAS_Device ON
INSERT [dbo].[NAS_Device](ID,Net_MAC_Address,NAS_Device_Type_ID, NAS_ID, Radius_NAS_ID, VLAN_Range_Start, VLAN_Range_End, Net_IP,Net_Hostname, Organization_ID)
VALUES
    (7,'11:22:33:44:55:66', 3, '38ar722v-b312-9822-i91a-p319vv01d817', 'Lyndon*', 1000, 1234, NULL,'hostname', 5),
    (8,'00:11:22:33:44:55', 3, '9a9re98v-a939-3d68-cdo1-d38aiv83p377', 'Lyndon*', 100, 867, NULL,'hostname', 5),
    (9,'E8-1D-A8-20-1B-88:WOODSPRING_GUEST', 1, '092e8a67-b049-4e46-bbf9-b45dfe185f67', 'Lyndon*', 100, 867, NULL,'hostname', 1),
    (10,'00-50-E8-04-0F-0A',3, '083f4d87-a148-17a6-ebf1-b83go3b95g17', 'Lyndon*', 100, 867, NULL,'hostname', 2)
GO
-- ALTER TABLE [dbo].[NAS_Device] ADD  CONSTRAINT [DF_NAS_Device_VLAN_Range_Start]  DEFAULT ((0)) FOR [VLAN_Range_Start]
-- GO
-- ALTER TABLE [dbo].[NAS_Device] ADD  CONSTRAINT [DF_NAS_Device_VLAN_Range_End]  DEFAULT ((0)) FOR [VLAN_Range_End]
-- GO
-- ALTER TABLE [dbo].[NAS_Device] ADD  CONSTRAINT [DF_NAS_Device_Admin_Port]  DEFAULT (80) FOR [Admin_Port]
-- GOUSE [Eleven_OS]
-- GO
-- ALTER TABLE [dbo].[NAS_Device] ADD  CONSTRAINT [DF_NAS_Device_Subnet]  DEFAULT ((0)) FOR [Subnet]
-- GO
-- ALTER TABLE [dbo].[NAS_Device] ADD  CONSTRAINT [DF_NAS_Device_Mask]  DEFAULT ((0)) FOR [Mask]
-- GO
-- ALTER TABLE [dbo].[NAS_Device] ADD  CONSTRAINT [DF_NAS_Device_Erad_Dirty]  DEFAULT ((1)) FOR [Erad_Dirty]
-- GO
-- ALTER TABLE [dbo].[NAS_Device] ADD  CONSTRAINT [DF_NAS_Device_Auth_Unknown]  DEFAULT ((0)) FOR [Auth_Unknown]
-- GO
-- ALTER TABLE [dbo].[NAS_Device]  WITH CHECK ADD  CONSTRAINT [FK_NAS_Device_NAS_Device_Status] FOREIGN KEY([NAS_Device_Status_ID])
-- REFERENCES [dbo].[NAS_Device_Status] ([ID])
-- GO
-- ALTER TABLE [dbo].[NAS_Device] CHECK CONSTRAINT [FK_NAS_Device_NAS_Device_Status]
-- GO
-- ALTER TABLE [dbo].[NAS_Device]  WITH CHECK ADD  CONSTRAINT [FK_NAS_Device_NAS_Device_Type] FOREIGN KEY([NAS_Device_Type_ID])
-- REFERENCES [dbo].[NAS_Device_Type] ([ID])
-- GO
-- ALTER TABLE [dbo].[NAS_Device] CHECK CONSTRAINT [FK_NAS_Device_NAS_Device_Type]
-- GO
-- ALTER TABLE [dbo].[NAS_Device]  WITH CHECK ADD  CONSTRAINT [FK_NAS_Device_Organization] FOREIGN KEY([Organization_ID])
-- REFERENCES [dbo].[Organization] ([ID])
-- GO
-- ALTER TABLE [dbo].[NAS_Device] CHECK CONSTRAINT [FK_NAS_Device_Organization]
-- GO

-- BULK INSERT NAS_Device
-- FROM 'csv/nas_device.csv'
-- WITH (
-- 	FORMAT = 'CSV',
-- 	FIELDTERMINATOR = ','
-- )
