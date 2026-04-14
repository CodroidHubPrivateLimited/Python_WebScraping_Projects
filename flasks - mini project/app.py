from flask import Flask, render_template, request, redirect, url_for, session, abort
from authlib.integrations.flask_client import OAuth
import os
import pandas as pd
from flask import send_from_directory
import importlib
import logging
import sys
import subprocess
import mysql.connector
from mysql.connector import Error, IntegrityError
import json
from urllib.parse import urlparse
import smtplib
import secrets
from datetime import datetime, timedelta
from email.message import EmailMessage

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
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key")

PUBLIC_ENDPOINTS = {"index", "login", "signup", "verify_email", "static", "auth_google", "auth_google_callback"}


def is_safe_next_url(target):
    if not target:
        return False
    parsed = urlparse(target)
    return parsed.scheme == "" and parsed.netloc == "" and target.startswith("/")


@app.before_request
def require_login():
    endpoint = request.endpoint
    if endpoint is None:
        return None
    if endpoint in PUBLIC_ENDPOINTS:
        return None
    if session.get("logged_in"):
        return None
    return redirect(url_for("login", next=request.path))

# MySQL Database Configuration
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', '127.0.0.1'),
    'port': int(os.environ.get('MYSQL_PORT', '3306')),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'Vishal92919511'),
    'database': os.environ.get('MYSQL_DATABASE', 'ana')
}

# Connection pool
db_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="flask_app_pool",
    pool_size=5,
    pool_reset_session=True,
    **DB_CONFIG
)

SMTP_CONFIG = {
    "host": os.environ.get("SMTP_HOST", ""),
    "port": int(os.environ.get("SMTP_PORT", "587")),
    "user": os.environ.get("SMTP_USER", ""),
    "password": os.environ.get("SMTP_PASSWORD", ""),
    "use_tls": os.environ.get("SMTP_USE_TLS", "true").lower() == "true",
    "from_email": os.environ.get("SMTP_FROM_EMAIL", os.environ.get("SMTP_USER", "")),
}

# Google OAuth
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://127.0.0.1:5000/auth/google/callback")

oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


def get_db_connection():
    """Get connection from pool with autocommit"""
    try:
        connection = db_pool.get_connection()
        connection.autocommit = True
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
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            cursor.execute(f"USE {DB_CONFIG['database']}")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    is_verified TINYINT(1) NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_verifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    code VARCHAR(6) NOT NULL,
                    expires_at DATETIME NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = 'email'
                """,
                (DB_CONFIG["database"],)
            )
            email_exists = cursor.fetchone()[0] > 0
            if not email_exists:
                cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255)")
                cursor.execute("ALTER TABLE users ADD UNIQUE KEY uq_users_email (email)")

            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = 'is_verified'
                """,
                (DB_CONFIG["database"],)
            )
            is_verified_exists = cursor.fetchone()[0] > 0
            if not is_verified_exists:
                cursor.execute("ALTER TABLE users ADD COLUMN is_verified TINYINT(1) NOT NULL DEFAULT 0")

            # Legacy users (created before email verification) had no email and should remain usable.
            cursor.execute(
                "UPDATE users SET is_verified = 1 WHERE is_verified = 0 AND (email IS NULL OR email = '')"
            )
            
            # Ensure admin account is always present and verified.
            cursor.execute(
                """
                INSERT INTO users (username, email, password, is_verified)
                VALUES ('admin', 'admin@example.com', 'admin123', 1)
                ON DUPLICATE KEY UPDATE
                    password = VALUES(password),
                    is_verified = 1
                """
            )
            
            connection.commit()
            cursor.close()
            connection.close()
            logger.info("Database initialized successfully")
    except Error as e:
        logger.info(f"Database initialization error: {e}")


