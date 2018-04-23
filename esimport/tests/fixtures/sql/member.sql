-- DROP TABLE [dbo].[Member]
-- GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Member'))
BEGIN
DROP TABLE [dbo].[Member]
END
GO

CREATE TABLE [dbo].[Member](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Number] [varchar](64) NOT NULL,
	[Display_Name] [varchar](256) NOT NULL,
	[Member_Status_ID] [int] NOT NULL,
	[Organization_ID] [int] NULL,
 CONSTRAINT [PK_Member] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 100) ON [PRIMARY]
) ON [PRIMARY]

GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Member](Number, Display_Name, Member_Status_ID, Organization_ID)
	VALUES('1', 'cc-9886_79C66442-7E37-4B0D-B512-E7D1C9EDFC11', 1, 1)
INSERT INTO [dbo].[Member](Number, Display_Name, Member_Status_ID, Organization_ID)
	VALUES('2', 'rt-0400_26C55BA3-1C56-4409-92F0-6E60CD4C4E56', 1, 1)
INSERT INTO [dbo].[Member](Number, Display_Name, Member_Status_ID, Organization_ID)
	VALUES('3', 'ug-7738_2F437425-D944-4AC6-B7E5-9A19EBF23320', 1, 2)
GO