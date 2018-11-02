USE [Eleven_OS]
GO
/****** Object:  Table [dbo].[Contact_Address]    Script Date: 4/26/2018 12:32:15 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Contact_Address](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Contact_ID] [int] NOT NULL,
	[Address_ID] [int] NOT NULL,
 CONSTRAINT [PK_Contact_Address] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY],
 CONSTRAINT [UQ_Contact_Address] UNIQUE NONCLUSTERED 
(
	[Contact_ID] ASC,
	[Address_ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]
GO
INSERT INTO [dbo].[Contact_Address]
VALUES 
	(1,1),
	(1,2),
	(2,1),
	(2,2)
-- ALTER TABLE [dbo].[Contact_Address]  WITH CHECK ADD  CONSTRAINT [FK_Contact_Address_Address] FOREIGN KEY([Address_ID])
-- REFERENCES [dbo].[Address] ([ID])
-- GO
-- ALTER TABLE [dbo].[Contact_Address] CHECK CONSTRAINT [FK_Contact_Address_Address]
-- GO
-- ALTER TABLE [dbo].[Contact_Address]  WITH NOCHECK ADD  CONSTRAINT [FK_Contact_Address_Contact] FOREIGN KEY([Contact_ID])
-- REFERENCES [dbo].[Contact] ([ID])
-- GO
-- ALTER TABLE [dbo].[Contact_Address] NOCHECK CONSTRAINT [FK_Contact_Address_Contact]
-- GO
-- ALTER TABLE [dbo].[Contact_Address]  WITH CHECK ADD  CONSTRAINT [FK_Contact_Address_Contact_Address_Type] FOREIGN KEY([Contact_Address_Type_ID])
-- REFERENCES [dbo].[Contact_Address_Type] ([ID])
-- GO
-- ALTER TABLE [dbo].[Contact_Address] CHECK CONSTRAINT [FK_Contact_Address_Contact_Address_Type]
-- GO
