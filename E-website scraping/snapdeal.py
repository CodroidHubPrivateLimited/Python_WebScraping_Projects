from urllib.parse import quote_plus

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils import choose_best_product, create_driver, match_score


def get_snapdeal_products(
    product: str,
    headless: bool = True,
    debug: bool = False,
    limit: int = 5,
) -> list[dict]:
    driver = create_driver(headless=headless)
    try:
        url = f"https://www.snapdeal.com/search?keyword={quote_plus(product)}"
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-tuple-listing"))
        )

        items = driver.find_elements(By.CSS_SELECTOR, "div.product-tuple-listing")
        candidates = []

        for item in items[:15]:
            try:
                title = item.find_element(By.CSS_SELECTOR, ".product-title").text
                price = item.find_element(By.CSS_SELECTOR, ".product-price").text
                link = item.find_element(By.TAG_NAME, "a").get_attribute("href")

                image = None
                img = item.find_elements(By.TAG_NAME, "img")
                if img:
                    image = img[0].get_attribute("src")

                if title and price:
                    candidates.append(
                        {
                            "title": title,
                            "price": price,
                            "url": link,
                            "image": image,
                            "rating": None,
                        }
                    )
            except Exception:
                continue

        if not candidates:
            return []

        scored = []
        for item in candidates:
            score = match_score(product, item.get("title", ""))
            item["score"] = score
            scored.append(item)

        scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        if debug:
            debug_candidates = [
                {
                    "title": item.get("title"),
                    "price": item.get("price"),
                    "score": round(item.get("score", 0.0), 3),
                }
                for item in scored[:5]
            ]
            print("Snapdeal Top:", debug_candidates)

        return scored[:limit]
    except Exception:
        return []
    finally:
        driver.quit()


def get_snapdeal_product(product: str, headless: bool = True, debug: bool = False) -> dict:
    candidates = get_snapdeal_products(product, headless=headless, debug=debug, limit=10)
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

    if debug:
        best_item["debug_candidates"] = candidates[:5]

    return best_item


def get_snapdeal_price(product: str, headless: bool = True) -> str:
    item = get_snapdeal_product(product, headless=headless, debug=False)
    return item.get("price") or "Not Found"
