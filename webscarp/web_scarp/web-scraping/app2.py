#scraping books.toscrape.com

#importing the libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd 
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def scrape_books():
    books = []
    url = "http://books.toscrape.com/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all book containers
        book_containers = soup.find_all('article', class_='product_pod')
        
        # Loop through each book container
        for book in book_containers:
            # Extract book title
            title_element = book.find('h3').find('a')
            title = title_element.get('title') if title_element else 'No title'
            
            # Extract book price
            price_element = book.find('p', class_='price_color')
            price = price_element.text if price_element else 'No price'
            
            # Extract availability
            availability_element = book.find('p', class_='instock availability')
            availability = availability_element.text.strip() if availability_element else 'No availability info'
            
            # Extract rating (optional)
            rating_element = book.find('p', class_='star-rating')
            rating = rating_element.get('class')[1] if rating_element else 'No rating'

            books.append({
                'Title': title,
                'Price': price,
                # 'availability': availability,
                # 'rating': rating,
            })
            
    except requests.RequestException as e:
        print(f"Error scraping the page: {e}")
    
    scraped_data =pd.DataFrame(books, columns=["Title","Price"] )
    
    return render_template("scrape.html", table=scraped_data.to_html(index=False, classes="table table-striped"))

#@app.route('/')
#def index():
   # return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True ,port=3000,host="0.0.0.0")