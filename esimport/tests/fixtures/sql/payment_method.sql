USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Payment_Method'))
BEGIN
DROP TABLE [dbo].[Payment_Method]
END
GO

CREATE TABLE [dbo].[Payment_Method](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Code] [varchar](10) NOT NULL,
	[Name] [varchar](64) NOT NULL,
	[Description] [varchar](256) NOT NULL,
 CONSTRAINT [PK_Payment_Method] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

-- PUT DATA INSERT SCRIPTS BELOW
SET IDENTITY_INSERT Payment_Method ON
INSERT INTO [dbo].[Payment_Method](ID, Code, Name, Description)
VALUES
	(1, 'CC', 'Credit Card', 'Payment via Credit card.'),
	(2, 'PMS', 'Property Management System', 'Payment via billing to room.'),
	(3, 'SVY', 'Survey Payment', 'via taking a survey.'),
	(4, 'FREE', 'Free', 'No payment required.'),
	(5, 'Batch', 'Batch Created', 'No payment, created via batch.'),
	(6, 'CHK', 'Check', 'Payment via check.'),
	(7, 'KIT', 'Kimpton InTouch Authentication', 'No payment; authenticated via Kimpton Web service.'),
	(8, 'SC', 'Santa Clara Authentication', 'No payment; authenticated via Santa Clara Web service.'),
	(9, 'AC', 'Access Code', 'No payment; authenticated via access code')
GO