USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Currency'))
BEGIN
DROP TABLE [dbo].[Currency]
END
GO

CREATE TABLE [dbo].[Currency](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Name] [varchar](64) NOT NULL,
	[Country_ID] [int] NULL,
	[Code] [varchar](10) NOT NULL,
	[Numeric_Code] [varchar](3) NULL,
 CONSTRAINT [PK_Currency] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

-- PUT DATA INSERT SCRIPTS BELOW
SET IDENTITY_INSERT [dbo].[Currency] ON
INSERT INTO [dbo].[Currency](ID, Name, Country_ID, Code, Numeric_Code)
VALUES 
	(1, 'Afghani', 1, 'AFA', 4),
	(2, 'Algerian Dinar', 3, 'DZD', 12),
	(3, 'Andorran Peseta', 5, 'ADP', 20),
	(4, 'Argentine Peso', 10, 'ARS', 32),
	(5, 'Armenian Dram', 11, 'AMD', 51),
	(6, 'Aruban Guilder', 12, 'AWG', 533)
GO