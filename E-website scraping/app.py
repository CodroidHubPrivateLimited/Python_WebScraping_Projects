import streamlit as st

from amazon import get_amazon_product
from blinkit import get_blinkit_product
from meesho import get_meesho_product
from myntra import get_myntra_product
from snapdeal import get_snapdeal_product
from utils import clean_price, compare_prices_multi, format_price


st.set_page_config(page_title="Price Comparison", page_icon="₹")
st.title("Price Comparison")

product = st.text_input("Enter product name")
debug = st.checkbox("Debug (show top 5 matches)")

if st.button("Search"):
    if not product.strip():
        st.warning("Please enter a product name.")
    else:
        with st.spinner("Fetching prices..."):
            amazon_item = get_amazon_product(product, headless=True, debug=debug)
            myntra_item = get_myntra_product(product, headless=True, debug=debug)
            blinkit_item = get_blinkit_product(product, headless=True, debug=debug)
            meesho_item = get_meesho_product(product, headless=True, debug=debug)
            snapdeal_item = get_snapdeal_product(product, headless=True, debug=debug)

        items = {
            "Amazon": amazon_item,
            "Myntra": myntra_item,
            "Blinkit": blinkit_item,
            "Meesho": meesho_item,
            "Snapdeal": snapdeal_item,
        }
        prices = {label: clean_price(item.get("price")) for label, item in items.items()}

        st.subheader("Prices")
        for label, item in items.items():
            st.write(f"{label}: {format_price(prices[label])}")
            if item.get("title"):
                st.caption(f"Title: {item.get('title')}")
            if item.get("rating"):
                st.caption(f"Rating: {item.get('rating')}")

        best_store, best_price = compare_prices_multi(prices)
        if best_store is None:
            st.error("Best Price: Not Found")
        elif best_store == "Equal":
            st.success("Best Price: Same on both")
        else:
            st.success(f"Best Price: {best_store} ({format_price(best_price)})")

        images = [item.get("image") for item in items.values() if item.get("image")]
        images = [img for img in images if img]
        if images:
            st.subheader("Images")
            st.image(images, width=220)

        if debug:
            st.subheader("Debug Top 5 Matches")
            for label, item in items.items():
                st.write(label)
                st.json(item.get("debug_candidates") or [])
