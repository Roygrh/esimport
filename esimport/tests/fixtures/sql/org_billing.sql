USE [Eleven_OS]
GO

IF (EXISTS (SELECT *
                 FROM INFORMATION_SCHEMA.TABLES
                 WHERE TABLE_SCHEMA = 'dbo'
                 AND  TABLE_NAME = 'Org_Billing'))
BEGIN
DROP TABLE [dbo].[Org_Billing]
END
GO

/****** Object:  Table [dbo].[Org_Billing]    Script Date: 4/26/2018 12:32:20 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Org_Billing](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Organization_ID] [int] NOT NULL,
	[First_Activity_Date_UTC] [datetime] NULL,
	[Time_Zone_ID] [int] NULL,
	[Go_Live_Date_UTC] [datetime] NULL,
	[Previous_Go_Live_Date_UTC] [datetime] NULL,
 CONSTRAINT [PK_Org_Billing] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]
GO

--  CONSTRAINT [UQ_Org_Billing_Organization] UNIQUE NONCLUSTERED 
-- (
-- 	[Organization_ID] ASC
-- )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
-- ) ON [PRIMARY]
-- GO
-- ALTER TABLE [dbo].[Org_Billing]  WITH CHECK ADD  CONSTRAINT [FK_Org_Billing_Organization] FOREIGN KEY([Organization_ID])
-- REFERENCES [dbo].[Organization] ([ID])
-- GO
-- ALTER TABLE [dbo].[Org_Billing] CHECK CONSTRAINT [FK_Org_Billing_Organization]
-- GO