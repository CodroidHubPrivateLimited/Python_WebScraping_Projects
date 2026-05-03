import csv
import os
from datetime import datetime
from io import BytesIO, StringIO

from flask import Flask, flash, redirect, render_template, request, send_file, send_from_directory, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from werkzeug.security import check_password_hash, generate_password_hash

from face_engine import FaceEngine

engine = FaceEngine()
app = Flask(__name__)
app.secret_key = "secret123"

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    face_image = db.Column(db.String(255))


class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    student_email = db.Column(db.String(100), nullable=False)
    from_date = db.Column(db.String(20), nullable=False)
    to_date = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    created_at = db.Column(db.String(30), nullable=False, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    student_email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    teacher_reply = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    created_at = db.Column(db.String(30), nullable=False, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at = db.Column(db.String(30), nullable=False, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def ensure_schema():
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("user")} if inspector.has_table("user") else set()

    if "face_image" not in columns and inspector.has_table("user"):
        db.session.execute(text("ALTER TABLE user ADD COLUMN face_image VARCHAR(255)"))
        db.session.commit()


with app.app_context():
    db.create_all()
    ensure_schema()

def remove_student_attendance_records(student_email):
    attendance_dir = "instance"
    if not os.path.exists(attendance_dir):
        return

    for file_name in os.listdir(attendance_dir):
        if not file_name.startswith("attendance_") or not file_name.endswith(".csv"):
            continue

        file_path = os.path.join(attendance_dir, file_name)
        with open(file_path, newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

        filtered_rows = [row for row in rows if row.get("email") != student_email]
        if len(filtered_rows) == len(rows):
            continue

        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["student_id", "name", "email", "status", "timestamp"],
            )
            writer.writeheader()
            writer.writerows(filtered_rows)


@app.route("/dataset/<path:filename>")
def dataset_file(filename):
    return send_from_directory("dataset", filename)


@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]
        face_image_data = request.form.get("face_image_data", "")

        TEACHER_ADMIN_CODE = "admin842792"
        if role == "teacher":
            entered_code = request.form.get("admin_code", "").strip()
            if entered_code != TEACHER_ADMIN_CODE:
                flash("Invalid admin code. Teacher signup not allowed.")
                return redirect(url_for("signup"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists!")
            return redirect(url_for("signup"))

        if role == "student" and not face_image_data:
            flash("Student signup requires a face photo.")
            return redirect(url_for("signup"))

        new_user = User(name=name, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        try:
            if role == "student":
                new_user.face_image = engine.save_face_image(new_user.id, face_image_data)
                db.session.commit()
        except Exception as exc:
            if new_user.face_image and os.path.exists(new_user.face_image):
                os.remove(new_user.face_image)
            db.session.delete(new_user)
            db.session.commit()
            flash(str(exc))
            return redirect(url_for("signup"))

        flash("Signup successful! Please login.")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user"] = user.name
            session["email"] = user.email
            session["role"] = user.role

            if user.role == "teacher":
                return redirect(url_for("teacher"))
            return redirect(url_for("student"))

        flash("Invalid email or password")

    return render_template("login.html")


@app.route("/student")
def student():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    stats = engine.get_student_stats(user)
    monthly_attendance = engine.get_student_monthly_attendance(user)
    leave_requests = (
        LeaveRequest.query.filter_by(student_id=user.id)
        .order_by(LeaveRequest.id.desc())
        .all()
    )
    complaints = (
        Complaint.query.filter_by(student_id=user.id)
        .order_by(Complaint.id.desc())
        .all()
    )
    return render_template(
        "student.html",
        user=user,
        name=user.name,
        stats=stats,
        has_face=bool(user.face_image),
        monthly_attendance=monthly_attendance,
        leave_requests=leave_requests,
        complaints=complaints,
    )

@app.route("/teacher/student/<int:student_id>/attendance/download")
def teacher_download_student_attendance(student_id):
    if "user_id" not in session or session.get("role") != "teacher":
        return redirect(url_for("login"))

    student = db.session.get(User, student_id)

    if not student or student.role != "student":
        flash("Student not found")
        return redirect(url_for("teacher"))

    rows = engine.get_student_attendance_rows(student)

    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["date", "student_id", "name", "email", "status", "timestamp"])

    for row in rows:
        writer.writerow([
            row["date"],
            row["student_id"],
            row["name"],
            row["email"],
            row["status"],
            row["timestamp"],
        ])

    buffer = BytesIO(csv_buffer.getvalue().encode("utf-8"))
    safe_name = student.name.strip().replace(" ", "_").lower() or "student"

    return send_file(
        buffer,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{safe_name}_attendance.csv",
    )

@app.route("/student/leave/apply", methods=["POST"])
def apply_leave():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    from_date = request.form.get("from_date", "").strip()
    to_date = request.form.get("to_date", "").strip()
    reason = request.form.get("reason", "").strip()

    if not from_date or not to_date or not reason:
        flash("Please fill all leave request fields.")
        return redirect(url_for("student"))

    if from_date > to_date:
        flash("Leave start date cannot be after end date.")
        return redirect(url_for("student"))

    leave_request = LeaveRequest(
        student_id=user.id,
        student_name=user.name,
        student_email=user.email,
        from_date=from_date,
        to_date=to_date,
        reason=reason,
        status="Pending",
    )
    db.session.add(leave_request)
    db.session.commit()

    flash("Leave request submitted successfully.")
    return redirect(url_for("student"))


@app.route("/student/photo/update", methods=["POST"])
def update_student_photo():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    uploaded_file = request.files.get("student_photo")
    if not uploaded_file:
        flash("Please choose a student photo to upload.")
        return redirect(url_for("student"))

    try:
        old_face_image = user.face_image
        user.face_image = engine.save_uploaded_face_image(user.id, uploaded_file)
        db.session.commit()
        if old_face_image and old_face_image != user.face_image and os.path.exists(old_face_image):
            os.remove(old_face_image)
        flash("Student photo updated successfully.")
    except Exception as exc:
        flash(str(exc))

    return redirect(url_for("student"))


@app.route("/student/complaint/submit", methods=["POST"])
def submit_complaint():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    message = request.form.get("message", "").strip()
    if not message:
        flash("Please write your complaint before sending.")
        return redirect(url_for("student"))

    complaint = Complaint(
        student_id=user.id,
        student_name=user.name,
        student_email=user.email,
        message=message,
        status="Pending",
    )
    db.session.add(complaint)
    db.session.commit()

    flash("Complaint sent to teacher successfully.")
    return redirect(url_for("student"))


@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        live_face_image = request.form.get("attendance_face_data", "")

        if not live_face_image:
            flash("Please capture your face before marking attendance.")
            return redirect(url_for("attendance"))

        try:
            matched, message = engine.compare_with_registered_face(user.face_image, live_face_image)
            if not matched:
                flash(message)
                return redirect(url_for("attendance"))

            _, attendance_message = engine.mark_attendance(user)
            flash(attendance_message)
            return redirect(url_for("student"))
        except Exception as exc:
            flash(str(exc))
            return redirect(url_for("attendance"))

    return render_template("attendance.html", name=user.name)

@app.route("/student/complaint/delete/<int:complaint_id>", methods=["POST"])
def delete_complaint(complaint_id):
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    complaint = db.session.get(Complaint, complaint_id)

    if not complaint:
        flash("Complaint not found")
        return redirect(url_for("student"))

    if complaint.student_id != user.id:
        flash("Unauthorized action")
        return redirect(url_for("student"))

    if complaint.status.lower() != "pending":
        flash("Only pending complaints can be deleted")
        return redirect(url_for("student"))

    db.session.delete(complaint)
    db.session.commit()

    flash("Complaint deleted successfully")
    return redirect(url_for("student"))

@app.route("/student/attendance/download")
def download_student_attendance():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    rows = engine.get_student_attendance_rows(user)
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["date", "student_id", "name", "email", "status", "timestamp"])

    for row in rows:
        writer.writerow(
            [
                row["date"],
                row["student_id"],
                row["name"],
                row["email"],
                row["status"],
                row["timestamp"],
            ]
        )

    buffer = BytesIO(csv_buffer.getvalue().encode("utf-8"))
    safe_name = user.name.strip().replace(" ", "_").lower() or "student"

    return send_file(
        buffer,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{safe_name}_attendance.csv",
    )


@app.route("/teacher")
def teacher():
    if "user_id" not in session or session.get("role") != "teacher":
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    students = User.query.filter_by(role="student").all()
    today_attendance = engine.get_today_attendance()
    leave_requests = LeaveRequest.query.order_by(LeaveRequest.id.desc()).all()
    complaints = Complaint.query.order_by(Complaint.id.desc()).all()
    return render_template(
        "teacher.html",
        students=students,
        name=user.name,
        today_attendance=today_attendance,
        leave_requests=leave_requests,
        complaints=complaints,
    )


@app.route("/teacher/student/<int:student_id>/delete", methods=["POST"])
def delete_student(student_id):
    if "user_id" not in session or session.get("role") != "teacher":
        return redirect(url_for("login"))

    student = db.session.get(User, student_id)
    if not student or student.role != "student":
        flash("Student not found.")
        return redirect(url_for("teacher"))

    student_email = student.email
    student_face_image = student.face_image

    LeaveRequest.query.filter_by(student_id=student.id).delete()
    Complaint.query.filter_by(student_id=student.id).delete()
    db.session.delete(student)
    db.session.commit()

    remove_student_attendance_records(student_email)

    if student_face_image and os.path.exists(student_face_image):
        os.remove(student_face_image)

    flash("Student removed successfully.")
    return redirect(url_for("teacher"))


@app.route("/teacher/leave/<int:leave_id>/<action>", methods=["POST"])
def update_leave_status(leave_id, action):
    if "user_id" not in session or session.get("role") != "teacher":
        return redirect(url_for("login"))

    leave_request = db.session.get(LeaveRequest, leave_id)
    if not leave_request:
        flash("Leave request not found.")
        return redirect(url_for("teacher"))

    if action == "approve":
        leave_request.status = "Approved"
        flash("Leave request approved.")
    elif action == "reject":
        leave_request.status = "Rejected"
        flash("Leave request rejected.")
    else:
        flash("Invalid leave action.")
        return redirect(url_for("teacher"))

    db.session.commit()
    return redirect(url_for("teacher"))


@app.route("/teacher/complaint/<int:complaint_id>", methods=["POST"])
def update_complaint(complaint_id):
    if "user_id" not in session or session.get("role") != "teacher":
        return redirect(url_for("login"))

    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        flash("Complaint not found.")
        return redirect(url_for("teacher"))

    teacher_reply = request.form.get("teacher_reply", "").strip()
    action = request.form.get("action", "").strip()

    if action in {"reply", "solve"} and not teacher_reply:
        flash("Please write a reply before updating complaint status.")
        return redirect(url_for("teacher"))

    complaint.teacher_reply = teacher_reply or complaint.teacher_reply
    complaint.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if action == "reply":
        complaint.status = "Replied"
        flash("Complaint replied successfully.")
    elif action == "solve":
        complaint.status = "Solved"
        flash("Complaint marked as solved.")
    else:
        flash("Invalid complaint action.")
        return redirect(url_for("teacher"))

    db.session.commit()
    return redirect(url_for("teacher"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/student/leave/delete/<int:leave_id>", methods=["POST"])
def delete_leave(leave_id):
    try:
        if "user_id" not in session or session.get("role") != "student":
            return redirect(url_for("login"))

        user = db.session.get(User, session["user_id"])
        leave = db.session.get(LeaveRequest, leave_id)

        if not leave:
            flash("Leave not found")
            return redirect(url_for("student"))

        if leave.student_id != user.id:
            flash("Unauthorized action")
            return redirect(url_for("student"))

        if leave.status.lower() != "pending":
            flash("Only pending leave can be cancelled")
            return redirect(url_for("student"))

        db.session.delete(leave)
        db.session.commit()

        flash("Leave deleted successfully")
        return redirect(url_for("student"))

    except Exception as e:
        print("ERROR:", e)   
        return "Something broke. Check terminal."
    
@app.route("/student/profile/upload", methods=["POST"])
def upload_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    file = request.files.get("profile_pic")

    if not file:
        flash("Select image first")
        return redirect(url_for("student"))

    # create folder
    os.makedirs("static/profile", exist_ok=True)

    # fixed filename (overwrite)
    filename = f"user_{user_id}.png"
    filepath = os.path.join("static/profile", filename)

    file.save(filepath)

    flash("Profile photo updated")
    return redirect(url_for("student"))
    
if __name__ == "__main__":
    app.run(debug=True)
