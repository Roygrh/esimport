USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Member_Status'))
BEGIN
DROP TABLE [dbo].[Member_Status]
END
GO

CREATE TABLE [dbo].[Member_Status](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Name] [varchar](64) NOT NULL,
	[Description] [varchar](256) NOT NULL,
 CONSTRAINT [PK_Member_Status] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Member_Status](Name, Description)
	VALUES
    ('Active', 'Membership is active.'),
    ('Expired', 'Membership has expired.'),
    ('Disabled', 'Membership has been disabled.'),
    ('Removed', 'Membership has been removed.'),
    ('Deleted', 'Membership is scheduled for deletion.')
GO
