from flask import Blueprint

from app.services.legacy import legacy

api_bp = Blueprint("api", __name__)


@api_bp.route("/get_visitor_questions")
def get_visitor_questions():
    return legacy.get_visitor_questions_route()


@api_bp.route("/get_daily_tasks")
def get_daily_tasks():
    return legacy.get_daily_tasks()


@api_bp.route("/save_daily_task", methods=["POST"])
def save_daily_task():
    return legacy.save_daily_task_route()


@api_bp.route("/delete_daily_task", methods=["POST"])
def delete_daily_task():
    return legacy.delete_daily_task_route()


@api_bp.route("/export_attendance")
def export_attendance():
    return legacy.export_attendance()


@api_bp.route("/export_visitors")
def export_visitors():
    return legacy.export_visitors()


@api_bp.route("/visitor_face")
def visitor_face():
    return legacy.visitor_face()


@api_bp.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    return legacy.mark_attendance()


@api_bp.route("/attendance_action", methods=["POST"])
def attendance_action():
    return legacy.attendance_action()


@api_bp.route("/admin_manual_checkout", methods=["POST"])
def admin_manual_checkout():
    return legacy.admin_manual_checkout()


@api_bp.route("/submit_visitor", methods=["POST"])
def submit_visitor():
    return legacy.submit_visitor()


@api_bp.route("/register_face", methods=["POST"])
def register_face():
    return legacy.register_face()


@api_bp.route("/get_attendance")
def get_attendance():
    return legacy.get_attendance()


@api_bp.route("/get_employee_attendance_history")
def get_employee_attendance_history():
    return legacy.get_employee_attendance_history()


@api_bp.route("/get_employee_tasks")
def get_employee_tasks():
    return legacy.get_employee_tasks_route()


@api_bp.route("/download_employee_attendance_csv")
def download_employee_attendance_csv():
    return legacy.download_employee_attendance_csv()


@api_bp.route("/get_visitors")
def get_visitors():
    return legacy.get_visitors()


@api_bp.route("/visitor_checkout", methods=["POST"])
def visitor_checkout():
    return legacy.visitor_checkout()
