import streamlit as st
import pandas as pd
from datetime import datetime
import pyodbc
import logging
import warnings
import matplotlib.pyplot as plt


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
        
        # Single student form
        with st.form("add_student"):
            student_id = st.text_input("Student ID")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            dob = st.date_input("Date of Birth", min_value=datetime(1900, 1, 1).date(), key="dob_input")
            gender = st.selectbox("Gender", ["M", "F"], key="gender_selectbox")
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
        
        st.markdown("---")
        st.subheader("Bulk Upload Students")
        
        # Bulk upload form
        uploaded_file = st.file_uploader("Upload a CSV File", type=["csv"], key="bulk_upload")
        
        if uploaded_file:
            try:
                # Read the uploaded CSV file
                df = pd.read_csv(uploaded_file)
                st.dataframe(df)  # Display the uploaded file for preview
                
                # Validate and transform the DataFrame
                # Ensure correct column names for matching SQL schema
                df.rename(columns={'ID': 'student_id', 'FirstName': 'first_name', 'LastName': 'last_name'}, inplace=True)

                # Default values for missing columns
                df['dob'] = pd.to_datetime('2000-01-01')  # Default DOB for all students
                df['gender'] = 'M'  # Default gender for all students (can be modified)
                df['enrollment_date'] = pd.to_datetime(datetime.now().date())  # Default enrollment date (current date)

                # Ensure proper data types before insert
                df['student_id'] = df['student_id'].astype(int)
                df['first_name'] = df['first_name'].astype(str)
                df['last_name'] = df['last_name'].astype(str)
                df['dob'] = pd.to_datetime(df['dob']).dt.date  # Ensure DATE type
                df['gender'] = df['gender'].astype(str)
                df['enrollment_date'] = pd.to_datetime(df['enrollment_date']).dt.date  # Ensure DATE type

                # Get existing student_ids from the database
                conn = create_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT student_id FROM Students")
                existing_ids = [row[0] for row in cursor.fetchall()]
                conn.close()

                # Filter out the students that already exist in the database
                df_filtered = df[~df['student_id'].isin(existing_ids)]

                if df_filtered.empty:
                    st.warning("All student IDs already exist in the database. No new students to upload.")
                else:
                    st.write("Transformed DataFrame:")
                    st.dataframe(df_filtered)

                    # Insert only the unique students that do not exist in the database
                    if st.button("Insert Students"):
                        conn = create_connection()
                        cursor = conn.cursor()
                        try:
                            for _, row in df_filtered.iterrows():
                                cursor.execute(""" 
                                    INSERT INTO Students (student_id, first_name, last_name, dob, gender, enrollment_date) 
                                    VALUES (?, ?, ?, ?, ?, ?) 
                                """, (row['student_id'], row['first_name'], row['last_name'], 
                                    row['dob'], row['gender'], row['enrollment_date']))
                            conn.commit()
                            st.success("Students uploaded successfully!")
                        except Exception as e:
                            st.error(f"Error during bulk upload: {str(e)}")
                        finally:
                            conn.close()
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

 
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

        # Dropdown options for selecting class
        class_options = [f"{c[0]} - {c[1]}" for c in classes]
        selected_class = st.selectbox("Select Class", class_options, key="mark_attendance_class")
        class_id = int(selected_class.split(" - ")[0])

        # Filter students based on selected class
        student_options = [f"{s[0]} - {s[1]} {s[2]}" for s in students if s[0] in [student[0] for student in students if student[1] == class_id]]
        selected_student = st.selectbox("Select Student", student_options, key="mark_attendance_student")
        attendance_status = st.selectbox("Attendance Status", ["Present", "Absent", "Late"], key="mark_attendance_status")
        date = st.date_input("Date", datetime.now().date(), key="mark_attendance_date")

        if st.button("Mark Attendance", key="mark_attendance_button"):
            conn = create_connection()
            cursor = conn.cursor()
            try:
                student_id = int(selected_student.split(" - ")[0])
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

        # Dropdown for selecting class
        class_options = [f"{c[0]} - {c[1]}" for c in classes]
        selected_class = st.selectbox("Select Class", class_options, key="view_attendance_class")
        class_id = int(selected_class.split(" - ")[0])

        try:
            cursor.execute("""
                SELECT A.attendance_id, S.first_name, S.last_name, C.class_name, A.status, A.date
                FROM Attendance A
                JOIN Students S ON A.student_id = S.student_id
                JOIN Classes C ON A.class_id = C.class_id
                WHERE C.class_id = ?
            """, (class_id,))
            result = cursor.fetchall()

            # Check if result contains any rows
            if result:
                columns = ['Attendance ID', 'Student First Name', 'Student Last Name', 'Class Name', 'Status', 'Date']
                formatted_result = [list(row) for row in result]
                df = pd.DataFrame(formatted_result, columns=columns)
                st.dataframe(df)
            else:
                st.info("No attendance records found for this class.")
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
                selected_attendance = st.selectbox("Select Attendance to Update", attendance_options, key="update_attendance_select")
                selected_attendance_id = int(selected_attendance.split(" - ")[0])

                cursor.execute("""
                    SELECT student_id, class_id, status, date
                    FROM Attendance
                    WHERE attendance_id = ?
                """, (selected_attendance_id,))
                attendance_data = cursor.fetchone()

                new_status = st.selectbox("Status", options=["Present", "Absent"], index=["Present", "Absent"].index(attendance_data[2]), key="update_attendance_status")
                new_date = st.date_input("Date", value=attendance_data[3], key="update_attendance_date")

                if st.button("Update Attendance", key="update_attendance_button"):
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

