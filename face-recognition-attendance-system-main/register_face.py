import cv2
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
import time

def register_face():
    root = tk.Tk()
    root.withdraw()  # Hide main window

    name = simpledialog.askstring("Register New User", "Enter name (e.g. hp):")
    if not name:
        messagebox.showerror("Error", "Name required!")
        return

    # Sanitize name for filename
    safe_name = ''.join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    images_dir = "./Images"
    os.makedirs(images_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Camera not accessible!")
        return

    print(f"Capture 5 photos for {name}. Press 'c' to capture, 'q' to quit.")
    messagebox.showinfo("Capture", f"Position face. Press 'c' to capture (5 times), 'q' to finish.")

    count = 0
    while count < 5:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.putText(frame, f"Capture {count+1}/5 - Press 'c'", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow(f"Register {name}", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            filename = f"{safe_name}_{count+1}.jpg"
            filepath = os.path.join(images_dir, filename)
            cv2.imwrite(filepath, frame)
            print(f"Saved {filepath}")
            count += 1
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if count > 0:
        messagebox.showinfo("Success", f"{count} photos saved for {name}!")
    else:
        messagebox.showwarning("Warning", "No photos saved.")

if __name__ == '__main__':
    register_face()
