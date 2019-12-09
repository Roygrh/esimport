USE [Radius]
GO

IF (EXISTS (SELECT *
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'dbo'
    AND TABLE_NAME = 'Radius_Acct_Event'))
BEGIN
    DROP TABLE [dbo].[Radius_Acct_Event]
END
GO

/****** Object:  Table [dbo].[Radius_Acct_Event]    Script Date: 6/29/2018 8:12:55 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Radius_Acct_Event]
(
    [ID] [bigint] IDENTITY(1,1) NOT NULL,
    [Session_ID] [varchar](256) NOT NULL,
    [Radius_Event_ID] [bigint] NOT NULL
)
GO
--  CONSTRAINT [PK_Radius_Acct_Event] PRIMARY KEY CLUSTERED 
-- (
-- 	[ID] ASC
-- )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PS_Partition_Acct_Event_By_Id]([ID])
-- ) ON [PS_Partition_Acct_Event_By_Id]([ID])

-- GO
-- ALTER TABLE [dbo].[Radius_Acct_Event]  WITH NOCHECK ADD  CONSTRAINT [FK_Radius_Acct_Event_Radius_Acct_Type] FOREIGN KEY([Radius_Acct_Type_ID])
-- REFERENCES [dbo].[Radius_Acct_Type] ([ID])
-- GO
-- ALTER TABLE [dbo].[Radius_Acct_Event] CHECK CONSTRAINT [FK_Radius_Acct_Event_Radius_Acct_Type]
-- GO
-- TODO: uncomment these in final commit
-- PUT DATA INSERT SCRIPTS BELOW
SET IDENTITY_INSERT Radius_Acct_Event ON
INSERT INTO [dbo].[Radius_Acct_Event]
    (ID, Session_ID, Radius_Event_ID)
VALUES
    (2652371592, '5B3657A7-331D8000', 1),
    (2652371591, '883D0997-0000ADC6', 2),
    (2652371590, '5A7FEF07-0032DEF1', 3),
    (2652371589, '5B63725B-0006162A', 4),
    (2652371588, '5B63725B-00061711', 5),
    (2652371587, '0601CEEB', 6),
    (2652371586, '0601CEE5', 7),
    (2652371585, '5B44733E-00007584', 8),
    (2652371584, '661E0ABD-00021305', 9 ),
    (2652371583, '661E0ABD-00021306', 10),
    (2652371582, '5B364DC4-3948C000', 11),
    (2652371581, '5B3657AE-3CE72000', 12)

GO