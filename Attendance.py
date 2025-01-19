import tkinter as tk
from tkinter import ttk, filedialog
import cv2
import os
import pytesseract
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
from tkinter.filedialog import askopenfilename

def get_student_info(roll_number):
    conn = mysql.connector.connect(
        host='localhost',
        user='amit',
        password='12345678',
        database='Attendance_Management_System'
    )
    cursor = conn.cursor()
    student_info = {}
    
    try:
        query = "SELECT name, email FROM students WHERE roll_number = %s"
        cursor.execute(query, (roll_number,))
        result = cursor.fetchone()
        
        if result:
            student_info['name'] = result[0]
            student_info['email'] = result[1]
        else:
            print(f"No student found with roll number: {roll_number}")
    
    except Exception as e:
        print(f"Failed to fetch student info: {e}")
    
    finally:
        cursor.close()
        conn.close()
    
    return student_info

def send_absence_email(student_email, student_name, date):
    from_email = "khomaneamit16@gmail.com"
    password = "dniu biuy pzqg rmzz"
    subject = "Attendance Notification"
    body = f"Dear {student_name},\n\nYou were marked absent on {date}.\nPlease contact your instructor if this is a mistake.\n\nBest regards,\nAttendance System"
    
    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = student_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=40)
        server.starttls()  # Secure connection
        server.login(from_email, password)
        server.send_message(message)
        print(f"Email sent to {student_name} ({student_email})")
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

def record_attendance_in_db(roll_number, subject_code, date, time, status):
    conn = mysql.connector.connect(
        host='localhost',
        user='amit',
        password='12345678',
        database='Attendance_Management_System'
    )
    cursor = conn.cursor()

    try:
        cursor.callproc('InsertAttendanceRecord', [roll_number, subject_code, date, time, status])
        conn.commit()
        print(f"Attendance for {roll_number} recorded as {status}")
    except Exception as e:
        print(f"Failed to record attendance: {e}")
    finally:
        cursor.close()
        conn.close()

def load_and_preprocess_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Image not found: {image_path}")
    image = cv2.resize(image, (500, 250))
    return image

def detect_and_compute_keypoints(image):
    orb = cv2.ORB_create()
    keypoints, descriptors = orb.detectAndCompute(image, None)
    return keypoints, descriptors

def match_descriptors(des1, des2):
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    return matches

def calculate_similarity(matches):
    if len(matches) == 0:
        return 0
    avg_distance = sum([m.distance for m in matches]) / len(matches)
    similarity = max(0, 100 - avg_distance)
    return similarity

def compare_signatures(image_path1, image_path2):
    image1 = load_and_preprocess_image(image_path1)
    image2 = load_and_preprocess_image(image_path2)
    kp1, des1 = detect_and_compute_keypoints(image1)
    kp2, des2 = detect_and_compute_keypoints(image2)
    matches = match_descriptors(des1, des2)
    similarity = calculate_similarity(matches)
    return similarity

def is_sign(img):
    output = False
    text = pytesseract.image_to_string(img)
    arr = [x for x in text if x.isalpha()]
    result = ''
    for char in arr:
        result += char
    if result.lower() == "sign":
        output = True
    return output

