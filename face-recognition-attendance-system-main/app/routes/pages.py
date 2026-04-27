from flask import Blueprint, redirect, render_template, request, url_for

from app.services.legacy import legacy

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def role_selection():
    return render_template("auth/role_selection.html")


@pages_bp.route("/admin/dashboard")
@pages_bp.route("/index")
def admin_dashboard():
    if not legacy.login_required("admin"):
        return redirect(url_for("pages.login", role="admin"))
    return render_template("admin/dashboard.html")


@pages_bp.route("/employee")
def employee():
    if not legacy.login_required("employee"):
        return redirect(url_for("pages.login", role="employee"))
    return render_template("user/employee.html", current_user=legacy.get_current_user())


@pages_bp.route("/employee_attendance_history")
def employee_attendance_history():
    if not legacy.login_required("employee"):
        return redirect(url_for("pages.login", role="employee"))
    return render_template("user/attendance_history.html", current_user=legacy.get_current_user())


@pages_bp.route("/user_tasks")
def user_tasks():
    if not legacy.login_required("employee"):
        return redirect(url_for("pages.login", role="employee"))
    current_user = legacy.get_current_user()
    return render_template(
        "user/user_tasks.html",
        current_user=current_user,
        tasks=legacy.get_employee_tasks(current_user=current_user),
    )


@pages_bp.route("/employee_profile")
def employee_profile():
    if not legacy.login_required("employee"):
        return redirect(url_for("pages.login", role="employee"))
    current_user = legacy.get_current_user()
    return render_template(
        "user/employee_profile.html",
        current_user=current_user,
        employee_profile=legacy.get_employee_profile_context(current_user),
    )


@pages_bp.route("/login")
def login():
    return render_template(
        "auth/login.html",
        selected_role=legacy.get_selected_role(request.args.get("role")),
    )


@pages_bp.route("/signup")
def signup():
    selected_role = legacy.get_selected_role(request.args.get("role"))
    if selected_role != "employee":
        return redirect(url_for("pages.login", role="employee"))
    return render_template("auth/signup.html", selected_role=selected_role)


@pages_bp.route("/new_register")
def new_register():
    if not legacy.login_required("admin"):
        return redirect(url_for("pages.login", role="admin"))
    return render_template("admin/new_register.html")


@pages_bp.route("/attendance_log")
def attendance_log():
    if not legacy.login_required("admin"):
        return redirect(url_for("pages.login", role="admin"))
    return render_template("admin/attendance_log.html")


@pages_bp.route("/visitor")
def visitor_log():
    if not legacy.login_required("admin"):
        return redirect(url_for("pages.login", role="admin"))
    return render_template("admin/visitor.html")


@pages_bp.route("/daily_task")
def daily_task():
    if not legacy.login_required("admin"):
        return redirect(url_for("pages.login", role="admin"))
    return render_template("admin/daily_task.html")


@pages_bp.route("/logout")
def legacy_logout_alias():
    return redirect(url_for("auth.logout"))
