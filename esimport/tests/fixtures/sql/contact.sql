USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Contact'))
BEGIN
DROP TABLE [dbo].[Contact]
END
GO

/****** Object:  Table [dbo].[Contact]    Script Date: 4/26/2018 12:32:15 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Contact](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[First_Name] [varchar](256) NULL,
	[Middle_Name] [varchar](256) NULL,
	[Last_Name] [varchar](256) NULL,
	[Social_Title_ID] [int] NULL,
	[Contact_Type_ID] [int] NULL,
	[Preferred_Contact_Method] [varchar](256) NULL,
	[Preferred_Contact_Time] [varchar](256) NULL,
	[Corporate_Title] [varchar](256) NULL,
	[Description] [varchar](256) NULL,
	[Organization_ID] [int] NULL,
 CONSTRAINT [PK_Contact] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
INSERT INTO [dbo].[Contact] (First_Name, Last_Name, Organization_ID)
VALUES
	('Lula', 'Buer', 1),
	('Dorree', 'Grogor', 2),
	('Philippine', 'Elvins', 3),
	('Jerrie', 'Chinnock', 4)
GO

-- ALTER TABLE [dbo].[Contact]  WITH NOCHECK ADD  CONSTRAINT [FK_Contact_Contact_Type] FOREIGN KEY([Contact_Type_ID])
-- REFERENCES [dbo].[Contact_Type] ([ID])
-- GO
-- ALTER TABLE [dbo].[Contact] CHECK CONSTRAINT [FK_Contact_Contact_Type]
-- GO
-- ALTER TABLE [dbo].[Contact]  WITH NOCHECK ADD  CONSTRAINT [FK_Contact_Organization] FOREIGN KEY([Organization_ID])
-- REFERENCES [dbo].[Organization] ([ID])
-- GO
-- ALTER TABLE [dbo].[Contact] CHECK CONSTRAINT [FK_Contact_Organization]
-- GO
-- ALTER TABLE [dbo].[Contact]  WITH CHECK ADD  CONSTRAINT [FK_Contact_Social_Title] FOREIGN KEY([Social_Title_ID])
-- REFERENCES [dbo].[Social_Title] ([ID])
-- GO
-- ALTER TABLE [dbo].[Contact] CHECK CONSTRAINT [FK_Contact_Social_Title]
-- GO
