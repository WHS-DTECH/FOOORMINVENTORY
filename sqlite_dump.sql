BEGIN TRANSACTION;
CREATE TABLE class_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_code TEXT,
            class_code TEXT,
            date_required TEXT,
            period INTEGER,
            recipe_id INTEGER,
            desired_servings INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
INSERT INTO "class_bookings" VALUES(1,'Dk','100HOSP','2025-12-25',4,19,24,'2025-12-13 00:07:35');
INSERT INTO "class_bookings" VALUES(2,'Dk','200HOSP','2025-12-25',3,21,24,'2025-12-13 01:28:54');
INSERT INTO "class_bookings" VALUES(3,'Dk','100HOSP','2025-12-25',3,22,24,'2025-12-13 01:32:49');
INSERT INTO "class_bookings" VALUES(4,'Dk','200HOSP','2025-12-25',3,8,24,'2025-12-13 01:49:19');
INSERT INTO "class_bookings" VALUES(5,'VP','300HOSP','2025-12-16',5,4,24,'2025-12-13 01:53:55');
INSERT INTO "class_bookings" VALUES(6,'VP','MFOOD','2025-12-17',2,19,24,'2025-12-13 01:54:17');
INSERT INTO "class_bookings" VALUES(7,'VP','SDFOOD','2025-12-18',4,19,24,'2025-12-13 01:54:46');
INSERT INTO "class_bookings" VALUES(8,'Dk','300HOSP','2025-12-19',4,3,24,'2025-12-13 02:37:59');
INSERT INTO "class_bookings" VALUES(9,'VP','300HOSP','2025-12-16',3,1,24,'2025-12-16 20:23:59');
INSERT INTO "class_bookings" VALUES(10,'VP','MFOOD','2025-12-23',2,5,24,'2025-12-16 20:58:00');
INSERT INTO "class_bookings" VALUES(11,'VP','200HOSP','2026-01-07',1,16,24,'2025-12-16 20:59:09');
INSERT INTO "class_bookings" VALUES(12,'VP','300HOSP','2025-12-18',1,22,4,'2025-12-18 19:19:27');
INSERT INTO "class_bookings" VALUES(13,'Dk','300HOSP','2025-12-25',1,1,24,'2025-12-18 21:37:11');
INSERT INTO "class_bookings" VALUES(14,'Dk','100HOSP','2025-12-19',1,19,48,'2025-12-19 02:14:08');
CREATE TABLE classes (
            ClassCode TEXT NOT NULL,
            LineNo INTEGER,
            Misc1 TEXT,
            RoomNo TEXT,
            CourseName TEXT,
            Misc2 TEXT,
            Year INTEGER,
            Dept TEXT,
            StaffCode TEXT,
            ClassSize INTEGER,
            TotalSize INTEGER,
            TimetableYear INTEGER,
            Misc3 TEXT,
            PRIMARY KEY (ClassCode, LineNo)
        );
