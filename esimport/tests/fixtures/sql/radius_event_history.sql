USE [Radius]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Radius_Event_History'))
BEGIN
DROP TABLE [dbo].[Radius_Event_History]
END
GO

/****** Object:  Table [dbo].[Radius_Event_History]    Script Date: 6/29/2018 8:12:55 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Radius_Event_History](
	[User_Name] [varchar](6000) NULL,
	[Radius_Event_ID] [bigint] IDENTITY(1,1) NOT NULL,
	[Organization_ID] [int] NULL,
	[Member_ID] [bigint] NULL,
	[Calling_Station_Id] [varchar](256) NULL,
	[Called_Station_Id] [varchar](256) NULL,
	[NAS_Identifier] [varchar](256) NULL,
	[VLAN] [int] NULL,
	[Date_UTC] [datetime] NULL)
GO

-- PUT DATA INSERT SCRIPTS BELOW
SET IDENTITY_INSERT Radius_Event_History ON
INSERT INTO [dbo].[Radius_Event_History](User_Name, Radius_Event_ID, Organization_ID, Member_ID)
VALUES
	('username1', 4464775943, 1, 1),
	('username2', 4464775940, 1, 2),
	('username3', 4464775937, 1, 3),
	('username4', 4464775934, 1, 1),
	('username5', 4464775933, 2, 2),
	('username6', 4464775932, 2, 3),
	('username7', 4464775931, 2, 1),
	('username8', 4464775930, 3, 2),
	('username9', 4464775928, 3, 3),
	('username10', 4464775925, 4, 1),
	('username11', 4464775924, 4, 2),
	('username12', 4464775917, 4, 3)
GO
--  CONSTRAINT [PK_Radius_Event_History] PRIMARY KEY CLUSTERED 
-- (
-- 	[Radius_Event_ID] ASC
-- )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PS_Partition_By_Id]([Radius_Event_ID])
-- ) ON [PS_Partition_By_Id]([Radius_Event_ID])

-- GO
-- ALTER TABLE [dbo].[Radius_Event_History] ADD  CONSTRAINT [DF_Radius_Event_History_Date]  DEFAULT (getdate()) FOR [Date]
-- GO
-- ALTER TABLE [dbo].[Radius_Event_History] ADD  CONSTRAINT [DF_Radius_Event_History_Date_UTC]  DEFAULT (getutcdate()) FOR [Date_UTC]
-- GO
-- ALTER TABLE [dbo].[Radius_Event_History]  WITH NOCHECK ADD  CONSTRAINT [FK_Radius_Event_History_Radius_Event_Type] FOREIGN KEY([Radius_Event_Type_ID])
-- REFERENCES [dbo].[Radius_Event_Type] ([ID])
-- GO
-- ALTER TABLE [dbo].[Radius_Event_History] NOCHECK CONSTRAINT [FK_Radius_Event_History_Radius_Event_Type]
-- GO
