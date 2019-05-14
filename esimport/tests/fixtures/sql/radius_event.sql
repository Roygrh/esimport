USE [Radius]
GO
/****** Object:  Table [dbo].[Radius_Event]    Script Date: 6/29/2018 8:12:55 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Radius_Event](
	[ID] [bigint] IDENTITY(1,1) NOT NULL,
	[User_Name] [varchar](6000) NULL,
	[Member_ID] [bigint] NULL,
	[Organization_ID] [int] NULL,
	[Date_UTC] [datetime] NULL,
    [NAS_Identifier] [varchar](256) NULL,
    [Called_Station_Id] [varchar](256) NULL,
    [VLAN] [int] NULL,
    [Calling_Station_Id] [varchar](256) NULL)
GO

SET IDENTITY_INSERT Radius_Event ON
INSERT INTO [dbo].[Radius_Event] (ID, User_Name, Member_ID, Organization_ID, Date_UTC, NAS_Identifier, Called_Station_Id, VLAN, Calling_Station_Id)
VALUES (2652371592, 'username1', 1, 1, '2018-06-27 15:12:19.677', 'E8-1D-A8-20-1B-88', 'E8-1D-A8-20-1B-88:WOODSPRING_GUEST', 95, '5C-52-1E-60-6A-17'),
       (2652371591, 'username2', 1, 2, '2018-06-27 15:12:19.690', 'DALEMES', '00-50-E8-04-0F-0A', 1021, '08-6D-41-E3-7B-B4'),
       (2652371590, 'username3', 1, 3, '2018-06-27 15:12:19.710', 'Mckinney Uptown', 'D4-C1-9E-7B-E2-48:MckinneyUptown_Resident', 0, '08-6D-41-E3-7B-B4'),
       (2652371589, 'username4', 1, 4, '2018-06-27 15:12:19.725', '30-87-D9-51-14-FC', '30-87-D9-51-14-FC:The_Ridge', 0, '08-6D-41-E3-7B-B4'),
       (2652371588, 'username5', 2, 1, '2018-06-27 15:12:19.730', 'RVISTASQ-WC', 'D8-38-FC-77-0F-D8:VistaSquare_Resident', 1016, '08-6D-41-E3-7B-B4'),
       (2652371587, 'username6', 2, 2, '2018-06-27 15:12:19.740', 'oasis', '00-50-E8-02-89-2A', 1016, '08-6D-41-E3-7B-B4'),
       (2652371586, 'username7', 2, 3, '2018-06-27 15:12:19.750', '30-87-D9-13-03-48', '30-87-D9-13-03-48:Ridgeview_Apartments', 1016, '88-19-08-BF-DE-01'),
       (2652371585, 'username8', 2, 4, '2018-06-27 15:12:19.760', 'nycbk', '00-50-E8-02-83-42', 300, '30-07-4D-2C-51-7B'),
       (2652371584, 'username9', 3, 1, '2018-06-27 15:12:19.780', 'Broadstone at Winter Park', 'D8-38-FC-7C-21-7C:Broadstone Resident', 250, '30-07-4D-2C-51-7B'),
       (2652371583, 'username10', 3, 2, '2018-06-27 15:12:19.795', 'TEMPLE', '00-50-E8-02-D3-7C', 311, '30-07-4D-2C-51-7B'),
       (2652371582, 'username11', 3, 3, '2018-06-27 15:12:19.810', 'Dunedin Commons', '90-3A-72-55-60-28:Dunedin_Commons_Resident', 1000, '30-07-4D-2C-51-7B'),
       (2652371581, 'username12', 3, 4, '2018-06-27 15:12:19.810', 'Mesa_Nueva-UCSD', '0C-F4-D5-7C-C5-18:Mesa Nueva Resident', 90, '30-07-4D-2C-51-7B')
GO
