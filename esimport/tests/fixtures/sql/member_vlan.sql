USE [Eleven_OS]
GO
/****** Object:  Table [dbo].[Member_Vlan]    Script Date: 4/26/2018 12:32:19 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Member_Vlan](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Vlan] [int] NOT NULL,
	[Member_ID] [int] NOT NULL,
 CONSTRAINT [PK_Member_Vlan] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY],
 CONSTRAINT [UQ_Member_Vlan_Member_ID] UNIQUE NONCLUSTERED 
(
	[Member_ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]
GO
-- ALTER TABLE [dbo].[Member_Vlan] ADD  CONSTRAINT [DF_NMember_Vlan_Date_Modified_UTC]  DEFAULT (getutcdate()) FOR [Date_Modified_UTC]
-- GO
-- ALTER TABLE [dbo].[Member_Vlan]  WITH CHECK ADD  CONSTRAINT [FK_Member_Vlan_Member] FOREIGN KEY([Member_ID])
-- REFERENCES [dbo].[Member] ([ID])
-- GO
-- ALTER TABLE [dbo].[Member_Vlan] CHECK CONSTRAINT [FK_Member_Vlan_Member]
-- GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Member_Vlan](Vlan, Member_ID)
VALUES
	(1, 1),
	(2, 2),
	(3, 3)
GO