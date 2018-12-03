USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Organization'))
BEGIN
DROP TABLE [dbo].[Organization]
END
GO

CREATE TABLE [dbo].[Organization](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Number] [varchar](64) NOT NULL,
	[Name] [varchar](128) NOT NULL,
	[Display_Name] [varchar](128) NOT NULL,
	[Org_Status_ID] [int] NOT NULL,
	[Time_Zone_ID] [int] NULL,
	[Guest_Room_Count] [int] NOT NULL,
	[Meeting_Room_Count] [int] NOT NULL,
	[Date_Added_UTC] [datetime] NOT NULL,
	[Is_Lite] [bit] NULL,
	[Pan_Enabled] [bit] NULL,
	[Org_Category_Type_ID] [int] NULL,
	[Contact_ID] [int] NULL,

 CONSTRAINT [PK_Organization] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]
GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Organization](Number, Name, Display_Name, Guest_Room_Count, Meeting_Room_Count, Is_Lite, Pan_Enabled, Date_Added_UTC, Org_Status_ID, Time_Zone_ID, Org_Category_Type_ID, Contact_ID)
	VALUES
	('FF-471-20', 'somename1', 'some display name 1', 1, 1, 0, 0, '2014-01-04 07:38:24.370', 1, 1, 4, 1),
	('TP-319-34', 'somename2', 'some display name 2', 1, 1, 0, 0, '2014-01-04 07:38:24.470', 2, 2, 4, 2),
	('GL-236-20', 'somename1', 'some display name 1', 1, 1, 0, 0, '2014-01-04 07:38:24.370', 1, 1, 3, 3),
	('DN-150-86', 'somename2', 'some display name 2', 1, 1, 0, 0, '2014-01-04 07:38:24.470', 2, 2, 3, 4),
	('UE-531-28', 'somename2', 'some display name 2', 1, 1, 0, 0, '2014-01-04 07:38:24.470', 2, 2, 4, 5)
GO
