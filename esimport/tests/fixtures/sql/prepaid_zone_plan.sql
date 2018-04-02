DROP TABLE [dbo].[Prepaid_Zone_Plan]
GO

CREATE TABLE [dbo].[Prepaid_Zone_Plan](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Zone_Plan_ID] [int] NOT NULL,
	[Consumable_Time] [int] NULL,
	[Consumable_Time_Unit_ID] [int] NULL,
	[Lifespan_Time] [int] NULL,
	[Lifespan_Time_Unit_ID] [int] NULL,
 CONSTRAINT [PK_Prepaid_Zone_Plan] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]

GO

-- PUT DATA INSERT SCRIPTS BELOW