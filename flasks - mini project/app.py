from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
from flask import send_from_directory
import importlib
import logging
import sys
import mysql.connector
from mysql.connector import Error
import json

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

# MySQL Database Configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'Vishal92919511',
    'database': 'ana'
}

# Hardcoded fallback credentials (for testing if DB is unavailable)
USERNAME = "vishal"
PASSWORD = "12345"
users = {}


def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.info(f"Database connection error: {e}")
        return None


def init_database():
    """Initialize database and create users table if it doesn't exist"""
    try:
        # First connect without database to create it if needed
        init_config = DB_CONFIG.copy()
        init_config.pop('database', None)
        connection = mysql.connector.connect(**init_config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            # Create database if not exists
            cursor.execute("CREATE DATABASE IF NOT EXISTS ana")
            cursor.execute("USE ana")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check if admin user exists, if not create default
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES ('admin', 'admin123')"
                )
                logger.info("Default admin user created")
            
            connection.commit()
            cursor.close()
            connection.close()
            logger.info("Database initialized successfully")
    except Error as e:
        logger.info(f"Database initialization error: {e}")


def authenticate_user(username, password):
    """Authenticate user against MySQL database"""
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username, password)
            )
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            return user is not None
        else:
            # Fallback to hardcoded credentials if database unavailable
            logger.info("Using fallback authentication")
            return username == USERNAME and password == PASSWORD
    except Error as e:
        logger.info(f"Authentication error: {e}")
        # Fallback to hardcoded credentials
        return username == USERNAME and password == PASSWORD

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

@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/journey")
def journey():
    return render_template("journey.html")

@app.route("/journey/problem-scoping")
def problem_scoping():
    return render_template("problem_scoping.html")

@app.route("/journey/data-exploration")
def data_exploration():
    return render_template("data_exploration.html")

@app.route("/csv-data")
def csv_data_page():
    folder = "data/csv_data"
    if not os.path.exists(folder):
        return "CSV data folder not found"
    
    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    return render_template("csv_files.html", files=files, folder=folder)

@app.route("/power-bi")
def power_bi_page():
    folder = "data/power_bi"
    if not os.path.exists(folder):
        return "Power BI folder not found"
    
    files = [f for f in os.listdir(folder) if f.endswith(".pbix")]
    return render_template("powerbi_files.html", files=files, folder=folder)

@app.route("/img/<filename>")
def serve_image(filename):
    """Serve images from data/img folder"""
    return send_from_directory("data/img", filename)

@app.route("/download-csv/<filename>")
def download_csv(filename):
    return send_from_directory("data/csv_data", filename, as_attachment=True)

@app.route("/view-csv/<filename>")
def view_csv(filename):
    """Display CSV file data in a table"""
    folder = "data/csv_data"
    file_path = os.path.join(folder, filename)
    
    if not os.path.exists(file_path):
        return "File not found"
    
    try:
        df = pd.read_csv(file_path)
        table = df.to_html(classes="table table-bordered", index=False)
        
        return render_template("view.html",
                               table=table,
                               filename=filename,
                               data_type="csv",
                               files_page="/csv-data",
                               scraper_executed=False,
                               scraper_error=None)
    except Exception as e:
        return f"Error reading CSV file: {str(e)}"

@app.route("/download-pbix/<filename>")
def download_pbix(filename):
    return send_from_directory("data/power_bi", filename, as_attachment=True)

@app.route("/view-pbix/<filename>")
def view_pbix(filename):
    folder = "data/power_bi"
    file_path = os.path.join(folder, filename)
    if not os.path.exists(file_path):
        return "File not found"
    file_size = os.path.getsize(file_path)
    file_size_mb = round(file_size / (1024 * 1024), 2)
    
    # Load embed config
    embed_config_path = os.path.join(folder, "embed_config.json")
    embed_code = None
    if os.path.exists(embed_config_path):
        with open(embed_config_path, 'r') as f:
            embed_config = json.load(f)
            embed_code = embed_config.get(filename)
    
    # Load CSV mapping and data
    csv_mapping_path = os.path.join(folder, "pbix_csv_mapping.json")
    csv_table = None
    image_filename = None
    if os.path.exists(csv_mapping_path):
        with open(csv_mapping_path, 'r') as f:
            csv_mapping = json.load(f)
            csv_filename = csv_mapping.get(filename)
            # Check if it's an image file (from img folder) or CSV file
            if csv_filename:
                image_path = os.path.join("data/img", csv_filename)
                csv_file_path = os.path.join("data/csv_data", csv_filename)
                if os.path.exists(image_path):
                    # It's an image file
                    image_filename = csv_filename
                elif os.path.exists(csv_file_path):
                    # It's a CSV file
                    try:
                        df = pd.read_csv(csv_file_path)
                        csv_table = df.to_html(classes="table table-bordered", index=False)
                    except Exception as e:
                        logger.info(f"Error reading CSV: {e}")
    
    return render_template("powerbi_view.html", filename=filename, file_size=file_size_mb, files_page="/power-bi", embed_code=embed_code, csv_table=csv_table, image_filename=image_filename)

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

        if authenticate_user(username, password):
            return redirect(url_for("select_page"))
        else:
            return render_template("login.html", error="Invalid Username or Password")

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
