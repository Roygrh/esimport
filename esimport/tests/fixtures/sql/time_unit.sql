USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Time_Unit'))
BEGIN
DROP TABLE [dbo].[Time_Unit]
END
GO

CREATE TABLE [dbo].[Time_Unit](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Name] [varchar](64) NOT NULL,
	[Description] [varchar](256) NOT NULL,
	[Seconds] [int] NOT NULL,
 CONSTRAINT [PK_Time_Unit] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO


-- PUT DATA INSERT SCRIPTS BELOW
SET IDENTITY_INSERT Time_Unit ON
INSERT INTO [dbo].[Time_Unit](ID, Name, Description, Seconds)
VALUES
	(1, 'Seconds', 'Units are in seconds.', 1),
	(2, 'Minutes', 'Units are in minutes.', 60),
	(3, 'Hours', 'Units are in hours.', 3600),
	(4, 'Days', 'Units are in days.', 86400),
	(5, 'Weeks', 'Units are in weeks.', 604800),
	(6, 'Months', 'Units are in months.', 2629746),
	(7, 'Years', 'Units are in years.', 31556952)
GO