def send_verification_code(email, code):
    """Send OTP verification code over SMTP."""
    if not SMTP_CONFIG["host"] or not SMTP_CONFIG["from_email"]:
        return False, "Email service is not configured. Set SMTP_* environment variables."

    try:
        msg = EmailMessage()
        msg["Subject"] = "Verify your account - Data Scraper"
        msg["From"] = SMTP_CONFIG["from_email"]
        msg["To"] = email
        msg.set_content(
            f"Your verification code is: {code}\nThis code will expire in 10 minutes."
        )

        with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"], timeout=20) as server:
            if SMTP_CONFIG["use_tls"]:
                server.starttls()
            if SMTP_CONFIG["user"]:
                server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
            server.send_message(msg)
        return True, "Verification code sent"
    except Exception as e:
        logger.info(f"Email sending error: {e}")
        return False, "Failed to send verification email. Check SMTP settings."


def create_user(username, email, password):
    """Create a user in MySQL; returns (success, message)."""
    connection = get_db_connection()
    if not connection or not connection.is_connected():
        return False, "Unable to connect to database"
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password, is_verified) VALUES (%s, %s, %s, 1)",
            (username, email, password)
        )
        return True, "Account created successfully"
    except IntegrityError:
        return False, "Username already exists"
    except Error as e:
        logger.info(f"Signup error: {e}")
        return False, "Unable to create account right now"
    finally:
        cursor.close()
        connection.close()


def save_pending_signup(email, username, password, code, expires_at):
    """Store pending signup details in MySQL for OTP verification."""
    connection = get_db_connection()
    if not connection or not connection.is_connected():
        return False, "Database not available"
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO email_verifications (email, username, password, code, expires_at)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                username = VALUES(username),
                password = VALUES(password),
                code = VALUES(code),
                expires_at = VALUES(expires_at)
            """,
            (email, username, password, code, expires_at)
        )
        return True, "Pending signup saved"
    except Error as e:
        logger.info(f"Pending signup save error: {e}")
        return False, "Unable to save verification request"
    finally:
        cursor.close()
        connection.close()


def get_pending_signup(email):
    """Fetch pending signup data from MySQL by email."""
    connection = get_db_connection()
    if not connection or not connection.is_connected():
        return None
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT email, username, password, code, expires_at
            FROM email_verifications
            WHERE email = %s
            """,
            (email,)
        )
        return cursor.fetchone()
    except Error as e:
        logger.info(f"Pending signup fetch error: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def delete_pending_signup(email):
    """Delete pending signup record after verification/expiry."""
    connection = get_db_connection()
    if not connection or not connection.is_connected():
        return
    
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM email_verifications WHERE email = %s", (email,))
    except Error as e:
        logger.info(f"Pending signup delete error: {e}")
    finally:
        cursor.close()
        connection.close()


def authenticate_user(username, password):
    """Authenticate user against MySQL database"""
    connection = get_db_connection()
    if not connection or not connection.is_connected():
        logger.info("Database unavailable during login")
        return False
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id FROM users WHERE (username = %s OR email = %s) AND password = %s AND is_verified = 1",
            (username, username, password)
        )
        return cursor.fetchone() is not None
    except Error as e:
        logger.info(f"Authentication error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

STATIC_FOLDER = "data/static_data"
API_FOLDER = "data/api_data"

DYNAMIC_SCRAPER_FOLDER = "scrapers/dynamic_data"
STATIC_SCRAPER_FOLDER = "scrapers/static_data"
API_SCRAPER_FOLDER = "scrapers/api"


def get_source_label(scraper_name):
    clean_name = scraper_name.lower().replace("-checkpoint", "")
    source_map = {
        "booktoscrape": "Books to Scrape",
        "codroidhub": "CodroidHub",
        "coingeckoh": "CoinGecko",
        "flipkart": "Flipkart",
        "imdb": "IMDb",
        "pharmeasy": "PharmEasy",
        "shopsy": "Shopsy",
        "wikipedia": "Wikipedia",
        "github": "GitHub",
        "gyansetu": "Gyansetu",
        "blinkit": "Blinkit",
        "dominos": "Dominos",
        "makemytrip": "MakeMyTrip",
        "swiggi": "Swiggy",
        "zamato": "Zomato",
        "reddit": "Reddit"
    }
    return source_map.get(clean_name, scraper_name.replace("-checkpoint", "").title())


def build_cards(files, page_type):
    cards = []
    for file_name in files:
        source = get_source_label(file_name)
        if page_type == "static":
            description = f"Static snapshot data scraped from {source} website."
        elif page_type == "dynamic":
            description = f"Dynamic live-update dataset collected from {source} source."
        else:
            description = f"API-driven dataset fetched from {source} source."

        cards.append({
            "name": file_name,
            "source": source,
            "description": description
        })
    return cards

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
        email = (request.form.get("email") or "").strip().lower()
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if not email or not username or not password:
            return render_template("signup.html", error="Email, username, and password are required")

        connection = get_db_connection()
        if not connection or not connection.is_connected():
            return render_template("signup.html", error="Database not available")
        
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT id FROM users WHERE username = %s OR email = %s",
                (username, email)
            )
            existing = cursor.fetchone()
            if existing:
                return render_template("signup.html", error="Username or email already exists")
        except Error as e:
            logger.info(f"Signup pre-check error: {e}")
            return render_template("signup.html", error="Unable to validate account details")
        finally:
            cursor.close()
            connection.close()

        code = f"{secrets.randbelow(900000) + 100000}"
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        saved, save_msg = save_pending_signup(email, username, password, code, expires_at)
        if not saved:
            return render_template("signup.html", error=save_msg)

        sent, msg = send_verification_code(email, code)
        if not sent:
            delete_pending_signup(email)
            return render_template("signup.html", error=msg)

        return redirect(url_for("verify_email", email=email))

    return render_template("signup.html")