def advanced_queries():
    st.title("Advanced Queries")
    st.markdown(""" 
    Discover insights into student performance, class efficiency, and attendance records. 
    Navigate through the tabs below to explore different analyses.
    """)
    
    # Create tabs
    tabs = st.tabs([
        "Top Performing Students", "Class Performance", "Student Attendance Summary",
        "Underperforming Students", "Attendance Trends Over Time", "Class Enrollment Counts",
        "Students with Consistent Attendance", "Class Performance Comparison Over Time"
    ])
    
    # Establish database connection
    conn = create_connection()
    if not conn:
        st.error("Failed to connect to the database.")
        return  # Stop execution if connection fails
    
    cursor = conn.cursor()

    try:
        # Example of executing a query (adjust for each tab)
        with tabs[0]:
            st.subheader("Top Performing Students")
            cursor.execute("""
                SELECT TOP 10
                    S.first_name, 
                    S.last_name, 
                    AVG(CASE grade 
                        WHEN 'A' THEN 95
                        WHEN 'B' THEN 85
                        WHEN 'C' THEN 75
                        WHEN 'D' THEN 65
                        WHEN 'F' THEN 55
                    END) AS average_grade
                FROM Grades G
                JOIN Students S ON G.student_id = S.student_id
                GROUP BY S.first_name, S.last_name
                ORDER BY average_grade DESC;
            """)
            result = cursor.fetchall()

            if result:
                result_data = [list(row) for row in result]
                df = pd.DataFrame(result_data, columns=['First Name', 'Last Name', 'Average Grade'])
                st.dataframe(df)
            else:
                st.write("No top-performing students available.")

        # Class Performance
        with tabs[1]:
            st.subheader("Class Performance")
            cursor.execute("""
                SELECT 
                    C.class_name, 
                    AVG(CASE grade 
                        WHEN 'A' THEN 95
                        WHEN 'B' THEN 85
                        WHEN 'C' THEN 75
                        WHEN 'D' THEN 65
                        WHEN 'F' THEN 55
                    END) AS average_grade
                FROM Grades G
                JOIN Classes C ON G.class_id = C.class_id
                GROUP BY C.class_name
                ORDER BY average_grade DESC;
            """)
            result = cursor.fetchall()
            if result:
                result_data = [list(row) for row in result]
                df = pd.DataFrame(result_data, columns=['Class Name', 'Average Grade'])
                st.dataframe(df)
            else:
                st.write("No class performance data available.")

        # Student Attendance Summary
        with tabs[2]:
            st.subheader("Student Attendance Summary")
            cursor.execute("""
                SELECT 
                    S.first_name, 
                    S.last_name, 
                    COUNT(CASE WHEN A.status = 'Present' THEN 1 END) AS present_count,
                    COUNT(A.attendance_id) AS total_classes,
                    CASE 
                        WHEN COUNT(A.attendance_id) > 0 THEN 
                            (CAST(COUNT(CASE WHEN A.status = 'Present' THEN 1 END) AS FLOAT) / COUNT(A.attendance_id)) * 100 
                        ELSE 0 
                    END AS attendance_rate
                FROM Students S
                LEFT JOIN Attendance A ON S.student_id = A.student_id
                GROUP BY S.first_name, S.last_name
                ORDER BY attendance_rate DESC;
            """)
            result = cursor.fetchall()
            if result:
                result_data = [list(row) for row in result]
                df = pd.DataFrame(result_data, columns=['First Name', 'Last Name', 'Present Count', 'Total Classes', 'Attendance Rate (%)'])
                st.dataframe(df)
            else:
                st.write("No attendance data available.")

        # Underperforming Students
        with tabs[3]:
            st.subheader("Underperforming Students")
            cursor.execute("""
                SELECT 
                    S.first_name, 
                    S.last_name, 
                    AVG(CASE grade 
                        WHEN 'A' THEN 95
                        WHEN 'B' THEN 85
                        WHEN 'C' THEN 75
                        WHEN 'D' THEN 65
                        WHEN 'F' THEN 55
                    END) AS average_grade
                FROM Grades G
                JOIN Students S ON G.student_id = S.student_id
                GROUP BY S.first_name, S.last_name
                HAVING AVG(CASE grade 
                        WHEN 'A' THEN 95
                        WHEN 'B' THEN 85
                        WHEN 'C' THEN 75
                        WHEN 'D' THEN 65
                        WHEN 'F' THEN 55
                    END) < 70
                ORDER BY average_grade ASC;
            """)
            result = cursor.fetchall()
            if result:
                result_data = [list(row) for row in result]
                df = pd.DataFrame(result_data, columns=['First Name', 'Last Name', 'Average Grade'])
                st.dataframe(df)
            else:
                st.write("No underperforming students found.")
        
        # Attendance Trends Over Time
        with tabs[4]:
            st.subheader("Attendance Trends Over Time")
            cursor.execute("""
                SELECT 
                    DATEPART(month, A.date) AS month,
                    COUNT(CASE WHEN A.status = 'Present' THEN 1 END) AS present_count,
                    COUNT(A.attendance_id) AS total_classes,
                    CASE 
                        WHEN COUNT(A.attendance_id) > 0 THEN 
                            (CAST(COUNT(CASE WHEN A.status = 'Present' THEN 1 END) AS FLOAT) / COUNT(A.attendance_id)) * 100
                        ELSE 0 
                    END AS attendance_rate
                FROM Attendance A
                GROUP BY DATEPART(month, A.date)
                ORDER BY month;
            """)
            result = cursor.fetchall()

            if result:
                result_data = [list(row) for row in result]
                df = pd.DataFrame(result_data, columns=['Month', 'Present Count', 'Total Classes', 'Attendance Rate (%)'])
                st.dataframe(df)

                # Adding sliders for figure size customization
                st.write("Adjust the figure size:")
                width = st.slider("Width", min_value=5, max_value=15, value=10)
                height = st.slider("Height", min_value=3, max_value=10, value=6)

                # Plot attendance trends
                fig, ax = plt.subplots(figsize=(width, height))
                ax.plot(df['Month'], df['Attendance Rate (%)'], marker='o')
                ax.set_title('Attendance Rate Over Time')
                ax.set_xlabel('Month')
                ax.set_ylabel('Attendance Rate (%)')
                st.pyplot(fig)
            else:
                st.write("No attendance trend data available.")
        
        # Other queries (Class Enrollment Counts, Consistent Attendance, etc.) remain similar.

    except Exception as e:
        st.error(f"An error occurred while executing the query: {str(e)}")
    finally:
        cursor.close()
        conn.close()

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
