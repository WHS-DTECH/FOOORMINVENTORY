-- PostgreSQL compatible schema and data for Neon
-- Batch 1: class_bookings and classes

-- Remove transaction wrappers for Neon
-- BEGIN TRANSACTION;
-- COMMIT;

-- Table: class_bookings
CREATE TABLE class_bookings (
    id SERIAL PRIMARY KEY,
    staff_code TEXT,
    class_code TEXT,
    date_required DATE,
    period INTEGER,
    recipe_id INTEGER,
    desired_servings INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data for class_bookings
INSERT INTO class_bookings (id, staff_code, class_code, date_required, period, recipe_id, desired_servings, created_at) VALUES
(1,'Dk','100HOSP','2025-12-25',4,19,24,'2025-12-13 00:07:35'),
(2,'Dk','200HOSP','2025-12-25',3,21,24,'2025-12-13 01:28:54'),
(3,'Dk','100HOSP','2025-12-25',3,22,24,'2025-12-13 01:32:49'),
(4,'Dk','200HOSP','2025-12-25',3,8,24,'2025-12-13 01:49:19'),
(5,'VP','300HOSP','2025-12-16',5,4,24,'2025-12-13 01:53:55'),
(6,'VP','MFOOD','2025-12-17',2,19,24,'2025-12-13 01:54:17'),
(7,'VP','SDFOOD','2025-12-18',4,19,24,'2025-12-13 01:54:46'),
(8,'Dk','300HOSP','2025-12-19',4,3,24,'2025-12-13 02:37:59'),
(9,'VP','300HOSP','2025-12-16',3,1,24,'2025-12-16 20:23:59'),
(10,'VP','MFOOD','2025-12-23',2,5,24,'2025-12-16 20:58:00'),
(11,'VP','200HOSP','2026-01-07',1,16,24,'2025-12-16 20:59:09'),
(12,'VP','300HOSP','2025-12-18',1,22,4,'2025-12-18 19:19:27'),
(13,'Dk','300HOSP','2025-12-25',1,1,24,'2025-12-18 21:37:11'),
(14,'Dk','100HOSP','2025-12-19',1,19,48,'2025-12-19 02:14:08');

-- Table: classes
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
    TimetableYear TEXT,
    Misc3 TEXT,
    PRIMARY KEY (ClassCode, LineNo)
);

-- Data for classes (first 100 lines, add more as needed)
-- Copy/paste more INSERTs from your dump as needed
