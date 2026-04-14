from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote_plus
import time

def scrape(query="software developer"):
    """Dynamic Naukri scrape - real jobs data."""
    return get_naukri_jobs(query)

def create_driver(headless=True):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-web-security")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_naukri_jobs(job, location="India", limit=15):
    driver = create_driver(headless=True)
    try:
        # Naukri search URL format
        search_query = job.replace(' ', '%20')
        search_url = f"https://www.naukri.com/{search_query}-jobs"
        print(f"Naukri searching: {search_url}")
        driver.get(search_url)
        time.sleep(8)  # Allow page load
        wait = WebDriverWait(driver, 15)
        
        # Multiple selector strategies for job cards
        card_selectors = [
            ".jobTuple",
            "li.jobTuple", 
            ".srp_jobtuple",
            "[class*='job']",
            "div[role='listitem']"
        ]
        
        cards = []
        for selector in card_selectors:
            cards = driver.find_elements(By.CSS_SELECTOR, selector)
            if cards:
                print(f"Found {len(cards)} cards with selector '{selector}'")
                break
        
        jobs = []
        for card in cards[:limit]:
            try:
                # Flexible title selectors
                title_selectors = ["a.title", ".job-title a", "h3 a", "span.title a", ".title a"]
                title = ""
                job_url = ""
                for sel in title_selectors:
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, sel)
                        title = title_elem.text.strip()
                        job_url = title_elem.get_attribute("href") or ""
                        if title:
                            break
                    except:
                        continue
                
                # Company
                company = "N/A"
                company_selectors = [".companyName", ".company", ".orgName", ".org-name"]
                for sel in company_selectors:
                    try:
                        company_elem = card.find_element(By.CSS_SELECTOR, sel)
                        company = company_elem.text.strip()
                        if company:
                            break
                    except:
                        continue
                
                # Location
                loc_selectors = [".location", ".jobLocation", ".job-loc"]
                location_found = location
                for sel in loc_selectors:
                    try:
                        loc_elem = card.find_element(By.CSS_SELECTOR, sel)
                        location_found = loc_elem.text.strip()
                        if location_found:
                            break
                    except:
                        continue
                
                # Salary
                salary = "Not Disclosed"
                salary_selectors = [".salary", "[class*='salary']", ".experience"]
                for sel in salary_selectors:
                    try:
                        salary_elem = card.find_element(By.CSS_SELECTOR, sel)
                        salary = salary_elem.text.strip()
                        if salary:
                            break
                    except:
                        continue
                
                if title and len(title) > 5:
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location_found,
                        "salary": salary,
                        "url": job_url,
                        "site": "naukri"
                    })
                    print(f"Added Naukri job: {title[:50]}...")
            except Exception as card_error:
                continue
        
        print(f"Final Naukri jobs scraped: {len(jobs)}")
        return jobs[:10]  # Return top 10
    except Exception as e:
        print(f"Naukri full error: {e}")
        return [{"title": "Naukri search active - try different query", "site": "naukri", "company": "System", "location": location, "salary": "", "url": ""}]
    finally:
        driver.quit()
