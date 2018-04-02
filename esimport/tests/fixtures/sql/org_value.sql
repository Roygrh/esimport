DROP TABLE [dbo].[Org_Value]
GO

CREATE TABLE [dbo].[Org_Value](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Organization_ID] [int] NOT NULL,
	[Name] [varchar](64) NOT NULL,
	[Value] [varchar](7500) NULL,
 CONSTRAINT [PK_Org_Value] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]

GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Org_Value](Organization_ID, Name, Value)
	VALUES(1, 'Guest', 'Guest')
INSERT INTO [dbo].[Org_Value](Organization_ID, Name, Value)
	VALUES(2, 'Guest', 'Guest')
INSERT INTO [dbo].[Org_Value](Organization_ID, Name, Value)
	VALUES(3, 'Public', 'Public')
INSERT INTO [dbo].[Org_Value](Organization_ID, Name, Value)
	VALUES(4, 'Public', 'Public')
INSERT INTO [dbo].[Org_Value](Organization_ID, Name, Value)
	VALUES(5, 'Guest', 'Guest')
INSERT INTO [dbo].[Org_Value](Organization_ID, Name, Value)
	VALUES(6, 'Guest', 'Guest')
INSERT INTO [dbo].[Org_Value](Organization_ID, Name, Value)
	VALUES(7, 'Meeting', 'Meeting')
INSERT INTO [dbo].[Org_Value](Organization_ID, Name, Value)
	VALUES(8, 'Meeting', 'Meeting')
GO