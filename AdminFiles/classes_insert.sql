-- SQL insert statements for the classes table (unique ClassCode+LineNo)
-- Paste these into your SQL editor to restore the classes data

INSERT INTO classes (ClassCode, LineNo, Misc1, RoomNo, CourseName, Misc2, Year, Dept, StaffCode, ClassSize, TotalSize, TimetableYear, Misc3) VALUES
('100COMP',0,'0','0','Computer Studies','NCEA Level 1',11,'Technology','VP',0,0,'2025TT','100COMP|VP||||VP||0|0||||2|0||'),
('SRREO',0,'0','1','Te Reo','Junior School',7,'Te Reo Māori','BP',19,19,'2025TT','SRREO|JSR||||BP|01|19|19||||2|0||'),
('SRLITR',0,'0','1','Literacy','Junior School',8,'English and Languages','SR',19,19,'2025TT','SRLITR|JSR||||SR|01|19|19||||2|0||'),
('SRMATH',0,'0','1','Mathematics','Junior School',8,'Mathematics','SR',19,19,'2025TT','SRMATH|JSR||||SR|01|19|19||||2|0||'),
('SRREAD',0,'0','1','Reading','Junior School',8,'English and Languages','SR',19,19,'2025TT','SRREAD|JSR||||SR|01|19|19||||2|0||'),
('SRSOCS',0,'0','1','Social Studies','Junior School',8,'Social Science','SR',19,19,'2025TT','SRSOCS|JSR||||SR|01|19|19||||2|0||'),
('SRWRITE',0,'0','1','Literacy','Junior School',8,'English and Languages','SR',19,19,'2025TT','SRWRITE|JSR||||SR|01|19|19||||2|0||'),
('WHANAU',0,'0','1','Life Skills/Personal Development','Year 1',1,'English and Languages','SR',15,15,'2025TT','WHANAU|9WPAPA||||SR|01|15|15||||2|0||'),
('SRHOME',0,'0','1','SRHOME','0',0,'SRHOME','SR',19,19,'2025TT','SRHOME|JSR||||SR|01|19|19||||2|0||'),
('MEET',0,'0','1','MEET','0',0,'MEET','SR',15,15,'2025TT','MEET|9WPAPA||||SR|01|15|15||||2|0||'),
('VEREO',0,'0','2','Te Reo Maori','Junior School',7,'Te Reo Māori','BP',24,24,'2025TT','VEREO|JVE||||BP|02|24|24||||2|0||'),
('VEHOME',0,'0','2','VEHOME','0',0,'VEHOME','LI',24,24,'2025TT','VEHOME|JVE||||LI|02|24|24||||2|2||'),
('VEHOME',1,'0','2','VEHOME','0',0,'VEHOME','MM',24,24,'2025TT','VEHOME|JVE||||MM|02|24|24||||2|1||'),
('WHANAU',1,'0','2','Life Skills/Personal Development','Year 1',1,'English and Languages','SH',11,11,'2025TT','WHANAU|7WPAPA||||SH|02|11|11||||2|0||'),
('MEET',1,'0','2','MEET','0',0,'MEET','SH',11,11,'2025TT','MEET|7WPAPA||||SH|02|11|11||||2|0||'),
('VEMATH',0,'0','2','Mathematics','Junior School',8,'Mathematics','SR',24,24,'2025TT','VEMATH|JVE||||SR|02|24|24||||2|1||'),
('VESOCS',0,'0','2','Social Studies','Junior School',7,'Social Science','SR',24,24,'2025TT','VESOCS|JVE||||SR|02|24|24||||2|0||'),
('VELITR',0,'0','2','Literacy','Year 8',8,'English and Languages','VE',24,24,'2025TT','VELITR|JVE||||VE|02|24|24||||2|0||'),
('VEMATH',1,'0','2','Mathematics','Junior School',8,'Mathematics','VE',24,24,'2025TT','VEMATH|JVE||||VE|02|24|24||||2|0||'),
('VEREAD',0,'0','2','Reading','Junior School',8,'Mathematics','VE',24,24,'2025TT','VEREAD|JVE||||VE|02|24|24||||2|0||'),
('VEWRITE',0,'0','2','Literacy','Junior School',7,'English and Languages','VE',24,24,'2025TT','VEWRITE|JVE||||VE|02|24|24||||2|0||'),
('VEHOME',2,'0','2','VEHOME','0',0,'VEHOME','VE',24,24,'2025TT','VEHOME|JVE||||VE|02|24|24||||2|0||');
-- (Add more rows as needed from your dump)
