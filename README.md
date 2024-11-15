<aside>

# Technical Documentation

### Overview

The School Management System is a comprehensive web application built using Streamlit that provides an interface for managing students, teachers, classes, grades, and attendance records. The application connects to a SQL Server database and provides CRUD (Create, Read, Update, Delete) operations for all main entities.

### Technical Stack

- **Frontend Framework**: Streamlit
- **Database**: Microsoft SQL Server
- **Programming Language**: Python 3.x
- **Key Dependencies**:
    - `streamlit`: Web application framework
    - `pyodbc`: SQL Server database connector
    - `pandas`: Data manipulation and display
    - `datetime`: Date handling
    - `logging`: Error logging
    - `warnings`: Warning suppression

### Database Connection

The application uses ODBC to connect to a SQL Server database named "School_Grading_and_Attendance_System_DB". Connection management is handled through two primary functions:

```python
def create_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=School_Grading_and_Attendance_System_DB;'
        'Trusted_Connection=yes;'
    )

def close_connection(conn):
    if conn:
        conn.close()

```

### Core Modules

### 1. Student Management

- Location: `student_crud()` function
- Features:
    - Add new students with ID, name, DOB, gender, and enrollment date
    - View all students in a tabular format
    - Update existing student information
    - Delete students from the system
- Key Tables: `Students`

### 2. Teacher Management

- Location: `teacher_crud()` function
- Features:
    - Add new teachers with ID, name, and subject
    - View all teachers and their subjects
    - Update teacher information
    - Delete teachers from the system
- Key Tables: `Teachers`

### 3. Class Management

- Location: `class_crud()` function
- Features:
    - Create new classes with assigned teachers
    - View class listings with teacher assignments
    - Update class information and teacher assignments
    - Delete classes
- Key Tables: `Classes`

### 4. Grade Management

- Location: `grade_crud()` function
- Features:
    - Assign grades to students for specific classes
    - View all grades with student and class information
    - Update existing grades
    - Delete grade entries
- Key Tables: `Grades`

### 5. Attendance Management

- Location: `attendance_management()` function
- Features:
    - Mark student attendance (Present/Absent/Late)
    - View attendance records
    - Update attendance status
- Key Tables: `Attendance`

### 6. Advanced Queries

- Location: `advanced_queries()` function
- Available Reports:
    - Top Performing Students
    - Class Performance Analysis
    - Student Attendance Summary

### User Interface Structure

The application uses Streamlit's sidebar navigation system with the following components:

- Sidebar menu for main navigation
- Tab-based interface for CRUD operations
- Forms for data input
- Interactive data tables for viewing records
- Success/Error notifications for user feedback

### Error Handling

The application implements comprehensive error handling through:

- Try-catch blocks around database operations
- Proper connection closure in finally blocks
- Error messages displayed through Streamlit's error notification system
- Logging configuration for system-level errors

### Database Schema

Key tables and their relationships:

1. **Students**
    - student_id (Primary Key)
    - first_name
    - last_name
    - dob
    - gender
    - enrollment_date
2. **Teachers**
    - teacher_id (Primary Key)
    - first_name
    - last_name
    - subject
3. **Classes**
    - class_id (Primary Key)
    - class_name
    - teacher_id (Foreign Key to Teachers)
4. **Grades**
    - grade_id (Primary Key)
    - student_id (Foreign Key to Students)
    - class_id (Foreign Key to Classes)
    - grade
    - date_assigned
5. **Attendance**
    - attendance_id (Primary Key)
    - student_id (Foreign Key to Students)
    - class_id (Foreign Key to Classes)
    - status
    - date

### Best Practices Implemented

1. **Database Connection Management**
    - Proper connection closure
    - Connection pooling through context managers
2. **Code Organization**
    - Modular function structure
    - Separation of concerns
    - Clear naming conventions
3. **Security**
    - Trusted connection for database access
    - Input validation through form controls
    - Error message sanitization
4. **User Experience**
    - Consistent interface across modules
    - Clear success/error messaging
    - Intuitive navigation structure

### Installation Requirements

1. Python 3.x
2. SQL Server
3. ODBC Driver 17 for SQL Server
4. Required Python packages:
    
    ```bash
    pip install streamlit pandas pyodbc
    
    ```
    

### Running the Application

To start the application:

```bash
streamlit run app.py

```
To install these requirements, you can run:
```bash
pip install -r requirements.txt
```

### Maintenance and Troubleshooting

1. **Common Issues**
    - Database connection errors: Check SQL Server connection string and credentials
    - ODBC driver issues: Verify correct driver installation
    - Date format errors: Ensure proper date parsing in forms
2. **Performance Optimization**
    - Database queries are optimized for performance
    - Connection pooling reduces database overhead
    - Efficient data loading through pandas DataFrames
3. **Logging**
    - System configured to log errors at ERROR level
    - Warning suppression for known Streamlit issues

### Future Enhancements

1. Additional reporting capabilities
2. User authentication and authorization
3. File upload functionality for student records
4. Export functionality for reports
5. Dashboard for key metrics
6. Mobile responsiveness improvements
</aside>
