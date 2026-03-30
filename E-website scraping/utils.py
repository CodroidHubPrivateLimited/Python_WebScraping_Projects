import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

_STOPWORDS = {
    "bluetooth",
    "wireless",
    "tws",
    "earbuds",
    "earbud",
    "earphone",
    "earphones",
    "headphone",
    "headphones",
    "in",
    "with",
    "and",
    "true",
    "stereo",
    "noise",
    "canceling",
    "cancelling",
    "mic",
    "mics",
    "gaming",
    "hours",
    "hour",
    "hrs",
    "playback",
    "battery",
    "fast",
    "charge",
    "charging",
    "new",
    "gen",
    "generation",
    "edition",
}


def create_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    return webdriver.Chrome(options=options)


def clean_price(price_text: str | int | None) -> int | None:
    if price_text is None:
        return None
    if isinstance(price_text, int):
        return price_text

    digits = re.sub(r"[^\d]", "", str(price_text))
    if not digits:
        return None

    return int(digits)


def clean_query(q: str) -> str:
    return q.lower().strip()


def parse_rating(text: str | None) -> float | None:
    if not text:
        return None
    match = re.search(r"([0-5](?:\.\d)?)", text)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def find_first_element(driver, selectors: list[str], by: By = By.CSS_SELECTOR):
    for selector in selectors:
        try:
            elements = driver.find_elements(by, selector)
            if elements:
                return elements[0]
        except Exception:
            continue
    return None


def format_price(value: int | None) -> str:
    if value is None:
        return "Not Found"

    return f"₹{value:,}"


def compare_prices(amazon_price: int | None, zepto_price: int | None):
    if amazon_price is None and zepto_price is None:
        return None, None

    if amazon_price is None:
        return "Zepto", zepto_price

    if zepto_price is None:
        return "Amazon", amazon_price

    if amazon_price < zepto_price:
        return "Amazon", amazon_price

    if zepto_price < amazon_price:
        return "Zepto", zepto_price

    return "Equal", amazon_price


def compare_prices_multi(prices: dict[str, int | None]):
    available = {store: price for store, price in prices.items() if price is not None}
    if not available:
        return None, None

    min_price = min(available.values())
    winners = [store for store, price in available.items() if price == min_price]
    if len(winners) > 1:
        return "Equal", min_price

    return winners[0], min_price


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9\s]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def _first_token(text: str) -> str:
    normalized = _normalize_text(text)
    if not normalized:
        return ""
    return normalized.split(" ")[0]


def _token_set(text: str) -> set[str]:
    if not text:
        return set()
    normalized = _normalize_text(text)
    tokens = [token for token in normalized.split(" ") if token]
    return {token for token in tokens if token not in _STOPWORDS}


def match_score(product: str, title: str) -> float:
    product_tokens = _token_set(product)
    title_tokens = _token_set(title)
    if not product_tokens or not title_tokens:
        return 0.0
    overlap = product_tokens & title_tokens
    return len(overlap) / len(product_tokens)


def match_details(product: str, title: str):
    product_tokens = _token_set(product)
    title_tokens = _token_set(title)
    if not product_tokens or not title_tokens:
        return 0.0, 0, product_tokens, title_tokens
    overlap = product_tokens & title_tokens
    score = len(overlap) / len(product_tokens)
    return score, len(overlap), product_tokens, title_tokens


def choose_best_candidate(product: str, candidates: list[tuple[str, str]]):
    if not candidates:
        return None

    best_price = None
    best_score = 0.0
    for title, price in candidates:
        if not title or not price:
            continue
        score = match_score(product, title)
        if score > best_score:
            best_score = score
            best_price = price

    if best_price is None:
        return None

    if best_score < 0.35:
        return candidates[0][1]

    return best_price


def choose_best_product(
    product: str,
    candidates: list[dict],
    min_score: float | None = None,
    min_overlap: int | None = None,
    require_brand: bool = True,
):
    if not candidates:
        return None

    product_tokens = _token_set(product)
    if min_overlap is None:
        min_overlap = 1 if len(product_tokens) <= 2 else 2
    if min_score is None:
        min_score = 0.3 if len(product_tokens) <= 2 else 0.45

    brand = _first_token(product)

    best_item = None
    best_score = 0.0
    for item in candidates:
        title = item.get("title", "")
        score, overlap_count, _, title_tokens = match_details(product, title)

        if require_brand and brand and len(brand) >= 3 and brand not in title_tokens:
            continue

        digit_tokens = {t for t in product_tokens if any(ch.isdigit() for ch in t)}
        if digit_tokens and not (digit_tokens & title_tokens):
            continue

        if overlap_count < min_overlap or score < min_score:
            continue

        if score > best_score:
            best_score = score
            best_item = item

    return best_item
