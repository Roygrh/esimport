USE [Eleven_OS]
GO

IF (EXISTS (SELECT *
                 FROM INFORMATION_SCHEMA.TABLES
                 WHERE TABLE_SCHEMA = 'dbo'
                 AND  TABLE_NAME = 'Radius_Active_Usage'))
BEGIN
DROP TABLE [dbo].[Radius_Active_Usage]
END
GO

/****** Object:  Table [dbo].[Radius_Active_Usage]    Script Date: 4/26/2018 12:32:23 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Radius_Active_Usage](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Organization_ID] [int] NOT NULL,
	[Member_ID] [int] NULL,
	[Calling_Station_Id] [varchar](256) NULL,
 CONSTRAINT [PK_Radius_Active_Usage] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]
GO

INSERT INTO [dbo].[Radius_Active_Usage](Organization_ID, Member_ID, Calling_Station_Id)
	VALUES(1, 1, '111-111-111-111')
INSERT INTO [dbo].[Radius_Active_Usage](Organization_ID, Member_ID, Calling_Station_Id)
	VALUES(2, 2, '222-222-222-222')
INSERT INTO [dbo].[Radius_Active_Usage](Organization_ID, Member_ID, Calling_Station_Id)
	VALUES(3, 3, '444-444-444-444')
INSERT INTO [dbo].[Radius_Active_Usage](Organization_ID, Member_ID, Calling_Station_Id)
	VALUES(4, 4, '555-555-555-555')
INSERT INTO [dbo].[Radius_Active_Usage](Organization_ID, Member_ID, Calling_Station_Id)
	VALUES(1, 5, '666-666-666-666')
INSERT INTO [dbo].[Radius_Active_Usage](Organization_ID, Member_ID, Calling_Station_Id)
	VALUES(2, 6, '777-777-777-777')
INSERT INTO [dbo].[Radius_Active_Usage](Organization_ID, Member_ID, Calling_Station_Id)
	VALUES(3, 7, '888-888-888-888')
INSERT INTO [dbo].[Radius_Active_Usage](Organization_ID, Member_ID, Calling_Station_Id)
	VALUES(4, 8, '333-333-333-333')