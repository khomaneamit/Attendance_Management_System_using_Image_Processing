Attendance Management System

Overview

The Attendance Management System automates the process of tracking and recording attendance for students. It uses signature detection and Optical Character Recognition (OCR) to identify attendance records from scanned images, compares signatures, and updates the database accordingly. Absent students are notified via email.

Key Features:

Image Processing: Detect and extract attendance table cells and signatures from uploaded images.

Signature Matching: Compare student signatures with pre-stored signatures for validation.

Database Integration: Record attendance in a MySQL database.

Email Notifications: Notify absent students automatically.

Graphical User Interface (GUI): User-friendly interface built using Tkinter.

Prerequisites

Software Requirements:

Python 3.x

MySQL Server

Libraries:

tkinter

opencv-python

pytesseract

mysql-connector-python

smtplib

Hardware Requirements:

A computer capable of running Python and MySQL.

Scanner for capturing attendance sheets.

Installation Steps

Clone the Repository:

git clone https://github.com/your-repo-link.git

Install Required Libraries:

pip install opencv-python pytesseract mysql-connector-python

Configure MySQL Database:

Create a database named Attendance_Management_System.

Create required tables:

students: Stores student details (roll number, name, email).

attendance: Stores attendance records.

subjects: Stores subject codes.

Add the following stored procedure:

CREATE PROCEDURE InsertAttendanceRecord (
    IN roll_number VARCHAR(8),
    IN subject_code VARCHAR(10),
    IN date DATE,
    IN time TIME,
    IN status VARCHAR(10)
)
BEGIN
    INSERT INTO attendance (roll_number, subject_code, date, time, status)
    VALUES (roll_number, subject_code, date, time, status);
END;

Set up pytesseract:

Download and install Tesseract OCR from here.

Configure the Tesseract path if not added to the system PATH.

Update Email Credentials:

Open the code and update the from_email and password variables in the send_absence_email function.

Ensure the email account has "Allow less secure apps" enabled or uses an app-specific password.

Usage

Run the Application:

python app.py

Add Attendance:

Navigate to the "Add Attendance" tab.

Select the date, time, subject code, and upload the attendance sheet image.

Click "Submit" to process the attendance.

View Attendance by Subject:

Navigate to the "Subject" tab.

Select date, time, and subject code to view attendance records.

View Attendance by Student:

Navigate to the "Student" tab.

Enter the roll number and optional filters (date, time, subject code).

Folder Structure

Student_signatures: Pre-stored student signature images.

sign_images: Extracted signatures from the uploaded attendance sheet.

Troubleshooting

No student found with roll number:
Ensure the students table in the database contains the correct data.

Failed to send email:
Verify internet connectivity and email credentials.

Signature mismatch issues:
Ensure the scanned image quality is clear and matches the original signature resolution.

License

This project is licensed under the MIT License.

Contact

For any queries or issues, contact:

Author: Amit Khomane

Email: khomaneamit16@gmail.com

