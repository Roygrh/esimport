USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Network_Access_Limits'))
BEGIN
DROP TABLE [dbo].[Network_Access_Limits]
END
GO

CREATE TABLE [dbo].[Network_Access_Limits](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Connection_Limit] [int] NOT NULL,
	[Up_kbs] [int] NULL,
	[Down_kbs] [int] NULL,
	[Start_Date_UTC] [datetime] NULL,
	[End_Date_UTC] [datetime] NULL,
	[Date_Modified_UTC] [datetime] NULL,
 CONSTRAINT [PK_Network_Access_Limits] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 100) ON [PRIMARY]
) ON [PRIMARY]

GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Network_Access_Limits](Connection_Limit, Up_kbs, Down_kbs, Start_Date_UTC, End_Date_UTC, Date_Modified_UTC)
	VALUES(5, 1236, 4196, '2014-01-04 07:38:24.357', '2018-04-05 10:31:46.768', '2018-05-02 09:15:11.237')
INSERT INTO [dbo].[Network_Access_Limits](Connection_Limit, Up_kbs, Down_kbs, Start_Date_UTC, End_Date_UTC, Date_Modified_UTC)
	VALUES(6, 321, 1228, '2014-01-04 07:38:26.607', '2018-04-05 10:31:58.679', '2018-05-02 09:15:11.240')
INSERT INTO [dbo].[Network_Access_Limits](Connection_Limit, Up_kbs, Down_kbs, Start_Date_UTC, End_Date_UTC, Date_Modified_UTC)
	VALUES(6, 409, 1096, '2014-01-05 07:43:03.933', '2018-04-05 10:32:14.551', '2018-05-02 09:15:11.242')
INSERT INTO [dbo].[Network_Access_Limits](Connection_Limit, Up_kbs, Down_kbs, Start_Date_UTC, End_Date_UTC, Date_Modified_UTC)
	VALUES(5, 122, 1228, '2014-01-05 07:43:06.490', '2018-04-05 10:32:28.728', '2018-05-02 09:15:11.244')	
INSERT INTO [dbo].[Network_Access_Limits](Connection_Limit, Up_kbs, Down_kbs, Start_Date_UTC, End_Date_UTC, Date_Modified_UTC)
	VALUES(10, 316, 1106, '2014-01-04 07:38:52.070', '2018-04-05 10:32:45.537', '2018-05-02 09:15:11.246')
INSERT INTO [dbo].[Network_Access_Limits](Connection_Limit, Up_kbs, Down_kbs, Start_Date_UTC, End_Date_UTC, Date_Modified_UTC)
	VALUES(1, 128, 1884, '2014-01-04 07:38:54.320', '2018-04-05 10:32:56.841', '2018-05-02 09:15:11.248')
INSERT INTO [dbo].[Network_Access_Limits](Connection_Limit, Up_kbs, Down_kbs, Start_Date_UTC, End_Date_UTC, Date_Modified_UTC)
	VALUES(1, 304, 1304, '2014-01-04 07:48:44.450', '2018-04-05 10:33:09.034', '2018-05-02 09:15:11.250')
INSERT INTO [dbo].[Network_Access_Limits](Connection_Limit, Up_kbs, Down_kbs, Start_Date_UTC, End_Date_UTC, Date_Modified_UTC)
	VALUES(3, 1036, 6096, '2014-01-04 07:48:47.143', '2018-04-05 10:33:19.594', '2018-05-02 09:15:11.252')
GO

