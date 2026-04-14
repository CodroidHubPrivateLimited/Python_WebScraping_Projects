from urllib.parse import quote_plus
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def scrape(query="python developer", location="Mohali", limit=20):
    """Main scrape function compatible with app.py - searches Indeed with query."""
    return get_indeed_jobs(query, location, limit=limit)


def create_driver(headless=True):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-web-security")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    if headless:
        options.add_argument("--headless=new")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def get_indeed_jobs(
    job: str,
    location: str = "Mohali",
    headless: bool = True,
    debug: bool = False,
    limit: int = 5,
) -> list[dict]:

    driver = create_driver(headless=headless)

    try:
        search_url = f"https://in.indeed.com/jobs?q={quote_plus(job)}&l={quote_plus(location)}"
        driver.get(search_url)

        wait = WebDriverWait(driver, 20)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.job_seen_beacon"))
        )

        jobs = []
        cards = driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon")

        for card in cards[:25]:
            try:
                # -------- TITLE --------
                title_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle span")
                title = title_elem.text

                # -------- COMPANY --------
                company_elem = card.find_elements(By.CSS_SELECTOR, "span.companyName")
                company = company_elem[0].text if company_elem else None

                # -------- LOCATION --------
                location_elem = card.find_elements(By.CSS_SELECTOR, "div.companyLocation")
                location = location_elem[0].text if location_elem else None

                # -------- SALARY --------
                salary_elem = card.find_elements(By.CSS_SELECTOR, "div.metadata.salary-snippet-container")
                salary = salary_elem[0].text if salary_elem else "Not Disclosed"

                # -------- JOB LINK --------
                link_elem = card.find_element(By.CSS_SELECTOR, "h2 a")
                job_url = "https://in.indeed.com" + link_elem.get_attribute("href")

                # -------- IMAGE (optional placeholder) --------
                image = None  # Indeed mostly jobs me image nahi hoti

                if title:
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "salary": salary,
                        "url": job_url,
                        "image": image,
                    })

            except Exception:
                continue

        if debug:
            print("\nTop Jobs:")
            for job in jobs[:5]:
                print(job["title"], "|", job["company"])

        return jobs[:limit]

    except Exception as e:
        print("Error:", e)
        return []

    finally:
        driver.quit()


# -------- SINGLE BEST JOB --------
def get_indeed_job(job: str, location: str = "Mohali"):
    jobs = get_indeed_jobs(job, location, limit=10)

    if not jobs:
        return {
            "title": "Not Found",
            "company": None,
            "location": None,
            "salary": None,
            "url": None,
        }

    return jobs[0]


# -------- ONLY TITLES --------
def get_indeed_titles(job: str, location: str = "Mohali"):
    jobs = get_indeed_jobs(job, location)
    return [j["title"] for j in jobs]