def extract_table_cells(image_path, output_folder):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(img.shape[0] / 30)))
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(img.shape[1] / 30), 1))
    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    table_lines = cv2.add(vertical_lines, horizontal_lines)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    table_lines = cv2.dilate(table_lines, kernel, iterations=1)
    contours, _ = cv2.findContours(table_lines, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    roll = extract_text_from_image(image_path)
    cells = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 20 and h > 20:
            cells.append((x,y,w,h))
    cells = sorted(cells, key=lambda x: (x[1], x[0]))
    os.makedirs(output_folder, exist_ok=True)
    i = 0
    sign_x = None
    for idx, (x,y,w,h) in enumerate(cells):
        if i == 0:
            i = 1
            continue
        cell_img = img[y:y+h, x:x+w]
        if(is_sign(cell_img)):
            sign_x = x
            break
    i=0
    for idx,(x,y,w,h) in enumerate(cells):
        if x == sign_x:
            if i == 0:
                i=1
                continue
            cell_img = img[y:y+h, x:x+w]
            cell_img_path = os.path.join(output_folder, f"{roll.pop(0)}.png")
            cv2.imwrite(cell_img_path, cell_img)

def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    text = pytesseract.image_to_string(img)
    arr = [x for x in text if x.isdigit() or x == '\n']
    result = []
    current_string = ''
    for char in arr:
        if char == '\n':
            if len(current_string) == 8:
                result.append(current_string)
                current_string = ''
        else:
            current_string += char
    if current_string:
        result.append(current_string)
    return result

def submit():
    file_path = tab1_file_label.cget("text")
    if tab1_date_entry.get() and tab1_time_entry.get() and tab1_subject_code.get() and file_path:
        roll_no = extract_text_from_image(file_path)
        output_folder = 'sign_images'
        extract_table_cells(file_path, output_folder)
        
        # Clear previous results in the Treeview
        for item in tab1_tree.get_children():
            tab1_tree.delete(item)
            exit
        for r in roll_no:
            image_path1 = 'Student_signatures/' + r + '.png'
            image_path2 = 'sign_images/' + r + '.png'
            similarity_score = compare_signatures(image_path1, image_path2)
            student_info = get_student_info(r)
            if similarity_score >= 85:
                status = 'Present'
            else:
                status = 'Absent'
                send_absence_email(student_info['email'], student_info['name'], tab1_date_entry.get())
            
            # Insert result into the table (Treeview)
            tab1_tree.insert("", tk.END, values=(r, student_info['name'], status))
            
            # Record attendance in MySQL database
            record_attendance_in_db(r, tab1_subject_code.get(), tab1_date_entry.get(), tab1_time_entry.get(), status)
        open_popup("Successfully recorded Attedndance and mail sent to Absent Students")
    else:
        open_popup("All fields are compulsory to fill!")

def get_subject_codes():
    conn = mysql.connector.connect(host='localhost', user='amit', password='12345678', database='Attendance_Management_System')
    cursor = conn.cursor()
    result = {}
    
    try:
        query = "SELECT subject_code FROM subjects"
        cursor.execute(query)
        result = cursor.fetchall()
    
    except Exception as e:
        print(f"Failed to fetch subject code info: {e}")
    
    finally:
        cursor.close()
        conn.close()
    
    return result

def open_popup(message):
    popup = tk.Toplevel(root)
    popup.title("Popup")
    popup.geometry("300x200")

    label = tk.Label(popup, text=message, font=("Arial",14), wraplength=260)
    label.pack(pady=20)

    close_button = tk.Button(popup, text="Close", command=popup.destroy)
    close_button.pack(pady=10)

def get_attendance_by_subject():
    conn = mysql.connector.connect(
        host='localhost',
        user='amit',
        password='12345678',
        database='Attendance_Management_System'
    )

    for item in tab2_tree.get_children():
        tab2_tree.delete(item)
        exit

    cursor = conn.cursor(dictionary=True)
    query = "SELECT attendance.roll_number, students.name, subject_code, date, time, status FROM attendance, students WHERE students.roll_number = attendance.roll_number AND 1=1"
    params = []
    if tab2_date_entry.get():
        query += " AND date = %s"
        params.append(tab2_date_entry.get())
    if tab2_time_entry.get():
        query += " AND time = %s"
        params.append(tab2_time_entry.get())
    if tab2_subject_name.get():
        query += " AND subject_code = %s"
        params.append(tab2_subject_name.get())
    
    cursor.execute(query, tuple(params))
    records = cursor.fetchall()

    for r in records:
        tab2_tree.insert("", tk.END, values=(r["roll_number"], r["name"], r["subject_code"], r["date"], r["time"], r["status"]))

    conn.close()

def get_attendance_by_student():
    conn = mysql.connector.connect(
        host='localhost',
        user='amit',
        password='12345678',
        database='Attendance_Management_System'
    )

    for item in tab3_tree.get_children():
        tab3_tree.delete(item)
        exit

    cursor = conn.cursor(dictionary=True)
    query = "SELECT attendance.roll_number, students.name, subject_code, date, time, status FROM attendance, students WHERE students.roll_number = attendance.roll_number AND 1=1"
    params = []
    if tab3_roll_entry.get():
        query += " AND attendance.roll_number = %s"
        params.append(tab3_roll_entry.get())
    if tab3_date_entry.get():
        query += " AND date = %s"
        params.append(tab3_date_entry.get())
    if tab3_time_entry.get():
        query += " AND time = %s"
        params.append(tab3_time_entry.get())
    if tab3_subject_name.get():
        query += " AND subject_code = %s"
        params.append(tab3_subject_name.get())
    
    cursor.execute(query, tuple(params))
    records = cursor.fetchall()

    for r in records:
        tab3_tree.insert("", tk.END, values=(r["roll_number"], r["name"], r["subject_code"], r["date"], r["time"], r["status"]))

    conn.close()


# Tkinter GUI setup
root = tk.Tk()
root.geometry("900x600")
root.configure(bg="#f0f0f0")

# Define fonts and styles
title_font = ("Arial", 16, "bold")
button_font = ("Arial", 12)
entry_font = ("Arial", 12)

# Add a title label
title_label = tk.Label(root, text="Attendance Management System", font=title_font, bg="#f0f0f0", fg="#333")
title_label.pack(pady=20)

#Notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

#create tabs
add_attendance = ttk.Frame(notebook)
subject = ttk.Frame(notebook)
student = ttk.Frame(notebook)

#add on notebook
notebook.add(add_attendance, text="Add Attendance")
notebook.add(subject, text="Subject")
notebook.add(student, text="Student")

#------------ tab 1 : add attendance ---------------------

#date entry
tk.Label(add_attendance, text="Date:").grid(row=0, column=0, padx=(100,0), pady=(25,0), sticky="e")
tab1_date_entry = tk.Entry(add_attendance, width=20)
tab1_date_entry.grid(row=0, column=1, padx=5, pady=(25,0))

# Time input
tk.Label(add_attendance, text="Time:").grid(row=0, column=2, padx=(100,0), pady=(25,0), sticky="e")
tab1_time_entry = tk.Entry(add_attendance, width=20)
tab1_time_entry.grid(row=0, column=3, padx=5, pady=(25,0))

# Subject code
tk.Label(add_attendance, text="Subject Code:").grid(row=1, column=0, padx=(100,0), pady=(25,0), sticky="e")
tab1_subject_code = ttk.Combobox(add_attendance, values= get_subject_codes(), state="readonly", width=18)
tab1_subject_code.grid(row=1, column=1, padx=5, pady=(25,0))

# File upload button
def upload_file():
    file_path = askopenfilename(title="Select File", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if file_path:
        tab1_file_label.config(text=file_path)


tk.Label(add_attendance, text="Upload File:").grid(row=1, column=2, padx=(100,0), pady=(25,0), sticky="e")
tab1_file_button = tk.Button(add_attendance, text="Choose File", command=upload_file)
tab1_file_button.grid(row=1, column=3, padx=5, pady=(25,0))
tab1_file_label = tk.Label(add_attendance, text="", fg="black")
tab1_file_label.grid(row=2, column=0, columnspan=4, padx=(100,0), pady=(25,0))

#submit button
tab1_submit_button = tk.Button(add_attendance, text="Submit", command = submit)
tab1_submit_button.grid(row=3, column=1, columnspan=4,pady=(25,0))

# table for status
tab1_columns = ("roll_no", "name", "attendance_status")
tab1_tree = ttk.Treeview(add_attendance, columns=tab1_columns, show="headings")
tab1_tree.heading("roll_no", text="Roll No")
tab1_tree.heading("name", text="Name")
tab1_tree.heading("attendance_status", text="Attendance Status")
tab1_tree.column("roll_no", width=100, anchor ="center")
tab1_tree.column("name", width=200, anchor ="center")
tab1_tree.column("attendance_status", width=150, anchor ="center")
tab1_tree.grid(row=4, column=1, sticky="nsew", padx=10, pady = (25,0), columnspan=4)

#------------ tab 2 : subject ----------------------

#date entry
tk.Label(subject, text="Date:").grid(row=0, column=0, padx=(100,0), pady=(25,0), sticky="e")
tab2_date_entry = tk.Entry(subject, width=20)
tab2_date_entry.grid(row=0, column=1, padx=5, pady=(25,0))

# Time input
tk.Label(subject, text="Time:").grid(row=0, column=2, padx=(100,0), pady=(25,0), sticky="e")
tab2_time_entry = tk.Entry(subject, width=20)
tab2_time_entry.grid(row=0, column=3, padx=5, pady=(25,0))

# Subject code
tk.Label(subject, text="Subject Code:").grid(row=1, column=0, padx=(100,0), pady=(25,0), sticky="e")
tab2_subject_name = ttk.Combobox(subject, values=get_subject_codes(), state="readonly", width=18)
tab2_subject_name.grid(row=1, column=1, padx=5, pady=(25,0))

#submit button
tab2_submit_button = tk.Button(subject, text="Submit", command = get_attendance_by_subject)
tab2_submit_button.grid(row=3, column=1, columnspan=4,pady=(25,0))

# table for status
tab2_columns = ("roll_no", "name","subject_code", "date", "time", "attendance_status")
tab2_tree = ttk.Treeview(subject, columns=tab2_columns, show="headings")
tab2_tree.heading("roll_no", text="Roll No")
tab2_tree.heading("name", text="Name")
tab2_tree.heading("subject_code", text="Subject Code")
tab2_tree.heading("date", text="Date")
tab2_tree.heading("time", text="Time")
tab2_tree.heading("attendance_status", text="Attendance Status")
tab2_tree.column("roll_no", width=100, anchor ="center")
tab2_tree.column("name", width=200, anchor ="center")
tab2_tree.column("subject_code", width=150, anchor ="center")
tab2_tree.column("date", width=100, anchor ="center")
tab2_tree.column("time", width=100, anchor ="center")
tab2_tree.column("attendance_status", width=150, anchor ="center")
tab2_tree.grid(row=4, column=0, sticky="nsew", padx=50, pady = (25,0), columnspan=4)
	
#------------ tab 3 : student ----------------------

#Roll number entry
tk.Label(student, text="Roll Number:").grid(row=0, column=0, padx=(100,0), pady=(25,0), sticky="e")
tab3_roll_entry = tk.Entry(student, width=20)
tab3_roll_entry.grid(row=0, column=1, padx=5, pady=(25,0))

#date entry
tk.Label(student, text="Date:").grid(row=1, column=0, padx=(100,0), pady=(25,0), sticky="e")
tab3_date_entry = tk.Entry(student, width=20)
tab3_date_entry.grid(row=1, column=1, padx=5, pady=(25,0))

# Time input
tk.Label(student, text="Time:").grid(row=1, column=2, padx=(100,0), pady=(25,0), sticky="e")
tab3_time_entry = tk.Entry(student, width=20)
tab3_time_entry.grid(row=1, column=3, padx=5, pady=(25,0))

# Subject code
tk.Label(student, text="Subject Code:").grid(row=0, column=2, padx=(100,0), pady=(25,0), sticky="e")
tab3_subject_name = ttk.Combobox(student, values=get_subject_codes(), state="readonly", width=18)
tab3_subject_name.grid(row=0, column=3, padx=5, pady=(25,0))

#submit button
tab3_submit_button = tk.Button(student, text="Submit", command=get_attendance_by_student)
tab3_submit_button.grid(row=3, column=1, columnspan=4,pady=(25,0))

# table for status
tab3_columns = ("roll_no", "name","subject_code", "date", "time", "attendance_status")
tab3_tree = ttk.Treeview(student, columns=tab3_columns, show="headings")
tab3_tree.heading("roll_no", text="Roll No")
tab3_tree.heading("name", text="Name")
tab3_tree.heading("subject_code", text="Subject Code")
tab3_tree.heading("date", text="Date")
tab3_tree.heading("time", text="Time")
tab3_tree.heading("attendance_status", text="Attendance Status")
tab3_tree.column("roll_no", width=100, anchor ="center")
tab3_tree.column("name", width=200, anchor ="center")
tab3_tree.column("subject_code", width=150, anchor ="center")
tab3_tree.column("date", width=100, anchor ="center")
tab3_tree.column("time", width=100, anchor ="center")
tab3_tree.column("attendance_status", width=150, anchor ="center")
tab3_tree.grid(row=4, column=0, sticky="nsew", padx=50, pady = (25,0), columnspan=4)

# Run the Tkinter main loop
root.mainloop()
