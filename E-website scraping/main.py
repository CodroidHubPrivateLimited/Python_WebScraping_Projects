import os

from amazon import get_amazon_product
from blinkit import get_blinkit_product
from cart import open_product_page
from meesho import get_meesho_product
from myntra import get_myntra_product
from snapdeal import get_snapdeal_product
from utils import clean_price, compare_prices_multi, format_price


def main():
    product = input("Enter product name: ").strip()
    if not product:
        print("Please enter a product name.")
        return

    debug = os.getenv("DEBUG", "") == "1"
    headless = os.getenv("HEADLESS", "1") != "0"

    print("Fetching prices...")
    amazon_item = get_amazon_product(product, headless=headless, debug=debug)
    myntra_item = get_myntra_product(product, headless=headless, debug=debug)
    blinkit_item = get_blinkit_product(product, headless=headless, debug=debug)
    meesho_item = get_meesho_product(product, headless=headless, debug=debug)
    snapdeal_item = get_snapdeal_product(product, headless=headless, debug=debug)

    items = {
        "Amazon": amazon_item,
        "Myntra": myntra_item,
        "Blinkit": blinkit_item,
        "Meesho": meesho_item,
        "Snapdeal": snapdeal_item,
    }
    prices = {label: clean_price(item.get("price")) for label, item in items.items()}

    print("\n--- Price Comparison ---")
    for label, item in items.items():
        print(f"{label}: {format_price(prices[label])}")
        if item.get("title"):
            print(f"  Title: {item.get('title')}")
        if item.get("rating"):
            print(f"  Rating: {item.get('rating')}")

    best_store, best_price = compare_prices_multi(prices)
    if best_store is None:
        print("Best Price: Not Found")
    elif best_store == "Equal":
        print("Best Price: Same on both")
    else:
        print(f"Best Price: {best_store} ({format_price(best_price)})")
        choice = input("Open best product page? (yes/no): ").strip().lower()
        if choice in {"yes", "y"}:
            result = open_product_page(best_store, product, headless=False, keep_open=True)
            print(result.get("message"))
            driver = result.get("driver")
            if driver:
                input("Press Enter after checkout/login to close the browser...")
                driver.quit()

    if debug:
        print("\n--- Debug Top 5 Matches ---")
        for label, item in items.items():
            print(f"{label}:")
            debug_list = item.get("debug_candidates") or []
            if not debug_list:
                print("  No candidates captured.")
                continue
            for cand in debug_list:
                print(f"  - {cand.get('title')} | {cand.get('price')} | {cand.get('score')}")


if __name__ == "__main__":
    main()
