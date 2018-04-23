-- DROP TABLE [dbo].[Payment_Method]
-- GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Payment_Method'))
BEGIN
DROP TABLE [dbo].[Payment_Method]
END
GO

CREATE TABLE [dbo].[Payment_Method](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Code] [varchar](10) NOT NULL,
 CONSTRAINT [PK_Payment_Method] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Payment_Method](Code)
	VALUES('Card')
GO