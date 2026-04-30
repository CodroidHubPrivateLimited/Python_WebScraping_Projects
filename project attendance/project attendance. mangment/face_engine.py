import base64
import csv
import os
from datetime import datetime
from io import BytesIO

import face_recognition
import numpy as np
from PIL import Image

DATASET_DIR = "dataset"
ATTENDANCE_DIR = "instance"


class FaceEngine:
    def __init__(self):
        os.makedirs(DATASET_DIR, exist_ok=True)
        os.makedirs(ATTENDANCE_DIR, exist_ok=True)

    def _decode_data_url(self, image_data):
        if not image_data or "," not in image_data:
            raise ValueError("Image data is missing.")

        _, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        return np.array(image)

    def _extract_face_encoding(self, image_array):
        encodings = face_recognition.face_encodings(image_array)
        if not encodings:
            raise ValueError("No face detected. Please keep your face clear in the frame.")
        return encodings[0]

    def _build_image_path(self, user_id):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return os.path.join(DATASET_DIR, f"user_{user_id}_{timestamp}.jpg")

    def save_face_image(self, user_id, image_data):
        image_array = self._decode_data_url(image_data)
        self._extract_face_encoding(image_array)

        image_path = self._build_image_path(user_id)
        Image.fromarray(image_array).save(image_path, format="JPEG")
        return image_path.replace("\\", "/")

    def save_uploaded_face_image(self, user_id, uploaded_file):
        if not uploaded_file or not uploaded_file.filename:
            raise ValueError("Please choose an image to upload.")

        image = Image.open(uploaded_file.stream).convert("RGB")
        image_array = np.array(image)
        self._extract_face_encoding(image_array)

        image_path = self._build_image_path(user_id)
        image.save(image_path, format="JPEG")
        return image_path.replace("\\", "/")

    def compare_with_registered_face(self, registered_image_path, live_image_data, tolerance=0.45):
        if not registered_image_path or not os.path.exists(registered_image_path):
            return False, "Registered face image not found. Please sign up again."

        registered_image = face_recognition.load_image_file(registered_image_path)
        registered_encoding = self._extract_face_encoding(registered_image)

        live_image = self._decode_data_url(live_image_data)
        live_encoding = self._extract_face_encoding(live_image)

        matched = face_recognition.compare_faces(
            [registered_encoding], live_encoding, tolerance=tolerance
        )[0]

        if matched:
            return True, "Face matched successfully."

        return False, "Face did not match your registered student profile."

    def mark_attendance(self, user):
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(ATTENDANCE_DIR, f"attendance_{today}.csv")

        existing_rows = []
        already_marked = False

        if os.path.exists(file_path):
            with open(file_path, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing_rows.append(row)
                    if row.get("email") == user.email:
                        already_marked = True

        if already_marked:
            return False, "Attendance already marked for today."

        write_header = not os.path.exists(file_path)
        with open(file_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow(["student_id", "name", "email", "status", "timestamp"])
            writer.writerow(
                [
                    user.id,
                    user.name,
                    user.email,
                    "Present",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

        return True, f"Attendance marked for {user.name}."

    def _get_attendance_files(self):
        attendance_files = []

        for file_name in os.listdir(ATTENDANCE_DIR):
            if file_name.startswith("attendance_") and file_name.endswith(".csv"):
                attendance_files.append(file_name)

        return sorted(attendance_files)

    def get_student_day_wise_attendance(self, user):
        rows = []

        for file_name in self._get_attendance_files():
            attendance_date = file_name.replace("attendance_", "").replace(".csv", "")
            file_path = os.path.join(ATTENDANCE_DIR, file_name)
            matched_row = None

            with open(file_path, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get("email") == user.email:
                        matched_row = row
                        break

            row_date = datetime.strptime(attendance_date, "%Y-%m-%d")
            rows.append(
                {
                    "date": attendance_date,
                    "display_date": row_date.strftime("%d %b %Y"),
                    "month_key": row_date.strftime("%Y-%m"),
                    "month_label": row_date.strftime("%B %Y"),
                    "student_id": matched_row.get("student_id", user.id) if matched_row else user.id,
                    "name": matched_row.get("name", user.name) if matched_row else user.name,
                    "email": user.email,
                    "status": matched_row.get("status", "Present") if matched_row else "Absent",
                    "timestamp": matched_row.get("timestamp", "") if matched_row else "",
                }
            )

        rows.sort(key=lambda row: row["date"], reverse=True)
        return rows

    def get_student_stats(self, user):
        attendance_rows = self.get_student_day_wise_attendance(user)
        total_classes = len(attendance_rows)
        present = sum(1 for row in attendance_rows if row["status"] == "Present")
        absent = max(total_classes - present, 0)
        percentage = round((present / total_classes) * 100, 2) if total_classes else 0

        return {
            "total_classes": total_classes,
            "present": present,
            "absent": absent,
            "percentage": percentage,
        }

    def get_today_attendance(self):
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(ATTENDANCE_DIR, f"attendance_{today}.csv")
        rows = []

        if os.path.exists(file_path):
            with open(file_path, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                rows = list(reader)

        return rows

    def get_student_attendance_rows(self, user):
        return self.get_student_day_wise_attendance(user)

    def get_student_monthly_attendance(self, user):
        monthly_summary = []
        month_map = {}

        for row in self.get_student_day_wise_attendance(user):
            month_data = month_map.setdefault(
                row["month_key"],
                {
                    "month_key": row["month_key"],
                    "month_label": row["month_label"],
                    "total_classes": 0,
                    "present": 0,
                    "absent": 0,
                    "percentage": 0,
                    "days": [],
                },
            )

            month_data["total_classes"] += 1
            if row["status"] == "Present":
                month_data["present"] += 1
            else:
                month_data["absent"] += 1

            month_data["days"].append(
                {
                    "display_date": row["display_date"],
                    "status": row["status"],
                    "timestamp": row["timestamp"] or "-",
                }
            )

        for month_key in sorted(month_map.keys(), reverse=True):
            month_data = month_map[month_key]
            if month_data["total_classes"]:
                month_data["percentage"] = round(
                    (month_data["present"] / month_data["total_classes"]) * 100, 2
                )
            monthly_summary.append(month_data)

        return monthly_summary
