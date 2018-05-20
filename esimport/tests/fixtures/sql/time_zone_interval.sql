USE [Eleven_OS]
GO

IF (EXISTS (SELECT *
                 FROM INFORMATION_SCHEMA.TABLES
                 WHERE TABLE_SCHEMA = 'dbo'
                 AND  TABLE_NAME = 'Time_Zone_Interval'))
BEGIN
DROP TABLE [dbo].[Time_Zone_Interval]
END
GO

/****** Object:  Table [dbo].[Time_Zone_Interval]    Script Date: 4/26/2018 12:32:25 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Time_Zone_Interval](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Time_Zone_ID] [int] NOT NULL,
	[Interval_Start] [datetimeoffset](7) NOT NULL,
	[Interval_End] [datetimeoffset](7) NOT NULL,
	[Local_Offset_Seconds] [int] NOT NULL,
	[Short_Name] [varchar](24) NULL,
 CONSTRAINT [PK_Time_Zone_Interval] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[Time_Zone_Interval]  WITH CHECK ADD  CONSTRAINT [FK_Time_Zone_Interval_Time_Zone] FOREIGN KEY([Time_Zone_ID])
REFERENCES [dbo].[Time_Zone] ([ID])
GO
ALTER TABLE [dbo].[Time_Zone_Interval] CHECK CONSTRAINT [FK_Time_Zone_Interval_Time_Zone]
GO