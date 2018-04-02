DROP TABLE [dbo].[Zone_Plan_Account_Promotional_Code]
GO

CREATE TABLE [dbo].[Zone_Plan_Account_Promotional_Code](
	[Zone_Plan_Account_ID] [int] NOT NULL,
	[Promotional_Code_ID] [int] NOT NULL,
 CONSTRAINT [PK_Zone_Plan_Account_Promotional_Code] PRIMARY KEY CLUSTERED 
(
	[Zone_Plan_Account_ID] ASC,
	[Promotional_Code_ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

-- PUT DATA INSERT SCRIPTS BELOW