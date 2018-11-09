USE [Eleven_OS]
GO
/****** Object:  Table [dbo].[Address]    Script Date: 4/26/2018 12:32:14 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Address](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Address_1] [varchar](256) NULL,
	[Address_2] [varchar](256) NULL,
	[City] [varchar](256) NULL,
	[Area] [varchar](256) NULL,
	[Postal_Code] [varchar](62) NULL,
	[Country_ID] [int] NULL,
 CONSTRAINT [PK_Address] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 100) ON [PRIMARY]
) ON [PRIMARY]
GO
INSERT INTO [dbo].[Address] 
VALUES
	('8', 'Twin Pines Lane', 'City', 'Area', '42000', 1),
	('9150', 'Menomonie Place', 'City', 'Area', '42000', 2),
	('581', 'Dottie Road', 'City', 'Area', '42000', 1),
	('26', 'Ronald Regan Drive', 'City', 'Area', '42000', 2)
-- ALTER TABLE [dbo].[Address]  WITH CHECK ADD  CONSTRAINT [FK_Address_Country] FOREIGN KEY([Country_ID])
-- REFERENCES [dbo].[Country] ([ID])
-- GO
-- ALTER TABLE [dbo].[Address] CHECK CONSTRAINT [FK_Address_Country]
-- GO