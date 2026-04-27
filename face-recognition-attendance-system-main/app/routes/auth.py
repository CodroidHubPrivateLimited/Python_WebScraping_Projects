from flask import Blueprint, jsonify, redirect, request, session, url_for
from werkzeug.security import check_password_hash

from app.services.legacy import legacy

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
def auth_login():
    payload = request.get_json(silent=True) or {}
    selected_role = legacy.get_selected_role(payload.get("role"))
    username = (payload.get("username") or "").strip().lower()
    password = (payload.get("password") or "").strip()

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required."}), 400

    session.clear()

    if selected_role == "admin":
        if username == legacy.ADMIN_USERNAME and password == legacy.ADMIN_PASSWORD:
            session["auth_role"] = "admin"
            session["auth_username"] = legacy.ADMIN_USERNAME
            session["auth_full_name"] = "Administrator"
            return jsonify({"status": "success", "redirect": url_for("pages.admin_dashboard")})
        return jsonify({"status": "error", "message": "Invalid admin credentials."}), 401

    if not legacy.is_mongo_available():
        return jsonify({"status": "error", "message": "MongoDB is not available. Start MongoDB and try again."}), 500

    account = legacy.get_employee_account_by_identifier(username)
    if not account or not check_password_hash(account.get("password") or "", password):
        return jsonify({"status": "error", "message": "Invalid employee credentials."}), 401

    session["auth_role"] = "employee"
    session["auth_username"] = account.get("username") or username
    session["auth_full_name"] = account.get("name") or username.title()
    session["auth_employee_id"] = account.get("employee_id") or ""
    return jsonify({"status": "success", "redirect": url_for("pages.employee")})


@auth_bp.route("/signup", methods=["POST"])
def auth_signup():
    payload = request.get_json(silent=True) or {}
    selected_role = legacy.get_selected_role(payload.get("role"))
    if selected_role != "employee":
        return jsonify({"status": "error", "message": "Only employees can sign up."}), 403

    full_name = (payload.get("full_name") or "").strip()
    employee_id = (payload.get("employee_id") or "").strip()
    department = (payload.get("department") or "General").strip() or "General"
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not full_name or not employee_id or not department or not email or not password:
        return jsonify({"status": "error", "message": "All fields are required."}), 400
    if len(password) < 4:
        return jsonify({"status": "error", "message": "Password must be at least 4 characters."}), 400

    success, message = legacy.create_employee_account(
        username="",
        password=password,
        full_name=full_name,
        employee_id=employee_id,
        email=email,
        department=department,
    )
    if not success:
        return jsonify({"status": "error", "message": message}), 400

    return jsonify(
        {
            "status": "success",
            "message": message,
            "redirect": url_for("pages.login", role="employee"),
        }
    )


@auth_bp.route("/change-password", methods=["POST"])
def change_password():
    if not legacy.login_required("employee"):
        return jsonify({"status": "error", "message": "Please log in as employee first."}), 401

    payload = request.get_json(silent=True) or {}
    current_password = payload.get("current_password") or ""
    new_password = payload.get("new_password") or ""

    if not current_password or not new_password:
        return jsonify({"status": "error", "message": "Both password fields are required."}), 400
    if len(new_password) < 4:
        return jsonify({"status": "error", "message": "New password must be at least 4 characters."}), 400

    success, message = legacy.update_employee_password(session.get("auth_username"), current_password, new_password)
    if not success:
        return jsonify({"status": "error", "message": message}), 400

    return jsonify({"status": "success", "message": message})


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("pages.role_selection"))
