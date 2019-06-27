USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Client_Tracking'))
BEGIN
DROP TABLE [dbo].[Client_Tracking]
END
GO

/****** Object:  Table [dbo].[Client_Tracking]    Script Date: 4/26/2018 12:32:14 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Client_Tracking](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Date] [datetime] NULL,
	[Organization_ID] [int] NULL,
	[IP_Address] [varchar](64) NOT NULL,
	[MAC_Address] [varchar](64) NOT NULL,
	[Platform_Type_ID] [int] NULL,
	[Browser_Type_ID] [int] NULL,
	[Member_ID] [int] NULL,
	[Client_Device_Type_ID] [int] NULL,
	[User_Agent_Raw] [varchar](512) NULL,
 CONSTRAINT [PK_Client_Tracking] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

-- SET IDENTITY_INSERT [dbo].[Client_Tracking] ON;
--
-- INSERT INTO [dbo].[Client_Tracking] (ID, Date, Organization_ID, IP_Address, MAC_Address, Platform_Type_ID, Browser_Type_ID, Member_ID, Client_Device_Type_ID, User_Agent_Raw)
-- VALUES
-- 	(1, '2014-01-04 07:38:24.370', 1, '172.168.1.11', '62:8D:2F:6A:F0:78', 1, 1, 1, 1, 'Chrome/60.0.3112.113'),
-- 	(2, '2014-01-04 08:40:24.370', 2, '172.168.1.12', 'F5:C4:05:2A:D4:9A', 2, 2, 2, 2, 'Gecko/20070802 Firefox'),
-- 	(3, '2014-01-04 08:45:24.370', 3, '172.168.1.15', 'F0:6D:3D:7B:66:F4', 1, 1, 3, 1, 'Chrome/60.0.3112.113'),
-- 	(4, '2014-01-04 09:50:24.370', 4, '172.168.1.21', '94:4B:F5:7C:FC:8E', 2, 2, 1, 2, 'Gecko/20070802 Firefox')
-- GO
-- ALTER TABLE [dbo].[Client_Tracking] ADD  CONSTRAINT [DF_Client_Tracking_Date]  DEFAULT (getdate()) FOR [Date]
-- GO
-- ALTER TABLE [dbo].[Client_Tracking] ADD  CONSTRAINT [DF_Client_Tracking_Date_UTC]  DEFAULT (getutcdate()) FOR [Date_UTC]
-- GO
-- ALTER TABLE [dbo].[Client_Tracking]  WITH CHECK ADD  CONSTRAINT [FK_Client_Tracking_Browser_Type] FOREIGN KEY([Browser_Type_ID])
-- REFERENCES [dbo].[Browser_Type] ([ID])
-- GO
-- ALTER TABLE [dbo].[Client_Tracking] CHECK CONSTRAINT [FK_Client_Tracking_Browser_Type]
-- GO
-- ALTER TABLE [dbo].[Client_Tracking]  WITH CHECK ADD  CONSTRAINT [FK_Client_Tracking_Client_Device_Type] FOREIGN KEY([Client_Device_Type_ID])
-- REFERENCES [dbo].[Client_Device_Type] ([ID])
-- GO
-- ALTER TABLE [dbo].[Client_Tracking] CHECK CONSTRAINT [FK_Client_Tracking_Client_Device_Type]
-- GO
-- ALTER TABLE [dbo].[Client_Tracking]  WITH CHECK ADD  CONSTRAINT [FK_Client_Tracking_Client_Tracking_Type] FOREIGN KEY([Client_Tracking_Type_ID])
-- REFERENCES [dbo].[Client_Tracking_Type] ([ID])
-- GO
-- ALTER TABLE [dbo].[Client_Tracking] CHECK CONSTRAINT [FK_Client_Tracking_Client_Tracking_Type]
-- GO
-- ALTER TABLE [dbo].[Client_Tracking]  WITH CHECK ADD  CONSTRAINT [FK_Client_Tracking_Member] FOREIGN KEY([Member_ID])
-- REFERENCES [dbo].[Member] ([ID])
-- GO
-- ALTER TABLE [dbo].[Client_Tracking] CHECK CONSTRAINT [FK_Client_Tracking_Member]
-- GO
-- ALTER TABLE [dbo].[Client_Tracking]  WITH CHECK ADD  CONSTRAINT [FK_Client_Tracking_Organization] FOREIGN KEY([Organization_ID])
-- REFERENCES [dbo].[Organization] ([ID])
-- GO
-- ALTER TABLE [dbo].[Client_Tracking] CHECK CONSTRAINT [FK_Client_Tracking_Organization]
-- GO
-- ALTER TABLE [dbo].[Client_Tracking]  WITH NOCHECK ADD  CONSTRAINT [FK_Client_Tracking_Platform_Type] FOREIGN KEY([Platform_Type_ID])
-- REFERENCES [dbo].[Platform_Type] ([ID])
-- GO
-- ALTER TABLE [dbo].[Client_Tracking] CHECK CONSTRAINT [FK_Client_Tracking_Platform_Type]
-- GO
