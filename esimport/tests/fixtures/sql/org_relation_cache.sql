USE [Eleven_OS]
GO

IF (EXISTS (SELECT *
                 FROM INFORMATION_SCHEMA.TABLES
                 WHERE TABLE_SCHEMA = 'dbo'
                 AND  TABLE_NAME = 'Org_Relation_Cache'))
BEGIN
DROP TABLE [dbo].[Org_Relation_Cache]
END
GO

/****** Object:  Table [dbo].[Org_Relation_Cache]    Script Date: 4/26/2018 12:32:21 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Org_Relation_Cache](
	[Parent_Org_ID] [int] NULL,
	[Child_Org_ID] [int] NULL,
	[Org_Relation_Type_ID] [int] NOT NULL,
	[Depth] [int] NOT NULL,
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
 CONSTRAINT [PK_Org_Relation_Cache] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY],
 CONSTRAINT [UQ_Org_Relation_Cache] UNIQUE NONCLUSTERED 
(
	[Parent_Org_ID] ASC,
	[Child_Org_ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]
GO

SET IDENTITY_INSERT Org_Relation_Cache ON
INSERT INTO [dbo].[Org_Relation_Cache](ID, Parent_Org_ID, Child_Org_ID, Org_Relation_Type_ID, Depth)
VALUES
	(1, 1, 1, 1, 1),
	(2, 1, 3, 1, 1),
	(3, 2, 2, 1, 1),
	(4, 2, 4, 1, 1),
	(5, 2, 5, 1, 1)
GO
