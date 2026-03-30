import re
import time
from urllib.parse import quote_plus

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import choose_best_product, create_driver, match_score, parse_rating


def _extract_candidate_from_text(text: str) -> tuple[str, str] | None:
    if not text:
        return None
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None

    price = None
    for line in lines:
        if "₹" in line:
            price = line
            break

    if not price:
        match = re.search(r"₹\s*[\d,]+", text)
        if match:
            price = match.group(0)

    if not price:
        return None

    title_lines = [line for line in lines if "₹" not in line]
    title = title_lines[0] if title_lines else lines[0]
    return title, price


def get_meesho_products(
    product: str,
    headless: bool = True,
    debug: bool = False,
    limit: int = 5,
) -> list[dict]:
    driver = create_driver(headless=headless)
    try:
        search_url = f"https://www.meesho.com/search?q={quote_plus(product)}"
        driver.get(search_url)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)

        anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
        candidates: list[dict] = []

        for anchor in anchors[:25]:
            url = anchor.get_attribute("href")
            text = anchor.text or ""
            if "₹" not in text:
                for level in (1, 2, 3):
                    try:
                        parent = anchor.find_element(By.XPATH, "./ancestor::div[%d]" % level)
                        parent_text = parent.text or ""
                        if "₹" in parent_text:
                            text = parent_text
                            break
                    except Exception:
                        continue

            extracted = _extract_candidate_from_text(text)
            if not extracted:
                continue

            title, price_text = extracted
            image_url = None
            img_elems = anchor.find_elements(By.CSS_SELECTOR, "img")
            if img_elems:
                image_url = img_elems[0].get_attribute("src")

            rating_value = None
            star_match = re.search(r"([0-5](?:\.\d)?)\s*★", text)
            if star_match:
                rating_value = parse_rating(star_match.group(1))

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
            print("Meesho Top:", debug_candidates)

        return scored[:limit]
    except Exception:
        return []
    finally:
        driver.quit()


def get_meesho_product(product: str, headless: bool = True, debug: bool = False) -> dict:
    candidates = get_meesho_products(product, headless=headless, debug=debug, limit=10)
    if not candidates:
        return {
            "title": None,
            "price": None,
            "image": None,
            "url": None,
            "rating": None,
            "debug_candidates": None,
        }

    best_item = choose_best_product(product, candidates, min_score=0.2)
    if not best_item:
        best_item = candidates[0]

    return best_item


def get_meesho_price(product: str, headless: bool = True) -> str:
    item = get_meesho_product(product, headless=headless, debug=False)
    return item.get("price") or "Not Found"
