import tkinter as tk
from tkinter import filedialog
import cv2
import os
import pytesseract

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
            # print(f"Saved cell image: {cell_img_path}")

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
        
def browse_files():
    file_path = filedialog.askopenfilename()
    if file_path:
        path_var.set(file_path)

def submit():
    file_path = path_var.get()
    if file_path:
        roll_no = extract_text_from_image(file_path)
        output_folder = 'sign_images'
        extract_table_cells(file_path, output_folder)
        for r in roll_no:
            image_path1 = 'Student_signatures/'+r+'.png'
            image_path2 = 'sign_images/'+r+'.png'
            similarity_score = compare_signatures(image_path1, image_path2)
            if similarity_score >= 85 :
                print(r+" : Present")
            else:
                print(r+" : Absent")

root = tk.Tk()
root.title("Attendance Management System Using Image Processing")
root.geometry("500x200")
center_frame = tk.Frame(root)
center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
path_var = tk.StringVar()
path_entry = tk.Entry(center_frame, textvariable=path_var, width=50)
path_entry.grid(row=0, column=0, padx=10, pady=10, columnspan=3)
browse_button = tk.Button(center_frame, text="Browse", command=browse_files)
browse_button.grid(row=0, column=3, padx=10, pady=10)
submit_button = tk.Button(center_frame, text="Submit", command=submit)
submit_button.grid(row=1, column=1, padx=10, pady=10, columnspan=2)
root.mainloop()