import cv2
import os
from deepface import DeepFace
import openpyxl 
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from threading import Thread
import traceback
import pygame  # For sound feedback

# Initialize sound
pygame.mixer.init()

def play_sound(file):
    try:
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Error playing sound: {e}")

# Initialize Excel for attendance tracking
def initialize_excel(filename):
    try:
        if not os.path.exists(filename):
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Attendance"
            sheet.append(["Name", "Date", "Time", "Status"])
            workbook.save(filename)
            print(f"Excel file created at {filename}")
        else:
            print(f"Excel file already exists at {filename}")
    except Exception as e:
        print(f"Error initializing Excel file: {e}")
        traceback.print_exc()

def save_to_excel(filename, row):
    try:
        workbook = openpyxl.load_workbook(filename)
        sheet = workbook["Attendance"]
        sheet.append(row)
        workbook.save(filename)
        print(f"Row saved successfully: {row}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        traceback.print_exc()

# Paths for Excel and reference images
attendance_filename = "attendance.xlsx"
initialize_excel(attendance_filename)

reference_images_path = "./Images"
if not os.path.exists(reference_images_path):
    print(f"Note: {reference_images_path} empty. Register users first.")
else:
    # Load valid reference images (skip corrupt/small)
    reference_images = {}
    try:
        valid_count = 0
        for file in os.listdir(reference_images_path):
            filepath = os.path.join(reference_images_path, file)
            if (file.endswith(".jpg") or file.endswith(".png")) and os.path.getsize(filepath) > 1000:
                name = os.path.splitext(file)[0].replace("_", " ")
                reference_images[name] = filepath
                valid_count += 1
        print(f"Loaded {valid_count} valid reference images: {list(reference_images.keys())}")
    except Exception as e:
        print(f"Error loading images: {e}")

# Global vars
attendance_dict = {}

def register_user():
    name = simpledialog.askstring("Register", "Enter name:")
    if name:
        id_input = simpledialog.askstring("Register", "Enter Employee ID:")
        if id_input:
            # Launch register
            import subprocess
            subprocess.run(["python", "register_face.py"])
            messagebox.showinfo("Register", f"Registered {name} (ID: {id_input}). Added photos to ./Images/")
        else:
            messagebox.showwarning("Cancel", "ID cancelled.")

# Start attendance function
def start_attendance(status_label, attendee_list):
    global attendance_dict
    attendance_dict.clear()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        status_label.config(text="Error: Camera access denied.", fg="red")
        return

    status_label.config(text="Attendance running. Face match → log.", fg="blue")
    while True:
        ret, frame = cap.read()
        if not ret:
            status_label.config(text="Error: No frame.", fg="red")
            break

        resized_frame = cv2.resize(frame, (640, 480))

        try:
            results = DeepFace.find(
                img_path=resized_frame,
                db_path=reference_images_path,
                enforce_detection=False,
                detector_backend="opencv",
            )

            if len(results) > 0:
                match = results[0].iloc[0]
                full_path = match["identity"]
                name = os.path.basename(full_path).split(".")[0].replace("_", " ")

                if name not in attendance_dict:
                    attendance_dict[name] = True
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S").split()
                    save_to_excel(attendance_filename, [name, timestamp[0], timestamp[1], "Present"])
                    play_sound("./sounds/feedback.wav")
                    attendee_list.insert(tk.END, f"{name} Present at {timestamp[1]}\n")
                    status_label.config(text=f"Attendance: {name}", fg="green")

                cv2.putText(frame, name, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "No match", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        except Exception as e:
            cv2.putText(frame, "Processing...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            print(f"Recog error: {e}")

        cv2.imshow("Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    status_label.config(text="Stopped.", fg="blue")

def start_attendance_thread(status_label, attendee_list):
    Thread(target=start_attendance, args=(status_label, attendee_list), daemon=True).start()

# GUI
root = tk.Tk()
root.title("Employee Face Recognition Attendance")
root.geometry("900x700")
root.config(bg="#f0f0f0")

# Header
tk.Label(root, text="Face Recognition Attendance System", font=("Arial", 24, "bold"), bg="#4CAF50", fg="white").pack(pady=20)

status_label = tk.Label(root, text="Ready. Register users first!", font=("Arial", 14), bg="#f0f0f0")
status_label.pack(pady=10)

# List
tk.Label(root, text="Attendance Log:", font=("Arial", 14)).pack(anchor="w", padx=20)
attendee_list = scrolledtext.ScrolledText(root, height=12, font=("Arial", 11), wrap=tk.WORD)
attendee_list.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=20)

ttk.Button(btn_frame, text="Register New Employee", command=register_user, width=20).pack(side=tk.LEFT, padx=10)
ttk.Button(btn_frame, text="Start Attendance", command=lambda: start_attendance_thread(status_label, attendee_list), width=20).pack(side=tk.LEFT, padx=10)
ttk.Button(btn_frame, text="Exit", command=root.quit, width=20).pack(side=tk.LEFT, padx=10)

# Footer
tk.Label(root, text="Register → Capture photos → Attendance auto-marks", font=("Arial", 10), fg="gray").pack(side=tk.BOTTOM, pady=10)

root.mainloop()
