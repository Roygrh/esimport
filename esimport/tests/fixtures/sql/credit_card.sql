USE [Eleven_OS]
GO

IF (EXISTS (SELECT *
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'dbo'
	AND TABLE_NAME = 'Credit_Card'))
BEGIN
	DROP TABLE [dbo].[Credit_Card]
END
GO

CREATE TABLE [dbo].[Credit_Card]
(
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Masked_Number] [varchar](4) NOT NULL,
	[Credit_Card_Type_ID] [int] NULL,
	CONSTRAINT [PK_Credit_Card] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO


-- PUT DATA INSERT SCRIPTS BELOW

INSERT INTO Eleven_OS.dbo.Credit_Card
	(Masked_Number,Credit_Card_Type_ID)
VALUES
	('*', 1)
GO