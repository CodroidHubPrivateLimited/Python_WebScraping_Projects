from urllib.parse import quote_plus
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import choose_best_product, create_driver, match_score, parse_rating


def get_amazon_products(
    product: str,
    headless: bool = True,
    debug: bool = False,
    limit: int = 5,
) -> list[dict]:
    driver = create_driver(headless=headless)
    try:
        search_url = f"https://www.amazon.in/s?k={quote_plus(product)}"
        driver.get(search_url)

        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
            )
        )

        candidates = []
        cards = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")

        for card in cards[:15]:
            try:
                title = card.find_element(By.CSS_SELECTOR, "h2 span").text

                url = None
                asin = card.get_attribute("data-asin")
                if asin:
                    url = f"https://www.amazon.in/dp/{asin}"
                else:
                    link_elems = card.find_elements(By.CSS_SELECTOR, "h2 a")
                    if link_elems:
                        url = link_elems[0].get_attribute("href")

                price = None
                price_elem = card.find_elements(By.CSS_SELECTOR, "span.a-price-whole")
                if price_elem:
                    price = price_elem[0].text

                rating_text = None
                rating_elem = card.find_elements(By.CSS_SELECTOR, "span.a-icon-alt")
                if rating_elem:
                    rating_text = rating_elem[0].text
                rating_value = parse_rating(rating_text)

                image = None
                img_elem = card.find_elements(By.CSS_SELECTOR, "img.s-image")
                if img_elem:
                    image = img_elem[0].get_attribute("src")

                if title and price:
                    candidates.append(
                        {
                            "title": title,
                            "price": price,
                            "image": image,
                            "url": url,
                            "rating": rating_value,
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
            print("\nTop Matches:")
            for item in scored[:5]:
                print(item["title"], "| Score:", item.get("score"))

        return scored[:limit]
    except Exception as e:
        print("Error:", e)
        return []
    finally:
        driver.quit()


def get_amazon_product(product: str, headless: bool = True, debug: bool = False) -> dict:
    candidates = get_amazon_products(product, headless=headless, debug=debug, limit=10)
    if not candidates:
        return {
            "title": "Not Found",
            "price": "Not Found",
            "image": None,
            "url": None,
        }

    best_item = choose_best_product(product, candidates, min_score=0.2)
    if not best_item:
        best_item = candidates[0]

    return best_item


def get_amazon_price(product: str, headless: bool = True) -> str:
    item = get_amazon_product(product, headless=headless)
    return item.get("price") or "Not Found"
  
