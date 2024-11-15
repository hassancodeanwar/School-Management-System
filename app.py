import streamlit as st
import pandas as pd
# import mysql.connector
from datetime import datetime
import pyodbc
import logging
import warnings

logging.getLogger().setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message="missing ScriptRunContext!")

# Database connection
def create_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=School_Grading_and_Attendance_System_DB;'
        'Trusted_Connection=yes;'
    )

# Connection closure function
def close_connection(conn):
    if conn:
        conn.close()

# Initialize Streamlit app
st.set_page_config(page_title="School Management System", layout="wide")

# Sidebar navigation
def sidebar_menu():
    st.sidebar.title("Navigation")
    return st.sidebar.radio(
        "Select Operation:",
        ["Students", "Teachers", "Classes", "Grades", "Attendance", "Advanced Queries"]
    )

# CRUD Operations for Students
def student_crud():
    st.header("Student Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Create", "Read", "Update", "Delete"])
    
    with tab1:
        st.subheader("Add New Student")
        with st.form("add_student"):
            student_id = st.text_input("Student ID")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            
            # Set min_value to allow dates from 1900 onwards
            dob = st.date_input("Date of Birth", min_value=datetime(1900, 1, 1).date(), key="dob_input")
            gender = st.selectbox("Gender", ["M", "F"], key="gender_selectbox")
            
            # Set min_value for enrollment date as well
            enrollment_date = st.date_input("Enrollment Date", min_value=datetime(1900, 1, 1).date(), key="enrollment_date_input")
        
            if st.form_submit_button("Add Student"):
                conn = create_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute(""" 
                        INSERT INTO Students (student_id, first_name, last_name, dob, gender, enrollment_date) 
                        VALUES (?, ?, ?, ?, ?, ?) 
                    """, (student_id, first_name, last_name, dob, gender, enrollment_date))
                    conn.commit()
                    st.success("Student added successfully!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    conn.close()
 
    with tab2:
        st.subheader("View Students")
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Students")
            result = cursor.fetchall()
            
            # Check if result contains any rows
            if result:
                columns = [column[0] for column in cursor.description]  # Extract column names
                formatted_result = [list(row) for row in result]  # Ensure rows are lists
                df = pd.DataFrame(formatted_result, columns=columns)  # Create DataFrame with columns
                st.dataframe(df)
            else:
                st.info("No students found in the database.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            close_connection(conn)
            
    with tab3:
        st.subheader("Update Student")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, first_name, last_name FROM Students")
        students = cursor.fetchall()

        student_id = st.selectbox("Select Student", 
                                options=[f"{s[0]} - {s[1]} {s[2]}" for s in students],
                                format_func=lambda x: x.split(" - ")[1],
                                key="update_student_selectbox")

        if student_id:
            student_id = int(student_id.split(" - ")[0])
            cursor.execute("SELECT * FROM Students WHERE student_id = ?", (student_id,))
            student_data = cursor.fetchone()

            with st.form("update_student"):
                new_first_name = st.text_input("First Name", value=student_data[1], key="update_first_name")
                new_last_name = st.text_input("Last Name", value=student_data[2], key="update_last_name")
                new_dob = st.date_input("Date of Birth", value=student_data[3], key="update_dob")
                new_gender = st.selectbox("Gender", ["M", "F"], index=0 if student_data[4] == "M" else 1, key="update_gender")

                if st.form_submit_button("Update Student"):
                    try:
                        cursor.execute("""
                            UPDATE Students 
                            SET first_name=?, last_name=?, dob=?, gender=? 
                            WHERE student_id=?
                        """, (new_first_name, new_last_name, new_dob, new_gender, student_id))
                        conn.commit()
                        st.success("Student updated successfully!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        conn.close()

    with tab4:
        st.subheader("Delete Student")
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT student_id, first_name, last_name FROM Students")
        students = cursor.fetchall()
        
        student_to_delete = st.selectbox(
            "Select Student to Delete",
            options=[f"{s[0]} - {s[1]} {s[2]}" for s in students],
            format_func=lambda x: x.split(" - ")[1],
            key="delete_student_selectbox"
        )
        
        if st.button("Delete Student"):
            try:
                student_id = int(student_to_delete.split(" - ")[0])
                cursor.execute("DELETE FROM Students WHERE student_id = ?", (student_id,))
                conn.commit()
                st.success("Student deleted successfully!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        conn.close()
# CRUD Operations for Teachers
def teacher_crud():
    st.header("Teacher Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Create", "Read", "Update", "Delete"])
    
    # Create Teacher
    with tab1:
        st.subheader("Add New Teacher")
        with st.form("add_teacher"):
            teacher_id = st.text_input("Teacher ID")  # Ensure ID is entered manually or handled differently if auto-generated
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            subject = st.text_input("Subject")

            if st.form_submit_button("Add Teacher"):
                conn = create_connection()
                cursor = conn.cursor()
                try:
                    # Insert teacher details into the database
                    cursor.execute("""
                        INSERT INTO Teachers (teacher_id, first_name, last_name, subject) 
                        VALUES (?, ?, ?, ?)
                    """, (teacher_id, first_name, last_name, subject))
                    
                    # Commit transaction after data insertion
                    conn.commit()
                    st.success("Teacher added successfully!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    close_connection(conn)


    # View Teachers
    # View Teachers
    with tab2:
        st.subheader("View Teachers")
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Teachers")
            result = cursor.fetchall()
            
            # Check if result contains any rows
            if result:
                columns = [column[0] for column in cursor.description]  # Extract column names
                formatted_result = [list(row) for row in result]  # Ensure rows are lists
                df = pd.DataFrame(formatted_result, columns=columns)  # Create DataFrame with columns
                st.dataframe(df)
            else:
                st.info("No teachers found in the database.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            close_connection(conn)


    # Update Teacher
    with tab3:
        st.subheader("Update Teacher")
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT teacher_id, first_name, last_name FROM Teachers")
            teachers = cursor.fetchall()
            
            teacher_id_options = [f"{t[0]} - {t[1]} {t[2]}" for t in teachers]
            teacher_to_update = st.selectbox("Select Teacher to Update", teacher_id_options)
            
            if teacher_to_update:
                teacher_id = int(teacher_to_update.split(" - ")[0])
                cursor.execute("SELECT * FROM Teachers WHERE teacher_id = ?", (teacher_id,))
                teacher_data = cursor.fetchone()

                with st.form("update_teacher"):
                    new_first_name = st.text_input("First Name", value=teacher_data[1])
                    new_last_name = st.text_input("Last Name", value=teacher_data[2])
                    new_subject = st.text_input("Subject", value=teacher_data[3])

                    if st.form_submit_button("Update Teacher"):
                        cursor.execute("""
                            UPDATE Teachers 
                            SET first_name=?, last_name=?, subject=? 
                            WHERE teacher_id=?
                        """, (new_first_name, new_last_name, new_subject, teacher_id))
                        conn.commit()
                        st.success("Teacher updated successfully!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            close_connection(conn)

    # Delete Teacher
    with tab4:
        st.subheader("Delete Teacher")
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT teacher_id, first_name, last_name FROM Teachers")
            teachers = cursor.fetchall()

            teacher_id_options = [f"{t[0]} - {t[1]} {t[2]}" for t in teachers]
            teacher_to_delete = st.selectbox("Select Teacher to Delete", teacher_id_options)

            if st.button("Delete Teacher"):
                teacher_id = int(teacher_to_delete.split(" - ")[0])
                cursor.execute("DELETE FROM Teachers WHERE teacher_id = ?", (teacher_id,))
                conn.commit()
                st.success("Teacher deleted successfully!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            close_connection(conn)
# Class Management CRUD Operations
def class_crud():
    st.header("Class Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Create", "Read", "Update", "Delete"])

    # Create Class
    with tab1:
        st.subheader("Add New Class")
        class_id = st.text_input("Class ID")
        class_name = st.text_input("Class Name")

        # Fetch teacher list for assigning to class
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT teacher_id, first_name, last_name FROM Teachers")
        teachers = cursor.fetchall()
        close_connection(conn)

        teacher_options = [f"{t[0]} - {t[1]} {t[2]}" for t in teachers]
        selected_teacher = st.selectbox("Select Teacher", teacher_options)

        if st.button("Add Class"):
            conn = create_connection()
            cursor = conn.cursor()
            try:
                teacher_id = int(selected_teacher.split(" - ")[0])  # Extract teacher_id
                cursor.execute("""
                    INSERT INTO Classes (class_id, class_name, teacher_id)
                    VALUES (?, ?, ?)
                """, (class_id, class_name, teacher_id))
                conn.commit()
                st.success("Class added successfully!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
            finally:
                close_connection(conn)


    # View Classes
    with tab2:
        st.subheader("View Classes")
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT C.class_id, C.class_name, T.first_name, T.last_name
                FROM Classes C
                JOIN Teachers T ON C.teacher_id = T.teacher_id
            """)
            result = cursor.fetchall()
            
            # Check if result contains any rows
            if result:
                columns = ['Class ID', 'Class Name', 'Teacher First Name', 'Teacher Last Name']
                formatted_result = [list(row) for row in result]  # Ensure each row is a list
                df = pd.DataFrame(formatted_result, columns=columns)
                st.dataframe(df)
            else:
                st.info("No classes found in the database.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            close_connection(conn)

    # Update Class
    with tab3:
        st.subheader("Update Class")

        # Fetch existing classes and teachers for selection
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT class_id, class_name FROM Classes")
            classes = cursor.fetchall()

            # If there are classes, proceed with update form
            if classes:
                class_options = [f"{c[0]} - {c[1]}" for c in classes]
                selected_class = st.selectbox("Select Class to Update", class_options)
                selected_class_id = int(selected_class.split(" - ")[0])

                cursor.execute("SELECT class_name, teacher_id FROM Classes WHERE class_id = ?", (selected_class_id,))
                class_data = cursor.fetchone()

                # Get updated class name and teacher list
                new_class_name = st.text_input("Class Name", value=class_data[0])
                cursor.execute("SELECT teacher_id, first_name, last_name FROM Teachers")
                teachers = cursor.fetchall()
                teacher_options = [f"{t[0]} - {t[1]} {t[2]}" for t in teachers]
                selected_teacher = st.selectbox("Select New Teacher", teacher_options, index=[t[0] for t in teachers].index(class_data[1]))

                if st.button("Update Class"):
                    new_teacher_id = int(selected_teacher.split(" - ")[0])
                    try:
                        cursor.execute("""
                            UPDATE Classes
                            SET class_name = ?, teacher_id = ?
                            WHERE class_id = ?
                        """, (new_class_name, new_teacher_id, selected_class_id))
                        conn.commit()
                        st.success("Class updated successfully!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.info("No classes found to update.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            close_connection(conn)

    # Delete Class
    with tab4:
        st.subheader("Delete Class")

        # Fetch classes for deletion
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT class_id, class_name FROM Classes")
            classes = cursor.fetchall()

            if classes:
                class_options = [f"{c[0]} - {c[1]}" for c in classes]
                selected_class = st.selectbox("Select Class to Delete", class_options)
                selected_class_id = int(selected_class.split(" - ")[0])

                if st.button("Delete Class"):
                    try:
                        cursor.execute("DELETE FROM Classes WHERE class_id = ?", (selected_class_id,))
                        conn.commit()
                        st.success("Class deleted successfully!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.info("No classes found to delete.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            close_connection(conn)

# Grade Management CRUD Operations
def grade_crud():
    st.header("Grade Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Create", "Read", "Update", "Delete"])

    # Create Grade
    with tab1:
        st.subheader("Add New Grade")
        
        # Fetch list of students and classes
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT student_id, first_name, last_name FROM Students")
            students = cursor.fetchall()
            cursor.execute("SELECT class_id, class_name FROM Classes")
            classes = cursor.fetchall()
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
        finally:
            close_connection(conn)

        # Dropdown options for selecting student and class
        student_options = [f"{s[0]} - {s[1]} {s[2]}" for s in students]
        class_options = [f"{c[0]} - {c[1]}" for c in classes]
        selected_student = st.selectbox("Select Student", student_options)
        selected_class = st.selectbox("Select Class", class_options)
        grade = st.text_input("Grade (e.g., A, B, C)")
        date_assigned = st.date_input("Date Assigned", datetime.now().date())

        if st.button("Add Grade"):
            conn = create_connection()
            cursor = conn.cursor()
            try:
                student_id = int(selected_student.split(" - ")[0])
                class_id = int(selected_class.split(" - ")[0])
                cursor.execute("""
                    INSERT INTO Grades (student_id, class_id, grade, date_assigned)
                    VALUES (?, ?, ?, ?)
                """, (student_id, class_id, grade, date_assigned))
                conn.commit()
                st.success("Grade added successfully!")
            except Exception as e:
                st.error(f"Error adding grade: {str(e)}")
            finally:
                close_connection(conn)
# View Grades
    with tab2:
        st.subheader("View Grades")
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT G.grade_id, S.first_name, S.last_name, C.class_name, G.grade, G.date_assigned
                FROM Grades G
                JOIN Students S ON G.student_id = S.student_id
                JOIN Classes C ON G.class_id = C.class_id
            """)
            result = cursor.fetchall()

            # Check if result contains any rows
            if result:
                columns = ['Grade ID', 'Student First Name', 'Student Last Name', 'Class Name', 'Grade', 'Date Assigned']
                formatted_result = [list(row) for row in result]
                df = pd.DataFrame(formatted_result, columns=columns)
                st.dataframe(df)
            else:
                st.info("No grades found in the database.")
        except Exception as e:
            st.error(f"Error retrieving grades: {str(e)}")
        finally:
            close_connection(conn)


    # Update Grade
    with tab3:
        st.subheader("Update Grade")

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT grade_id, student_id, class_id, grade FROM Grades")
            grades = cursor.fetchall()
            
            if grades:
                grade_options = [f"{g[0]} - Student ID: {g[1]}, Class ID: {g[2]}, Grade: {g[3]}" for g in grades]
                selected_grade = st.selectbox("Select Grade to Update", grade_options)
                selected_grade_id = int(selected_grade.split(" - ")[0])

                cursor.execute("""
                    SELECT student_id, class_id, grade, date_assigned
                    FROM Grades
                    WHERE grade_id = ?
                """, (selected_grade_id,))
                grade_data = cursor.fetchone()

                new_grade = st.text_input("Grade", value=grade_data[2])
                new_date_assigned = st.date_input("Date Assigned", value=grade_data[3])

                if st.button("Update Grade"):
                    try:
                        cursor.execute("""
                            UPDATE Grades
                            SET grade = ?, date_assigned = ?
                            WHERE grade_id = ?
                        """, (new_grade, new_date_assigned, selected_grade_id))
                        conn.commit()
                        st.success("Grade updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating grade: {str(e)}")
        except Exception as e:
            st.error(f"Error fetching grades for update: {str(e)}")
        finally:
            close_connection(conn)

    # Delete Grade
    with tab4:
        st.subheader("Delete Grade")

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT grade_id, student_id, class_id, grade FROM Grades")
            grades = cursor.fetchall()

            if grades:
                grade_options = [f"{g[0]} - Student ID: {g[1]}, Class ID: {g[2]}, Grade: {g[3]}" for g in grades]
                selected_grade = st.selectbox("Select Grade to Delete", grade_options)
                selected_grade_id = int(selected_grade.split(" - ")[0])

                if st.button("Delete Grade"):
                    try:
                        cursor.execute("DELETE FROM Grades WHERE grade_id = ?", (selected_grade_id,))
                        conn.commit()
                        st.success("Grade deleted successfully!")
                    except Exception as e:
                        st.error(f"Error deleting grade: {str(e)}")
        except Exception as e:
            st.error(f"Error fetching grades for deletion: {str(e)}")
        finally:
            close_connection(conn)


# Attendance Management CRUD Operations
def attendance_management():
    st.header("Attendance Management")
    
    tab1, tab2, tab3 = st.tabs(["Mark Attendance", "View Attendance", "Update Attendance"])

    # Mark Attendance
    with tab1:
        st.subheader("Mark Attendance")
        
        # Fetch list of students and classes
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT student_id, first_name, last_name FROM Students")
            students = cursor.fetchall()
            cursor.execute("SELECT class_id, class_name FROM Classes")
            classes = cursor.fetchall()
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
        finally:
            close_connection(conn)

        # Dropdown options for selecting student and class
        student_options = [f"{s[0]} - {s[1]} {s[2]}" for s in students]
        class_options = [f"{c[0]} - {c[1]}" for c in classes]
        selected_student = st.selectbox("Select Student", student_options)
        selected_class = st.selectbox("Select Class", class_options)
        attendance_status = st.selectbox("Attendance Status", ["Present", "Absent", "Late"])
        date = st.date_input("Date", datetime.now().date())

        if st.button("Mark Attendance"):
            conn = create_connection()
            cursor = conn.cursor()
            try:
                student_id = int(selected_student.split(" - ")[0])
                class_id = int(selected_class.split(" - ")[0])
                cursor.execute("""
                    INSERT INTO Attendance (student_id, class_id, status, date)
                    VALUES (?, ?, ?, ?)
                """, (student_id, class_id, attendance_status, date))
                conn.commit()
                st.success("Attendance marked successfully!")
            except Exception as e:
                st.error(f"Error marking attendance: {str(e)}")
            finally:
                close_connection(conn)

    # View Attendance
    with tab2:
        st.subheader("View Attendance")
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT A.attendance_id, S.first_name, S.last_name, C.class_name, A.status, A.date
                FROM Attendance A
                JOIN Students S ON A.student_id = S.student_id
                JOIN Classes C ON A.class_id = C.class_id
            """)
            result = cursor.fetchall()

            # Check if result contains any rows
            if result:
                columns = ['Attendance ID', 'Student First Name', 'Student Last Name', 'Class Name', 'Status', 'Date']
                formatted_result = [list(row) for row in result]
                df = pd.DataFrame(formatted_result, columns=columns)
                st.dataframe(df)
            else:
                st.info("No attendance records found.")
        except Exception as e:
            st.error(f"Error retrieving attendance: {str(e)}")
        finally:
            close_connection(conn)

    # Update Attendance
    with tab3:
        st.subheader("Update Attendance")

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT attendance_id, student_id, class_id, status FROM Attendance")
            attendance_records = cursor.fetchall()
            
            if attendance_records:
                attendance_options = [f"{a[0]} - Student ID: {a[1]}, Class ID: {a[2]}, Status: {a[3]}" for a in attendance_records]
                selected_attendance = st.selectbox("Select Attendance to Update", attendance_options)
                selected_attendance_id = int(selected_attendance.split(" - ")[0])

                cursor.execute("""
                    SELECT student_id, class_id, status, date
                    FROM Attendance
                    WHERE attendance_id = ?
                """, (selected_attendance_id,))
                attendance_data = cursor.fetchone()

                new_status = st.selectbox("Status", options=["Present", "Absent"], index=["Present", "Absent"].index(attendance_data[2]))
                new_date = st.date_input("Date", value=attendance_data[3])

                if st.button("Update Attendance"):
                    try:
                        cursor.execute("""
                            UPDATE Attendance
                            SET status = ?, date = ?
                            WHERE attendance_id = ?
                        """, (new_status, new_date, selected_attendance_id))
                        conn.commit()
                        st.success("Attendance updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating attendance: {str(e)}")
        except Exception as e:
            st.error(f"Error fetching attendance for update: {str(e)}")
        finally:
            close_connection(conn)

# Advanced Queries
def advanced_queries():
    st.header("Advanced Queries")
    
    # Dropdown for selecting an advanced query
    query_option = st.selectbox(
        "Select an Advanced Query", 
        ["Top Performing Students", "Class Performance", "Student Attendance Summary"]
    )
    
    conn = create_connection()
    cursor = conn.cursor()
    
    if query_option == "Top Performing Students":
        st.subheader("Top Performing Students")
        try:
            cursor.execute("""
                SELECT TOP 10 S.first_name, S.last_name, AVG(TRY_CAST(G.grade AS FLOAT)) AS average_grade
                FROM Grades G
                JOIN Students S ON G.student_id = S.student_id
                GROUP BY S.first_name, S.last_name
                ORDER BY average_grade DESC
            """)

            result = cursor.fetchall()
            if result:
                columns = ['First Name', 'Last Name', 'Average Grade']
                formatted_result = [list(row) for row in result]
                df = pd.DataFrame(formatted_result, columns=columns)
                st.dataframe(df)
            else:
                st.info("No data found.")
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
    
    elif query_option == "Class Performance":
        st.subheader("Class Performance")
        try:
            cursor.execute("""
                SELECT TOP 10 C.class_name, AVG(TRY_CAST(G.grade AS FLOAT)) AS average_grade
                FROM Grades G
                JOIN Classes C ON G.class_id = C.class_id
                GROUP BY C.class_name
                ORDER BY average_grade DESC
            """)
            result = cursor.fetchall()
            if result:
                columns = ['Class Name', 'Average Grade']
                formatted_result = [list(row) for row in result]
                df = pd.DataFrame(formatted_result, columns=columns)
                st.dataframe(df)
            else:
                st.info("No data found.")
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")

    elif query_option == "Student Attendance Summary":
        st.subheader("Student Attendance Summary")
        try:
            cursor.execute("""
                SELECT TOP 10 S.first_name, S.last_name, COUNT(A.attendance_id) AS total_attendance
                FROM Attendance A
                JOIN Students S ON A.student_id = S.student_id
                WHERE A.status = 'Present'
                GROUP BY S.first_name, S.last_name
                ORDER BY total_attendance DESC
            """)

            result = cursor.fetchall()
            if result:
                columns = ['First Name', 'Last Name', 'Total Attendance']
                formatted_result = [list(row) for row in result]
                df = pd.DataFrame(formatted_result, columns=columns)
                st.dataframe(df)
            else:
                st.info("No data found.")
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
    
    
        finally:
            close_connection(conn)

def main():
    st.title("School Management System")
    
    menu_choice = sidebar_menu()
    
    if menu_choice == "Students":
        student_crud()
    elif menu_choice == "Teachers":
        teacher_crud()
    elif menu_choice == "Classes":
        class_crud()
    elif menu_choice == "Grades":
        grade_crud()  
    elif menu_choice == "Attendance":
        attendance_management()
    elif menu_choice == "Advanced Queries":
        advanced_queries()

if __name__ == "__main__":
    main()
