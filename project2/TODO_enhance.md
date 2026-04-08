# Multi-Site Dynamic Search TODO
Status: [ ] Complete

## Steps:
1. [x] Add query-aware scrape(query) to naukri_dynamic_scraper.py (structured dicts like Indeed)
2. [x] Add query-aware scrape(query) to jobsphere_dynamic_scraper.py (structured dicts)
3. [x] Update app.py: Modify /scrape/naukri & /scrape/jobsphere for query, pass jobs=jobs
4. [x] Add /scrape-all route in app.py: parallel scrape all three +site label
5. [x] templates/index.html: Add search forms for Naukri/Jobsphere + new "Search All Sites" button
6. [x] templates/results.html: Display job.site label, handle combined
7. [x] static/style.css: Styles if needed
8. [ ] Test all searches & parallel

After: attempt_completion

