USE [Eleven_OS]
GO
/****** Object:  Table [dbo].[Zone_Plan_Tag]    Script Date: 12/15/2022 12:21:26 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Zone_Plan_Tag](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Name] [varchar](64) NOT NULL,
	[Description] [varchar](256) NOT NULL,
 CONSTRAINT [PK_Zone_Plan_Tag] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_Zone_Plan_Tag_Name] UNIQUE NONCLUSTERED
(
	[Name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

SET IDENTITY_INSERT Zone_Plan_Tag ON
INSERT INTO [dbo].[Zone_Plan_Tag] (ID, Name, Description)
VALUES
	(1, 'Tier 0', 'Tier 0 Plans'),
	(2, 'Tier 1', 'Tier 1 Plans'),
	(3, 'Tier 2', 'Tier 2 Plans'),
	(4, 'Tier 3', 'Tier 3 Plans'),
	(5, 'Tier 4', 'Tier 4 Plans'),
	(6, 'Tier 5', 'Tier 5 Plans'),
	(7, 'Tier 6', 'Tier 6 Plans'),
	(8, 'Tier 7', 'Tier 7 Plans'),
	(9, 'Tier 8', 'Tier 8 Plans'),
	(10, 'Tier 9', 'Tier 9 Plans'),
	(11, 'Tier 10', 'Tier 10 Plans'),
	(12, 'Tier 11', 'Tier 11 Plans'),
	(13, 'Tier 12', 'Tier 12 Plans'),
	(14, 'Tier 13', 'Tier 13 Plans'),
	(15, 'Tier 14', 'Tier 14 Plans'),
	(16, 'Tier 15', 'Tier 15 Plans'),
	(17, 'Tier 16', 'Tier 16 Plans'),
	(18, 'Tier 17', 'Tier 17 Plans'),
	(19, 'Tier 18', 'Tier 18 Plans'),
	(20, 'Tier 19', 'Tier 19 Plans')
GO