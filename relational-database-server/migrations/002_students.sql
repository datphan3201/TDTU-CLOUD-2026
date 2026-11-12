-- DB-01: additive and repeatable; do not overwrite existing student rows.
CREATE DATABASE IF NOT EXISTS studentdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE studentdb;
CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(10),
    fullname VARCHAR(100),
    dob DATE,
    major VARCHAR(50)
);
INSERT INTO students (student_id, fullname, dob, major)
SELECT 'DEMO001', 'Nguyễn Minh An', '2005-01-15', 'Công nghệ thông tin'
WHERE NOT EXISTS (SELECT 1 FROM students WHERE student_id = 'DEMO001');
INSERT INTO students (student_id, fullname, dob, major)
SELECT 'DEMO002', 'Trần Bảo Bình', '2005-06-20', 'Khoa học máy tính'
WHERE NOT EXISTS (SELECT 1 FROM students WHERE student_id = 'DEMO002');
INSERT INTO students (student_id, fullname, dob, major)
SELECT 'DEMO003', 'Lê Khánh Chi', '2005-09-10', 'Kỹ thuật phần mềm'
WHERE NOT EXISTS (SELECT 1 FROM students WHERE student_id = 'DEMO003');
-- The migration runner grants SELECT to the configured MARIADB_USER.
