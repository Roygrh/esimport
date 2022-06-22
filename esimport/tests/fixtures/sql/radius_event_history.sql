USE [Radius]
GO

IF (EXISTS (SELECT *
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'dbo'
	AND TABLE_NAME = 'Radius_Accounting_Event_History'))
BEGIN
	DROP TABLE [dbo].[Radius_Accounting_Event_History]
END
GO

/****** Object:  Table [dbo].[Radius_Accounting_Event_History]    Script Date: 6/29/2018 8:12:55 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Radius_Accounting_Event_History]
(
	[User_Name] [varchar](6000) NULL,
	[Radius_Accounting_Event_ID] [bigint] IDENTITY(1,1) NOT NULL,
	[Organization_ID] [int] NULL,
	[Member_ID] [bigint] NULL,
	[Calling_Station_Id] [varchar](256) NULL,
	[Called_Station_Id] [varchar](256) NULL,
	[NAS_Identifier] [varchar](256) NULL,
	[VLAN] [int] NULL,
	[Date_UTC] [datetime] NULL
)
GO
-- TODO: uncomment these in final commit

-- PUT DATA INSERT SCRIPTS BELOW
SET IDENTITY_INSERT Radius_Accounting_Event_History ON
INSERT INTO [dbo].[Radius_Accounting_Event_History]
	(User_Name, Radius_Accounting_Event_ID, Organization_ID, Member_ID, NAS_Identifier, Called_Station_Id, VLAN, Calling_Station_Id, Date_UTC)
VALUES
	('username1', 4464775943, 1, 1, 'E8-1D-A8-20-1B-88', 'E8-1D-A8-20-1B-88:WOODSPRING_GUEST', 95, '5C-52-1E-60-6A-17', '2018-06-27 15:12:19.677'),
	('username2', 4464775940, 1, 2, 'DALEMES', '00-50-E8-04-0F-0A', 1021, '08-6D-41-E3-7B-B4', '2018-06-27 15:12:19.690'),
	('username3', 4464775937, 1, 3, 'Mckinney Uptown', 'D4-C1-9E-7B-E2-48:MckinneyUptown_Resident', 0, '08-6D-41-E3-7B-B4', '2018-06-27 15:12:19.700'),
	('username4', 4464775934, 1, 1, '30-87-D9-51-14-FC', '30-87-D9-51-14-FC:The_Ridge', 0, '08-6D-41-E3-7B-B4', '2018-06-27 15:12:19.710'),
	('username5', 4464775933, 2, 2, 'RVISTASQ-WC', 'D8-38-FC-77-0F-D8:VistaSquare_Resident', 1016, '08-6D-41-E3-7B-B4', '2018-06-27 15:12:19.725'),
	('username6', 4464775932, 2, 3, 'oasis', '00-50-E8-02-89-2A', 1016, '08-6D-41-E3-7B-B4', '2018-06-27 15:12:19.730'),
	('username7', 4464775931, 2, 1, '30-87-D9-13-03-48', '30-87-D9-13-03-48:Ridgeview_Apartments', 1016, '88-19-08-BF-DE-01', '2018-06-27 15:12:19.740'),
	('username8', 4464775930, 3, 2, 'nycbk', '00-50-E8-02-83-42', 300, '30-07-4D-2C-51-7B', '2018-06-27 15:12:19.750'),
	('username9', 4464775928, 3, 3, 'Broadstone at Winter Park', 'D8-38-FC-7C-21-7C:Broadstone Resident', 250, '30-07-4D-2C-51-7B', '2018-06-27 15:12:19.760'),
	('username10', 4464775925, 4, 1, 'TEMPLE', '00-50-E8-02-D3-7C', 311, '30-07-4D-2C-51-7B', '2018-06-27 15:12:19.780'),
	('username11', 4464775924, 4, 2, 'Dunedin Commons', '90-3A-72-55-60-28:Dunedin_Commons_Resident', 1000, '30-07-4D-2C-51-7B', '2018-06-27 15:12:19.795'),
	('username12', 4464775917, 4, 3, 'Mesa_Nueva-UCSD', '0C-F4-D5-7C-C5-18:Mesa Nueva Resident', 90, '30-07-4D-2C-51-7B', '2018-06-27 15:12:19.810'),
	('username1', 1, 1, 1, 'E8-1D-A8-20-1B-88', 'E8-1D-A8-20-1B-88:WOODSPRING_GUEST', 95, '5C-52-1E-60-6A-17', '2018-06-27 15:12:19.677'),
	('username2', 2, 1, 2, 'DALEMES', '00-50-E8-04-0F-0A', 1021, '08-6D-41-E3-7B-B4', '2018-06-27 15:12:19.690'),
	('username3', 3, 1, 3, 'Mckinney Uptown', 'D4-C1-9E-7B-E2-48:MckinneyUptown_Resident', 0, '08-6D-41-E3-7B-B4', '2018-06-27 15:12:19.700'),
	('username4', 4, 1, 1, '30-87-D9-51-14-FC', '30-87-D9-51-14-FC:The_Ridge', 0, '08-6D-41-E3-7B-B4', '2018-06-27 15:12:19.710'),
	('username5', 5, 2, 2, 'RVISTASQ-WC', 'D8-38-FC-77-0F-D8:VistaSquare_Resident', 1016, '08-6D-41-E3-7B-B4', '2018-06-27 15:12:19.725'),
	('username6', 6, 2, 3, 'oasis', '00-50-E8-02-89-2A', 1016, '08-6D-41-E3-7B-B4', '2018-06-27 15:12:19.730'),
	('username7', 7, 2, 1, '30-87-D9-13-03-48', '30-87-D9-13-03-48:Ridgeview_Apartments', 1016, '88-19-08-BF-DE-01', '2018-06-27 15:12:19.740'),
	('username8', 8, 3, 2, 'nycbk', '00-50-E8-02-83-42', 300, '30-07-4D-2C-51-7B', '2018-06-27 15:12:19.750'),
	('username9', 9, 3, 3, 'Broadstone at Winter Park', 'D8-38-FC-7C-21-7C:Broadstone Resident', 250, '30-07-4D-2C-51-7B', '2018-06-27 15:12:19.760'),
	('username10', 10, 4, 1, 'TEMPLE', '00-50-E8-02-D3-7C', 311, '30-07-4D-2C-51-7B', '2018-06-27 15:12:19.780'),
	('username11', 11, 4, 2, 'Dunedin Commons', '90-3A-72-55-60-28:Dunedin_Commons_Resident', 1000, '30-07-4D-2C-51-7B', '2018-06-27 15:12:19.795'),
	('username12', 12, 4, 3, 'Mesa_Nueva-UCSD', '0C-F4-D5-7C-C5-18:Mesa Nueva Resident', 90, '30-07-4D-2C-51-7B', '2018-06-27 15:12:19.810')
GO
--  CONSTRAINT [PK_Radius_Accounting_Event_History] PRIMARY KEY CLUSTERED 
-- (
-- 	[Radius_Accounting_Event_ID] ASC
-- )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PS_Partition_By_Id]([Radius_Accounting_Event_ID])
-- ) ON [PS_Partition_By_Id]([Radius_Accounting_Event_ID])

-- GO
-- ALTER TABLE [dbo].[Radius_Accounting_Event_History] ADD  CONSTRAINT [DF_Radius_Accounting_Event_History_Date]  DEFAULT (getdate()) FOR [Date]
-- GO
-- ALTER TABLE [dbo].[Radius_Accounting_Event_History] ADD  CONSTRAINT [DF_Radius_Accounting_Event_History_Date_UTC]  DEFAULT (getutcdate()) FOR [Date_UTC]
-- GO
-- ALTER TABLE [dbo].[Radius_Accounting_Event_History]  WITH NOCHECK ADD  CONSTRAINT [FK_Radius_Accounting_Event_History_Radius_Accounting_Event_Type] FOREIGN KEY([Radius_Accounting_Event_Type_ID])
-- REFERENCES [dbo].[Radius_Accounting_Event_Type] ([ID])
-- GO
-- ALTER TABLE [dbo].[Radius_Accounting_Event_History] NOCHECK CONSTRAINT [FK_Radius_Accounting_Event_History_Radius_Accounting_Event_Type]
-- GO
