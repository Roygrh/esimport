USE [Eleven_OS]
GO
/****** Object:  Table [dbo].[Zone_Plan_Status]    Script Date: 4/26/2018 12:32:26 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Zone_Plan_Status](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Name] [varchar](64) NOT NULL,
	[Description] [varchar](256) NOT NULL,
 CONSTRAINT [PK_Zone_Plan_Status] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_Zone_Plan_Status_Name] UNIQUE NONCLUSTERED 
(
	[Name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


SET IDENTITY_INSERT Zone_Plan_Status ON
INSERT INTO [dbo].[Zone_Plan_Status] (ID, Name, Description) 
VALUES 
	(1, 'Testing', 'Zone_Plan is in testing mode.'),
	(2, 'Active', 'Zone_Plan is active.'),
	(3, 'Disabled', 'Zone_Plan has been disabled.'),
	(4, 'Removed', 'Zone_Plan has been removed.')
GO