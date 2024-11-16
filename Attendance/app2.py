from flask import Flask, render_template, request, redirect, url_for
import pyodbc
from datetime import datetime
import qrcode
import io
import base64

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'Driver': '{SQL Server}',
    'Server': 'CODEPC',
    'Database': 'School_Grading_and_Attendance_System_DB',
    'Trusted_Connection': 'yes'
}

def get_db_connection():
    conn_str = ';'.join(f"{k}={v}" for k, v in DB_CONFIG.items())
    return pyodbc.connect(conn_str)

@app.route('/')
def index():
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url_for('attendance_form', _external=True))
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64 for embedding in HTML
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    
    return render_template('index.html', qr_code=img_str)

@app.route('/form')
def attendance_form():
    # Get list of classes from database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT class_id, class_name FROM Classes")
    classes = cursor.fetchall()
    conn.close()
    
    return render_template('form.html', classes=classes)

@app.route('/submit', methods=['POST'])
def submit_attendance():
    try:
        student_id = request.form['student_id']
        class_id = request.form['class_id']
        ip_address = request.remote_addr
        
        # Verify student exists
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM Students WHERE student_id = ?", student_id)
        if not cursor.fetchone():
            return "Invalid student ID", 400
            
        # Check if attendance already recorded for today
        cursor.execute("""
            SELECT 1 FROM Attendance 
            WHERE student_id = ? AND class_id = ? AND date = CAST(GETDATE() AS DATE)
        """, student_id, class_id)
        
        if cursor.fetchone():
            return "Attendance already recorded for today", 400
            
        # Insert attendance record
        cursor.execute("""
            INSERT INTO Attendance (student_id, class_id, status, ip_address)
            VALUES (?, ?, 'Present', ?)
        """, student_id, class_id, ip_address)
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('success'))
        
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred", 500

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(
        host='192.168.0.106',  # Makes the server externally visible
        port=5000,       # You can change this port if needed
        debug=True       # Set to False in production
    )
    
    
    