USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
				FROM INFORMATION_SCHEMA.TABLES
				WHERE TABLE_SCHEMA = 'dbo'
				AND TABLE_NAME = 'Org_Zone'))
BEGIN
DROP TABLE [dbo].[Org_Zone]
END
GO			

/****** Object:  Table [dbo].[Org_Zone]    Script Date: 4/26/2018 12:32:21 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Org_Zone](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Organization_ID] [int] NOT NULL,
	[Custom_Implementation_URL] [varchar](256) NULL,
 CONSTRAINT [PK_Org_Zone] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]
GO

SET IDENTITY_INSERT Org_Zone ON
INSERT INTO [dbo].[Org_Zone] (ID, Organization_ID, Custom_Implementation_URL)
VALUES
	(1, 1, 'https://secure.guestinternet.com/portal/juno/brands/mdu/resident/index.html?api_domain=https://secure.11os.com'),
	(2, 2, 'https://secure.guestinternet.com/portal/juno/brands/mdu/resident/index.html?api_domain=https://secure.11os.com'),
	(3, 3, 'https://secure.guestinternet.com/portal/juno/brands/wrong/resident/index.html?api_domain=https://secure.11os.com'),
	(4, 4, 'https://secure.guestinternet.com/portal/juno/brands/mdu/resident/index.html?api_domain=https://secure.11os.com'),
	(5, 5, 'https://secure.guestinternet.com/portal/juno/brands/mdu/resident/index.html?api_domain=https://secure.11os.com')
GO
