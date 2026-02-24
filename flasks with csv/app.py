from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
from flask import send_from_directory

app = Flask(__name__)

USERNAME = "vishal"
PASSWORD = "12345"
# Dummy user storage (temporary)
users = {}

STATIC_FOLDER = "data/static_data"
API_FOLDER = "data/api_data"


# ================= INDEX =================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users:
            return "User already exists!"

        users[username] = password
        return redirect(url_for("login"))

    return render_template("signup.html")


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == USERNAME and password == PASSWORD:
            return redirect(url_for("select_page"))
        else:
            return "Invalid Username or Password"

    return render_template("login.html")


# ================= SELECT PAGE =================
@app.route("/select")
def select_page():
    return render_template("select.html")


# ================= STATIC FILE LIST =================
@app.route("/static-data")
def home_static():
    if not os.path.exists(STATIC_FOLDER):
        return "Static folder not found"

    files = [f for f in os.listdir(STATIC_FOLDER) if f.endswith(".csv")]

    return render_template("files.html",
                           files=files,
                           data_type="static")


# ================= DYNAMIC FILE LIST =================
@app.route("/dynamic-data")
def home_api():
    if not os.path.exists(API_FOLDER):
        return "API folder not found"

    files = [f for f in os.listdir(API_FOLDER) if f.endswith(".csv")]

    return render_template("files.html",
                           files=files,
                           data_type="api")



# ================= VIEW DATA PAGE =================
@app.route("/view/<data_type>/<filename>")
def view_file(data_type, filename):

    if data_type == "static":
        folder = STATIC_FOLDER
        files_page = "/static-data"
    else:
        folder = API_FOLDER
        files_page="/dynamic-data"

    file_path = os.path.join(folder, filename)

    if not os.path.exists(file_path):
        return "File Not Found"

    df = pd.read_csv(file_path)
    table = df.to_html(classes="table", index=False)

    return render_template("view.html",
                           table=table,
                           filename=filename,
                           data_type=data_type,
                           files_page=files_page )

# ================= DOWNLOAD CSV =================
@app.route("/download/<data_type>/<filename>")
def download_file(data_type, filename):

    if data_type == "static":
        folder = STATIC_FOLDER
    else:
        folder = API_FOLDER

    return send_from_directory(folder, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)