import os
import queue
import re

from flask import Flask, Response, render_template, request, stream_with_context, jsonify

from amazon import get_amazon_products
from blinkit import get_blinkit_products
from meesho import get_meesho_products
from myntra import get_myntra_products
from snapdeal import get_snapdeal_products
from utils import _STOPWORDS, clean_price, compare_prices_multi, format_price

app = Flask(__name__)
VOICE_QUEUE: "queue.Queue[str]" = queue.Queue()

STORE_OPTIONS = [
    ("amazon", "Amazon"),
    ("myntra", "Myntra"),
    ("blinkit", "Blinkit"),
    ("meesho", "Meesho"),
    ("snapdeal", "Snapdeal"),
]


def _extract_brand(title: str | None) -> tuple[str | None, str | None]:
    if not title:
        return None, None
    tokens = re.findall(r"[A-Za-z0-9]+", title)
    if not tokens:
        return None, None

    for token in tokens:
        lowered = token.lower()
        if not any(ch.isalpha() for ch in token):
            continue
        if lowered in _STOPWORDS:
            continue
        if lowered in {"dr", "mr", "ms"}:
            continue
        if len(token) <= 1:
            continue

        label = token if token.isupper() and len(token) <= 4 else token.title()
        return label, lowered

    return None, None


def _with_price_text(items: list[dict]) -> list[dict]:
    for item in items:
        price_value = clean_price(item.get("price"))
        item["price_value"] = price_value
        item["price_text"] = format_price(price_value)
        label, key = _extract_brand(item.get("title"))
        item["brand_label"] = label
        item["brand_key"] = key
    return items


def _min_price(items: list[dict]) -> int | None:
    values = [item.get("price_value") for item in items if item.get("price_value") is not None]
    if not values:
        return None
    return min(values)


def _price_bounds(items: list[dict]) -> tuple[int | None, int | None]:
    values = [item.get("price_value") for item in items if item.get("price_value") is not None]
    if not values:
        return None, None
    return min(values), max(values)


def _collect_rating_options(items: list[dict]) -> list[tuple[str, str]]:
    ratings = [item.get("rating") for item in items if item.get("rating") is not None]
    if not ratings:
        return []
    options = []
    if any(r >= 4 for r in ratings):
        options.append(("4", "★★★★ & Up"))
    if any(r >= 3 for r in ratings):
        options.append(("3", "★★★ & Up"))
    if any(r >= 2 for r in ratings):
        options.append(("2", "★★ & Up"))
    return options


def _collect_brand_options(groups: list[list[dict]], limit: int = 12) -> list[tuple[str, str]]:
    counts: dict[str, int] = {}
    labels: dict[str, str] = {}
    for items in groups:
        for item in items:
            key = item.get("brand_key")
            label = item.get("brand_label")
            if not key or not label:
                continue
            counts[key] = counts.get(key, 0) + 1
            labels[key] = label

    ordered = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    result = []
    for key, _ in ordered[:limit]:
        result.append((key, labels.get(key, key.title())))
    return result


def _apply_brand_filter(items: list[dict], selected: list[str]) -> list[dict]:
    if not selected:
        return items
    selected_set = {s.lower() for s in selected}
    return [item for item in items if item.get("brand_key") in selected_set]


def _apply_price_filter(items: list[dict], min_value: int | None, max_value: int | None) -> list[dict]:
    if min_value is None and max_value is None:
        return items
    filtered = []
    for item in items:
        value = item.get("price_value")
        if value is None:
            continue
        if min_value is not None and value < min_value:
            continue
        if max_value is not None and value > max_value:
            continue
        filtered.append(item)
    return filtered


def _apply_rating_filter(items: list[dict], ratings: list[str]) -> list[dict]:
    if not ratings:
        return items
    values = []
    for r in ratings:
        try:
            values.append(float(r))
        except ValueError:
            continue
    if not values:
        return items
    min_rating = min(values)
    filtered = []
    for item in items:
        rating_value = item.get("rating")
        if rating_value is not None and rating_value >= min_rating:
            filtered.append(item)
    return filtered


def _apply_store_filter(stores: list[dict], selected: list[str]) -> list[dict]:
    if not selected:
        return stores
    selected_set = {s.lower() for s in selected}
    return [store for store in stores if store["store"].lower() in selected_set]


@app.get("/")
def landing():
    return render_template("landing.html")


