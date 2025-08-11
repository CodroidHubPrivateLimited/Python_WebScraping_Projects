from  flask import Flask, render_template, url_for, redirect
import requests
from bs4 import BeautifulSoup
import pandas as pd 
import matplotlib.pyplot as plt
import os 
import re 

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

# Global Dataframe to hold scraped data
scraped_data = pd.DataFrame()


# @app.route('/')
# def index():
#     return render_template('home.html')

@app.route('/')
def scrape_books():
    global scraped_data
    url = "http://books.toscrape.com/catalogue/category/books/science_22/index.html"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    products = []

    items = soup.find_all("article", class_="product_pod")  # corrected class name

    for item in items:
        name_tag = item.find("h3").find("a")
        price_tag = item.find("p", class_="price_color")

        name = name_tag.get("title") if name_tag else "N/A"
        price_text = price_tag.get_text(strip=True) if price_tag else "£0"
        price_clean = re.sub(r"[^\d.]", "", price_text)  # keep the decimal point
        price = float(price_clean) if price_clean else 0.0

        products.append([name, price])

    scraped_data = pd.DataFrame(products, columns=["Name", "Price (£)"])

    return render_template("scrape.html", table=scraped_data.to_html(index=False, classes="table table-striped"))


@app.route('/bar-chart')    
def bar_chart():
    if scraped_data.empty:
        return redirect('/')
    

    plt.figure(figsize=(10,6))
    plt.bar(scraped_data["Name"], scraped_data["Price (£)"])
    # plt.xticks(rotation=90)
    plt.ylabel("price ($)")
    plt.title("Books prices - Bar chart")
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart.png')
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return render_template('bar_chart.html', chart_url = url_for('static',filename='chart.png'))

if __name__ == '__main__':
    app.run(debug=True ,port=3000,host="0.0.0.0")