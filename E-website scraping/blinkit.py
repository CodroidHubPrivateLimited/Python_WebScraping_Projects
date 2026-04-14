import re
import time
from urllib.parse import quote_plus

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils import create_driver, find_first_element, match_score, parse_rating


def _has_location_gate(driver) -> bool:
    text_markers = [
        "Select Location",
        "Choose Location",
        "Enter delivery location",
    ]
    for marker in text_markers:
        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{marker}')]")
        if elements:
            return True
    return False


def _extract_candidate_from_block(text: str) -> tuple[str, str] | None:
    if not text:
        return None
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None

    price_match = None
    for line in lines:
        if "₹" in line:
            price_match = line
            break

    if not price_match:
        match = re.search(r"₹\s*[\d,]+", text)
        if match:
            price_match = match.group(0)

    if not price_match:
        return None

    title_lines = [line for line in lines if "₹" not in line]
    title = title_lines[0] if title_lines else lines[0]
    return title, price_match


def get_blinkit_products(
    product: str,
    headless: bool = True,
    debug: bool = False,
    limit: int = 5,
) -> list[dict]:
    driver = create_driver(headless=headless)
    try:
        search_url = f"https://blinkit.com/s/?q={quote_plus(product)}"
        driver.get("https://blinkit.com/")

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)

        if _has_location_gate(driver):
            driver.get(search_url)
            time.sleep(2)
        else:
            search_input = find_first_element(
                driver, ["input[placeholder*='Search']", "input[type='text']"]
            )
            if search_input:
                search_input.clear()
                search_input.send_keys(product)
                search_input.send_keys(Keys.ENTER)
            else:
                driver.get(search_url)
                time.sleep(2)

        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[data-testid='product-card'], div[role='button']")
                )
            )
        except Exception:
            pass

        candidates: list[dict] = []
        cards = driver.find_elements(
            By.CSS_SELECTOR,
            "div[data-testid='product-card'], div[data-test-id='product-card'], "
            "div[role='button']",
        )
        for card in cards:
            candidate = _extract_candidate_from_block(card.text)
            if candidate:
                title, price_text = candidate
                image_url = None
                image_elems = card.find_elements(By.CSS_SELECTOR, "img")
                if image_elems:
                    image_url = image_elems[0].get_attribute("src")

                rating_value = None
                star_match = re.search(r"([0-5](?:\.\d)?)\s*★", card.text)
                if star_match:
                    rating_value = parse_rating(star_match.group(1))

                url = None
                link_elems = card.find_elements(By.CSS_SELECTOR, "a[href]")
                if link_elems:
                    url = link_elems[0].get_attribute("href")
                if url and url.startswith("/"):
                    url = f"https://blinkit.com{url}"
                if not url:
                    url = search_url

                candidates.append(
                    {
                        "title": title,
                        "price": price_text,
                        "image": image_url,
                        "url": url,
                        "rating": rating_value,
                    }
                )

        if not candidates:
            return []

        scored = []
        for item in candidates:
            score = match_score(product, item.get("title", ""))
            item["score"] = score
            scored.append(item)

        scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        if debug:
            debug_candidates = []
            for item in scored[:5]:
                debug_candidates.append(
                    {
                        "title": item.get("title"),
                        "price": item.get("price"),
                        "score": round(item.get("score", 0.0), 3),
                    }
                )
            print("Blinkit Top:", debug_candidates)

        return scored[:limit]
    except Exception:
        return []
    finally:
        driver.quit()


def get_blinkit_product(product: str, headless: bool = True, debug: bool = False) -> dict:
    candidates = get_blinkit_products(product, headless=headless, debug=debug, limit=10)
    if not candidates:
        return {
            "title": None,
            "price": None,
            "image": None,
            "url": None,
            "rating": None,
            "debug_candidates": None,
        }

    best_item = candidates[0]
    if debug:
        best_item["debug_candidates"] = candidates[:5]

    return best_item


def get_blinkit_price(product: str, headless: bool = True) -> str:
    item = get_blinkit_product(product, headless=headless, debug=False)
    return item.get("price") or "Not Found"
