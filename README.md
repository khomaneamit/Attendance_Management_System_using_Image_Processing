# Overview
This Python-based program automates the attendance management process by using image processing techniques to detect and compare student signatures from tabular images. The system extracts roll numbers from the input image, detects student signatures, compares them with the stored signatures, and determines whether the student is present or absent based on the similarity score.

The core technologies used in this project include OpenCV, Tesseract OCR, and Tkinter for building the graphical user interface (GUI).

# Features
Signature Detection and Comparison: Automatically identifies student signatures from the table in the input image and compares them with stored signatures using feature matching.
OCR Roll Number Extraction: Utilizes Tesseract OCR to extract roll numbers from the image.
GUI: Provides a simple and intuitive GUI using Tkinter for file browsing and displaying attendance results.
Image Processing: Preprocesses images to extract keypoints and descriptors for accurate comparison of student signatures.
Flexible Attendance Criteria: Compares signatures and marks students as present if the similarity score exceeds a defined threshold (default: 85%).

# Requirements
Python 3.x
OpenCV
pytesseract
Tkinter (usually comes with Python)
Tesseract-OCR installed on your system (required for OCR functionality)

# Python Libraries
Install the required libraries using pip:
pip install opencv-python pytesseract

Tesseract Installation
Windows: Download and install Tesseract OCR and add it to your system path.
Linux/Mac: Install using your package manager.
Example for Ubuntu:
sudo apt-get install tesseract-ocr

# Usage
Place Stored Signatures: Ensure that stored student signatures are placed in the Student_signatures/ directory. Each signature image should be named using the student's roll number (e.g., 12345678.png).

Run the Program:
You can run the program directly from the terminal or IDE:
python attendance.py
Select Input Image: Use the "Browse" button in the GUI to select the input image containing the table of roll numbers and signatures.

Process Image: Click "Submit" to process the image and compare the signatures.

View Results: The program will display whether each student is "Present" or "Absent" based on the similarity of their signatures.

# Functionality Details
1. load_and_preprocess_image(image_path)
Loads the image from the given path, converts it to grayscale, and resizes it for uniformity in further processing.

2. detect_and_compute_keypoints(image)
Detects ORB (Oriented FAST and Rotated BRIEF) keypoints and computes descriptors for the given image.

3. match_descriptors(des1, des2)
Uses a Brute-Force Matcher to find matches between the descriptors of the stored and detected signatures.

4. calculate_similarity(matches)
Calculates a similarity score based on the average distance of the matched keypoints.

5. extract_table_cells(image_path, output_folder)
Extracts individual cells from the input image, focusing on detecting signature regions.

6. extract_text_from_image(image_path)
Extracts roll numbers from the image using Tesseract OCR.

7. compare_signatures(image_path1, image_path2)
Compares the extracted signature with the stored signature and returns a similarity score.

8. is_sign(img)
Detects whether the given image contains the word "sign," which helps locate the signature region in the table.

9. GUI Components
Browse Button: Opens a file dialog to select the input image.
Submit Button: Initiates the image processing, signature comparison, and displays attendance results.

# Directory Structure
attendance_management/
│
├── attendance.py               # Main program file
├── Student_signatures/          # Directory containing stored signature images
├── sign_images/                 # Directory where detected signature images are saved temporarily
└── README.md                    # This README file

# Example
Input image containing a table of roll numbers and signatures.
Signature images for each student are stored in the Student_signatures folder.
The program outputs the attendance status as "Present" or "Absent" based on signature similarity.

# Troubleshooting
Tesseract Not Found: Ensure that Tesseract-OCR is installed and added to your system path.
Image Not Detected: Verify that the input image is in the correct format and contains clear roll numbers and signatures.
Low Similarity Score: Adjust the image preprocessing steps (like resizing or filtering) if the similarity scores are consistently low.
