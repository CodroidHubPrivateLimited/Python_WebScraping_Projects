from flask import Flask, render_template, redirect, url_for, request
import sqlite3
import os

app = Flask(__name__)

def build_query_from_form(default_query):
    role = (request.form.get('query') or default_query).strip()
    experience = request.form.get('experience', '').strip()
    location = request.form.get('location', '').strip()
    extras = " ".join([part for part in [experience, location] if part])
    return f"{role} {extras}".strip()

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
    query = build_query_from_form('python developer')
    from indeed_dynamic_scraper import scrape
    jobs = scrape(query=query)
    return render_template('results.html', site='indeed', jobs=jobs)

@app.route('/scrape/naukri', methods=['POST'])
def scrape_naukri():
    init_db()
    query = build_query_from_form('software developer')
    from naukri_dynamic_scraper import scrape
    jobs = scrape(query)
    return render_template('results.html', site='naukri', jobs=jobs)

from flask import send_from_directory

@app.route('/download_csv')
def download_csv():
    return send_from_directory('.', 'indeed_scraped_data.csv', as_attachment=True)



@app.route('/results/<site>')
def results(site):
    init_db()
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM jobs WHERE site=? ORDER BY scraped_at DESC", (site,))
    jobs = c.fetchall()
    conn.close()
    return render_template('results.html', site=site, jobs=jobs)

import concurrent.futures

def scrape_site(scraper_module, query):
    if scraper_module == 'indeed_dynamic_scraper':
        from indeed_dynamic_scraper import scrape as scrape_func
    elif scraper_module == 'naukri_dynamic_scraper':
        from naukri_dynamic_scraper import scrape as scrape_func
    else:
        return []
    jobs = scrape_func(query)
    site_map = {
        'indeed_dynamic_scraper': 'indeed',
        'naukri_dynamic_scraper': 'naukri'
    }
    site = site_map.get(scraper_module, 'unknown')
    for job in jobs:
        job['site'] = site
    return jobs

@app.route('/scrape-all', methods=['POST'])
def scrape_all():
    init_db()
    query = build_query_from_form('software developer')
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(scrape_site, 'indeed_dynamic_scraper', query),
            executor.submit(scrape_site, 'naukri_dynamic_scraper', query)
        ]
        all_jobs = []
        for future in concurrent.futures.as_completed(futures):
            all_jobs.extend(future.result() or [])
    return render_template('results.html', site='all', jobs=all_jobs)

if __name__ == "__main__":
  app.run(debug=True, port=5009)
