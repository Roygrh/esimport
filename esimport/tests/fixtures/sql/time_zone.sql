USE [Eleven_OS]
GO

IF (EXISTS (SELECT *
                 FROM INFORMATION_SCHEMA.TABLES
                 WHERE TABLE_SCHEMA = 'dbo'
                 AND  TABLE_NAME = 'Time_Zone'))
BEGIN
DROP TABLE [dbo].[Time_Zone]
END
GO

/****** Object:  Table [dbo].[Time_Zone]    Script Date: 4/26/2018 12:32:25 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Time_Zone](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Description] [varchar](256) NOT NULL,
	[Tzid] [varchar](64) NULL,
	-- [Base_Utc_Offset] [int] NOT NULL,
	-- [Short] [varchar](16) NOT NULL,
	-- [Enabled] [bit] NOT NULL,
	-- [Base_Pst_Offset]  AS ((-25200)-[Base_Utc_Offset]),
 CONSTRAINT [PK_Time_Zone] PRIMARY KEY CLUSTERED 
(-
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[Time_Zone] ADD  CONSTRAINT [DF_Time_Zone_Enabled]  DEFAULT ((1)) FOR [Enabled]
GO


INSERT INTO [dbo].[Time_Zone](Description, Tzid)
	VALUES('UTC+06:00', '1')
INSERT INTO [dbo].[Time_Zone](Description, Tzid)
	VALUES('UTC-06:00', '2')