USE [Eleven_OS]
GO

IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = 'Scheduled_Access'))
BEGIN
DROP TABLE [dbo].[Scheduled_Access]
END
GO

CREATE TABLE [dbo].[Scheduled_Access](
	[ID] [int] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Event_Name] [varchar](128) NOT NULL,
	[Date_Created_UTC] [datetime] NULL,
	[Actual_User_Count] [int] NOT NULL,
	[Total_Input_Bytes] [bigint] NOT NULL,
	[Total_Output_Bytes] [bigint] NOT NULL,
	[Total_Session_Time] [bigint] NOT NULL,
	[Member_ID] [int] NOT NULL,
	[Organization_ID] [int] NULL,
	[Network_Access_ID] [int] NULL,
 CONSTRAINT [PK_Scheduled_Access] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
) ON [PRIMARY]
GO

-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[Scheduled_Access](Event_Name, Date_Created_UTC, Actual_User_Count, Total_Input_Bytes, Total_Output_Bytes, Total_Session_Time, Member_ID, Organization_ID, Network_Access_ID)
	VALUES('Event_Name1', '2018-06-08 13:38:24.357', '12', '128369818', '91276953', '1213', 1, 1, 1)
INSERT INTO [dbo].[Scheduled_Access](Event_Name, Date_Created_UTC, Actual_User_Count, Total_Input_Bytes, Total_Output_Bytes, Total_Session_Time, Member_ID, Organization_ID, Network_Access_ID)
	VALUES('Event_Name2', '2018-06-09 14:38:24.357', '3', '3498173', '13819593', '793', 2, 2, 2)
INSERT INTO [dbo].[Scheduled_Access](Event_Name, Date_Created_UTC, Actual_User_Count, Total_Input_Bytes, Total_Output_Bytes, Total_Session_Time, Member_ID, Organization_ID, Network_Access_ID)
	VALUES('Event_Name3', '2018-06-10 15:38:24.357', '4', '1427492', '9194825', '601', 3, 3, 3)
INSERT INTO [dbo].[Scheduled_Access](Event_Name, Date_Created_UTC, Actual_User_Count, Total_Input_Bytes, Total_Output_Bytes, Total_Session_Time, Member_ID, Organization_ID, Network_Access_ID)
	VALUES('Event_Name4', '2018-06-11 16:38:24.357', '5', '4313841', '184968241', '551', 4, 4, 4)