@app.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    email = (request.args.get("email") or request.form.get("email") or "").strip().lower()
    if not email:
        return redirect(url_for("signup"))
    pending = get_pending_signup(email)
    if not pending:
        return render_template("signup.html", error="No pending verification found for this email")

    if request.method == "POST":
        entered_code = (request.form.get("code") or "").strip()
        expires_at = pending.get("expires_at")
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at)
            except ValueError:
                expires_at = datetime.utcnow() - timedelta(seconds=1)

        if datetime.utcnow() > expires_at:
            delete_pending_signup(email)
            return render_template("signup.html", error="Verification code expired. Please sign up again.")

        if entered_code != pending.get("code"):
            return render_template("verify_email.html", email=pending.get("email"), error="Invalid verification code")

        created, message = create_user(
            pending.get("username", ""),
            pending.get("email", ""),
            pending.get("password", ""),
        )
        delete_pending_signup(email)
        if created:
            return redirect(url_for("login", signup="success"))
        return render_template("signup.html", error=message)

    return render_template("verify_email.html", email=pending.get("email"))


@app.route("/auth/google")
def auth_google():
    if not GOOGLE_CLIENT_ID:
        abort(503, "Google OAuth not configured")
    redirect_uri = url_for('auth_google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/auth/google/callback")
def auth_google_callback():
    if not GOOGLE_CLIENT_ID:
        abort(503, "Google OAuth not configured")
    try:
        token = google.authorize_access_token()
    except Exception as e:
        logger.info(f"Google auth error: {e}")
        print(e)
        return redirect(url_for("signup", error="Google login failed"))

    userinfo = token.get('userinfo')
    if not userinfo:
        return redirect(url_for("signup", error="Failed to get user info"))

    google_id = userinfo['sub']
    email = userinfo['email']
    name = userinfo['name']

    # Check if user exists by email or create with INSERT IGNORE
    connection = get_db_connection()
    if not connection or not connection.is_connected():
        return redirect(url_for("signup", error="Database unavailable"))
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            # Login existing user
            session["logged_in"] = True
            session["username"] = user['username']
            logger.info(f"Google login for existing user: {email}")
            return redirect(url_for("select_page"))
        else:
            # Create new user (no password needed for OAuth) - use INSERT IGNORE
            username = name.replace(" ", "_").lower()[:50]  # Simple username from name
            cursor.execute("""
                INSERT IGNORE INTO users (username, email, password, is_verified) 
                VALUES (%s, %s, %s, 1)
                ON DUPLICATE KEY UPDATE 
                    is_verified = 1, password = VALUES(password)
            """, (username, email, "oauth_google"))
            session["logged_in"] = True
            session["username"] = username
            logger.info(f"Created/Updated OAuth user: {email}")
            return redirect(url_for("select_page"))
    finally:
        cursor.close()
        connection.close()

@app.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get("next", "")
    signup_success = request.args.get("signup") == "success"

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        next_url = request.form.get("next", "")

        if authenticate_user(username, password):
            session["logged_in"] = True
            session["username"] = username
            if is_safe_next_url(next_url):
                return redirect(next_url)
            return redirect(url_for("select_page"))

        return render_template(
            "login.html",
            error="Invalid username/email or password",
            next_url=next_url,
            signup_success=False,
        )

    return render_template("login.html", next_url=next_url, signup_success=signup_success)

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
    cards = build_cards(files, "static")

    return render_template("files.html",
                           cards=cards,
                           files=files,
                           data_type="static")

@app.route("/dynamic-data")
def home_api():
    if not os.path.exists(API_SCRAPER_FOLDER):
        return "API scraper folder not found"

    files = [f[:-3] for f in os.listdir(API_SCRAPER_FOLDER)
             if f.endswith(".py") and not f.startswith("__")]
    cards = build_cards(files, "dynamic")

    return render_template("files.html",
                           cards=cards,
                           files=files,
                           data_type="api",
                           page_label="DYNAMIC")

@app.route("/api-data")
def api_page():
    if not os.path.exists(DYNAMIC_SCRAPER_FOLDER):
        return "Dynamic scraper folder not found"

    files = [f[:-3] for f in os.listdir(DYNAMIC_SCRAPER_FOLDER)
             if f.endswith(".py") and not f.startswith("__")]
    cards = build_cards(files, "api")

    return render_template("api.html", files=files, cards=cards)

@app.route("/view-api/<filename>")
def view_api_file(filename):
    file_path = os.path.join(API_SCRAPER_FOLDER, f"{filename}.py")
    if not os.path.exists(file_path):
        return "API file not found"

    try:
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=180
        )
    except Exception as e:
        return f"Error running API scraper: {str(e)}"

    if result.returncode != 0:
        return f"Scraper failed.<br>{result.stderr.replace(chr(10), '<br>')}"

    scraped_lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]

    if not scraped_lines:
        scraped_lines = ["No output received from scraper."]

    df = pd.DataFrame({"scraped_data": scraped_lines})

    os.makedirs(API_FOLDER, exist_ok=True)
    csv_filename = f"{filename}_data.csv"
    csv_path = os.path.join(API_FOLDER, csv_filename)
    df.to_csv(csv_path, index=False)

    table = df.to_html(classes="table table-bordered", index=False)

    return render_template("view.html",
                           table=table,
                           filename=filename,
                           data_type="api",
                           files_page="/dynamic-data",
                           scraper_executed=True,
                           scraper_error=None)

def find_matching_scraper(data_type, filename):
    """Find the correct scraper module by matching filename with scraper files"""
    scraper_name = filename.replace(".csv", "").lower()
    
    if data_type == "static":
        scraper_folder = STATIC_SCRAPER_FOLDER
    elif data_type == "api":
        scraper_folder = API_SCRAPER_FOLDER
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
    init_database()
    app.run(host='0.0.0.0', debug=True)