USE [Radius]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Radius_Terminate_Cause'))
BEGIN
DROP TABLE [dbo].[Radius_Terminate_Cause]
END
GO

/****** Object:  Table [dbo].[Radius_Terminate_Cause]    Script Date: 6/29/2018 8:12:55 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Radius_Terminate_Cause](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Name] [varchar](64) NOT NULL)
--  CONSTRAINT [PK_Radius_Terminate_Cause] PRIMARY KEY CLUSTERED 
-- (
-- 	[ID] ASC
-- )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
--  CONSTRAINT [UQ_Radius_Terminate_Cause_Name] UNIQUE NONCLUSTERED 
-- (
-- 	[Name] ASC
-- )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
--  CONSTRAINT [UQ_Radius_Terminate_Cause_Value] UNIQUE NONCLUSTERED 
-- (
-- 	[Value] ASC
-- )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
-- ) ON [PRIMARY]

GO


-- PUT DATA INSERT SCRIPTS BELOW
SET IDENTITY_INSERT Radius_Terminate_Cause ON
INSERT INTO [dbo].[Radius_Terminate_Cause](ID, Name)
VALUES
	(7,'Admin-Reboot'),
	(6,'Admin-Reset'),
	(16,'Callback'),
	(18,'Host-Request'),
	(4,'Idle-Timeout'),
	(2,'Lost-Carrier'),
	(3,'Lost-Service'),
	(9,'NAS-Error'),
	(11,'NAS-Reboot'),
	(10,'NAS-Request'),
	(22,'Port-Administratively-Disabled'),
	(8,'Port-Error'),
	(13,'Port-Preempted'),
	(21,'Port-Reinitialized'),
	(14,'Port-Suspended'),
	(12,'Port-Unneeded'),
	(23,'PW-Portal-Reset'),
	(20,'Reauthentication-Failure'),
	(15,'Service-Unavailable'),
	(5,'Session-Timeout'),
	(19,'Supplicant-Restart'),
	(17,'User-Error'),
	(1,'User-Request')
GO