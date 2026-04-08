# Job Search Enhancement TODO
Status: [ ] Complete

## Steps from Approved Plan:
1. [x] Update indeed_dynamic_scraper.py: Make `get_indeed_jobs` available as `scrape(query)`
2. [x] Update app.py: Modify `/scrape/indeed` route to handle query param, call scrape(query), pass jobs to results.html
3. [x] Update templates/index.html: Add search input + button for Indeed
4. [x] Update static/style.css: Add styles for search box/button
5. [x] Update templates/results.html: Add support for displaying jobs dict list (title, company, etc.)
6. [x] Test: python app.py, search on index → results page with Indeed jobs

After all: attempt_completion

