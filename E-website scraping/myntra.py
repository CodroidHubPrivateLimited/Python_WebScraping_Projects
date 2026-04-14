import time
from urllib.parse import quote_plus

from selenium.webdriver.common.by import By
from utils import create_driver, match_score, parse_rating


def get_myntra_products(
    product: str,
    headless: bool = False,
    debug: bool = False,
    limit: int = 5,
) -> list[dict]:
    driver = create_driver(headless=headless)
    try:
        search_url = f"https://www.myntra.com/{quote_plus(product)}"
        driver.get(search_url)

        time.sleep(5)

        cards = driver.find_elements(By.CSS_SELECTOR, "li.product-base")
        if debug:
            print("Total cards:", len(cards))

        candidates = []
        for card in cards[:15]:
            try:
                title = None
                brand = card.find_elements(By.CSS_SELECTOR, "h3.product-brand")
                name = card.find_elements(By.CSS_SELECTOR, "h4.product-product")
                if brand and name:
                    title = brand[0].text + " " + name[0].text

                price = None
                price_elem = card.find_elements(By.CSS_SELECTOR, "span.product-discountedPrice")
                if price_elem:
                    price = price_elem[0].text
                else:
                    price_elem = card.find_elements(By.CSS_SELECTOR, "span.product-strike")
                    if price_elem:
                        price = price_elem[0].text

                image = None
                img_elem = card.find_elements(By.CSS_SELECTOR, "img")
                if img_elem:
                    image = img_elem[0].get_attribute("src")

                url = None
                link_elem = card.find_elements(By.CSS_SELECTOR, "a")
                if link_elem:
                    url = link_elem[0].get_attribute("href")

                rating_text = None
                rating_elem = card.find_elements(
                    By.CSS_SELECTOR,
                    "div.product-ratingsContainer span, span.product-ratingsCount",
                )
                if rating_elem:
                    rating_text = rating_elem[0].text
                rating_value = parse_rating(rating_text)

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

                    if debug:
                        print("Found:", title, "|", price)
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
        return scored[:limit]
    except Exception as e:
        print("Myntra Error:", e)
        return []
    finally:
        driver.quit()


def get_myntra_product(product: str, headless: bool = False, debug: bool = False) -> dict:
    candidates = get_myntra_products(product, headless=headless, debug=debug, limit=10)
    if not candidates:
        return {
            "title": "Not Found",
            "price": "Not Found",
            "image": None,
            "url": None,
        }

    best = max(candidates, key=lambda x: x.get("score", 0.0))
    if debug:
        print("\nSelected:", best)

    return best


def get_myntra_price(product: str, headless: bool = False) -> str:
    item = get_myntra_product(product, headless=headless)
    return item.get("price") or "Not Found"
