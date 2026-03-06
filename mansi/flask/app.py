from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys
import csv

sys.dont_write_bytecode = True

# ================= APP =================
app = Flask(__name__)
app.secret_key = "your_secret_key"

# ================= DATABASE PATH (FIXED FOR RENDER + LOCAL) =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


create_table()

# ================= HOME =================
@app.route("/")
def home():
    return render_template("base/home.html")


# ================= SIGNUP =================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        if not email or not username or not password:
            flash("All fields are required!")
            return redirect("/signup")

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (email, username, password) VALUES (?, ?, ?)",
                (email, username, hashed_password)
            )
            conn.commit()
            conn.close()

            flash("Account created successfully! Please login.")
            return redirect("/login")

        except sqlite3.IntegrityError:
            flash("Email or Username already exists!")
            return redirect("/signup")

    return render_template("signup.html")


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = user["username"]
            return redirect("/dashboard")
        else:
            flash("Invalid email or password")
            return redirect("/login")

    return render_template("login.html")


# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("base/dashboard.html", user=session["user"])


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# ================= DYNAMIC WEBSITES =================
from router.dynamic import myntra, Snapdeal, Meesho, ajio, blinkit

SCRAPER_MAP = {
    "myntra": myntra,
    "snapdeal": Snapdeal,
    "meesho": Meesho,
    "ajio": ajio,
    "blinkit": blinkit,
}

DYNAMIC_CSV_FALLBACKS = {
    "myntra": os.path.join(BASE_DIR, "data", "dynamicfiles", "myntra_shoes.csv"),
    "snapdeal": os.path.join(BASE_DIR, "data", "dynamicfiles", "snapdeal_tshirts.csv"),
    "meesho": os.path.join(BASE_DIR, "data", "dynamicfiles", "Meesho_products.csv"),
    "ajio": os.path.join(BASE_DIR, "data", "dynamicfiles", "ajio_products.csv"),
    "blinkit": os.path.join(BASE_DIR, "data", "dynamicfiles", "blinkit_products.csv"),
}


def load_dynamic_fallback(site):
    csv_path = DYNAMIC_CSV_FALLBACKS.get(site)
    if not csv_path or not os.path.exists(csv_path):
        return [], []

    with open(csv_path, mode="r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return [], []

    return rows[0], rows[1:]

@app.route("/dynamic-websites")
def dynamic_websites():
    if "user" not in session:
        return redirect("/login")
    return render_template("dynamic/dynamic_websites.html")


@app.route("/view/dynamic/<site>")
def view_dynamic(site):
    if "user" not in session:
        return redirect("/login")

    site = site.lower()
    module = SCRAPER_MAP.get(site)
    if not module:
        flash("Invalid dynamic website selected.")
        return redirect("/dynamic-websites")

    try:
        headers, rows = module.fetch_data()
    except Exception:
        app.logger.exception("Dynamic scraper failed for site: %s", site)
        headers, rows = load_dynamic_fallback(site)
        if rows:
            flash("Live scrape failed on server, showing last saved data.")
        else:
            flash("Live scrape failed and no backup data found.")

    return render_template(
        "dynamic/view_common.html",
        title=f"{site.capitalize()} Data",
        headers=headers,
        rows=rows
    )


# ================= STATIC WEBSITES =================
from router.Static import amazon, flipkart, bookscrap, ecommers, shopsy, codroidhub2, polo

@app.route("/static-websites")
def static_websites():
    if "user" not in session:
        return redirect("/login")
    return render_template("Static/Static_websites.html")


@app.route("/view/<dataType>/<site>")
def viewFile(dataType, site):
    if "user" not in session:
        return redirect("/login")

    modules = {
        "amazon": amazon,
        "flipkart": flipkart,
        "book": bookscrap,
        "ecommers": ecommers,
        "shopsy": shopsy,
        "codroidhub2": codroidhub2,
        "polo": polo
    }

    module = modules.get(site)
    headers, rows = module.fetch_data()

    return render_template(
        "Static/view_common.html",
        title=site.capitalize(),
        headers=headers,
        rows=rows
    )


# ================= API SERVICES =================
from router.Api import reddit, codroidhub, dummyjson, github, gyansetu

@app.route("/api-services")
def api_services():
    if "user" not in session:
        return redirect("/login")
    return render_template("api/api_services.html")


@app.route("/view/api/<site>")
def view_api(site):
    if "user" not in session:
        return redirect("/login")

    API_MAP = {
        "reddit": reddit,
        "codroidhub": codroidhub,
        "dummyjson": dummyjson,
        "github": github,
        "gyansetu": gyansetu
    }

    module = API_MAP.get(site)
    headers, rows = module.fetch_data()

    return render_template(
        "api/view_common.html",
        title=site.capitalize(),
        headers=headers,
        rows=rows
    )


# ================= EXTRA PAGES =================
@app.route("/Journey")
def Journey():
    return render_template("base/Journey.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/feedback")
def feedback():
    return render_template("feedback.html")


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
