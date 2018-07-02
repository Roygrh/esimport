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
	[UID] [uniqueidentifier] NOT NULL,
	[Organization_ID] [int] NOT NULL,
	[NAS_ID] [varchar](64) NOT NULL,
	[Net_MAC_Address] [varchar](64) NOT NULL,
	[VLAN_Range_Start] [int] NOT NULL,
	[VLAN_Range_End] [int] NOT NULL,
	[Radius_NAS_ID] [varchar](128) NULL,
	[Net_IP] [varchar](64) NULL,
	[Routable_Net_IP] [varchar](64) NULL,
	[Net_Hostname] [varchar](256) NULL,
	[Subscriber_IP] [varchar](64) NULL,
	[Routable_Subscriber_IP] [varchar](64) NULL,
	[Subscriber_Hostname] [varchar](256) NULL,
	[Subnet_Mask] [varchar](64) NULL,
	[Gateway_IP] [varchar](64) NULL,
	[Admin_Username] [varchar](32) NULL,
	[Admin_Password] [varchar](32) NULL,
	[Admin_Port] [int] NULL,
	[NAS_Device_Status_ID] [int] NOT NULL,
	[NAS_Device_Type_ID] [int] NOT NULL,
	[PMS_Meta_Refresh_Enabled] [bit] NULL,
	[PMS_Auth_Expiry_Seconds] [int] NULL,
	[PMS_Auth_Timeout_Seconds] [int] NULL,
	[PMS_Auth_Retry_Delay_Seconds] [int] NULL,
	[PMS_Meta_Refresh_Expiry_Seconds] [int] NULL,
	[PMS_Meta_Refresh_Delay_Seconds] [int] NULL,
	[Subnet] [int] NOT NULL,
	[Mask] [int] NOT NULL,
	[SNMP_IP] [varchar](64) NULL,
	[SNMP_Port] [int] NULL,
	[SNMP_Read_Community] [varchar](128) NULL,
	[SNMP_Write_Community] [varchar](128) NULL,
	[SNMP_User] [varchar](128) NULL,
	[SNMP_Auth_Phrase] [varchar](128) NULL,
	[SNMP_Privacy_Phrase] [varchar](128) NULL,
	[Needs_Reboot] [bit] NULL,
	[Telnet_IP] [varchar](64) NULL,
	[Telnet_Port] [int] NULL,
	[Local_User] [varchar](128) NULL,
	[Local_Password] [varchar](128) NULL,
	[SSH_IP] [varchar](64) NULL,
	[SSH_Port] [int] NULL,
	[Erad_Dirty] [bit] NOT NULL,
	[Match_To_Identifier] [bit] NULL,
	[RADIUS_DM_Port] [int] NULL,
	[Auth_Unknown] [bit] NOT NULL,
	[Blob] [varchar](max) NULL,
	[RADIUS_DM_Hostname] [varchar](256) NULL)
--  CONSTRAINT [PK_NAS_Device] PRIMARY KEY CLUSTERED 
-- (
-- 	[ID] ASC
-- )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY],
--  CONSTRAINT [UQ_NAS_Device] UNIQUE NONCLUSTERED 
-- (
-- 	[UID] ASC
-- )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
-- ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

-- PUT DATA INSERT SCRIPTS BELOW
SET IDENTITY_INSERT NAS_Device ON
INSERT [dbo].[NAS_Device](ID,UID,Organization_ID,NAS_ID,Net_MAC_Address,VLAN_Range_Start,VLAN_Range_End,Radius_NAS_ID,Net_IP,Routable_Net_IP,Net_Hostname,Subscriber_IP,Routable_Subscriber_IP,Subscriber_Hostname,Subnet_Mask,Gateway_IP,Admin_Username,Admin_Password,Admin_Port,NAS_Device_Status_ID,NAS_Device_Type_ID,PMS_Meta_Refresh_Enabled,PMS_Auth_Expiry_Seconds,PMS_Auth_Timeout_Seconds,PMS_Auth_Retry_Delay_Seconds,PMS_Meta_Refresh_Expiry_Seconds,PMS_Meta_Refresh_Delay_Seconds,Subnet,Mask,SNMP_IP,SNMP_Port,SNMP_Read_Community,SNMP_Write_Community,SNMP_User,SNMP_Auth_Phrase,SNMP_Privacy_Phrase,Needs_Reboot,Telnet_IP,Telnet_Port,Local_User,Local_Password,SSH_IP,SSH_Port,Erad_Dirty,Match_To_Identifier,RADIUS_DM_Port,Auth_Unknown,Blob,RADIUS_DM_Hostname)
VALUES (9,'A20D3427-65B2-4A4D-9373-8DAC14359428',22,'020007','E8-1D-A8-20-1B-88:WOODSPRING_GUEST',0,0,'Hotel Eleven','131.252.16.72',NULL,NULL,'67.50.162.71',NULL,NULL,'255.255.255.224','67.50.162.65','11admin','w!f!eleven',80,3,1,NULL,NULL,NULL,NULL,NULL,NULL,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,0,NULL,NULL)
INSERT [dbo].[NAS_Device](ID,UID,Organization_ID,NAS_ID,Net_MAC_Address,VLAN_Range_Start,VLAN_Range_End,Radius_NAS_ID,Net_IP,Routable_Net_IP,Net_Hostname,Subscriber_IP,Routable_Subscriber_IP,Subscriber_Hostname,Subnet_Mask,Gateway_IP,Admin_Username,Admin_Password,Admin_Port,NAS_Device_Status_ID,NAS_Device_Type_ID,PMS_Meta_Refresh_Enabled,PMS_Auth_Expiry_Seconds,PMS_Auth_Timeout_Seconds,PMS_Auth_Retry_Delay_Seconds,PMS_Meta_Refresh_Expiry_Seconds,PMS_Meta_Refresh_Delay_Seconds,Subnet,Mask,SNMP_IP,SNMP_Port,SNMP_Read_Community,SNMP_Write_Community,SNMP_User,SNMP_Auth_Phrase,SNMP_Privacy_Phrase,Needs_Reboot,Telnet_IP,Telnet_Port,Local_User,Local_Password,SSH_IP,SSH_Port,Erad_Dirty,Match_To_Identifier,RADIUS_DM_Port,Auth_Unknown,Blob,RADIUS_DM_Hostname)
VALUES (10,'1A16206A-D3CA-4143-9EE9-6D6E4D129BA1',23,'001558','00-50-E8-04-0F-0A',0,0,'Eleven Wireless: Testing',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,80,1,1,NULL,NULL,NULL,NULL,NULL,NULL,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,0,NULL,NULL)
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