@app.route("/search", methods=["GET", "POST"])
def index():
    data = {
        "product": "",
        "error": None,
        "stores": [],
        "best_store": None,
        "best_price": None,
        "store_options": STORE_OPTIONS,
        "selected_stores": [],
        "brand_options": [],
        "rating_options": [],
        "selected_brands": [],
        "selected_ratings": [],
        "min_price": "",
        "max_price": "",
        "price_min_hint": None,
        "price_max_hint": None,
    }

    if request.method == "POST":
        product = (request.form.get("product") or "").strip()
        data["product"] = product
        if not product:
            data["error"] = "Please enter a product name."
            return render_template("index.html", **data)

        debug = os.getenv("DEBUG", "") == "1"
        headless = os.getenv("HEADLESS", "1") != "0"
        limit = int(os.getenv("RESULT_LIMIT", "4"))

        selected_brands = request.form.getlist("brand")
        selected_ratings = request.form.getlist("rating")
        selected_stores = request.form.getlist("store")
        min_price_raw = (request.form.get("min_price") or "").strip()
        max_price_raw = (request.form.get("max_price") or "").strip()

        data["selected_brands"] = selected_brands
        data["selected_ratings"] = selected_ratings
        data["selected_stores"] = selected_stores
        data["min_price"] = min_price_raw
        data["max_price"] = max_price_raw

        min_price = None
        max_price = None
        if min_price_raw.isdigit():
            min_price = int(min_price_raw)
        if max_price_raw.isdigit():
            max_price = int(max_price_raw)

        try:
            amazon_items = _with_price_text(
                get_amazon_products(product, headless=headless, debug=debug, limit=limit)
            )
            myntra_items = _with_price_text(
                get_myntra_products(product, headless=headless, debug=debug, limit=limit)
            )
            blinkit_items = _with_price_text(
                get_blinkit_products(product, headless=headless, debug=debug, limit=limit)
            )
            meesho_items = _with_price_text(
                get_meesho_products(product, headless=headless, debug=debug, limit=limit)
            )
            snapdeal_items = _with_price_text(
                get_snapdeal_products(product, headless=headless, debug=debug, limit=limit)
            )
        except Exception as e:
            print("Error occurred:", e)   # console me print hoga
            data["error"] = str(e)       # frontend pe show hoga
            return render_template("index.html", **data)
        all_items = (
            amazon_items
            + myntra_items
            + blinkit_items
            + meesho_items
            + snapdeal_items
        )
        price_min_hint, price_max_hint = _price_bounds(all_items)
        data["price_min_hint"] = price_min_hint
        data["price_max_hint"] = price_max_hint

        data["brand_options"] = _collect_brand_options(
            [
                amazon_items,
                myntra_items,
                blinkit_items,
                meesho_items,
                snapdeal_items,
            ]
        )
        data["rating_options"] = _collect_rating_options(all_items)

        def apply_filters(items: list[dict]) -> list[dict]:
            items = _apply_brand_filter(items, selected_brands)
            items = _apply_price_filter(items, min_price, max_price)
            items = _apply_rating_filter(items, selected_ratings)
            return items

        amazon_items = apply_filters(amazon_items)
        myntra_items = apply_filters(myntra_items)
        blinkit_items = apply_filters(blinkit_items)
        meesho_items = apply_filters(meesho_items)
        snapdeal_items = apply_filters(snapdeal_items)
        stores = [
            {"store": "Amazon", "items": amazon_items, "min_price": _min_price(amazon_items)},
            {"store": "Myntra", "items": myntra_items, "min_price": _min_price(myntra_items)},
            {"store": "Blinkit", "items": blinkit_items, "min_price": _min_price(blinkit_items)},
            {"store": "Meesho", "items": meesho_items, "min_price": _min_price(meesho_items)},
            {"store": "Snapdeal", "items": snapdeal_items, "min_price": _min_price(snapdeal_items)},
        ]

        stores = _apply_store_filter(stores, selected_stores)

        best_store, best_price = compare_prices_multi(
            {store["store"]: store["min_price"] for store in stores}
        )

        data["stores"] = stores
        data["best_store"] = best_store
        data["best_price"] = best_price

    return render_template("index.html", **data)


@app.post("/voice-command")
def voice_command():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text") or request.form.get("text") or ""
    text = str(text).strip()
    if not text:
        return jsonify({"ok": False, "error": "empty"}), 400
    safe_text = " ".join(text.splitlines()).strip()
    VOICE_QUEUE.put(safe_text)
    return jsonify({"ok": True})


@app.get("/voice-stream")
def voice_stream():
    def generate():
        while True:
            try:
                text = VOICE_QUEUE.get(timeout=10)
                yield f"data: {text}\n\n"
            except queue.Empty:
                yield ": keepalive\n\n"

    response = Response(stream_with_context(generate()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


