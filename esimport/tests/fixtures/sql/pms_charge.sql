DROP TABLE [dbo].[PMS_Charge]
GO

CREATE TABLE [dbo].[PMS_Charge](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Last_Name] [varchar](256) NOT NULL,
	[Room_Number] [varchar](256) NOT NULL,
 CONSTRAINT [PK_PMS_Charge] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO


-- PUT DATA INSERT SCRIPTS BELOW
INSERT INTO [dbo].[PMS_Charge](Last_Name, Room_Number)
	VALUES('trava', '4051')
INSERT INTO [dbo].[PMS_Charge](Last_Name, Room_Number)
	VALUES('trava', '4051')
INSERT INTO [dbo].[PMS_Charge](Last_Name, Room_Number)
	VALUES('trava', '4051')
INSERT INTO [dbo].[PMS_Charge](Last_Name, Room_Number)
	VALUES('trava', '4051')
INSERT INTO [dbo].[PMS_Charge](Last_Name, Room_Number)
	VALUES('Hansen', '1635')
INSERT INTO [dbo].[PMS_Charge](Last_Name, Room_Number)
	VALUES('Hansen', '1635')
INSERT INTO [dbo].[PMS_Charge](Last_Name, Room_Number)
	VALUES('andrews', '320')
INSERT INTO [dbo].[PMS_Charge](Last_Name, Room_Number)
	VALUES('andrews', '320')
GO