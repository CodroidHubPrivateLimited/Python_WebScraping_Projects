from flask import Flask, render_template, redirect, url_for, request
import sqlite3
import os

app = Flask(__name__)

def init_db():
    db_path = 'jobs.db'
    import time
    if os.path.exists(db_path):
        os.remove(db_path)
    time.sleep(1)  # Ensure file unlocked
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  site TEXT,
                  title TEXT,
                  company TEXT,
                  location TEXT,
                  description TEXT,
                  link TEXT,
                  scraped_at TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route("/", methods=['GET', 'POST'])
def index():
  return render_template("index.html")

@app.route('/scrape/indeed', methods=['POST'])
def scrape_indeed():
    init_db()
    from indeed_dynamic_scraper import scrape
    csv_jobs = scrape()
    return render_template('results.html', site='indeed', csv_jobs=csv_jobs)

@app.route('/scrape/naukri', methods=['POST'])
def scrape_naukri():
    init_db()
    from naukri_dynamic_scraper import scrape
    csv_jobs = scrape()
    return render_template('results.html', site='naukri', csv_jobs=csv_jobs)

from flask import send_from_directory

@app.route('/download_csv')
def download_csv():
    return send_from_directory('.', 'indeed_scraped_data.csv', as_attachment=True)

@app.route('/scrape/jobsphere', methods=['POST'])
def scrape_jobsphere():
    init_db()
    from jobsphere_dynamic_scraper import scrape
    csv_jobs = scrape()
    return render_template('results.html', site='jobsphere', csv_jobs=csv_jobs)

@app.route('/results/<site>')
def results(site):
    init_db()
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM jobs WHERE site=? ORDER BY scraped_at DESC", (site,))
    jobs = c.fetchall()
    conn.close()
    return render_template('results.html', site=site, jobs=jobs)

if __name__ == "__main__":
  app.run(debug=True, port=5009)
