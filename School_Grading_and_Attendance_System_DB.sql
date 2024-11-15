-- Create the database
CREATE DATABASE School_Grading_and_Attendance_System_DB;
USE School_Grading_and_Attendance_System_DB;

-- Recreate tables without IDENTITY columns, requiring explicit IDs
CREATE TABLE Students (
    student_id INT PRIMARY KEY,
    first_name NVARCHAR(50),
    last_name NVARCHAR(50),
    dob DATE,
    gender NVARCHAR(10),
    enrollment_date DATE
);

CREATE TABLE Teachers (
    teacher_id INT PRIMARY KEY,
    first_name NVARCHAR(50),
    last_name NVARCHAR(50),
    subject NVARCHAR(100)
);

CREATE TABLE Classes (
    class_id INT PRIMARY KEY,
    class_name NVARCHAR(100),
    teacher_id INT FOREIGN KEY REFERENCES Teachers(teacher_id)
);

CREATE TABLE Attendance (
    attendance_id INT PRIMARY KEY IDENTITY(1,1),
    student_id INT FOREIGN KEY REFERENCES Students(student_id),
    class_id INT FOREIGN KEY REFERENCES Classes(class_id),
    date DATE DEFAULT GETDATE(),
    status NVARCHAR(10) CHECK (status IN ('Present', 'Absent', 'Late')),
    ip_address NVARCHAR(15) NULL
);


CREATE TABLE Grades (
    grade_id INT PRIMARY KEY IDENTITY(1,1),   -- Automatically generates unique values starting from 1
    student_id INT FOREIGN KEY REFERENCES Students(student_id),
    class_id INT FOREIGN KEY REFERENCES Classes(class_id),
    grade NVARCHAR(5) CHECK (grade IN ('A', 'B', 'C', 'D', 'F')),  -- Restrict grades to A, B, C, D, F
    date_assigned DATE DEFAULT GETDATE()  -- Default the date to current date if not provided
);
