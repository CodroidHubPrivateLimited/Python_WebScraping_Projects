from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
from flask import send_from_directory
import importlib
import logging
import sys

# Configure logging to show output in terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()

app = Flask(__name__)

USERNAME = "vishal"
PASSWORD = "12345"
users = {}

STATIC_FOLDER = "data/static_data"
API_FOLDER = "data/api_data"

DYNAMIC_SCRAPER_FOLDER = "scrapers/dynamic_data"
STATIC_SCRAPER_FOLDER = "scrapers/static_data"

def run_dynamic_scrapers():
    if not os.path.exists(DYNAMIC_SCRAPER_FOLDER):
        print("Dynamic scraper folder not found")
        return

    for file in os.listdir(DYNAMIC_SCRAPER_FOLDER):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]

            module = importlib.import_module(
                f"scrapers.dynamic_data.{module_name}"
            )

            if hasattr(module, "run"):
                module.run()
                print(f"{module_name} dynamic scraper executed")

def run_static_scrapers():
    if not os.path.exists(STATIC_SCRAPER_FOLDER):
        print("Static scraper folder not found")
        return

    for file in os.listdir(STATIC_SCRAPER_FOLDER):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]

            module = importlib.import_module(
                f"scrapers.static_data.{module_name}"
            )

            if hasattr(module, "run"):
                module.run()
                print(f"{module_name} static scraper executed")

@app.route("/")
def index():
    return render_template("landing.html")

@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/journey")
def journey():
    return render_template("journey.html")

@app.route("/project")
def project():
    return render_template("project.html")

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

@app.route("/select")
def select_page():
    return render_template("select.html")

@app.route("/static-data")
def home_static():
    # Get scraper file names (without .py) from static_data scrapers folder
    if not os.path.exists(STATIC_SCRAPER_FOLDER):
        return "Static scraper folder not found"

    files = [f[:-3] for f in os.listdir(STATIC_SCRAPER_FOLDER) 
             if f.endswith(".py") and not f.startswith("__")]

    return render_template("files.html",
                           files=files,
                           data_type="static")

@app.route("/dynamic-data")
def home_api():
  
    if not os.path.exists(DYNAMIC_SCRAPER_FOLDER):
        return "Dynamic scraper folder not found"

    files = [f[:-3] for f in os.listdir(DYNAMIC_SCRAPER_FOLDER) 
             if f.endswith(".py") and not f.startswith("__")]

    return render_template("files.html",
                           files=files,
                           data_type="api")

def find_matching_scraper(data_type, filename):
    """Find the correct scraper module by matching filename with scraper files"""
    scraper_name = filename.replace(".csv", "").lower()
    
    if data_type == "static":
        scraper_folder = STATIC_SCRAPER_FOLDER
    else:
        scraper_folder = DYNAMIC_SCRAPER_FOLDER
    
    # Get all Python files in scraper folder
    scraper_files = [f[:-3] for f in os.listdir(scraper_folder) 
                    if f.endswith(".py") and not f.startswith("__")]
    
    # Try to find matching scraper (case-insensitive match)
    for scraper_file in scraper_files:
        # Remove -checkpoint from both for comparison
        sf_clean = scraper_file.lower().replace("-checkpoint", "")
        sn_clean = scraper_name.replace("-checkpoint", "")
        if sf_clean in sn_clean or sn_clean in sf_clean:
            return scraper_file
    
    # If no match found, return original name
    return filename.replace(".csv", "")

@app.route("/view/<data_type>/<filename>")
def view_file(data_type, filename):
    scraper_name = find_matching_scraper(data_type, filename)
    scraper_error = None
    scraper_executed = False

    if data_type == "static":
        scraper_path = f"scrapers.static_data.{scraper_name}"
        folder = STATIC_FOLDER
        files_page = "/static-data"
    else:
        scraper_path = f"scrapers.dynamic_data.{scraper_name}"
        folder = API_FOLDER
        files_page = "/dynamic-data"

    # First, run the scraper to generate CSV
    try:
        logger.info(f"Attempting to import: {scraper_path}")
        module = importlib.import_module(scraper_path)

        if hasattr(module, "run"):
            module.run()
            scraper_executed = True
            logger.info(f"{scraper_name} scraper executed successfully")
    except Exception as e:
        scraper_error = str(e)
        logger.info(f"Scraper error: {e}")

    # Now find the CSV file - look for files with pattern {name}_data.csv
    csv_filename = None
    file_path = None
    
    # Clean scraper name (remove -checkpoint)
    clean_name = scraper_name.lower().replace("-checkpoint", "")
    
    if os.path.exists(folder):
        csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]
        for f in csv_files:
            # Remove .csv and _data, then compare
            base_name = f.lower().replace(".csv", "").replace("_data", "")
            if base_name == clean_name:
                csv_filename = f
                file_path = os.path.join(folder, f)
                break

    if not file_path or not os.path.exists(file_path):
        return f"File Not Found<br>Scraper Error: {scraper_error if scraper_error else 'No CSV file generated'}<br>Expected path: {folder}/{clean_name}_data.csv"

    df = pd.read_csv(file_path)
    table = df.to_html(classes="table table-bordered", index=False)

    return render_template("view.html",
                           table=table,
                           filename=filename,
                           data_type=data_type,
                           files_page=files_page,
                           scraper_executed=scraper_executed,
                           scraper_error=scraper_error)


@app.route("/download/<data_type>/<filename>")
def download_file(data_type, filename):
    scraper_name = find_matching_scraper(data_type, filename)
    
    if data_type == "static":
        folder = STATIC_FOLDER
    else:
        folder = API_FOLDER

    # Find the CSV file
    csv_filename = None
    clean_name = scraper_name.lower().replace("-checkpoint", "")
    if os.path.exists(folder):
        csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]
        for f in csv_files:
            base_name = f.lower().replace(".csv", "").replace("_data", "")
            if base_name == clean_name:
                csv_filename = f
                break

    if not csv_filename:
        return "File not found"

    return send_from_directory(folder, csv_filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