INSERT INTO "classes" VALUES('100COMP',0,'0','0','Computer Studies','NCEA Level 1',11,'Technology','VP',0,0,'2025TT','100COMP|VP||||VP||0|0||||2|0||');
INSERT INTO "classes" VALUES('SRREO',NULL,'0','1','Te Reo','Junior School',7,'Te Reo Māori','BP',19,19,'2025TT','SRREO|JSR||||BP|01|19|19||||2|0||');
INSERT INTO "classes" VALUES('SRLITR',NULL,'0','1','Literacy','Junior School',8,'English and Languages','SR',19,19,'2025TT','SRLITR|JSR||||SR|01|19|19||||2|0||');
INSERT INTO "classes" VALUES('SRMATH',NULL,'0','1','Mathematics','Junior School',8,'Mathematics','SR',19,19,'2025TT','SRMATH|JSR||||SR|01|19|19||||2|0||');
INSERT INTO "classes" VALUES('SRREAD',NULL,'0','1','Reading','Junior School',8,'English and Languages','SR',19,19,'2025TT','SRREAD|JSR||||SR|01|19|19||||2|0||');
INSERT INTO "classes" VALUES('SRSOCS',NULL,'0','1','Social Studies','Junior School',8,'Social Science','SR',19,19,'2025TT','SRSOCS|JSR||||SR|01|19|19||||2|0||');
INSERT INTO "classes" VALUES('SRWRITE',NULL,'0','1','Literacy','Junior School',8,'English and Languages','SR',19,19,'2025TT','SRWRITE|JSR||||SR|01|19|19||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','1','Life Skills/Personal Development','Year 1',1,'English and Languages','SR',15,15,'2025TT','WHANAU|9WPAPA||||SR|01|15|15||||2|0||');
INSERT INTO "classes" VALUES('SRHOME',NULL,'0','1','SRHOME','0',0,'SRHOME','SR',19,19,'2025TT','SRHOME|JSR||||SR|01|19|19||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','1','MEET','0',0,'MEET','SR',15,15,'2025TT','MEET|9WPAPA||||SR|01|15|15||||2|0||');
INSERT INTO "classes" VALUES('VEREO',NULL,'0','2','Te Reo Maori','Junior School',7,'Te Reo Māori','BP',24,24,'2025TT','VEREO|JVE||||BP|02|24|24||||2|0||');
INSERT INTO "classes" VALUES('VEHOME',NULL,'0','2','VEHOME','0',0,'VEHOME','LI',24,24,'2025TT','VEHOME|JVE||||LI|02|24|24||||2|2||');
INSERT INTO "classes" VALUES('VEHOME',NULL,'0','2','VEHOME','0',0,'VEHOME','MM',24,24,'2025TT','VEHOME|JVE||||MM|02|24|24||||2|1||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','2','Life Skills/Personal Development','Year 1',1,'English and Languages','SH',11,11,'2025TT','WHANAU|7WPAPA||||SH|02|11|11||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','2','MEET','0',0,'MEET','SH',11,11,'2025TT','MEET|7WPAPA||||SH|02|11|11||||2|0||');
INSERT INTO "classes" VALUES('VEMATH',NULL,'0','2','Mathematics','Junior School',8,'Mathematics','SR',24,24,'2025TT','VEMATH|JVE||||SR|02|24|24||||2|1||');
INSERT INTO "classes" VALUES('VESOCS',NULL,'0','2','Social Studies','Junior School',7,'Social Science','SR',24,24,'2025TT','VESOCS|JVE||||SR|02|24|24||||2|0||');
INSERT INTO "classes" VALUES('VELITR',NULL,'0','2','Literacy','Year 8',8,'English and Languages','VE',24,24,'2025TT','VELITR|JVE||||VE|02|24|24||||2|0||');
INSERT INTO "classes" VALUES('VEMATH',NULL,'0','2','Mathematics','Junior School',8,'Mathematics','VE',24,24,'2025TT','VEMATH|JVE||||VE|02|24|24||||2|0||');
INSERT INTO "classes" VALUES('VEREAD',NULL,'0','2','Reading','Junior School',8,'Mathematics','VE',24,24,'2025TT','VEREAD|JVE||||VE|02|24|24||||2|0||');
INSERT INTO "classes" VALUES('VEWRITE',NULL,'0','2','Literacy','Junior School',7,'English and Languages','VE',24,24,'2025TT','VEWRITE|JVE||||VE|02|24|24||||2|0||');
INSERT INTO "classes" VALUES('VEHOME',NULL,'0','2','VEHOME','0',0,'VEHOME','VE',24,24,'2025TT','VEHOME|JVE||||VE|02|24|24||||2|0||');
INSERT INTO "classes" VALUES('SDREO',NULL,'0','3','Te Re Maori','Junior School',7,'Te Reo Māori','HE',19,19,'2025TT','SDREO|JSD||||HE|03|19|19||||2|0||');
INSERT INTO "classes" VALUES('SDDRAMA',NULL,'0','3','Drama','Junior School',8,'Arts','KV',19,19,'2025TT','SDDRAMA|JSD||||KV|03|19|19||||2|0||');
INSERT INTO "classes" VALUES('SDSOCS',NULL,'0','3','Social Studies','Year 8',7,'Junior School','LI',19,19,'2025TT','SDSOCS|JSD||||LI|03|19|19||||2|0||');
INSERT INTO "classes" VALUES('SDLITR',NULL,'0','3','Literacy','Year 8',8,'English and Languages','SD',19,19,'2025TT','SDLITR|JSD||||SD|03|19|19||||2|0||');
INSERT INTO "classes" VALUES('SDMATH',NULL,'0','3','Mathematics','Year 7',7,'Junior School','SD',19,19,'2025TT','SDMATH|JSD||||SD|03|19|19||||2|0||');
INSERT INTO "classes" VALUES('SDREAD',NULL,'0','3','Drama','Year 1',1,'Learning Support','SD',19,19,'2025TT','SDREAD|JSD||||SD|03|19|19||||2|0||');
INSERT INTO "classes" VALUES('SDWRITE',NULL,'0','3','Literacy','Year 1',1,'English and Languages','SD',19,19,'2025TT','SDWRITE|JSD||||SD|03|19|19||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','3','Life Skills/Personal Development','Year 1',1,'English and Languages','SD',13,13,'2025TT','WHANAU|7WHAU||||SD|03|13|13||||2|0||');
INSERT INTO "classes" VALUES('SDHOME',NULL,'0','3','SDHOME','0',0,'SDHOME','SD',19,19,'2025TT','SDHOME|JSD||||SD|03|19|19||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','3','MEET','0',0,'MEET','SD',13,13,'2025TT','MEET|7WHAU||||SD|03|13|13||||2|0||');
INSERT INTO "classes" VALUES('SDLITR',NULL,'0','3','Literacy','Year 8',8,'English and Languages','VP',19,19,'2025TT','SDLITR|JSD||||VP|03|19|19||||2|1||');
INSERT INTO "classes" VALUES('MIREO',NULL,'0','4','Te Reo Maori','Junior School',7,'Te Reo Māori','BP',20,20,'2025TT','MIREO|JMI||||BP|04|20|20||||2|0||');
INSERT INTO "classes" VALUES('MICONS',NULL,'0','4','Conservation','Junior School',7,'Science','BT',20,20,'2025TT','MICONS|JMI||||BT|04|20|20||||2|0||');
INSERT INTO "classes" VALUES('MILITR',NULL,'0','4','Literacy','Year 8',8,'English and Languages','MM',20,20,'2025TT','MILITR|JMI||||MM|04|20|20||||2|0||');
INSERT INTO "classes" VALUES('MIMATH',NULL,'0','4','Mathematics','Junior School',8,'Mathematics','MM',20,20,'2025TT','MIMATH|JMI||||MM|04|20|20||||2|0||');
INSERT INTO "classes" VALUES('MIREAD',NULL,'0','4','Specify Subject Name','Junior School',7,'English and Languages','MM',20,20,'2025TT','MIREAD|JMI||||MM|04|20|20||||2|0||');
INSERT INTO "classes" VALUES('MISOCS',NULL,'0','4','Social Studies','Junior School',7,'Social Science','MM',20,20,'2025TT','MISOCS|JMI||||MM|04|20|20||||2|0||');
INSERT INTO "classes" VALUES('MIWRITE',NULL,'0','4','Literacy','Junior School',7,'English and Languages','MM',20,20,'2025TT','MIWRITE|JMI||||MM|04|20|20||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','4','Life Skills/Personal Development','Year 1',1,'English and Languages','MM',14,14,'2025TT','WHANAU|8WAHI||||MM|04|14|14||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','4','MEET','0',0,'MEET','MM',14,14,'2025TT','MEET|8WAHI||||MM|04|14|14||||2|0||');
INSERT INTO "classes" VALUES('MIHOME',NULL,'0','4','Media Studies','Junior School',8,'Social Science','PI',20,20,'2025TT','MIHOME|JMI||||PI|04|20|20||||2|0||');
INSERT INTO "classes" VALUES('PIHOME',NULL,'0','5','Literacy','Junior School',8,'English and Languages','PI',21,21,'2025TT','PIHOME|JPI||||PI|05|21|21||||2|0||');
INSERT INTO "classes" VALUES('PILITR',NULL,'0','5','Literacy','Junior School',8,'English and Languages','PI',21,21,'2025TT','PILITR|JPI||||PI|05|21|21||||2|0||');
INSERT INTO "classes" VALUES('PIMATH',NULL,'0','5','Mathematics','Year 8',8,'Mathematics','PI',21,21,'2025TT','PIMATH|JPI||||PI|05|21|21||||2|0||');
INSERT INTO "classes" VALUES('PIREAD',NULL,'0','5','Specify Subject Name','Junior School',7,'English and Languages','PI',21,21,'2025TT','PIREAD|JPI||||PI|05|21|21||||2|0||');
INSERT INTO "classes" VALUES('PISOCS',NULL,'0','5','Social Studies','Junior School',7,'Social Science','PI',21,21,'2025TT','PISOCS|JPI||||PI|05|21|21||||2|0||');
INSERT INTO "classes" VALUES('PIWRITE',NULL,'0','5','Writing','Junior School',7,'English and Languages','PI',21,21,'2025TT','PIWRITE|JPI||||PI|05|21|21||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','5','Life Skills/Personal Development','Year 1',1,'English and Languages','PI',12,12,'2025TT','WHANAU|8WWAI||||PI|05|12|12||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','5','MEET','0',0,'MEET','PI',12,12,'2025TT','MEET|8WWAI||||PI|05|12|12||||2|0||');
INSERT INTO "classes" VALUES('PITEXT',NULL,'0','5','Textiles Technology','Junior School',8,'Technology','RS',21,21,'2025TT','PITEXT|JPI||||RS|05|21|21||||2|0||');
INSERT INTO "classes" VALUES('PIREO',NULL,'0','5','Te Reo Maori','Junior School',8,'Te Reo Māori','WE',21,21,'2025TT','PIREO|JPI||||WE|05|21|21||||2|0||');
INSERT INTO "classes" VALUES('12STUDYLI',NULL,'0','6','12STUDYLI','Year 12',12,'STUDYLI','CY',17,17,'2025TT','12STUDYLI|Year12PE||||CY|06|17|17||||2|0||');
INSERT INTO "classes" VALUES('10SS',NULL,'0','6','Social Studies','Year 10',10,'Social Science','MC',25,25,'2025TT','10SS|10H||||MC|6|25|25||||2|0||');
INSERT INTO "classes" VALUES('100LITR',0,'0','6','Level 1 Literacy','NCEA Level 1',11,'English and Languages','PQ',18,18,'2025TT','100LITR|Year11LITR||||PQ|6|18|18||||2|0||');
INSERT INTO "classes" VALUES('300CLST',6,'1','6','Classics','NCEA Level 3',13,'Social Science','SO',5,5,'2025TT','300CLST||6|1|0|SO|6|5|5||||1|0||');
INSERT INTO "classes" VALUES('300ENG',4,'1','6','English','NCEA Level 3',13,'English and Languages','SO',21,21,'2025TT','300ENG||4|1|0|SO|6|21|21||||1|0||');
INSERT INTO "classes" VALUES('Gateway',0,'0','6','Transition/Pre-Employment','NCEA Level 2',12,'Gateway','SO',6,6,'2025TT','Gateway|||||SO|6|6|6|21056;21056;20035;21031;21049;21049|||3|0');
INSERT INTO "classes" VALUES('200CLST',6,'1','6','Classics','NCEA Level 2',12,'Social Science','SO',9,9,'2025TT','200CLST||6|1|0|SO|6|9|9||||1|0||');
INSERT INTO "classes" VALUES('200ENG',2,'1','6','English','NCEA Level 2',12,'English and Languages','SO',24,24,'2025TT','200ENG||2|1|0|SO|6|24|24||||1|0||');
INSERT INTO "classes" VALUES('10ENG',NULL,'0','6','English','Year 10',10,'English and Languages','SO',25,25,'2025TT','10ENG|10H||||SO|6|25|25||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','6','Life Skills/Personal Development','Year 1',1,'English and Languages','SO',12,12,'2025TT','WHANAU|11WPAPA||||SO|6|12|12||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','6','MEET','0',0,'MEET','SO',12,12,'2025TT','MEET|11WPAPA||||SO|6|12|12||||2|0||');
INSERT INTO "classes" VALUES('13STUDYBt',7,'1','7','13STUDYBt','Year 13',13,'STUDYBt','BT',15,15,'2025TT','13STUDYBt||7|1|0|BT|7|15|15||||1|0||');
INSERT INTO "classes" VALUES('11STUDYBt',7,'1','7','11STUDYBt','Year 11',11,'STUDYBt','BT',20,20,'2025TT','11STUDYBt||7|1|0|BT|7|20|20||||1|0||');
INSERT INTO "classes" VALUES('9MATH',NULL,'0','7','Mathematics','Year 9',9,'Mathematics','JK',20,20,'2025TT','9MATH|9S||||JK|7|20|20||||2|0||');
INSERT INTO "classes" VALUES('9SS',NULL,'0','7','Social Studies','Year 9',9,'Social Science','LI',20,20,'2025TT','9SS|9S||||LI|7|20|20||||2|0||');
INSERT INTO "classes" VALUES('9ENG',NULL,'0','7','English','Year 9',9,'English and Languages','MC',20,20,'2025TT','9ENG|9S||||MC|7|20|20||||2|0||');
INSERT INTO "classes" VALUES('10ENG',NULL,'0','7','English','Year 10',10,'English and Languages','PQ',16,16,'2025TT','10ENG|10S||||PQ|7|16|16||||2|0||');
INSERT INTO "classes" VALUES('MJOURNAL',NULL,'1','7','Journalism','Middle School',10,'English and Languages','PQ',9,25,'2025TT','MJOURNAL||82|1|4|PQ|7|9|25||||1|0||');
INSERT INTO "classes" VALUES('MJOURNAL',NULL,'1','7','Journalism','Middle School',10,'English and Languages','PQ',9,25,'2025TT','MJOURNAL||82|1|3|PQ|7|9|25||||1|0||');
INSERT INTO "classes" VALUES('MJOURNAL',NULL,'1','7','Journalism','Middle School',10,'English and Languages','PQ',18,25,'2025TT','MJOURNAL||82|1|2|PQ|7|18|25||||1|0||');
INSERT INTO "classes" VALUES('MJOURNAL',NULL,'1','7','Journalism','Middle School',10,'English and Languages','PQ',19,25,'2025TT','MJOURNAL||82|1|1|PQ|7|19|25||||1|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','7','Life Skills/Personal Development','Year 1',1,'English and Languages','PQ',13,13,'2025TT','WHANAU|10WPAPA||||PQ|7|13|13||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','7','MEET','0',0,'MEET','PQ',13,13,'2025TT','MEET|10WPAPA||||PQ|7|13|13||||2|0||');
INSERT INTO "classes" VALUES('13STUDYSh',7,'1','7','13STUDYSh','Year 13',13,'STUDYSh','SH',16,16,'2025TT','13STUDYSh||7|1|0|SH|7|16|16||||1|0||');
INSERT INTO "classes" VALUES('100NUMR',2,'1','8','Level 1 Numeracy','NCEA Level 1',11,'Mathematics','CL',13,27,'2025TT','100NUMR||2|1|0|CL|8|13|27||||1|0||');
INSERT INTO "classes" VALUES('300MATC',5,'1','8','Mathematics with Calculus','NCEA Level 3',13,'Mathematics','JD',8,8,'2025TT','300MATC||5|1|0|JD|8|8|8||||1|0||');
INSERT INTO "classes" VALUES('9MATH',NULL,'0','8','Mathematics','Year 9',9,'Mathematics','JD',17,17,'2025TT','9MATH|9H||||JD|8|17|17||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','8','Life Skills/Personal Development','Year 1',1,'English and Languages','JM',13,13,'2025TT','WHANAU|9WWAI||||JM|8|13|13||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','8','MEET','0',0,'MEET','JM',13,13,'2025TT','MEET|9WWAI||||JM|8|13|13||||2|0||');
INSERT INTO "classes" VALUES('9SS',NULL,'0','8','Social Studies','Year 9',9,'Social Science','MC',17,17,'2025TT','9SS|9H||||MC|8|17|17||||2|0||');
INSERT INTO "classes" VALUES('9ENG',NULL,'0','8','English','Year 9',9,'English and Languages','PQ',17,17,'2025TT','9ENG|9H||||PQ|8|17|17||||2|0||');
INSERT INTO "classes" VALUES('100ENG',3,'1','8','English','NCEA Level 1',11,'English and Languages','WA',22,40,'2025TT','100ENG||3|1|0|WA|8|22|40||||1|0||');
INSERT INTO "classes" VALUES('200MATH',3,'1','9','Mathematics - Advanced','NCEA Level 2',12,'Mathematics','CL',23,23,'2025TT','200MATH||3|1|0|CL|9|23|23||||1|0||');
INSERT INTO "classes" VALUES('100MATH',1,'1','9','Mathematics','NCEA Level 1',11,'Mathematics','CL',27,27,'2025TT','100MATH||1|1|0|CL|9|27|27||||1|0||');
INSERT INTO "classes" VALUES('9MATH',NULL,'0','9','Mathematics','Year 9',9,'Mathematics','CL',18,18,'2025TT','9MATH|9W||||CL|9|18|18||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','9','Life Skills/Personal Development','Year 1',1,'English and Languages','CL',14,14,'2025TT','WHANAU|10WWAI||||CL|9|14|14||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','9','MEET','0',0,'MEET','CL',14,14,'2025TT','MEET|10WWAI||||CL|9|14|14||||2|0||');
INSERT INTO "classes" VALUES('9SS',NULL,'0','9','Social Studies','Year 9',9,'Social Science','JM',18,18,'2025TT','9SS|9W||||JM|9|18|18||||2|0||');
INSERT INTO "classes" VALUES('9ENG',NULL,'0','9','English','Year 9',9,'English and Languages','WA',18,18,'2025TT','9ENG|9W||||WA|9|18|18||||2|0||');
INSERT INTO "classes" VALUES('MCONS',NULL,'1','10','Conservation','Middle School',10,'Social Science','BT',19,31,'2025TT','MCONS||82|1|4|BT|10|19|31||||1|0||');
INSERT INTO "classes" VALUES('MCONS',NULL,'1','10','Conservation','Middle School',10,'Social Science','BT',18,31,'2025TT','MCONS||82|1|3|BT|10|18|31||||1|0||');
INSERT INTO "classes" VALUES('MCONS',NULL,'1','10','Conservation','Middle School',10,'Social Science','BT',19,31,'2025TT','MCONS||82|1|2|BT|10|19|31||||1|0||');
INSERT INTO "classes" VALUES('10SS',NULL,'0','10','Social Studies','Year 10',10,'Social Science','CY',16,16,'2025TT','10SS|10S||||CY|10|16|16||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','10','Life Skills/Personal Development','Year 1',1,'English and Languages','CY',19,19,'2025TT','WHANAU|10WHAU||||CY|10|19|19||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','10','MEET','0',0,'MEET','CY',19,19,'2025TT','MEET|10WHAU||||CY|10|19|19||||2|0||');
INSERT INTO "classes" VALUES('100HIST',4,'1','10','History','NCEA Level 1',11,'Social Science','JM',19,19,'2025TT','100HIST||4|1|0|JM|10|19|19||||1|0||');
INSERT INTO "classes" VALUES('NETNZ',3,'1','10','NETNZ','NCEA Level 1',11,'Administration','JT',1,1,'2025TT','NETNZ||3|1|0|JT|10|1|1||||1|0|1|200021604');
INSERT INTO "classes" VALUES('NETNZTEREO',3,'1','10','Level 1 Te Reo Maori','NCEA Level 1',11,'Te Reo Māori','JT',0,3,'2025TT','NETNZTEREO||3|1|0|JT|10|0|3||||1|0|1|200021604');
INSERT INTO "classes" VALUES('SocialStud',0,'0','10','SocialStud','0',0,'SocialStud','RY',28,28,'2025TT','SocialStud|||||RY|10|28|28|19066;19066;19066;19066;19066;19066;19066;19066;19066;19066;19066;19066;19066;19066;22019;22019;22019;22019;22019;22019;22019;22019;22019;22019;22019;22019;22019;22019|||3|0');
INSERT INTO "classes" VALUES('10MATH',NULL,'0','10','Mathematics','Year 10',10,'Mathematics','SD',16,16,'2025TT','10MATH|10S||||SD|10|16|16||||2|0||');
INSERT INTO "classes" VALUES('10ENG',NULL,'0','10','English','Year 10',10,'English and Languages','TJ',23,23,'2025TT','10ENG|10W||||TJ|10|23|23||||2|0||');
INSERT INTO "classes" VALUES('10SS',NULL,'0','10','Social Studies','Year 10',10,'Social Science','TJ',23,23,'2025TT','10SS|10W||||TJ|10|23|23||||2|0||');
INSERT INTO "classes" VALUES('10SCIHE',0,'0','12','10SCIHE','Year 10',10,'SCIHE','AE',1,1,'2025TT','10SCIHE|||||AE|12|1|1|23053|||3|0');
INSERT INTO "classes" VALUES('MISCI',NULL,'0','12','Science','Junior School',7,'Science','AE',20,20,'2025TT','MISCI|JMI||||AE|12|20|20||||2|0||');
INSERT INTO "classes" VALUES('200CHEM',6,'1','12','Chemistry','NCEA Level 2',12,'Science','SH',11,16,'2025TT','200CHEM||6|1|0|SH|12|11|16||||1|0||');
INSERT INTO "classes" VALUES('9SCI',NULL,'0','12','Science','Year 9',9,'Science','SH',17,17,'2025TT','9SCI|9H||||SH|12|17|17||||2|0||');
INSERT INTO "classes" VALUES('VESCI',NULL,'0','12','Science','Junior School',7,'Science','SH',24,24,'2025TT','VESCI|JVE||||SH|12|24|24||||2|0||');
INSERT INTO "classes" VALUES('MISCI',NULL,'0','12','Science','Junior School',7,'Science','VR',20,20,'2025TT','MISCI|JMI||||VR|12|20|20||||2|1||');
INSERT INTO "classes" VALUES('300CHEM',3,'1','12','Chemistry','NCEA Level 3',13,'Science','WY',5,5,'2025TT','300CHEM||3|1|0|WY|12|5|5||||1|0||');
INSERT INTO "classes" VALUES('200CHEM',3,'1','12','Chemistry','NCEA Level 2',12,'Science','WY',5,16,'2025TT','200CHEM||3|1|0|WY|12|5|16||||1|0||');
INSERT INTO "classes" VALUES('100SCIE',1,'1','12','Science','NCEA Level 1',11,'Science','WY',16,53,'2025TT','100SCIE||1|1|0|WY|12|16|53||||1|0||');
INSERT INTO "classes" VALUES('10SCI',NULL,'0','12','Science','Year 10',10,'Science','WY',25,25,'2025TT','10SCI|10H||||WY|12|25|25||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','12','Life Skills/Personal Development','Year 1',1,'English and Languages','WY',12,12,'2025TT','WHANAU|7WAHI||||WY|12|12|12||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','12','MEET','0',0,'MEET','WY',12,12,'2025TT','MEET|7WAHI||||WY|12|12|12||||2|0||');
INSERT INTO "classes" VALUES('100SCIE',6,'1','13','Science','NCEA Level 1',11,'Science','BT',21,53,'2025TT','100SCIE||6|1|0|BT|13|21|53||||1|0||');
INSERT INTO "classes" VALUES('300BIOL',1,'1','13','Biology','NCEA Level 3',13,'Science','SH',11,11,'2025TT','300BIOL||1|1|0|SH|13|11|11||||1|0||');
INSERT INTO "classes" VALUES('MTRSCI',NULL,'0','13','Science','Middle School',10,'Science','SH',10,10,'2025TT','MTRSCI|MTR||||SH|13|10|10||||2|0||');
INSERT INTO "classes" VALUES('JTRSCI',NULL,'0','13','Science','Junior School',7,'Science','SH',14,14,'2025TT','JTRSCI|JTR||||SH|13|14|14||||2|0||');
INSERT INTO "classes" VALUES('200BIOL',4,'1','13','Biology','NCEA Level 2',12,'Science','VR',20,20,'2025TT','200BIOL||4|1|0|VR|13|20|20||||1|0||');
INSERT INTO "classes" VALUES('100SCIE',3,'1','13','Science','NCEA Level 1',11,'Science','VR',16,53,'2025TT','100SCIE||3|1|0|VR|13|16|53||||1|0||');
INSERT INTO "classes" VALUES('10SCI',NULL,'0','13','Science','Year 10',10,'Science','VR',16,16,'2025TT','10SCI|10S||||VR|13|16|16||||2|0||');
INSERT INTO "classes" VALUES('9SCI',NULL,'0','13','Science','Year 9',9,'Science','VR',20,20,'2025TT','9SCI|9S||||VR|13|20|20||||2|0||');
INSERT INTO "classes" VALUES('PISCI',NULL,'0','13','Science','Junior School',7,'Science','VR',21,21,'2025TT','PISCI|JPI||||VR|13|21|21||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','13','Life Skills/Personal Development','Year 1',1,'English and Languages','VR',12,12,'2025TT','WHANAU|9WHAU||||VR|13|12|12||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','13','MEET','0',0,'MEET','VR',12,12,'2025TT','MEET|9WHAU||||VR|13|12|12||||2|0||');
INSERT INTO "classes" VALUES('300PHYS',2,'1','14','Physics','NCEA Level 3',13,'Science','AE',10,10,'2025TT','300PHYS||2|1|0|AE|14|10|10||||1|0||');
INSERT INTO "classes" VALUES('200PHYS',5,'1','14','Physics','NCEA Level 2',12,'Science','AE',17,17,'2025TT','200PHYS||5|1|0|AE|14|17|17||||1|0||');
INSERT INTO "classes" VALUES('10SCI',NULL,'0','14','Science','Year 10',10,'Science','AE',23,23,'2025TT','10SCI|10W||||AE|14|23|23||||2|0||');
INSERT INTO "classes" VALUES('9SCI',NULL,'0','14','Science','Year 9',9,'Science','AE',18,18,'2025TT','9SCI|9W||||AE|14|18|18||||2|0||');
INSERT INTO "classes" VALUES('SRSCI',NULL,'0','14','Science','Year 7',7,'Science','AE',19,19,'2025TT','SRSCI|JSR||||AE|14|19|19||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','14','Life Skills/Personal Development','Year 1',1,'English and Languages','AE',7,7,'2025TT','WHANAU|12WWAI||||AE|14|7|7||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','14','MEET','0',0,'MEET','AE',7,7,'2025TT','MEET|12WWAI||||AE|14|7|7||||2|0||');
INSERT INTO "classes" VALUES('SDSCI',NULL,'0','14','Science','Junior School',8,'Science','SH',19,19,'2025TT','SDSCI|JSD||||SH|14|19|19||||2|0||');
INSERT INTO "classes" VALUES('200AGHO',6,'1','15','Agriculture and Horticulture','NCEA Level 2',12,'Science','WY',8,8,'2025TT','200AGHO||6|1|0|WY|15|8|8||||1|0||');
INSERT INTO "classes" VALUES('200COLAB',1,'1','22','Colab Mathematics','NCEA Level 2',12,'Mathematics','JK',0,0,'2025TT','200COLAB||1|1|0|JK|22|0|0||||1|0||');
INSERT INTO "classes" VALUES('100NUMR',4,'1','22','Level 1 Numeracy','NCEA Level 1',11,'Mathematics','JK',14,27,'2025TT','100NUMR||4|1|0|JK|22|14|27||||1|0||');
INSERT INTO "classes" VALUES('10MATH',NULL,'0','22','Mathematics','Year 10',10,'Mathematics','JK',25,25,'2025TT','10MATH|10H||||JK|22|25|25||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','22','Life Skills/Personal Development','Year 1',1,'English and Languages','JK',14,14,'2025TT','WHANAU|11WWAI||||JK|22|14|14||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','22','MEET','0',0,'MEET','JK',14,14,'2025TT','MEET|11WWAI||||JK|22|14|14||||2|0||');
INSERT INTO "classes" VALUES('10MATH',NULL,'0','22','Mathematics','Year 10',10,'Mathematics','JM',23,23,'2025TT','10MATH|10W||||JM|22|23|23||||2|0||');
INSERT INTO "classes" VALUES('12STUDYRs',7,'1','23','12STUDYRs','Year 12',12,'STUDYRs','RS',28,28,'2025TT','12STUDYRs||7|1|0|RS|23|28|28||||1|0||');
INSERT INTO "classes" VALUES('MCONS',NULL,'1','8a','Conservation','Middle School',10,'Social Science','BT',14,31,'2025TT','MCONS||82|1|1|BT|8a|14|31||||1|0||');
INSERT INTO "classes" VALUES('200HIST',5,'1','8a','History','NCEA Level 2',12,'Social Science','CY',7,7,'2025TT','200HIST||5|1|0|CY|8a|7|7||||1|0||');
INSERT INTO "classes" VALUES('ESOL',0,'0','8a','ESOL','0',0,'ESOL','CY',6,6,'2025TT','ESOL|||||CY|8a|6|6|25094;23091;24067;25092;25091;25093|||3|0');
INSERT INTO "classes" VALUES('RightTrack',0,'0','BMeet','RightTrack','0',0,'RightTrack','KV',4,4,'2025TT','RightTrack|||||KV|BMeet|4|4|23043;21029;21050;21009|||3|0');
INSERT INTO "classes" VALUES('300COMP',8,'1','CW','Computer Studies','NCEA Level 3',13,'Technology','VP',0,0,'2025TT','300COMP||8|1|0|VP|CW|0|0||||1|0||');
INSERT INTO "classes" VALUES('300DTECH',4,'1','CW','Digital Technologies','NCEA Level 3',13,'Technology','VP',1,5,'2025TT','300DTECH||4|1|0|VP|CW|1|5||||1|0||');
INSERT INTO "classes" VALUES('300DTECH',1,'1','CW','Digital Technologies','NCEA Level 3',13,'Technology','VP',4,5,'2025TT','300DTECH||1|1|0|VP|CW|4|5||||1|0||');
INSERT INTO "classes" VALUES('200COMP',8,'1','CW','Computer Studies','NCEA Level 2',12,'Technology','VP',0,0,'2025TT','200COMP||8|1|0|VP|CW|0|0||||1|0||');
INSERT INTO "classes" VALUES('200DTECH',4,'1','CW','Digital Technologies','NCEA Level 2',12,'Technology','VP',3,11,'2025TT','200DTECH||4|1|0|VP|CW|3|11||||1|0||');
INSERT INTO "classes" VALUES('200DTECH',1,'1','CW','Digital Technologies','NCEA Level 2',12,'Technology','VP',8,11,'2025TT','200DTECH||1|1|0|VP|CW|8|11||||1|0||');
INSERT INTO "classes" VALUES('100DTECHS',9,'1','CW','Digital Technologies','NCEA Level 1',11,'Technology','VP',1,1,'2025TT','100DTECHS||9|1|0|VP|CW|1|1||||1|0||');
INSERT INTO "classes" VALUES('100COMP',8,'1','CW','Computer Studies','NCEA Level 1',11,'Technology','VP',0,1,'2025TT','100COMP||8|1|0|VP|CW|0|1||||1|0||');
INSERT INTO "classes" VALUES('100DTECH',4,'1','CW','Digital Technologies','NCEA Level 1',11,'Technology','VP',7,14,'2025TT','100DTECH||4|1|0|VP|CW|7|14||||1|0||');
INSERT INTO "classes" VALUES('100DTECH',1,'1','CW','Digital Technologies','NCEA Level 1',11,'Technology','VP',7,14,'2025TT','100DTECH||1|1|0|VP|CW|7|14||||1|0||');
INSERT INTO "classes" VALUES('MWEB',NULL,'1','CW','Web Design','Middle School',10,'Technology','VP',25,25,'2025TT','MWEB||81|1|4|VP|CW|25|25||||1|0||');
INSERT INTO "classes" VALUES('MWEB',NULL,'1','CW','Web Design','Middle School',10,'Technology','VP',25,25,'2025TT','MWEB||81|1|3|VP|CW|25|25||||1|0||');
INSERT INTO "classes" VALUES('MPROG',NULL,'1','CW','Middle DTECH - Programming','Middle School',10,'Technology','VP',24,24,'2025TT','MPROG||81|1|2|VP|CW|24|24||||1|0||');
INSERT INTO "classes" VALUES('MPROG',NULL,'1','CW','Middle DTECH - Programming','Middle School',10,'Technology','VP',24,24,'2025TT','MPROG||81|1|1|VP|CW|24|24||||1|0||');
INSERT INTO "classes" VALUES('SRDTECH',NULL,'0','CW','Digital Technology','Junior School',8,'Technology','VP',19,19,'2025TT','SRDTECH|JSR||||VP|CW|19|19||||2|0||');
INSERT INTO "classes" VALUES('SDDTECH',NULL,'0','CW','Digital Technologies','Junior School',7,'Technology','VP',19,19,'2025TT','SDDTECH|JSD||||VP|CW|19|19||||2|0||');
INSERT INTO "classes" VALUES('PIDTECH',NULL,'0','CW','Digital Technologies','Year 7',7,'Technology','VP',21,21,'2025TT','PIDTECH|JPI||||VP|CW|21|21||||2|0||');
INSERT INTO "classes" VALUES('MIDTECH',NULL,'0','CW','Digital Technologies','Junior School',7,'Technology','VP',20,20,'2025TT','MIDTECH|JMI||||VP|CW|20|20||||2|0||');
INSERT INTO "classes" VALUES('8SDTECH',NULL,'0','CW','Digital Technologies','Year 7',7,'Technology','VP',11,11,'2025TT','8SDTECH|8S||||VP|CW|11|11||||2|0||');
INSERT INTO "classes" VALUES('7SDTECH',NULL,'0','CW','Digtal Technologies','Year 7',7,'Technology','VP',13,13,'2025TT','7SDTECH|7S||||VP|CW|13|13||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','CW','Life Skills/Personal Development','Year 1',1,'English and Languages','VP',14,14,'2025TT','WHANAU|8WHAU||||VP|CW|14|14||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','CW','MEET','0',0,'MEET','VP',14,14,'2025TT','MEET|8WHAU||||VP|CW|14|14||||2|0||');
INSERT INTO "classes" VALUES('300MATS',5,'1','DR','Mathematics with Statistics','NCEA Level 3',13,'Mathematics','CL',16,16,'2025TT','300MATS||5|1|0|CL|DR|16|16||||1|0||');
INSERT INTO "classes" VALUES('MDRAMA',NULL,'1','DR','Drama','Middle School',10,'Arts','JA',18,30,'2025TT','MDRAMA||81|1|4|JA|DR|18|30||||1|0||');
INSERT INTO "classes" VALUES('MDRAMA',NULL,'1','DR','Drama','Middle School',10,'Arts','JA',17,30,'2025TT','MDRAMA||81|1|3|JA|DR|17|30||||1|0||');
INSERT INTO "classes" VALUES('MDRAMA',NULL,'1','DR','Drama','Middle School',10,'Arts','JA',15,30,'2025TT','MDRAMA||81|1|2|JA|DR|15|30||||1|0||');
INSERT INTO "classes" VALUES('MDRAMA',NULL,'1','DR','Drama','Middle School',10,'Arts','JA',0,30,'2025TT','MDRAMA||81|1|1|JA|DR|0|30||||1|0||');
INSERT INTO "classes" VALUES('VEDRAMA',NULL,'0','DR','Drama','Junior School',7,'Arts','JA',24,24,'2025TT','VEDRAMA|JVE||||JA|DR|24|24||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','DR','Life Skills/Personal Development','Year 1',1,'English and Languages','JA',11,11,'2025TT','WHANAU|12WHAU||||JA|DR|11|11||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','DR','MEET','0',0,'MEET','JA',11,11,'2025TT','MEET|12WHAU||||JA|DR|11|11||||2|0||');
INSERT INTO "classes" VALUES('NETNZDRAMA',6,'1','DR','Drama','Year 1',1,'Arts','RS',1,6,'2025TT','NETNZDRAMA||6|1|0|RS|DR|1|6||||1|1||');
INSERT INTO "classes" VALUES('NETNZDRAMA',4,'1','DR','Drama','Year 1',1,'Arts','RS',2,6,'2025TT','NETNZDRAMA||4|1|0|RS|DR|2|6||||1|1||');
INSERT INTO "classes" VALUES('NETNZDRAMA',2,'1','DR','Drama','Year 1',1,'Arts','RS',1,6,'2025TT','NETNZDRAMA||2|1|0|RS|DR|1|6||||1|1||');
INSERT INTO "classes" VALUES('300HOSP',1,'1','F','Hospitality','NCEA Level 3',13,'Technology','DK',18,18,'2025TT','300HOSP||1|1|0|DK|F|18|18||||1|0||');
INSERT INTO "classes" VALUES('100HOSP',6,'1','F','Hospitality','NCEA Level 1',11,'Technology','DK',18,38,'2025TT','100HOSP||6|1|0|DK|F|18|38||||1|0||');
INSERT INTO "classes" VALUES('MFOOD',NULL,'1','F','Food and Nutrition','Middle School',10,'Technology','DK',23,83,'2025TT','MFOOD||82|1|4|DK|F|23|83||||1|0||');
INSERT INTO "classes" VALUES('MFOOD',NULL,'1','F','Food and Nutrition','Middle School',10,'Technology','DK',22,83,'2025TT','MFOOD||82|1|3|DK|F|22|83||||1|0||');
INSERT INTO "classes" VALUES('MFOOD',NULL,'1','F','Food and Nutrition','Middle School',10,'Technology','DK',22,83,'2025TT','MFOOD||82|1|2|DK|F|22|83||||1|0||');
INSERT INTO "classes" VALUES('MFOOD',NULL,'1','F','Food and Nutrition','Middle School',10,'Technology','DK',22,83,'2025TT','MFOOD||82|1|1|DK|F|22|83||||1|0||');
INSERT INTO "classes" VALUES('MFOOD',NULL,'1','F','Food and Nutrition','Middle School',10,'Technology','DK',24,83,'2025TT','MFOOD||81|1|4|DK|F|24|83||||1|0||');
INSERT INTO "classes" VALUES('MFOOD',NULL,'1','F','Food and Nutrition','Middle School',10,'Technology','DK',24,83,'2025TT','MFOOD||81|1|3|DK|F|24|83||||1|0||');
INSERT INTO "classes" VALUES('MIFOOD',NULL,'0','F','Food and Nutrition','Junior School',8,'Technology','DK',20,20,'2025TT','MIFOOD|JMI||||DK|F|20|20||||2|0||');
INSERT INTO "classes" VALUES('8SFOOD',NULL,'0','F','Year 8 Food Sm','Year 8',8,'Technology','DK',11,11,'2025TT','8SFOOD|8S||||DK|F|11|11||||2|0||');
INSERT INTO "classes" VALUES('VEFOOD',NULL,'0','F','Food and Nutrition','Junior School',7,'Technology','DK',24,24,'2025TT','VEFOOD|JVE||||DK|F|24|24||||2|0||');
INSERT INTO "classes" VALUES('SRFOOD',NULL,'0','F','Food and Nutrition','Junior School',7,'Technology','DK',19,19,'2025TT','SRFOOD|JSR||||DK|F|19|19||||2|0||');
INSERT INTO "classes" VALUES('SDFOOD',NULL,'0','F','Food and Nutrition','Junior School',7,'Technology','DK',19,19,'2025TT','SDFOOD|JSD||||DK|F|19|19||||2|0||');
INSERT INTO "classes" VALUES('7SFOOD',NULL,'0','F','Food and Nutrition','Year 1',1,'Technology','DK',13,13,'2025TT','7SFOOD|7S||||DK|F|13|13||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','F','Life Skills/Personal Development','Year 1',1,'English and Languages','DK',13,13,'2025TT','WHANAU|11WHAU||||DK|F|13|13||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','F','MEET','0',0,'MEET','DK',13,13,'2025TT','MEET|11WHAU||||DK|F|13|13||||2|0||');
INSERT INTO "classes" VALUES('PIFOOD',NULL,'0','F','Food and Nutrition','Junior School',7,'Technology','HM',21,21,'2025TT','PIFOOD|JPI||||HM|F|21|21||||2|0||');
INSERT INTO "classes" VALUES('200HOSP',4,'1','F','Hospitality','NCEA Level 2',12,'Technology','MK',18,18,'2025TT','200HOSP||4|1|0|MK|F|18|18||||1|0||');
INSERT INTO "classes" VALUES('100HOSP',2,'1','F','Hospitality','NCEA Level 1',11,'Technology','MK',20,38,'2025TT','100HOSP||2|1|0|MK|F|20|38||||1|0||');
INSERT INTO "classes" VALUES('MFOOD',NULL,'1','F','Food and Nutrition','Middle School',10,'Technology','MK',23,83,'2025TT','MFOOD||81|1|2|MK|F|23|83||||1|0||');
INSERT INTO "classes" VALUES('MFOOD',NULL,'1','F','Food and Nutrition','Middle School',10,'Technology','MK',22,83,'2025TT','MFOOD||81|1|1|MK|F|22|83||||1|0||');
INSERT INTO "classes" VALUES('300PHED',6,'1','G','Physical Education','NCEA Level 3',13,'Physical Education','BA',10,10,'2025TT','300PHED||6|1|0|BA|G|10|10||||1|0||');
INSERT INTO "classes" VALUES('100PHED',5,'1','G','Physical Education','NCEA Level 1',11,'Physical Education','BA',21,33,'2025TT','100PHED||5|1|0|BA|G|21|33||||1|0||');
INSERT INTO "classes" VALUES('PISPORT',NULL,'0','G','Sport','Year 8',8,'Physical Education','CY',21,21,'2025TT','PISPORT|JPI||||CY|G|21|21||||2|0||');
INSERT INTO "classes" VALUES('200PHED',NULL,'0','G','Physical Education','NCEA Level 2',12,'Physical Education','HM',17,17,'2025TT','200PHED|Year12PE||||HM|G|17|17||||2|0||');
INSERT INTO "classes" VALUES('100PHED',2,'1','G','Physical Education','NCEA Level 1',11,'Physical Education','JM',12,33,'2025TT','100PHED||2|1|0|JM|G|12|33||||1|0||');
INSERT INTO "classes" VALUES('SDPEH',NULL,'0','G','Physical Education','Year 8',8,'Physical Education','MI',19,19,'2025TT','SDPEH|JSD||||MI|G|19|19||||2|0||');
INSERT INTO "classes" VALUES('MIPEH',NULL,'0','G','Physical Education','Year 8',7,'Physical Education','MI',20,20,'2025TT','MIPEH|JMI||||MI|G|20|20||||2|0||');
INSERT INTO "classes" VALUES('VEPEH',0,'0','G','Physical Education','Junior School',7,'Physical Education','MI',2,2,'2025TT','VEPEH|||||MI|G|2|2|22031;22031|||3|0');
INSERT INTO "classes" VALUES('SRPEH',NULL,'0','G','Physical Education','Year 8',7,'Physical Education','PI',19,19,'2025TT','SRPEH|JSR||||PI|G|19|19||||2|0||');
INSERT INTO "classes" VALUES('SDSPORT',NULL,'0','G','Sport','Year 8',8,'Physical Education','RW',19,19,'2025TT','SDSPORT|JSD||||RW|G|19|19||||2|0||');
INSERT INTO "classes" VALUES('9PEH',NULL,'0','G1','Physical Education','Year 9',9,'Physical Education','BP',17,17,'2025TT','9PEH|9H||||BP|G1|17|17||||2|0||');
INSERT INTO "classes" VALUES('9HPEH',0,'0','G1','9HPEH','Year 9',9,'HPEH','BP',1,1,'2025TT','9HPEH|||||BP|G1|1|1|22031|||3|0');
INSERT INTO "classes" VALUES('VESPORT',NULL,'0','G1','Sport','Year 8',8,'Physical Education','CY',24,24,'2025TT','VESPORT|JVE||||CY|G1|24|24||||2|0||');
INSERT INTO "classes" VALUES('PIPEH',NULL,'0','G1','Physical Education','Year 8',7,'Physical Education','JA',21,21,'2025TT','PIPEH|JPI||||JA|G1|21|21||||2|0||');
INSERT INTO "classes" VALUES('MSPORT',NULL,'1','G1','Sport','Middle School',10,'Physical Education','JM',22,45,'2025TT','MSPORT||81|1|4|JM|G1|22|45||||1|0||');
INSERT INTO "classes" VALUES('MSPORT',NULL,'1','G1','Sport','Middle School',10,'Physical Education','JM',21,45,'2025TT','MSPORT||81|1|3|JM|G1|21|45||||1|0||');
INSERT INTO "classes" VALUES('SRSPORT',NULL,'0','G1','Sport','Year 7',7,'Physical Education','RW',19,19,'2025TT','SRSPORT|JSR||||RW|G1|19|19||||2|0||');
INSERT INTO "classes" VALUES('10PEH',NULL,'0','G2','Physical Education','Year 10',10,'Physical Education','BA',23,23,'2025TT','10PEH|10W||||BA|G2|23|23||||2|0||');
INSERT INTO "classes" VALUES('10PEHHE',0,'0','G2','10PEHHE','Year 10',10,'PEHHE','BA',2,2,'2025TT','10PEHHE|||||BA|G2|2|2|23053;22031|||3|0');
INSERT INTO "classes" VALUES('9PEH',NULL,'0','G2','Physical Education','Year 9',9,'Physical Education','BA',20,20,'2025TT','9PEH|9S||||BA|G2|20|20||||2|0||');
INSERT INTO "classes" VALUES('MTRPEH',NULL,'0','G2','Physical Education','Middle School',10,'Physical Education','BP',10,10,'2025TT','MTRPEH|MTR||||BP|G2|10|10||||2|0||');
INSERT INTO "classes" VALUES('10PEH',NULL,'0','G2','Physical Education','Year 10',10,'Physical Education','BP',25,25,'2025TT','10PEH|10H||||BP|G2|25|25||||2|0||');
INSERT INTO "classes" VALUES('JTRPEH',NULL,'0','G2','Physical Education','Junior School',8,'Physical Education','BP',14,14,'2025TT','JTRPEH|JTR||||BP|G2|14|14||||2|0||');
INSERT INTO "classes" VALUES('10PEH',NULL,'0','G2','Physical Education','Year 10',10,'Physical Education','MI',16,16,'2025TT','10PEH|10S||||MI|G2|16|16||||2|0||');
INSERT INTO "classes" VALUES('VEPEH',NULL,'0','G2','Physical Education','Junior School',7,'Physical Education','MI',24,24,'2025TT','VEPEH|JVE||||MI|G2|24|24||||2|0||');
INSERT INTO "classes" VALUES('9PEH',NULL,'0','GCC','Physical Education','Year 9',9,'Physical Education','JA',18,18,'2025TT','9PEH|9W||||JA|GCC|18|18||||2|0||');
INSERT INTO "classes" VALUES('9WPEH',0,'0','GCC','9WPEH','Year 9',9,'WPEH','JA',1,1,'2025TT','9WPEH|||||JA|GCC|1|1|22031|||3|0');
INSERT INTO "classes" VALUES('MSPORT',NULL,'1','GCC','Sport','Middle School',10,'Physical Education','JM',26,45,'2025TT','MSPORT||81|1|2|JM|GCC|26|45||||1|0||');
INSERT INTO "classes" VALUES('MSPORT',NULL,'1','GCC','Sport','Middle School',10,'Physical Education','JM',25,45,'2025TT','MSPORT||81|1|1|JM|GCC|25|45||||1|0||');
INSERT INTO "classes" VALUES('300FURN',5,'1','GR','Hard Materials','NCEA Level 3',13,'Technology','MR',3,3,'2025TT','300FURN||5|1|0|MR|GR|3|3||||1|0||');
INSERT INTO "classes" VALUES('200FURN',6,'1','GR','Hard Materials','NCEA Level 2',12,'Technology','MR',19,19,'2025TT','200FURN||6|1|0|MR|GR|19|19||||1|0||');
INSERT INTO "classes" VALUES('100FURN',5,'1','GR','Furniture','NCEA Level 1',11,'Technology','MR',11,11,'2025TT','100FURN||5|1|0|MR|GR|11|11||||1|0||');
INSERT INTO "classes" VALUES('MDVC',NULL,'1','GR','Design and Visual Communication (DVC)','Middle School',10,'Technology','MR',6,16,'2025TT','MDVC||82|1|4|MR|GR|6|16||||1|0||');
INSERT INTO "classes" VALUES('MDVC',NULL,'1','GR','Design and Visual Communication (DVC)','Middle School',10,'Technology','MR',6,16,'2025TT','MDVC||82|1|3|MR|GR|6|16||||1|0||');
INSERT INTO "classes" VALUES('MDVC',NULL,'1','GR','Design and Visual Communication (DVC)','Middle School',10,'Technology','MR',13,16,'2025TT','MDVC||82|1|2|MR|GR|13|16||||1|0||');
INSERT INTO "classes" VALUES('MDVC',NULL,'1','GR','Design and Visual Communication (DVC)','Middle School',10,'Technology','MR',12,16,'2025TT','MDVC||82|1|1|MR|GR|12|16||||1|0||');
INSERT INTO "classes" VALUES('MWOOD',NULL,'1','GR','Hard Materials','Middle School',10,'Technology','MR',18,32,'2025TT','MWOOD||81|1|4|MR|GR|18|32||||1|0||');
INSERT INTO "classes" VALUES('MWOOD',NULL,'1','GR','Hard Materials','Middle School',10,'Technology','MR',18,32,'2025TT','MWOOD||81|1|3|MR|GR|18|32||||1|0||');
INSERT INTO "classes" VALUES('MWOOD',NULL,'1','GR','Hard Materials','Middle School',10,'Technology','MR',17,32,'2025TT','MWOOD||81|1|2|MR|GR|17|32||||1|0||');
INSERT INTO "classes" VALUES('MWOOD',NULL,'1','GR','Hard Materials','Middle School',10,'Technology','MR',14,32,'2025TT','MWOOD||81|1|1|MR|GR|14|32||||1|0||');
INSERT INTO "classes" VALUES('VEWOOD',NULL,'0','GR','Hard Materials','Junior School',8,'Technology','MR',24,24,'2025TT','VEWOOD|JVE||||MR|GR|24|24||||2|0||');
INSERT INTO "classes" VALUES('SRWOOD',NULL,'0','GR','Woodwork','Junior School',8,'Technology','MR',19,19,'2025TT','SRWOOD|JSR||||MR|GR|19|19||||2|0||');
INSERT INTO "classes" VALUES('8SWOOD',NULL,'0','GR','Hard Materials','Year 8',8,'Technology','MR',11,11,'2025TT','8SWOOD|8S||||MR|GR|11|11||||2|0||');
INSERT INTO "classes" VALUES('PIWOOD',NULL,'0','GR','Hard Materials','Junior School',7,'Technology','MR',21,21,'2025TT','PIWOOD|JPI||||MR|GR|21|21||||2|0||');
INSERT INTO "classes" VALUES('MIWOOD',NULL,'0','GR','Hard Materials','Junior School',7,'Technology','MR',20,20,'2025TT','MIWOOD|JMI||||MR|GR|20|20||||2|0||');
INSERT INTO "classes" VALUES('7SWOOD',NULL,'0','GR','Y7 Wood Technology SM','Year 7',7,'Technology','MR',13,13,'2025TT','7SWOOD|7S||||MR|GR|13|13||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','GR','Life Skills/Personal Development','Year 1',1,'English and Languages','MR',13,13,'2025TT','WHANAU|8WPAPA||||MR|GR|13|13||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','GR','MEET','0',0,'MEET','MR',13,13,'2025TT','MEET|8WPAPA||||MR|GR|13|13||||2|0||');
INSERT INTO "classes" VALUES('10ENGHE',0,'0','GR','10ENGHE','Year 10',10,'ENGHE','TJ',2,2,'2025TT','10ENGHE|||||TJ|GR|2|2|23053;23005|||3|0');
INSERT INTO "classes" VALUES('100DVC',1,'1','GR','Design & Visual Communication','NCEA Level 1',11,'Technology','VP',5,5,'2025TT','100DVC||1|1|0|VP|GR|5|5||||1|1||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','Green','Life Skills/Personal Development','Year 1',1,'English and Languages','LR',7,7,'2025TT','WHANAU|12LR||||LR|GREEN|7|7||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','Green','MEET','0',0,'MEET','LR',7,7,'2025TT','MEET|12LR||||LR|GREEN|7|7||||2|0||');
INSERT INTO "classes" VALUES('GATEWAY',3,'1','GW','Transition/Pre-Employment','NCEA Level 2',12,'GATEWAY','KV',2,22,'2025TT','Gateway||3|1|0|KV|GW|2|22||||1|0||');
INSERT INTO "classes" VALUES('GATEWAY',2,'1','GW','Transition/Pre-Employment','NCEA Level 2',12,'GATEWAY','KV',20,22,'2025TT','Gateway||2|1|0|KV|GW|20|22||||1|0||');
INSERT INTO "classes" VALUES('11STUDYLTR',NULL,'0','GW','11STUDYLTR','Year 11',11,'STUDYLTR','KV',18,18,'2025TT','11STUDYLTR|Year11LITR||||KV|GW|18|18||||2|0||');
INSERT INTO "classes" VALUES('11STUDYKv',7,'1','GW','Specify Subject Name','NCEA Level 1',11,'Gateway','KV',20,20,'2025TT','11STUDYKv||7|1|0|KV|GW|20|20||||1|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','GW','Life Skills/Personal Development','Year 1',1,'English and Languages','KV',13,13,'2025TT','WHANAU|9WAHI||||KV|GW|13|13||||2|0||');
INSERT INTO "classes" VALUES('GWAdmin',NULL,'0','GW','GWAdmin','0',0,'GWAdmin','KV',0,0,'2025TT','GWAdmin|KV||||KV|GW|0|0||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','GW','MEET','0',0,'MEET','KV',13,13,'2025TT','MEET|9WAHI||||KV|GW|13|13||||2|0||');
INSERT INTO "classes" VALUES('100ENG',5,'1','GW','English','NCEA Level 1',11,'English and Languages','PQ',18,40,'2025TT','100ENG||5|1|0|PQ|GW|18|40||||1|0||');
INSERT INTO "classes" VALUES('12STUDYBt',7,'1','GW','12STUDYBt','Year 12',12,'STUDYBt','0',0,0,'2025TT','12STUDYBt||7|1|0||GW|0|0||||1|0||');
INSERT INTO "classes" VALUES('STUDY',0,'0','Hall','STUDY','0',0,'STUDY','SH',3,3,'2025TT','STUDY|||||SH|Hall|3|3|24070;20091;20003|||3|0');
INSERT INTO "classes" VALUES('NL3HIS',4,'1','LIB','NETNZ L3 History','NCEA Level 3',13,'Social Science','JT',1,1,'2025TT','NL3HIS||4|1|0|JT|LIB|1|1||||1|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','LIB','Life Skills/Personal Development','Year 1',1,'English and Languages','MK',12,12,'2025TT','WHANAU|12WPAPA||||MK|LIB|12|12||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','LIB','MEET','0',0,'MEET','MK',12,12,'2025TT','MEET|12WPAPA||||MK|LIB|12|12||||2|0||');
INSERT INTO "classes" VALUES('100MUSC',6,'1','MR','Music','NCEA Level 1',11,'Arts','JA',2,2,'2025TT','100MUSC||6|1|0|JA|MR|2|2||||1|0||');
INSERT INTO "classes" VALUES('MMUSIC',NULL,'1','MR','Music','Middle School',10,'Arts','JA',21,23,'2025TT','MMUSIC||82|1|4|JA|MR|21|23||||1|0||');
INSERT INTO "classes" VALUES('MMUSIC',NULL,'1','MR','Music','Middle School',10,'Arts','JA',22,23,'2025TT','MMUSIC||82|1|3|JA|MR|22|23||||1|0||');
INSERT INTO "classes" VALUES('VEMUSIC',NULL,'0','MR','Music','Junior School',7,'Arts','JA',24,24,'2025TT','VEMUSIC|JVE||||JA|MR|24|24||||2|0||');
INSERT INTO "classes" VALUES('SRDRAMA',NULL,'0','MR','Drama','Year 7',7,'Arts','JA',19,19,'2025TT','SRDRAMA|JSR||||JA|MR|19|19||||2|0||');
INSERT INTO "classes" VALUES('PIMUSIC',NULL,'0','MR','Music','Junior School',7,'Arts','JA',21,21,'2025TT','PIMUSIC|JPI||||JA|MR|21|21||||2|0||');
INSERT INTO "classes" VALUES('MIMUSIC',NULL,'0','MR','Music','Junior School',7,'Arts','JA',20,20,'2025TT','MIMUSIC|JMI||||JA|MR|20|20||||2|0||');
INSERT INTO "classes" VALUES('200APMAT',1,'1','MR','Mathematics - Core','NCEA Level 2',12,'Mathematics','JD',16,16,'2025TT','200APMAT||1|1|0|JD|MR|16|16||||1|0||');
INSERT INTO "classes" VALUES('MJAPANESE',NULL,'1','MR','Japanese','Middle School',10,'English and Languages','NR',14,14,'2025TT','MJAPANESE||81|1|1|NR|MR|14|14||||1|0||');
INSERT INTO "classes" VALUES('200APENG',5,'1','MR','200 Applied English','NCEA Level 2',12,'English and Languages','WA',11,11,'2025TT','200APENG||5|1|0|WA|MR|11|11||||1|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','MR','Life Skills/Personal Development','Year 1',1,'English and Languages','WA',13,13,'2025TT','WHANAU|11WAHI||||WA|MR|13|13||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','MR','MEET','0',0,'MEET','WA',13,13,'2025TT','MEET|11WAHI||||WA|MR|13|13||||2|0||');
INSERT INTO "classes" VALUES('MOUED',NULL,'1','OE','Outdoor Education','Middle School',10,'Physical Education','HM',19,37,'2025TT','MOUED||82|1|4|HM|OE|19|37||||1|1||');
INSERT INTO "classes" VALUES('MOUED',NULL,'1','OE','Outdoor Education','Middle School',10,'Physical Education','HM',18,37,'2025TT','MOUED||82|1|3|HM|OE|18|37||||1|1||');
INSERT INTO "classes" VALUES('MOUED',NULL,'1','OE','Outdoor Education','Middle School',10,'Physical Education','HM',19,37,'2025TT','MOUED||82|1|2|HM|OE|19|37||||1|1||');
INSERT INTO "classes" VALUES('MOUED',NULL,'1','OE','Outdoor Education','Middle School',10,'Physical Education','HM',19,37,'2025TT','MOUED||82|1|1|HM|OE|19|37||||1|1||');
INSERT INTO "classes" VALUES('300OUEDA',3,'1','OE','Outdoor Education (Adventure)','NCEA Level 3',13,'Physical Education','TB',5,5,'2025TT','300OUEDA||3|1|0|TB|OE|5|5||||1|0||');
INSERT INTO "classes" VALUES('200OUEDR',5,'1','OE','Outdoor Education (Recreation)','NCEA Level 2',12,'Physical Education','TB',9,9,'2025TT','200OUEDR||5|1|0|TB|OE|9|9||||1|0||');
INSERT INTO "classes" VALUES('200OUEDA',1,'1','OE','Outdoor Education (Adventure)','NCEA Level 2',12,'Physical Education','TB',11,11,'2025TT','200OUEDA||1|1|0|TB|OE|11|11||||1|0||');
INSERT INTO "classes" VALUES('100OUEDA',4,'1','OE','Outdoor Education (Adventure)','NCEA Level 1',11,'Physical Education','TB',9,9,'2025TT','100OUEDA||4|1|0|TB|OE|9|9||||1|0||');
INSERT INTO "classes" VALUES('MOUED',NULL,'1','OE','Outdoor Education','Middle School',10,'Physical Education','TB',19,37,'2025TT','MOUED||82|1|4|TB|OE|19|37||||1|0||');
INSERT INTO "classes" VALUES('MOUED',NULL,'1','OE','Outdoor Education','Middle School',10,'Physical Education','TB',18,37,'2025TT','MOUED||82|1|3|TB|OE|18|37||||1|0||');
INSERT INTO "classes" VALUES('MOUED',NULL,'1','OE','Outdoor Education','Middle School',10,'Physical Education','TB',19,37,'2025TT','MOUED||82|1|2|TB|OE|19|37||||1|0||');
INSERT INTO "classes" VALUES('MOUED',NULL,'1','OE','Outdoor Education','Middle School',10,'Physical Education','TB',19,37,'2025TT','MOUED||82|1|1|TB|OE|19|37||||1|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','OE','Life Skills/Personal Development','Year 1',1,'English and Languages','TB',19,19,'2025TT','WHANAU|10WAHI||||TB|OE|19|19||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','OE','MEET','0',0,'MEET','TB',19,19,'2025TT','MEET|10WAHI||||TB|OE|19|19||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','PAV','Life Skills/Personal Development','Year 1',1,'English and Languages','BT',13,13,'2025TT','WHANAU|7WWAI||||BT|PAV|13|13||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','PAV','MEET','0',0,'MEET','BT',13,13,'2025TT','MEET|7WWAI||||BT|PAV|13|13||||2|0||');
INSERT INTO "classes" VALUES('RDA',0,'0','RDA','RDA','0',0,'RDA','CV',6,6,'2025TT','RDA|||||CV|RDA|6|6|24025;25030;24029;23096;19066;22019|||3|0');
INSERT INTO "classes" VALUES('RDAVolunte',0,'0','RDA','RDAVolunte','0',0,'RDAVolunte','GH',1,1,'2025TT','RDAVolunte|||||GH|RDA|1|1|24119|||3|0');
INSERT INTO "classes" VALUES('MITEXT',NULL,'0','TT','Textiles Technology','Junior School',8,'Technology','DK',20,20,'2025TT','MITEXT|JMI||||DK|TT|20|20||||2|0||');
INSERT INTO "classes" VALUES('7STEXT',NULL,'0','TT','Textiles/Clothing','Year 7',7,'Technology','HM',13,13,'2025TT','7STEXT|7S||||HM|TT|13|13||||2|0||');
INSERT INTO "classes" VALUES('SDDRAMA',NULL,'0','TT','Drama','Junior School',8,'Arts','JA',19,19,'2025TT','SDDRAMA|JSD||||JA|TT|19|19||||2|0||');
INSERT INTO "classes" VALUES('TANURS3',9,'1','TT','Nursery Year 3','NCEA Level 3',13,'Trades Academy','RS',1,1,'2025TT','TANurs3||9|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('NL3DRA',8,'1','TT','L3Drama NeTNZ','NCEA Level 3',13,'Arts','RS',3,3,'2025TT','NL3DRA||8|1|0|RS|TT|3|3||||1|0||');
INSERT INTO "classes" VALUES('NL3HIS',8,'1','TT','NETNZ L3 History','NCEA Level 3',13,'Social Science','RS',1,1,'2025TT','NL3HIS||8|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('NL3SPA',8,'1','TT','L3 Spanish','NCEA Level 3',13,'English and Languages','RS',1,1,'2025TT','NL3SPA||8|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('TACON2',8,'1','TT','Building and Construction','NCEA Level 3',13,'Trades Academy','RS',0,0,'2025TT','TACON2||8|1|0|RS|TT|0|0||||1|0||');
INSERT INTO "classes" VALUES('TACOOK2',8,'1','TT','Cookery Year 2','NCEA Level 3',13,'Trades Academy','RS',1,1,'2025TT','TACOOK2||8|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('TAHANDB2',8,'1','TT','Hair and Beauty Year 2','NCEA Level 3',13,'Trades Academy','RS',1,1,'2025TT','TAHANDB2||8|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('TKL3GER',8,'1','TT','German L3 Tk','NCEA Level 3',13,'English and Languages','RS',2,2,'2025TT','TKL3GER||8|1|0|RS|TT|2|2||||1|0||');
INSERT INTO "classes" VALUES('TKL3MAO',8,'1','TT','Te Reo Maori','NCEA Level 3',13,'Te Reo Māori','RS',3,6,'2025TT','TKL3MAO||8|1|0|RS|TT|3|6||||1|0||');
INSERT INTO "classes" VALUES('NL2DVC',9,'1','TT','Level 2 NETNZ Design & Visual Communication','NCEA Level 2',12,'Technology','RS',1,1,'2025TT','NL2DVC||9|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('NL2MED',9,'1','TT','Media Studies','NCEA Level 2',12,'Social Science','RS',1,1,'2025TT','NL2MED||9|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('TACOOK1',9,'1','TT','Cookery Year 1','NCEA Level 2',12,'Trades Academy','RS',2,2,'2025TT','TACOOK1||9|1|0|RS|TT|2|2||||1|0||');
INSERT INTO "classes" VALUES('MANTAP2',8,'1','TT','Manaaki Tapoi Level 2','NCEA Level 2',12,'Te Reo Māori','RS',3,3,'2025TT','MANTAP2||8|1|0|RS|TT|3|3||||1|0||');
INSERT INTO "classes" VALUES('NL2DRA',8,'1','TT','Level 2 NETNZ Drama','NCEA Level 2',12,'Arts','RS',3,3,'2025TT','NL2DRA||8|1|0|RS|TT|3|3||||1|0||');
INSERT INTO "classes" VALUES('NL2PYS',8,'1','TT','L2 Psychology','NCEA Level 2',12,'Social Science','RS',1,1,'2025TT','NL2PYS||8|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('TAAUTO1',8,'1','TT','Automotive Year 1','NCEA Level 2',12,'Trades Academy','RS',2,2,'2025TT','TAAUTO1||8|1|0|RS|TT|2|2||||1|0||');
INSERT INTO "classes" VALUES('TACAF',8,'1','TT','Cafe Skills','NCEA Level 2',12,'Trades Academy','RS',1,1,'2025TT','TACAF||8|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('TACOOK1',8,'1','TT','Cookery Year 1','NCEA Level 2',12,'Trades Academy','RS',0,2,'2025TT','TACOOK1||8|1|0|RS|TT|0|2||||1|0||');
INSERT INTO "classes" VALUES('TAHANDB1',8,'1','TT','Hair and Beauty Year 1','NCEA Level 2',12,'Trades Academy','RS',4,4,'2025TT','TAHANDB1||8|1|0|RS|TT|4|4||||1|0||');
INSERT INTO "classes" VALUES('TAMECAD1',8,'1','TT','Engineering and CAD Design Year 1','NCEA Level 2',12,'Trades Academy','RS',1,1,'2025TT','TAMECAD1||8|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('TAMECAD2',8,'1','TT','Engineering and CAD Design Year 2','NCEA Level 2',12,'Trades Academy','RS',4,4,'2025TT','TAMECAD2||8|1|0|RS|TT|4|4||||1|0||');
INSERT INTO "classes" VALUES('TAPEST',8,'1','TT','Trades Pest Control Level 2','NCEA Level 2',12,'Trades Academy','RS',1,1,'2025TT','TAPEST||8|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('TK2DTE',8,'1','TT','L2 Digital Technology','NCEA Level 2',12,'Technology','RS',1,1,'2025TT','TK2DTE||8|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('TK2PHY',8,'1','TT','Level 2 Physics (Te Kura)','NCEA Level 2',12,'Science','RS',0,0,'2025TT','TK2PHY||8|1|0|RS|TT|0|0||||1|0||');
INSERT INTO "classes" VALUES('TKL2MAO',8,'1','TT','Te Reo Maori','NCEA Level 2',12,'Te Reo Māori','RS',0,0,'2025TT','TKL2MAO||8|1|0|RS|TT|0|0||||1|0||');
INSERT INTO "classes" VALUES('EESL1',9,'1','TT','Explore Emergency Services Level 1 Whenua Iti','NCEA Level 1',11,'Trades Academy','RS',1,1,'2025TT','EESL1||9|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('NL1MAO',9,'1','TT','L1 Te Reo Māori','NCEA Level 1',11,'Te Reo Māori','RS',4,4,'2025TT','NL1MAO||9|1|0|RS|TT|4|4||||1|0||');
INSERT INTO "classes" VALUES('NL1COM',8,'1','TT','Commerce','NCEA Level 1',11,'Social Science','RS',1,1,'2025TT','NL1COM||8|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('MTEXT',NULL,'1','TT','Textiles','Middle School',10,'Technology','RS',23,33,'2025TT','MTEXT||82|1|4|RS|TT|23|33||||1|0||');
INSERT INTO "classes" VALUES('MTEXT',NULL,'1','TT','Textiles','Middle School',10,'Technology','RS',23,33,'2025TT','MTEXT||82|1|3|RS|TT|23|33||||1|0||');
INSERT INTO "classes" VALUES('MTEXT',NULL,'1','TT','Textiles','Middle School',10,'Technology','RS',21,33,'2025TT','MTEXT||82|1|2|RS|TT|21|33||||1|0||');
INSERT INTO "classes" VALUES('MTEXT',NULL,'1','TT','Textiles','Middle School',10,'Technology','RS',21,33,'2025TT','MTEXT||82|1|1|RS|TT|21|33||||1|0||');
INSERT INTO "classes" VALUES('8STEXT',NULL,'0','TT','St Mary''s Textiles Technology','Year 8',8,'Technology','RS',11,11,'2025TT','8STEXT|8S||||RS|TT|11|11||||2|0||');
INSERT INTO "classes" VALUES('VETEXT',NULL,'0','TT','Textiles Technology','Junior School',7,'Technology','RS',24,24,'2025TT','VETEXT|JVE||||RS|TT|24|24||||2|0||');
INSERT INTO "classes" VALUES('SRTEXT',NULL,'0','TT','Textiles Technology','Junior School',7,'Technology','RS',19,19,'2025TT','SRTEXT|JSR||||RS|TT|19|19||||2|0||');
INSERT INTO "classes" VALUES('SDTEXT',NULL,'0','TT','Textiles Technology','Junior School',7,'Technology','RS',19,19,'2025TT','SDTEXT|JSD||||RS|TT|19|19||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','TT','Life Skills/Personal Development','Year 1',1,'English and Languages','RS',9,9,'2025TT','WHANAU|13RS||||RS|TT|9|9||||2|0||');
INSERT INTO "classes" VALUES('TKBGER',8,'1','TT','Specify Subject Name','Year 1',1,'Learning Support','RS',1,1,'2025TT','TKBGER||8|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','TT','MEET','0',0,'MEET','RS',9,9,'2025TT','MEET|13RS||||RS|TT|9|9||||2|0||');
INSERT INTO "classes" VALUES('LIFESKILLS',8,'1','TT','LIFESKILLS','0',0,'LIFESKILLS','RS',1,1,'2025TT','LIFESKILLS||8|1|0|RS|TT|1|1||||1|0||');
INSERT INTO "classes" VALUES('TKL3GER',6,'1','TT1','German L3 Tk','NCEA Level 3',13,'English and Languages','JT',2,2,'2025TT','TKL3GER||6|1|0|JT|TT1|2|2||||1|0|5|200021604');
INSERT INTO "classes" VALUES('NETNZ',6,'1','TT1','NETNZ','NCEA Level 1',11,'Administration','JT',0,1,'2025TT','NETNZ||6|1|0|JT|TT1|0|1||||1|0|5|200021604');
INSERT INTO "classes" VALUES('NETNZTEREO',6,'1','TT1','Level 1 Te Reo Maori','NCEA Level 1',11,'Te Reo Māori','JT',2,3,'2025TT','NETNZTEREO||6|1|0|JT|TT1|2|3||||1|0|5|200021604');
INSERT INTO "classes" VALUES('NETNZ',5,'1','TT1','NETNZ','NCEA Level 1',11,'Administration','JT',0,1,'2025TT','NETNZ||5|1|0|JT|TT1|0|1||||1|0|3|200021635');
INSERT INTO "classes" VALUES('NETNZCOM',5,'1','TT1','Level 1 NETNZ Commerce','NCEA Level 1',11,'Social Science','JT',1,1,'2025TT','NETNZCOM||5|1|0|JT|TT1|1|1||||1|0|4|200021604');
INSERT INTO "classes" VALUES('NETNZTEREO',5,'1','TT1','Level 1 Te Reo Maori','NCEA Level 1',11,'Te Reo Māori','JT',1,3,'2025TT','NETNZTEREO||5|1|0|JT|TT1|1|3||||1|0|4|200021604');
INSERT INTO "classes" VALUES('NETNZ',4,'1','TT1','NETNZ','NCEA Level 1',11,'Administration','JT',0,1,'2025TT','NETNZ||4|1|0|JT|TT1|0|1||||1|0||');
INSERT INTO "classes" VALUES('NETNZ',2,'1','TT1','NETNZ','NCEA Level 1',11,'Administration','JT',0,1,'2025TT','NETNZ||2|1|0|JT|TT1|0|1||||1|0||');
INSERT INTO "classes" VALUES('NETNZ',1,'1','TT1','NETNZ','NCEA Level 1',11,'Administration','JT',0,1,'2025TT','NETNZ||1|1|0|JT|TT1|0|1||||1|0||');
INSERT INTO "classes" VALUES('NETNZDRAMA',5,'1','TT1','Drama','Year 1',1,'Arts','JT',2,6,'2025TT','NETNZDRAMA||5|1|0|JT|TT1|2|6||||1|0|4|200021604');
INSERT INTO "classes" VALUES('NETMEDST',6,'1','TT1','NETMEDST','0',0,'NETMEDST','JT',0,0,'2025TT','NETMEDST||6|1|0|JT|TT1|0|0||||1|0|3|200021657');
INSERT INTO "classes" VALUES('NETNZGER',6,'1','TT1','NETNZGER','0',0,'NETNZGER','JT',0,0,'2025TT','NETNZGER||6|1|0|JT|TT1|0|0||||1|0|4|200021635');
INSERT INTO "classes" VALUES('NETNZMEDS',6,'1','TT1','NETNZMEDS','0',0,'NETNZMEDS','JT',1,1,'2025TT','NETNZMEDS||6|1|0|JT|TT1|1|1||||1|0|4|200021635');
INSERT INTO "classes" VALUES('NETNZSPA',6,'1','TT1','NETNZSPA','0',0,'NETNZSPA','JT',1,1,'2025TT','NETNZSPA||6|1|0|JT|TT1|1|1||||1|0|5|200021604');
INSERT INTO "classes" VALUES('NETNZPSYC',4,'1','TT1','NETNZPSYC','0',0,'NETNZPSYC','JT',1,1,'2025TT','NETNZPSYC||4|1|0|JT|TT1|1|1||||1|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','TUHUA','Life Skills/Personal Development','Year 1',1,'English and Languages','NR',10,10,'2025TT','WHANAU|13NR||||NR|TUHUA|10|10||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','TUHUA','MEET','0',0,'MEET','NR',10,10,'2025TT','MEET|13NR||||NR|TUHUA|10|10||||2|0||');
INSERT INTO "classes" VALUES('Driver',9,'1','TWA','Driver''s Licence','NCEA Level 2',12,'Administration','KV',0,0,'2025TT','Driver||9|1|0|KV|TWA|0|0||||1|0||');
INSERT INTO "classes" VALUES('Licence',9,'1','TWA','English','Year 1',1,'Gateway','KV',0,0,'2025TT','Licence||9|1|0|KV|TWA|0|0||Driver||4|0||');
INSERT INTO "classes" VALUES('s',9,'1','TWA','Specify Subject Name','Year 1',1,'Gateway','KV',0,0,'2025TT','s||9|1|0|KV|TWA|0|0||Driver||4|0||');
INSERT INTO "classes" VALUES('TWA',0,'0','TWA','Special Needs Programme','Year 1',1,'Learning Support','SA',1,1,'2025TT','TWA|||||SA|TWA|1|1|22031|||3|0');
INSERT INTO "classes" VALUES('VEVART',NULL,'0','VA','Art','Junior School',8,'Arts','BR',24,24,'2025TT','VEVART|JVE||||BR|VA|24|24||||2|0||');
INSERT INTO "classes" VALUES('MIVART',NULL,'0','VA','Art','Junior School',8,'Arts','BR',20,20,'2025TT','MIVART|JMI||||BR|VA|20|20||||2|0||');
INSERT INTO "classes" VALUES('SRVART',NULL,'0','VA','Art','Year 7',7,'Arts','BR',19,19,'2025TT','SRVART|JSR||||BR|VA|19|19||||2|0||');
INSERT INTO "classes" VALUES('SDART',NULL,'0','VA','Art','Junior School',7,'Arts','BR',19,19,'2025TT','SDART|JSD||||BR|VA|19|19||||2|0||');
INSERT INTO "classes" VALUES('PIVART',NULL,'0','VA','Art','Junior School',7,'Arts','BR',21,21,'2025TT','PIVART|JPI||||BR|VA|21|21||||2|0||');
INSERT INTO "classes" VALUES('300Paint',6,'1','VA','L3 Painting','NCEA Level 3',13,'Arts','Mn',2,2,'2025TT','300Paint||6|1|0|Mn|VA|2|2||||1|0|2|200021658');
INSERT INTO "classes" VALUES('300Print',6,'1','VA','L3 Printmaking','NCEA Level 3',13,'Arts','Mn',0,3,'2025TT','300Print||6|1|0|Mn|VA|0|3||||1|0|2|200021658');
INSERT INTO "classes" VALUES('300SCULPT',6,'1','VA','L3 Sculpture','NCEA Level 3',13,'Arts','Mn',1,1,'2025TT','300SCULPT||6|1|0|Mn|VA|1|1||||1|0||');
INSERT INTO "classes" VALUES('300Paint',2,'1','VA','L3 Painting','NCEA Level 3',13,'Arts','Mn',0,2,'2025TT','300Paint||2|1|0|Mn|VA|0|2||||1|0|3|200021653');
INSERT INTO "classes" VALUES('300Print',2,'1','VA','L3 Printmaking','NCEA Level 3',13,'Arts','Mn',3,3,'2025TT','300Print||2|1|0|Mn|VA|3|3||||1|0|3|200021653');
INSERT INTO "classes" VALUES('300SCULPT',2,'1','VA','L3 Sculpture','NCEA Level 3',13,'Arts','Mn',1,1,'2025TT','300SCULPT||2|1|0|Mn|VA|1|1||||1|0||');
INSERT INTO "classes" VALUES('200DESIGN',6,'1','VA','L2 Design','NCEA Level 2',12,'Arts','Mn',1,1,'2025TT','200DESIGN||6|1|0|Mn|VA|1|1||||1|0||');
INSERT INTO "classes" VALUES('200Paint',6,'1','VA','L2 Painting','NCEA Level 2',12,'Arts','Mn',8,11,'2025TT','200Paint||6|1|0|Mn|VA|8|11||||1|0|9|200021637');
INSERT INTO "classes" VALUES('200Photo',6,'1','VA','L2 Photography','NCEA Level 2',12,'Arts','Mn',0,5,'2025TT','200Photo||6|1|0|Mn|VA|0|5||||1|0|9|200021637');
INSERT INTO "classes" VALUES('200Print',6,'1','VA','L2 Printmaking','NCEA Level 2',12,'Arts','Mn',1,1,'2025TT','200Print||6|1|0|Mn|VA|1|1||||1|0|9|200021637');
INSERT INTO "classes" VALUES('200Sculpt',6,'1','VA','L2 Sculpture','NCEA Level 2',12,'Arts','Mn',0,3,'2025TT','200Sculpt||6|1|0|Mn|VA|0|3||||1|0|9|200021637');
INSERT INTO "classes" VALUES('200Paint',2,'1','VA','L2 Painting','NCEA Level 2',12,'Arts','Mn',3,11,'2025TT','200Paint||2|1|0|Mn|VA|3|11||||1|0|11|200021632');
INSERT INTO "classes" VALUES('200Photo',2,'1','VA','L2 Photography','NCEA Level 2',12,'Arts','Mn',5,5,'2025TT','200Photo||2|1|0|Mn|VA|5|5||||1|0|11|200021632');
INSERT INTO "classes" VALUES('200Print',2,'1','VA','L2 Printmaking','NCEA Level 2',12,'Arts','Mn',0,1,'2025TT','200Print||2|1|0|Mn|VA|0|1||||1|0|11|200021632');
INSERT INTO "classes" VALUES('200Sculpt',2,'1','VA','L2 Sculpture','NCEA Level 2',12,'Arts','Mn',3,3,'2025TT','200Sculpt||2|1|0|Mn|VA|3|3||||1|0|11|200021632');
INSERT INTO "classes" VALUES('100VART',6,'1','VA','Visual Art','NCEA Level 1',11,'Arts','MN',5,10,'2025TT','100VART||6|1|0|Mn|VA|5|10||||1|0||');
INSERT INTO "classes" VALUES('100VART',2,'1','VA','Visual Art','NCEA Level 1',11,'Arts','MN',5,10,'2025TT','100VART||2|1|0|Mn|VA|5|10||||1|0||');
INSERT INTO "classes" VALUES('MVART',NULL,'1','VA','Art','Middle School',10,'Arts','Mn',20,38,'2025TT','MVART||81|1|4|Mn|VA|20|38||||1|0||');
INSERT INTO "classes" VALUES('MVART',NULL,'1','VA','Art','Middle School',10,'Arts','Mn',21,38,'2025TT','MVART||81|1|3|Mn|VA|21|38||||1|0||');
INSERT INTO "classes" VALUES('MVART',NULL,'1','VA','Art','Middle School',10,'Arts','Mn',20,38,'2025TT','MVART||81|1|2|Mn|VA|20|38||||1|0||');
INSERT INTO "classes" VALUES('MVART',NULL,'1','VA','Art','Middle School',10,'Arts','Mn',21,38,'2025TT','MVART||81|1|1|Mn|VA|21|38||||1|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','VA','Life Skills/Personal Development','Year 1',1,'English and Languages','Mn',13,13,'2025TT','WHANAU|12WAHI||||Mn|VA|13|13||||2|0||');
INSERT INTO "classes" VALUES('NetNZAH',NULL,'0','VA','NetNZAH','0',0,'NetNZAH','Mn',0,0,'2025TT','NetNZAH|Mn||||Mn|VA|0|0||||2|0||');
INSERT INTO "classes" VALUES('NETNZClass',NULL,'0','VA','NETNZClass','0',0,'NETNZClass','Mn',0,0,'2025TT','NETNZClass|Mn||||Mn|VA|0|0||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','VA','MEET','0',0,'MEET','Mn',13,13,'2025TT','MEET|12WAHI||||Mn|VA|13|13||||2|0||');
INSERT INTO "classes" VALUES('WHANAU',NULL,'0','WHARE','Life Skills/Personal Development','Year 1',1,'English and Languages','WE',38,38,'2025TT','WHANAU|WTEREO||||WE|WHARE|38|38||||2|0||');
INSERT INTO "classes" VALUES('MEET',NULL,'0','WHARE','MEET','0',0,'MEET','WE',38,38,'2025TT','MEET|WTEREO||||WE|WHARE|38|38||||2|0||');
INSERT INTO "classes" VALUES('300TEAO',4,'1','WHARE','Te Ao Māori','NCEA Level 3',13,'Te Reo Māori','WW',6,6,'2025TT','300TEAO||4|1|0|WW|WHARE|6|6||||1|1||');
INSERT INTO "classes" VALUES('TKL3MAO',3,'1','WHARE','Te Reo Maori','NCEA Level 3',13,'Te Reo Māori','WW',6,6,'2025TT','TKL3MAO||3|1|0|WW|WHARE|6|6||||1|0||');
INSERT INTO "classes" VALUES('200TEAO',4,'1','WHARE','Te Ao Māori','NCEA Level 2',12,'Te Reo Māori','WW',0,0,'2025TT','200TEAO||4|1|0|WW|WHARE|0|0||||1|1||');
INSERT INTO "classes" VALUES('TKL2MAO',3,'1','WHARE','Te Reo Maori','NCEA Level 2',12,'Te Reo Māori','WW',0,0,'2025TT','TKL2MAO||3|1|0|WW|WHARE|0|0||||1|0||');
INSERT INTO "classes" VALUES('100TEAO',4,'1','WHARE','Te Ao Māori','NCEA Level 1',11,'Te Reo Māori','WW',4,4,'2025TT','100TEAO||4|1|0|WW|WHARE|4|4||||1|1||');
INSERT INTO "classes" VALUES('300TREO',3,'1','WHARE','Te Reo Maori','NCEA Level 3',13,'Te Reo Māori','0',0,0,'2025TT','300TREO||3|1|0||WHARE|0|0||||1|0||');
INSERT INTO "classes" VALUES('200TREO',3,'1','WHARE','Te Reo Maori','NCEA Level 2',12,'Te Reo Māori','0',0,0,'2025TT','200TREO||3|1|0||WHARE|0|0||||1|0||');
INSERT INTO "classes" VALUES('100TREO',3,'1','WHARE','Te Reo Maori','NCEA Level 1',11,'Te Reo Māori','0',0,0,'2025TT','100TREO||3|1|0||WHARE|0|0||||1|0||');
INSERT INTO "classes" VALUES('MTEREO',NULL,'1','WHARE1','Te Reo Maori','Middle School',10,'Te Reo Māori','BP',8,18,'2025TT','MTEREO||82|1|4|BP|WHARE1|8|18||||1|0||');
INSERT INTO "classes" VALUES('MTEREO',NULL,'1','WHARE1','Te Reo Maori','Middle School',10,'Te Reo Māori','BP',8,18,'2025TT','MTEREO||82|1|3|BP|WHARE1|8|18||||1|0||');
INSERT INTO "classes" VALUES('MTEREO',NULL,'1','WHARE1','Te Reo Maori','Middle School',10,'Te Reo Māori','BP',13,18,'2025TT','MTEREO||82|1|2|BP|WHARE1|13|18||||1|0||');
INSERT INTO "classes" VALUES('MTEREO',NULL,'1','WHARE1','Te Reo Maori','Middle School',10,'Te Reo Māori','BP',13,18,'2025TT','MTEREO||82|1|1|BP|WHARE1|13|18||||1|0||');
INSERT INTO "classes" VALUES('MTRMATH',NULL,'0','WHARE1','Mathematics','Middle School',10,'Mathematics','SD',10,10,'2025TT','MTRMATH|MTR||||SD|WHARE1|10|10||||2|0||');
INSERT INTO "classes" VALUES('MTRENG',NULL,'0','WHARE1','English','Middle School',10,'English and Languages','WA',10,10,'2025TT','MTRENG|MTR||||WA|WHARE1|10|10||||2|0||');
INSERT INTO "classes" VALUES('MAKORANGA',NULL,'0','WHARE1','MAkoranga','Year 9',9,'Te Reo Māori','WE',10,10,'2025TT','MAKORANGA|MTR||||WE|WHARE1|10|10||||2|0||');
INSERT INTO "classes" VALUES('MTREO',NULL,'0','WHARE1','JMTe reo Maori','Year 9',9,'Te Reo Māori','WE',10,10,'2025TT','MTREO|MTR||||WE|WHARE1|10|10||||2|0||');
INSERT INTO "classes" VALUES('MPANGARAU',NULL,'0','WHARE1','MPANGARAU','0',0,'MPANGARAU','WE',10,10,'2025TT','MPANGARAU|MTR||||WE|WHARE1|10|10||||2|0||');
INSERT INTO "classes" VALUES('MTRPAKEHA',NULL,'0','WHARE1','MTRPAKEHA','0',0,'MTRPAKEHA','WE',10,10,'2025TT','MTRPAKEHA|MTR||||WE|WHARE1|10|10||||2|0||');
INSERT INTO "classes" VALUES('JTRENG',NULL,'0','WHARE2','English','Junior School',8,'English and Languages','WA',14,14,'2025TT','JTRENG|JTR||||WA|WHARE2|14|14||||2|0||');
INSERT INTO "classes" VALUES('JMAHITOI',NULL,'0','WHARE2','Mahi Toi','Year 8',8,'Te Reo Māori','WE',14,14,'2025TT','JMAHITOI|JTR||||WE|WHARE2|14|14||||2|0||');
INSERT INTO "classes" VALUES('JPANGARAU',NULL,'0','WHARE2','Junior Pangarau','Year 8',8,'Te Reo Māori','WE',14,14,'2025TT','JPANGARAU|JTR||||WE|WHARE2|14|14||||2|0||');
INSERT INTO "classes" VALUES('JAKORANGA',NULL,'0','WHARE2','JAkoranga','Year 7',7,'Te Reo Māori','WE',14,14,'2025TT','JAKORANGA|JTR||||WE|WHARE2|14|14||||2|0||');
INSERT INTO "classes" VALUES('JTREO',NULL,'0','WHARE2','JTe reo Maori','Year 7',7,'Te Reo Māori','WE',14,14,'2025TT','JTREO|JTR||||WE|WHARE2|14|14||||2|0||');
INSERT INTO "classes" VALUES('JTRPAKEHA',NULL,'0','WHARE2','JTRPAKEHA','0',0,'JTRPAKEHA','WE',14,14,'2025TT','JTRPAKEHA|JTR||||WE|WHARE2|14|14||||2|0||');
INSERT INTO "classes" VALUES('JTRMATH',NULL,'0','WHARE3','Mathematics','Junior School',8,'Mathematics','SD',14,14,'2025TT','JTRMATH|JTR||||SD|WHARE3|14|14||||2|0||');
INSERT INTO "classes" VALUES('Timetable',0,'0','0','Timetable','0',0,'Timetable','JD',0,0,'2025TT','Timetable|JD||||JD||0|0||||2|0||');
INSERT INTO "classes" VALUES('Dogtrain',0,'0','0','Dogtrain','0',0,'Dogtrain','JT',41,41,'2025TT','Dogtrain|||||JT||41|41|22031;19017;19051;20023;20073;21066;21077;21004;20033;20096;20024;23043;23036;21029;21050;21009;21056;20018;21085;19016;20014;20039;19009;20035;22007;20031;19055;20025;20074;20074;20079;19022;20008;19025;19025;21028;20003;20006;20002;21031;23112|||3|0');
INSERT INTO "classes" VALUES('STUDY',6,'1','0','STUDY','0',0,'STUDY','JT',1,25,'2025TT','STUDY||6|1|0|JT||1|25||||1|0||');
INSERT INTO "classes" VALUES('STUDY',5,'1','0','STUDY','0',0,'STUDY','JT',0,25,'2025TT','STUDY||5|1|0|JT||0|25||||1|0||');
INSERT INTO "classes" VALUES('STUDY',4,'1','0','STUDY','0',0,'STUDY','JT',3,25,'2025TT','STUDY||4|1|0|JT||3|25||||1|0||');
INSERT INTO "classes" VALUES('STUDY',3,'1','0','STUDY','0',0,'STUDY','JT',10,25,'2025TT','STUDY||3|1|0|JT||10|25||||1|0||');
INSERT INTO "classes" VALUES('STUDY',2,'1','0','STUDY','0',0,'STUDY','JT',10,25,'2025TT','STUDY||2|1|0|JT||10|25||||1|0||');
INSERT INTO "classes" VALUES('NETNZDVC',1,'1','0','NETNZDVC','0',0,'NETNZDVC','JT',1,1,'2025TT','NETNZDVC||1|1|0|JT||1|1||||1|0||');
INSERT INTO "classes" VALUES('STUDY',1,'1','0','STUDY','0',0,'STUDY','JT',2,25,'2025TT','STUDY||1|1|0|JT||2|25||||1|0||');
INSERT INTO "classes" VALUES('MackDL',NULL,'0','0','MackDL','0',0,'MackDL','KV',0,0,'2025TT','MackDL|KV||||KV||0|0||||2|0||');
INSERT INTO "classes" VALUES('REVI',0,'0','0','REVI','0',0,'REVI','Michael',2,2,'2025TT','REVI|||||Michael||2|2|20061;20061|||3|0');
INSERT INTO "classes" VALUES('GATESDT',0,'0','0','GATESDT','0',0,'GATESDT','VP',4,4,'2025TT','GATESDT|||||VP||4|4|20024;20039;20080;23112|||3|0');
INSERT INTO "classes" VALUES('MMUSIC',NULL,'1','0','Music','Middle School',10,'Arts','0',0,23,'2025TT','MMUSIC||81|1|2|||0|23||||1|0||');
INSERT INTO "classes" VALUES('MMUSIC',NULL,'1','0','Music','Middle School',10,'Arts','0',0,23,'2025TT','MMUSIC||81|1|1|||0|23||||1|0||');
CREATE TABLE ingredient_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ingredient_name TEXT NOT NULL UNIQUE,
                quantity REAL DEFAULT 0,
                unit TEXT,
                category TEXT DEFAULT 'Other',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
CREATE TABLE recipe_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                recipe_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_email, recipe_id),
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            );
INSERT INTO "recipe_favorites" VALUES(1,'marykediplock@westlandhigh.school.nz',24,'2025-12-19 02:19:16');
CREATE TABLE recipe_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_name TEXT NOT NULL,
                recipe_url TEXT,
                reason TEXT,
                suggested_by_name TEXT NOT NULL,
                suggested_by_email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending'
            );
INSERT INTO "recipe_suggestions" VALUES(1,'Spag Bol','','Tertiary Student Staple','Vanessa Pringle','vanessapringle@westlandhigh.school.nz','2025-12-17 02:24:47','pending');
INSERT INTO "recipe_suggestions" VALUES(2,'Chicken Noodle Soup','','When you are sick','Vanessa Pringle','vanessapringle@westlandhigh.school.nz','2025-12-17 02:33:39','pending');
INSERT INTO "recipe_suggestions" VALUES(3,'Milo','','NZ Staple','Vanessa Pringle','vanessapringle@westlandhigh.school.nz','2025-12-17 02:47:23','pending');
INSERT INTO "recipe_suggestions" VALUES(4,'Onion Dip','','NZ Staple','Vanessa Pringle','vanessapringle@westlandhigh.school.nz','2025-12-17 03:41:50','pending');
INSERT INTO "recipe_suggestions" VALUES(5,'kiwi fruit','','Roxs','Vanessa Pringle','vanessapringle@westlandhigh.school.nz','2025-12-17 03:49:34','pending');
INSERT INTO "recipe_suggestions" VALUES(6,'chocolate cake','','Ve''s B''Day','Vanessa Pringle','vanessapringle@westlandhigh.school.nz','2025-12-17 03:58:07','pending');
INSERT INTO "recipe_suggestions" VALUES(7,'cheese block`','','Fav','Vanessa Pringle','vanessapringle@westlandhigh.school.nz','2025-12-18 21:36:27','pending');
INSERT INTO "recipe_suggestions" VALUES(8,'Pavlova','https://www.chelsea.co.nz/recipes/browse-recipes/pavlova','T4 - 300Hospo','Maryke Diplock','marykediplock@westlandhigh.school.nz','2025-12-19 02:17:47','pending');
CREATE TABLE recipes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      ingredients TEXT,
                      instructions TEXT,
                      serving_size INTEGER,
                      equipment TEXT, photo TEXT, dietary_tags TEXT, cuisine TEXT, difficulty TEXT);
INSERT INTO "recipes" VALUES(1,'Chocolate Chip Cookies','[{"quantity": "2", "unit": "cups", "ingredient": "Flour"}, {"quantity": "1", "unit": "cup", "ingredient": "Butter (softened)"}, {"quantity": "0.75", "unit": "cup", "ingredient": "Brown sugar"}, {"quantity": "0.5", "unit": "cup", "ingredient": "Granulated sugar"}, {"quantity": "2", "unit": "whole", "ingredient": "Eggs"}, {"quantity": "1", "unit": "tsp", "ingredient": "Vanilla extract"}, {"quantity": "1", "unit": "tsp", "ingredient": "Baking soda"}, {"quantity": "0.5", "unit": "tsp", "ingredient": "Salt"}, {"quantity": "2", "unit": "cups", "ingredient": "Chocolate chips"}]','Mix dry ingredients. Add wet ingredients. Drop onto baking sheet. Bake at 350F for 12 minutes.',24,'["Mixing bowl|Measuring cups|Baking sheet|Oven"]',NULL,NULL,NULL,NULL);
INSERT INTO "recipes" VALUES(3,'Cauliflower Cheese','[{"quantity": "1.0", "unit": "head", "ingredient": "of cauliflower OR 1 head of broccoli OR a mix of both"}, {"quantity": "50.0", "unit": "plain", "ingredient": "flour"}, {"quantity": "500.0", "unit": "milk", "ingredient": "milk"}, {"quantity": "50.0", "unit": "butter", "ingredient": "butter"}, {"quantity": "100.0", "unit": "grated", "ingredient": "cheese"}, {"quantity": "", "unit": "", "ingredient": "Black pepper"}, {"quantity": "", "unit": "", "ingredient": "1-2 tblsp fresh breadcrumbs"}, {"quantity": "", "unit": "", "ingredient": "Don\u2019t forget a container to take your cauliflower cheese home in"}]','1. 2cm hot water into a pan
2.  Bring to the boil, add the vegetables and cover with a lid
3.  Cook for 5mins maximum then drain using a colander then place them in a
dish
4.  Put the butter into a pan and melt it
5.  Add flour and stir to form a paste
6.  Gradually add the milk – keep stirring until it thickens.
7.  Remove from the heat and stir in most of the cheese. Season.
8.  Pour over the veg.
9. Sprinkle on breadcrumbs and the remaining cheese
10. Grill under  a hot grill until golden brown.
Feeling a dventurous?  You could….
• Try using different vegetables
• Add herbs to the sauce',1,'[]',NULL,NULL,NULL,NULL);
INSERT INTO "recipes" VALUES(4,'Mini Carrot Cakes','[{"quantity": "150.0", "unit": "margarine", "ingredient": "150g margarine"}, {"quantity": "250.0", "unit": "carrots", "ingredient": "250g carrots"}, {"quantity": "200.0", "unit": "sugar", "ingredient": "200g sugar"}, {"quantity": "2.0", "unit": "large", "ingredient": "eggs"}, {"quantity": "200.0", "unit": "flour", "ingredient": "200g flour"}, {"quantity": "2.0", "unit": "", "ingredient": "5 ml cinnamon"}, {"quantity": "2.0", "unit": "", "ingredient": "5ml baking powder"}, {"quantity": "125.0", "unit": "sultanas", "ingredient": "125g sultanas"}, {"quantity": "50.0", "unit": "nuts", "ingredient": "50g nuts"}]','1. Preheat the oven to 200oC or gas mark 6.
2. Melt the margarine in a saucepan .
3. Top and tail, and then peel and grate the carrots.
4. Combine the carrots, sugar and margarine in the mining bowl.
5. Sift in the flour, cinnamon and baking powder.
6. Beat the eggs in a small bowl, and then add to the mixture.
7. Mix in the sultanas and nuts.
8. Divide the mixture equally between the muffin cases, using the two metal spoons.
9. Bake for 20 minutes.',1,'["Muffin tray", "scales", "sieve", "saucepan chopping board", "knife", "grater", "small bowl", "mixing bowl", "wooden spoon"]',NULL,NULL,NULL,NULL);
INSERT INTO "recipes" VALUES(5,'Mushroom Risotto','[{"quantity": "150.0", "unit": "chestnut", "ingredient": "mushrooms"}, {"quantity": "1.0", "unit": "onion", "ingredient": "1 onion"}, {"quantity": "2.0", "unit": "cloves", "ingredient": "garlic"}, {"quantity": "1.0", "unit": "", "ingredient": "15ml spoon olive oil"}, {"quantity": "250.0", "unit": "risotto", "ingredient": "rice"}, {"quantity": "1.0", "unit": "", "ingredient": "5ml spoon vegetable stock powder"}, {"quantity": "", "unit": "", "ingredient": "1-1.5 litres water, boiling"}, {"quantity": "1.0", "unit": "", "ingredient": "15ml spoon parmesan, grated"}, {"quantity": "1.0", "unit": "", "ingredient": "10ml spoon thyme, chopped"}]','1. Prepare the vegetables:
2. peel and chop the onion;
3. slice the mushrooms;
4. Peel and crush the garlic.
5. Fry the onion and garlic in the oil until softened.
6. Add the mushrooms, and fry f or another 2 minutes.
7. Stir in the rice.
8. Mix the stock powder with the water.
9. Add a little o f the stock to the rice - a little at a time.  Wait for the stock to be absorbed, stirring
constantly.
10. Continue adding the stock until the rice cooks – this will tak e 20-25 minutes. The rice should be soft, but
still retain a nutty bite.
11. Stir in the parmes an and thyme into the rice.',1,'["Weighing scale s", "chopping board", "knife", "wooden spoon", "frying pan", "spoon", "mixing bowl"]',NULL,NULL,NULL,NULL);
INSERT INTO "recipes" VALUES(6,'Fajitas','[{"quantity": "", "unit": "", "ingredient": "1/2 lime"}, {"quantity": "", "unit": "", "ingredient": "1/2 green chilli"}, {"quantity": "1.0", "unit": "clove", "ingredient": "garlic"}, {"quantity": "", "unit": "", "ingredient": "1x15ml spoon coriander"}, {"quantity": "", "unit": "", "ingredient": "1x10ml spoon oil"}, {"quantity": "1.0", "unit": "small", "ingredient": "chicken breast (or 3 -4 boneless thighs or vegetarian substitute eg quorn"}, {"quantity": "", "unit": "", "ingredient": "1/2 onion"}, {"quantity": "", "unit": "", "ingredient": "1/2 green pepper"}, {"quantity": "2.0", "unit": "tortillas", "ingredient": "2 tortillas"}, {"quantity": "1.0", "unit": "tomato", "ingredient": "1 tomato"}, {"quantity": "25.0", "unit": "Cheddar", "ingredient": "cheese"}, {"quantity": "", "unit": "", "ingredient": "1x15ml spoon guacamole (or salsa), optional"}]','1. Prepare the marinade:
· squeeze the lime;
· peel and crush t he garlic;
· de-seed and slice the chilli;
· chop the coriander;
· stir everything together with the oil.
2. Remove any skin from the chicken and cut into strips. Mix with the marinade and place in the fridge, covered,
until needed.
3. Prepare the remainin g ingredients with a fresh knife on a clean chopping board:
· slice the onion and g reen pepper;
· chop the tomato;
· grate the cheese.
4. Add the marinated chicken to the wok or frying pan and stir -fry for about 4 minutes. Check that the  chicken is
cooked.
5. Add the onion and green pepper and continue to cook for a further 2 minutes.
6. Spread a little chicken in the centre of the tortilla, add some tomato, cheese and guacamole, then roll up.',1,'["weighing scales", "chopping board", "knife", "wooden spoon", "frying pan/wok", "spoon", "mixing bowl"]',NULL,NULL,NULL,NULL);
INSERT INTO "recipes" VALUES(7,'Vegetable Couscous','[{"quantity": "170.0", "unit": "water,", "ingredient": "boiling"}, {"quantity": "1.0", "unit": "vegetable", "ingredient": "stock cube"}, {"quantity": "100.0", "unit": "couscous", "ingredient": "100g couscous"}, {"quantity": "1.0", "unit": "medium", "ingredient": "tomato"}, {"quantity": "1.0", "unit": "spring", "ingredient": "onion"}, {"quantity": "", "unit": "", "ingredient": "\u00bc cucumber"}, {"quantity": "", "unit": "", "ingredient": "\u00bd yellow pepper"}, {"quantity": "4.0", "unit": "dried", "ingredient": "apricots"}, {"quantity": "1.0", "unit": "", "ingredient": "15ml spoon parsley"}, {"quantity": "2.0", "unit": "", "ingredient": "15ml spoons low fat dressing"}]','1. Make up the stock by dissolving the stock cube in the boiling water.
2. Pour the stock over the couscous in a large bowl.
3. Fluff with a fork and leave to stand for 5 minutes.
4. Chop the tomato and cucumber into small chunks.
5. Slice the pepper into small strips.
6. Slic e the dried apricots and parsley into small pieces.
7. Add all the vegetables to the couscous and snip the spring onions into the bowl using the scissors.
8. Stir everything together.
9. Add the dressing.',1,'["Kettle", "measuring jug", "measuring spoons", "weighing scales", "large bowl", "fork", "chopping board", "sharp knife", "can opener", "scissors", "mixing spoon."]',NULL,NULL,NULL,NULL);
INSERT INTO "recipes" VALUES(8,'Pizza','[{"quantity": "500.0", "unit": "wh", "ingredient": "ite strong bread flour"}, {"quantity": "", "unit": "", "ingredient": "1x 7g packet or 2 teaspoons fast action dried yeast"}, {"quantity": "1.0", "unit": "tablespoon", "ingredient": "oil"}, {"quantity": "2.0", "unit": "teaspoons", "ingredient": "salt"}, {"quantity": "1.0", "unit": "teaspoon", "ingredient": "sugar"}, {"quantity": "", "unit": "", "ingredient": "Warm water"}, {"quantity": "3.0", "unit": "tablespoons", "ingredient": "of Tomato puree or 400g tinned tomatoes"}, {"quantity": "", "unit": "", "ingredient": "A range of toppings ; e.g. sliced peppers, mushrooms , grated che ddar or  sliced mozzarella, cooked"}, {"quantity": "", "unit": "", "ingredient": "bacon, t inned sweetcorn, sliced ham or cooked bacon, salami, pineapple ."}]','1. Preheat the oven at 2200 C or Gas Mark 7
2. Sieve the flour and salt into a bowl and stir in the dried yeast and sugar
3. Add the oil and start to add warm water gradually adding a little at a ti me.  With your hands or a spoon
gradually bring the dough together.  It should feel s lightly sticky.  If it is very sticky add a little more flour, if
it is very dry still add a little more warm water.
4. Flour a work surface and knead the dough until it is smooth and stretchy, at least 5 minutes
5. Roll the dough out to a large circle and place it onto t he baking tray.  Place into the top oven to prove if there is
time.
6. Spoon over the tomato puree if using.  If using tinned tomatoes drain off the liquid before spreading them over
the pizza base
7. Scatter your chosen in gredien ts over the pizza base, putting the cheese on last.
8. Bake for 15 minutes until the base looks cooked and the cheese is golden brown .',1,'["weighing scales", "measuring spoons", "mixing bowl", "wooden spoon", "rolling pin", "baking tray"]',NULL,NULL,NULL,NULL);
INSERT INTO "recipes" VALUES(9,'Beef Nachos','[{"quantity": "100", "unit": "g", "ingredient": "beef mince"}, {"quantity": "1", "unit": "no.", "ingredient": "brown onion, diced"}, {"quantity": "1", "unit": "T", "ingredient": "minced garlic"}, {"quantity": "0.25", "unit": "can", "ingredient": "chilli beans"}, {"quantity": "2", "unit": "T", "ingredient": "tomato paste"}, {"quantity": "0.5", "unit": "can", "ingredient": "chopped tomatoes"}, {"quantity": "0.5", "unit": "cup", "ingredient": "frozen corn"}, {"quantity": "1", "unit": "no.", "ingredient": "carrot, grated"}, {"quantity": "0.5", "unit": "c", "ingredient": "beef stock (1 cube + 0.5 c water)"}, {"quantity": "0.5", "unit": "t", "ingredient": "smoked paprika"}, {"quantity": "0.5", "unit": "t", "ingredient": "dried oregano"}, {"quantity": "0.5", "unit": "t", "ingredient": "onion powder"}, {"quantity": "0.5", "unit": "t", "ingredient": "ground cumin"}, {"quantity": "0.5", "unit": "t", "ingredient": "ground coriander"}, {"quantity": "0.5", "unit": "c", "ingredient": "cheese"}, {"quantity": "", "unit": "", "ingredient": "sour cream"}, {"quantity": "", "unit": "", "ingredient": "corn chips"}]','1. Heat a little oil in a large frying pan on high heat cook mince, garlic and onion
breaking up mince with a wooden spoon as it cooks until browned add spices.
2. Stir in beans, to mato paste, tomatoes, corn, and carrot and beef stock
3. Bring to a simmer then reduce heat to low stirring occasionally for 9 -12
minutes until thickened.
4. Put corn chips in a bowl and spoon mince over the top, sprinkle with cheese
and put under grill until  till cheese is melted
5. Top with sour cream',4,'[]',NULL,NULL,NULL,NULL);
INSERT INTO "recipes" VALUES(16,'Courgette and Cheese Muffins','[{"quantity": "1.0", "unit": "small", "ingredient": "courgette (or \u00bd large)"}, {"quantity": "60.0", "unit": "cheddar", "ingredient": "cheese"}, {"quantity": "150.0", "unit": "self", "ingredient": "-raising flour"}, {"quantity": "30.0", "unit": "oil", "ingredient": "30ml oil"}, {"quantity": "100.0", "unit": "semi", "ingredient": "-skimmed milk"}, {"quantity": "1.0", "unit": "egg", "ingredient": "1 egg"}, {"quantity": "", "unit": "", "ingredient": "\u00bd tsp salt"}, {"quantity": "", "unit": "", "ingredient": "Black pepper  1 courgette"}, {"quantity": "100.0", "unit": "cheddar", "ingredient": "cheese"}, {"quantity": "225.0", "unit": "self", "ingredient": "-raising flour"}, {"quantity": "50.0", "unit": "oil", "ingredient": "50ml oil"}, {"quantity": "170.0", "unit": "semi", "ingredient": "-skimmed milk"}, {"quantity": "1.0", "unit": "egg", "ingredient": "1 egg"}, {"quantity": "1.0", "unit": "tsp", "ingredient": "salt"}, {"quantity": "", "unit": "", "ingredient": "Black pepper"}]','1. Preheat the oven to 200oC or gas mark 6.
2. Place the muffin cases in the muffin tin.
3. Cut the ends off the courgette.
4. Grate the courgette and cheese.
5. Use a wooden spoon to mix all the ingredients together to form a smooth batter for 2 minutes.
6. Divide the mixture equally between the muffin cases using 2 spoons.
7. Bake for 25 minutes, until golden.
8. Allow to cool on a cooling rack.',NULL,'["6 muffin cases", "muffin tin", "chopping board", "knife", "grater", "measuring jug", "mixing bowl", "wooden spoon", "2 spoons", "cooling rack."]',NULL,NULL,NULL,NULL);
INSERT INTO "recipes" VALUES(17,'Banana & Chocolate chip Muffins','[{"quantity": "1.0", "unit": "Ripe", "ingredient": "Banana"}, {"quantity": "", "unit": "", "ingredient": "\u00bd cup Wholemeal flour"}, {"quantity": "1.0", "unit": "Cup", "ingredient": "flour"}, {"quantity": "1.0", "unit": "\u00bc", "ingredient": "t baking powder"}, {"quantity": "", "unit": "", "ingredient": "2/3 Cup sugar"}, {"quantity": "2.0", "unit": "T", "ingredient": "chocolate chips"}, {"quantity": "1.0", "unit": "egg", "ingredient": "\u2013 beaten in a cup with a fork"}, {"quantity": "", "unit": "", "ingredient": "2/3 cup Milk"}, {"quantity": "50.0", "unit": "melted", "ingredient": "butter 2 Ripe Banana"}, {"quantity": "1.0", "unit": "cup", "ingredient": "Wholemeal flour"}, {"quantity": "2.0", "unit": "Cup", "ingredient": "flour"}, {"quantity": "2.0", "unit": "1/2", "ingredient": "t baking powder"}, {"quantity": "1.0", "unit": "1/2", "ingredient": "Cup sugar"}, {"quantity": "4.0", "unit": "T", "ingredient": "chocolate chips"}, {"quantity": "2.0", "unit": "egg", "ingredient": "\u2013 beaten in a cup with a fork"}, {"quantity": "1.0", "unit": "1/2", "ingredient": "cup Milk"}, {"quantity": "100.0", "unit": "melted", "ingredient": "butter"}]','9. Preheat oven to 180oC fan bake.
10. Place the muffin cases in the muffin tin.
11. Melt the butter on a low setting in the microwave – covered.
12. Mash banana with a fork in a large bowl.
13. Sift flour(s) and baking powder into a bowl with the banana in it.
14. Add sugar, chocolate chips, egg, milk and melted butter. Mix gently with a wooden spoon.
15. Divide the mixture equally between the muffin cases using 2 spoons.
16. Bake for 20 minutes, until golden.
17. Allow to cool on a cooling rack.',NULL,'["6 muffin cases", "muffin tin", "chopping board", "knife", "grater", "measuring jug", "mixing bowl", "wooden spoon", "2 spoons", "cooling rack."]',NULL,NULL,NULL,NULL);
INSERT INTO "recipes" VALUES(19,'Apple and Sultana Crumble','[{"quantity": "80.0", "unit": "g", "ingredient": "flour"}, {"quantity": "60.0", "unit": "g", "ingredient": "butter or margarine"}, {"quantity": "40.0", "unit": "g", "ingredient": "oats"}, {"quantity": "30.0", "unit": "g", "ingredient": "brown or white sugar"}, {"quantity": "2.0", "unit": "no.", "ingredient": "apples"}, {"quantity": "50.0", "unit": "g", "ingredient": "sultanas"}]','1. Preheat the oven to 190
oC or gas mark 5.
2. Rub in the butter or margarine into the flour until it resembles breadcrumbs.
3. Stir in the oats and sugar.
4. Cut the apples into quarters and remove the core. Slice thinly.
5. Arrange the apple slices in the oven -proof dish, and then add the sultanas.
6. Sprinkle the crumble topping over the apple slices.
7. Bake for 25 -30 minutes, until the apple is soft and the crumble is golden.',NULL,'["Weighing scales", "sieve", "mixing bowl", "wooden spoon", "chopping board", "knife", "ovenproof dish", "baking tray.."]',NULL,NULL,NULL,NULL);
INSERT INTO "recipes" VALUES(21,'OnePan Steak Caprese with Basil and Blistered Cherry Tomatoes','[{"quantity": "2", "unit": "no.", "ingredient": "Quality Mark beef eye fillet (about 170g each)"}, {"quantity": "2", "unit": "Tbsp", "ingredient": "olive oil, divided"}, {"quantity": "2", "unit": "tsp", "ingredient": "salt, divided"}, {"quantity": "1", "unit": "tsp", "ingredient": "black pepper, divided, \u00bd tsp garlic powder"}, {"quantity": "2", "unit": "cups", "ingredient": "cherry tomatoes i ((different colours if you can get them))"}, {"quantity": "4", "unit": "no.", "ingredient": "garlic cloves, crushed"}, {"quantity": "200", "unit": "g", "ingredient": "mozzarella cheese (sliced), \u00bc cup fresh basil leaves, cracked pepper, glaze of balsamic vinegar (for garnish)"}]','Method1Remove steaks from the fridge and pat with paper towels to remove excess moisture. Leave to come up to room temperature.2Toss the tomatoes with olive oil, garlic, salt, and pepper.3Preheat your 26cm skillet (or dual handled pan) over medium-high heat, about 5 minutes.4Season steaks on all sides with salt, pepper, and garlic powder. Bring your oven rack to the highest level and set the grill to high.5Add 1 tablespoon olive oil to the skillet and sear the steaks for 4 minutes per side.  Depending on the thickness of your fillet, you may need to sear the sides as well.6Remove steaks and set aside to rest.7Reduce heat to medium, add tomatoes and cook undisturbed for 2-3 minutes. Stir the tomatoes and cook for 2 additional minutes. Remove from heat.8Slice filets into 1cm strips.9Layer the beef strips with mozzarella slices on top of the tomatoes and set the skillet in the oven.10Grill for 1-2 minutes or more, depending on desired doneness.11Remove the pan from the oven and sprinkle with salt and cracked pepper.12Top with basil and drizzle with balsamic glaze.
Method1Remove steaks from the fridge and pat with paper towels to remove excess moisture. Leave to come up to room temperature.2Toss the tomatoes with olive oil, garlic, salt, and pepper.3Preheat your 26cm skillet (or dual handled pan) over medium-high heat, about 5 minutes.4Season steaks on all sides with salt, pepper, and garlic powder. Bring your oven rack to the highest level and set the grill to high.5Add 1 tablespoon olive oil to the skillet and sear the steaks for 4 minutes per side.  Depending on the thickness of your fillet, you may need to sear the sides as well.6Remove steaks and set aside to rest.7Reduce heat to medium, add tomatoes and cook undisturbed for 2-3 minutes. Stir the tomatoes and cook for 2 additional minutes. Remove from heat.8Slice filets into 1cm strips.9Layer the beef strips with mozzarella slices on top of the tomatoes and set the skillet in the oven.10Grill for 1-2 minutes or more, depending on desired doneness.11Remove the pan from the oven and sprinkle with salt and cracked pepper.12Top with basil and drizzle with balsamic glaze.
1Remove steaks from the fridge and pat with paper towels to remove excess moisture. Leave to come up to room temperature.2Toss the tomatoes with olive oil, garlic, salt, and pepper.3Preheat your 26cm skillet (or dual handled pan) over medium-high heat, about 5 minutes.4Season steaks on all sides with salt, pepper, and garlic powder. Bring your oven rack to the highest level and set the grill to high.5Add 1 tablespoon olive oil to the skillet and sear the steaks for 4 minutes per side.  Depending on the thickness of your fillet, you may need to sear the sides as well.6Remove steaks and set aside to rest.7Reduce heat to medium, add tomatoes and cook undisturbed for 2-3 minutes. Stir the tomatoes and cook for 2 additional minutes. Remove from heat.8Slice filets into 1cm strips.9Layer the beef strips with mozzarella slices on top of the tomatoes and set the skillet in the oven.10Grill for 1-2 minutes or more, depending on desired doneness.11Remove the pan from the oven and sprinkle with salt and cracked pepper.12Top with basil and drizzle with balsamic glaze.
1
2
3
4
5
6
7
8
9
10
11
12',4,'[]',NULL,NULL,NULL,NULL);
INSERT INTO "recipes" VALUES(22,'Hot honey nuggets with brisket','[{"quantity": "500", "unit": "g", "ingredient": "Quality Mark beef steaks i (brisket, sirloin or chuck - cut into 2cm cubes)"}, {"quantity": "0.5", "unit": "tsp", "ingredient": "baking soda"}, {"quantity": "1", "unit": "Tbsp", "ingredient": "water"}, {"quantity": "1", "unit": "tsp", "ingredient": "apple cider vinegar"}, {"quantity": "2", "unit": "Tbsp", "ingredient": "liquid honey"}, {"quantity": "1", "unit": "Tbsp", "ingredient": "soy sauce"}, {"quantity": "1", "unit": "to taste", "ingredient": "salt and pepper"}, {"quantity": "2", "unit": "Tbsp", "ingredient": "cornflour i"}, {"quantity": "1", "unit": "to taste", "ingredient": "olive oil"}, {"quantity": "0.5", "unit": "cup", "ingredient": "liquid honey"}, {"quantity": "2", "unit": "Tbsp", "ingredient": "cider vinegar"}, {"quantity": "1", "unit": "tsp", "ingredient": "garlic powder"}, {"quantity": "0.5", "unit": "tsp", "ingredient": "smoked paprika"}, {"quantity": "1", "unit": "tsp", "ingredient": "(\u00bd-1 range) chilli flakes i"}, {"quantity": "1", "unit": "pinch", "ingredient": "of salt"}]','Method1In a bowl, toss beef cubes with baking soda, water, vinegar, honey, soy sauce, salt and pepper.2Let it sit for 10 minutes to tenderise and get sticky.3Coat the marinated beef lightly in cornflour or rice flour — this helps form that crispy crust.4Heat a frying pan or air fryer to 200°C. Cook beef nuggets in a single layer until golden and caramelised, about 8–10 minutes, turning halfway.5While the beef cooks, make the hot honey: in a small saucepan, combine honey, cider vinegar, garlic powder, paprika, chilli flakes and salt.6Warm for 2–3 minutes until glossy and fragrant.7Drizzle the hot honey over the nuggets or toss them to coat.8Serve hot with kumara wedges and crunchy coleslaw.
Method1In a bowl, toss beef cubes with baking soda, water, vinegar, honey, soy sauce, salt and pepper.2Let it sit for 10 minutes to tenderise and get sticky.3Coat the marinated beef lightly in cornflour or rice flour — this helps form that crispy crust.4Heat a frying pan or air fryer to 200°C. Cook beef nuggets in a single layer until golden and caramelised, about 8–10 minutes, turning halfway.5While the beef cooks, make the hot honey: in a small saucepan, combine honey, cider vinegar, garlic powder, paprika, chilli flakes and salt.6Warm for 2–3 minutes until glossy and fragrant.7Drizzle the hot honey over the nuggets or toss them to coat.8Serve hot with kumara wedges and crunchy coleslaw.
1In a bowl, toss beef cubes with baking soda, water, vinegar, honey, soy sauce, salt and pepper.2Let it sit for 10 minutes to tenderise and get sticky.3Coat the marinated beef lightly in cornflour or rice flour — this helps form that crispy crust.4Heat a frying pan or air fryer to 200°C. Cook beef nuggets in a single layer until golden and caramelised, about 8–10 minutes, turning halfway.5While the beef cooks, make the hot honey: in a small saucepan, combine honey, cider vinegar, garlic powder, paprika, chilli flakes and salt.6Warm for 2–3 minutes until glossy and fragrant.7Drizzle the hot honey over the nuggets or toss them to coat.8Serve hot with kumara wedges and crunchy coleslaw.
1
2
3
4
5
6
7
8',4,'[]',NULL,NULL,NULL,NULL);
INSERT INTO "recipes" VALUES(23,'Lamb Salad','[{"quantity": 100.0, "unit": "g", "ingredient": "Quality Mark lamb mince"}, {"quantity": 0.25, "unit": "Tbsp", "ingredient": "olive oil"}, {"quantity": 0.25, "unit": "tsp", "ingredient": "ground cumin"}, {"quantity": 0.25, "unit": "tsp", "ingredient": "smoked paprika"}, {"quantity": 0.25, "unit": "tsp", "ingredient": "honey, pepper, to taste"}, {"quantity": 0.5, "unit": "whole", "ingredient": "telegraph cucumbers, cut into chunks"}, {"quantity": 62.5, "unit": "g", "ingredient": "cherry tomatoes, halved, \u00bd red onion, finely sliced, \u00bd cup fresh herbs, chopped, \u00bd cup olives, pitted and roughly chopped"}, {"quantity": 37.5, "unit": "g", "ingredient": "feta cheese, \u00bd cup Greek style yoghurt"}, {"quantity": 0.25, "unit": "Tbsp", "ingredient": "lemon juice"}, {"quantity": 0.25, "unit": "Tbsp", "ingredient": "olive oil, Hot honey"}, {"quantity": 1.0, "unit": "whole", "ingredient": "pita pockets, cut into triangles"}]','Mix ingredients and serve.',1,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "recipes" VALUES(24,'Perfect Pavlova','[{"quantity": "6", "unit": "item", "ingredient": "egg whites (at room temperature)"}, {"quantity": "2", "unit": "cups", "ingredient": "Chelsea Caster Sugar (450g)"}, {"quantity": "1", "unit": "tsp", "ingredient": "vanilla essence"}, {"quantity": "1", "unit": "tsp", "ingredient": "white vinegar"}, {"quantity": "2", "unit": "tsp", "ingredient": "Edmonds Fielder''s Cornflour"}, {"quantity": "300", "unit": "ml", "ingredient": "Meadow Fresh Original Cream, whipped"}, {"quantity": "1", "unit": "to taste", "ingredient": "Fruit, to decorate"}]','Preheat oven to 110ÂºC bake (not fan bake). Line a baking tray with baking paper. In a large metal, ceramic or glass bowl (not plastic), beat the egg whites until soft peaks form. Continue beating while adding theÂ Chelsea Caster Sugar a quarter of a cup at a time. The mixture should get glossier and thicker with each addition and this should take at least 10 minutes. Beat in the vanilla, vinegar and Edmonds Fielder''s Cornflour. Spoon mixture out onto the prepared tray into a dinner plate sized mound. Bake for approximately 1 1/2 hours, until dry and crisp and it lifts easily off the baking paper. Turn the oven off and leave the pavlova for at least an hour before removing from the oven. Finish cooling on a wire rack, then transfer to an airtight container. When ready to serve, place on a serving plate, swirl the top with the whippedÂ Meadow Fresh Original Cream and decorate with sliced or chopped fruit of your choice.',12,'[]',NULL,NULL,NULL,NULL);
CREATE TABLE role_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            route TEXT NOT NULL,
            UNIQUE(role, route)
        );
INSERT INTO "role_permissions" VALUES(1,'VP','recipes');
INSERT INTO "role_permissions" VALUES(2,'VP','recbk');
INSERT INTO "role_permissions" VALUES(3,'VP','class_ingredients');
INSERT INTO "role_permissions" VALUES(4,'VP','booking');
INSERT INTO "role_permissions" VALUES(5,'VP','shoplist');
INSERT INTO "role_permissions" VALUES(6,'VP','admin');
INSERT INTO "role_permissions" VALUES(7,'DK','recipes');
INSERT INTO "role_permissions" VALUES(8,'DK','recbk');
INSERT INTO "role_permissions" VALUES(9,'DK','class_ingredients');
INSERT INTO "role_permissions" VALUES(10,'DK','booking');
INSERT INTO "role_permissions" VALUES(11,'DK','shoplist');
INSERT INTO "role_permissions" VALUES(12,'MU','recipes');
INSERT INTO "role_permissions" VALUES(13,'MU','recbk');
INSERT INTO "role_permissions" VALUES(14,'MU','booking');
INSERT INTO "role_permissions" VALUES(15,'MU','shoplist');
INSERT INTO "role_permissions" VALUES(16,'public','recbk');
INSERT INTO "role_permissions" VALUES(17,'DK','admin');
INSERT INTO "role_permissions" VALUES(18,'public','recipes');
INSERT INTO "role_permissions" VALUES(19,'public','class_ingredients');
INSERT INTO "role_permissions" VALUES(20,'MU','class_ingredients');
INSERT INTO "role_permissions" VALUES(21,'public','booking');
INSERT INTO "role_permissions" VALUES(22,'public','shoplist');
INSERT INTO "role_permissions" VALUES(23,'public','admin');
INSERT INTO "role_permissions" VALUES(24,'MU','admin');
CREATE TABLE saved_shopping_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_name TEXT NOT NULL,
                week_label TEXT,
                items TEXT NOT NULL,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
INSERT INTO "saved_shopping_lists" VALUES(1,'Shopping List 17/12/2025','Week of 15/12/25 to 19/12/25','[{"name": "margarine", "quantity": 3600, "unit": "g", "category": "Other"}, {"name": "carrots", "quantity": 6000, "unit": "g", "category": "Produce"}, {"name": "sugar", "quantity": 4800, "unit": "g", "category": "Pantry"}, {"name": "eggs", "quantity": 48, "unit": "pcs", "category": "Other"}, {"name": "flour", "quantity": 7920, "unit": "g", "category": "Pantry"}, {"name": "cinnamon", "quantity": 120, "unit": "ml", "category": "Pantry"}, {"name": "baking powder", "quantity": 120, "unit": "g", "category": "Pantry"}, {"name": "sultanas", "quantity": 4200, "unit": "g", "category": "Other"}, {"name": "nuts", "quantity": 1200, "unit": "g", "category": "Pantry"}, {"name": "butter", "quantity": 2640, "unit": "g", "category": "Dairy"}, {"name": "oats", "quantity": 960, "unit": "g", "category": "Pantry"}, {"name": "brown", "quantity": 720, "unit": "g", "category": "Other"}, {"name": "apples", "quantity": 48, "unit": "pcs", "category": "Produce"}, {"name": "of cauliflower", "quantity": 24, "unit": "", "category": "Produce"}, {"name": "milk", "quantity": 12000, "unit": "ml", "category": "Dairy"}, {"name": "cheese", "quantity": 2400, "unit": "g", "category": "Dairy"}]','vanessapringle@westlandhigh.school.nz','2025-12-16 22:05:37');
CREATE TABLE shopping_list_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_start TEXT NOT NULL,
                ingredient_name TEXT NOT NULL,
                quantity REAL,
                unit TEXT,
                category TEXT DEFAULT 'Other',
                already_have INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(week_start, ingredient_name)
            );
CREATE TABLE teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            title TEXT,
            email TEXT
        );
INSERT INTO "teachers" VALUES(1,'JA','Aro','Jesah','Ms','jesaharo@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(2,'Ba','Bateup','Sarah','Ms','sarahbateup@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(3,'CY','Bradley','Conor','Mr','conorbradley@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(4,'JY','Bradley','Janna','Mrs','JannaBradley@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(5,'JB','Brownie','Jane','','janebrownie@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(6,'HB','Bruns','Hilke','Ms','hilkebruns@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(7,'FC','Cabanero','Joy','Ms','joycabanero@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(8,'CA','Callawick','Alexandra','Mrs','alexcallawick@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(9,'CP','Campion','Peter','Mr','PeterCampion@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(10,'Ch','Chinn','Gail','Mrs','GailChinn@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(11,'JK','Clark','James','Mr','JamesClark@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(12,'CL','Collins','Chris','Dr','chriscollins@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(13,'Col','Colman','Cassandra','Ms','CassandraColman@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(14,'CB','Conn','Belinda','','belindaconn@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(15,'JC','Cook','Justin','Mr','JustinCook@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(16,'JD','Dalgarno','John','Mr','johndalgarno@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(17,'Dk','Diplock','Maryke','Mrs','marykediplock@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(18,'SD','Dutt','Shalendra','Mr','ShalendraDutt@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(19,'AE','Evasco','Arleen','Ms','arleenevasco@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(20,'Gr','Greig','Annemarie','Mrs','annemariegreig@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(21,'Hj','Harrison','Janice','Mrs','janiceharrison@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(22,'MI','Hetherington','Michelle','Mrs','michellehetherington@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(23,'SH','Hilson','Sonica','Mrs','sonicahilson@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(24,'HE','Hulme','Monica','Ms','monicahulme@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(25,'TJ','Johnson','Tina','Ms','tinajohnson@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(26,'KN','Kelderman','Ino','Mr','inokelderman@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(27,'LI','King','Lachlan','Mr','LachlanKing@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(28,'Lr','Lauder','Fiona','Ms','fionalauder@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(29,'Le','Lee','Sheldon','Mr','sheldonlee@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(30,'Mn','Mallinson','Philippa','Ms','philippamallinson@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(31,'MA','Mathieson','Christine','Mrs','christinemathieson@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(32,'Mu','McClure','Bernie','Mrs','berniemcclure@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(33,'IMC','McDonald','Ian','Mr','IanMcDonald@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(34,'Am','McGrath','Anne','Mrs','annemcgrath@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(35,'HM','McKee','Holly','Ms','hollymckee@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(36,'Mc','McMullan','Raelene','Mrs','raelenemcmullan@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(37,'BMP','Mellsop','Brooke','Ms','brookemellsop@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(38,'JM','Minnaar','Johan','Mr','johanminnaar@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(39,'MM','Minnaar','Mariska','Mrs','mariskaminnaar@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(40,'GM','Monaheng','Gloria','Ms','gloriamonaheng@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(41,'SO','O''Malley','Siobhan','Mrs','siobhanomalley@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(42,'PH','Parikh','Brijen','Mr','sportshub@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(43,'BP','Parker','Brooke','Miss','brookeparker@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(44,'PI','Pinkerton','Anna','Mrs','annapinkerton@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(45,'VP','Pringle','Vanessa','Ms','vanessapringle@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(46,'PQ','Quilala','Paolo','Mr','PaoloQuilala@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(47,'MR','Ram','Mohinesh','Mr','mohineshram@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(48,'VR','Ram','Vikashni','Mrs','vikashniram@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(49,'Rs','Reeves','Adrienne','Mrs','adriennereeves@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(50,'RI','Rennie','Shanae','Miss','ShanaeRennie@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(51,'NR','Richards','Nic','Mr','principal@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(52,'BR','Roper','Bronte','Ms','bronteroper@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(53,'RY','Ryan','Rebecca','Ms','beckryan@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(54,'SR','Sadler','Janice','Ms','janicesadler@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(55,'GS','Smith','Gus','Mr','GusSmith@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(56,'TB','Talbot','Mike','Mr','miketalbot@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(57,'LT','Tame','Linda','Ms','LindaTame@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(58,'BT','Tapper','Ben','M','bentapper@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(59,'Tm','Thompson','Steve','Mr','stevethompson@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(60,'MTN','Thomson','Mike','Mr','mikethomson@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(61,'Jt','Thorpe','Judith','Ms','judiththorpe@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(62,'FUS','Usion','F','s','FUsion@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(63,'CV','Veale','Ciara','Ms','ciaraveale@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(64,'Ve','Veale','Kate','Ms','kateveale@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(65,'KV','Veale','Kristy','Ms','KristyVeale@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(66,'Wa','Waller','Michael','Mr','michaelwaller@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(67,'WY','Wastney','Rachel','Ms','rachelwastney@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(68,'JW','Webster','Janet','Ms','janetwebster@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(69,'We','Weepu','Christine','Mrs','christineweepu@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(70,'JE','Wellard','Jane','Miss','janewellard@westlandhigh.school.nz');
INSERT INTO "teachers" VALUES(73,'AS','Smith','Alice','Mrs','alice.smith@school.edu');
CREATE TABLE user_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(email, role)
        );
INSERT INTO "user_roles" VALUES(1,'janetwebster@westlandhigh.school.nz','DK','2025-12-16 10:27:52');
INSERT INTO "user_roles" VALUES(2,'adriennereeves@westlandhigh.school.nz','DK','2025-12-17 21:54:17');
INSERT INTO "user_roles" VALUES(3,'marykediplock@westlandhigh.school.nz','VP','2025-12-19 02:00:52');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('teachers',73);
INSERT INTO "sqlite_sequence" VALUES('recipes',24);
INSERT INTO "sqlite_sequence" VALUES('class_bookings',14);
INSERT INTO "sqlite_sequence" VALUES('user_roles',3);
INSERT INTO "sqlite_sequence" VALUES('role_permissions',24);
INSERT INTO "sqlite_sequence" VALUES('saved_shopping_lists',1);
INSERT INTO "sqlite_sequence" VALUES('recipe_suggestions',8);
INSERT INTO "sqlite_sequence" VALUES('recipe_favorites',1);
COMMIT;
