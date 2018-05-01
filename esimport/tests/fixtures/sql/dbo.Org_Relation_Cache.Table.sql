USE [Eleven_OS]
GO
/****** Object:  Table [dbo].[Org_Relation_Cache]    Script Date: 4/26/2018 12:32:21 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Org_Relation_Cache](
	[Parent_Org_ID] [int] NULL,
	[Child_Org_ID] [int] NULL,
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

INSERT INTO [dbo].[Org_Relation_Cache](Parent_Org_ID, Child_Org_ID)
	VALUES(1, 1)
INSERT INTO [dbo].[Org_Relation_Cache](Parent_Org_ID, Child_Org_ID)
	VALUES(2, 2)
INSERT INTO [dbo].[Org_Relation_Cache](Parent_Org_ID, Child_Org_ID)
	VALUES(3, 1)
INSERT INTO [dbo].[Org_Relation_Cache](Parent_Org_ID, Child_Org_ID)
	VALUES(4, 2)
GO