# Attendance Management System using Image Processing
The Attendance Management System is a Python-based project designed to automate attendance tracking using image processing and database integration. It leverages Optical Character Recognition (OCR) and signature matching to streamline the process of marking attendance.
<br><br>
## Key Features:
- Image Processing: Detect and extract attendance table cells and signatures from uploaded images.
- Signature Matching: Compare student signatures with pre-stored signatures for validation.
- Database Integration: Record attendance in a MySQL database.
- Email Notifications: Notify absent students automatically.
- Graphical User Interface (GUI): User-friendly interface built using Tkinter.
<br><br>
## Prerequisites
### Software Requirements:
1. Python 3.x
2. MySQL Server
3. Libraries:
    - tkinter
    - opencv-python
    - pytesseract
    - mysql-connector-python
    - smtplib

### Hardware Requirements:</b><br>
- A computer capable of running Python and MySQL.
- Scanner for capturing attendance sheets.
<br><br>
## Installation Steps
### Clone the Repository:

    git clone https://github.com/khomaneamit/Attendance_Management_System_using_Image_Processing.git

### Install Required Libraries:

    pip install opencv-python pytesseract mysql-connector-python

### Configure MySQL Database:
#### Open your MySQL client or command line tool.
#### Create a new database:

    CREATE DATABASE Attendance_Management_System;

#### Import the .sql file into the database:

    mysql -u <username> -p Attendance_Management_System < attendance_backup.sql
Replace <username> with your MySQL username and provide the password when prompted.

### Set up pytesseract:

- Download and install Tesseract OCR from here.

- Configure the Tesseract path if not added to the system PATH.

### Update Email Credentials:

- Open the code and update the from_email and password variables in the send_absence_email function.

- Ensure the email account has "Allow less secure apps" enabled or uses an app-specific password.
<br><br>
## Usage

### Run the Application:

    python Attendance.py

### Add Attendance:

- Navigate to the "Add Attendance" tab.
- Select the date, time, subject code, and upload the attendance sheet image.
- Click "Submit" to process the attendance.
  
### View Attendance by Subject:

- Navigate to the "Subject" tab.
- Select date, time, and subject code to view attendance records.

### View Attendance by Student:

- Navigate to the "Student" tab.
- Enter the roll number and optional filters (date, time, subject code).
<br><br>
## Folder Structure

- <b>Student_signatures:</b> Pre-stored student signature images.
- <b>sign_images:</b> Extracted signatures from the uploaded attendance sheet.
<br><br>
## Contact

For any queries or issues, contact:

<b>Author:</b> Amit Khomane

<b>Email:</b> khomaneamit16@gmail.com

