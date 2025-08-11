from flask import Flask, render_template
import pandas as pd
import os
import re

app = Flask(__name__)

# --- Get the absolute path for the project's root directory ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# --- Helper functions to get project colors ---
def get_color_for_route(route):
    """Returns the color name associated with a project route for UI consistency."""
    colors = {
        '/books-to-scrape': 'violet',
        '/amazon-facewash': 'orange',
        '/flipkart-laptops': 'sky',
        '/goodreads-quotes': 'lime',
        '/top-mutual-funds': 'teal',
        '/crypto-gainers': 'fuchsia'
    }
    return colors.get(route, 'gray')

def get_color_rgb(color_name):
    """Returns the RGB value for a given color name for the chart's styling."""
    rgb_map = {
        'violet': '139, 92, 246',
        'orange': '249, 115, 22',
        'sky': '14, 165, 233',
        'lime': '132, 204, 22',
        'teal': '20, 184, 166',
        'fuchsia': '217, 70, 239'
    }
    return rgb_map.get(color_name, '107, 114, 128')

# --- Main App Routes ---
@app.route('/')
def index():
    """Renders the main portfolio landing page."""
    return render_template('index.html')

@app.route('/projects')
def projects():
    """Renders the showcase page with buttons for all projects."""
    return render_template('home.html')

# --- Data Loading and Visualization Project Routes ---

@app.route('/books-to-scrape')
def show_books():
    """Displays data and charts for 'Books to Scrape'."""
    try:
        csv_path = os.path.join(DATA_DIR, 'books.csv')
        df = pd.read_csv(csv_path)
        df = df[['title', 'price', 'availability']]
        df['price'] = df['price'].str.replace('Â£', '', regex=False).astype(float)
        
        headers = ["Title", "Price (£)", "Availability"]
        df.columns = headers
        data = list(df.to_records(index=False))

        charts_data = []
        # Chart 1: Price of first 20 books (Bar Chart)
        chart_df_1 = df.head(20).copy()
        chart_df_1['Title'] = chart_df_1['Title'].apply(lambda x: x[:25] + '...' if len(x) > 25 else x)
        charts_data.append({
            'type': 'bar',
            'title': 'Price of First 20 Books',
            'labels': chart_df_1['Title'].tolist(),
            'data': chart_df_1['Price (£)'].tolist(),
            'label': 'Price (£)'
        })

        # Chart 2: Book Availability (Pie Chart)
        availability_counts = df['Availability'].value_counts()
        charts_data.append({
            'type': 'pie',
            'title': 'Book Availability',
            'labels': availability_counts.index.tolist(),
            'data': availability_counts.values.tolist(),
            'label': 'Availability'
        })
        
        color = get_color_for_route('/books-to-scrape')
        source_url = "http://books.toscrape.com"

    except FileNotFoundError:
        return "Error: books.csv not found in the 'data' folder.", 404
    except Exception as e:
        return f"An error occurred in show_books: {e}", 500

    return render_template('showcase.html', project_title="Books To Scrape", description="Data from a fictional online bookstore.", headers=headers, data=data, color=color, color_rgb=get_color_rgb(color), source_url=source_url, charts_data=charts_data)

@app.route('/amazon-facewash')
def show_amazon_facewash():
    """Displays data and a chart for the top 15 most expensive Amazon Facewash products."""
    try:
        csv_path = os.path.join(DATA_DIR, 'amazon_facewash.csv')
        df = pd.read_csv(csv_path)
        df = df[['Title', 'Price']]
        df['Price'] = df['Price'].astype(str).str.replace('₹', '', regex=False).str.replace(',', '', regex=False)
        df = df[pd.to_numeric(df['Price'], errors='coerce').notna()]
        df['Price'] = df['Price'].astype(float)
        
        headers = ["Product Name", "Price (₹)"]
        df.columns = headers
        data = list(df.to_records(index=False))

        charts_data = []
        chart_df = df.nlargest(15, 'Price (₹)').copy()
        chart_df['Product Name'] = chart_df['Product Name'].apply(lambda x: x[:25] + '...' if len(x) > 25 else x)
        charts_data.append({
            'type': 'bar',
            'title': 'Top 15 Most Expensive Products',
            'labels': chart_df['Product Name'].tolist(),
            'data': chart_df['Price (₹)'].tolist(),
            'label': 'Price (₹)'
        })
        
        color = get_color_for_route('/amazon-facewash')
        source_url = "https://www.amazon.in/s?k=facewash&crid=1JIWRT8KWWKOL&sprefix=%2Caps%2C361&ref=nb_sb_ss_recent_2_0_recent"

    except FileNotFoundError:
        return "Error: amazon_facewash.csv not found in the 'data' folder.", 404
    except Exception as e:
        return f"An error occurred in show_amazon_facewash: {e}", 500

    return render_template('showcase.html', project_title="Amazon Facewash", description="Top facewash products from Amazon.", headers=headers, data=data, color=color, color_rgb=get_color_rgb(color), source_url=source_url, charts_data=charts_data)

@app.route('/flipkart-laptops')
def show_flipkart_laptops():
    """Displays data and charts for Flipkart Laptops."""
    try:
        csv_path = os.path.join(DATA_DIR, 'flipkart-laptops.csv')
        df = pd.read_csv(csv_path)
        df = df[['Name', 'Price', 'Ratings']]
        df['Price'] = df['Price'].astype(str).str.replace('₹', '', regex=False).str.replace(',', '', regex=False)
        df['Ratings'] = pd.to_numeric(df['Ratings'], errors='coerce')
        df = df[pd.to_numeric(df['Price'], errors='coerce').notna()]
        df['Price'] = df['Price'].astype(int)
        
        headers = ["Laptop Model", "Price (₹)", "Rating"]
        df.columns = headers
        data = list(df.to_records(index=False))

        charts_data = []
        # Chart 1: Top 15 Most Expensive Laptops
        chart_df_1 = df.nlargest(15, 'Price (₹)').copy()
        chart_df_1['Laptop Model'] = chart_df_1['Laptop Model'].apply(lambda x: x[:25] + '...' if len(x) > 25 else x)
        charts_data.append({
            'type': 'bar',
            'title': 'Top 15 Most Expensive Laptops',
            'labels': chart_df_1['Laptop Model'].tolist(),
            'data': chart_df_1['Price (₹)'].tolist(),
            'label': 'Price (₹)'
        })

        # Chart 2: Price vs Rating (Scatter Plot)
        scatter_df = df.dropna(subset=['Price (₹)', 'Rating'])
        scatter_data = [{'x': row['Price (₹)'], 'y': row['Rating']} for index, row in scatter_df.iterrows()]
        charts_data.append({
            'type': 'scatter',
            'title': 'Price vs. Rating',
            'labels': [], 
            'data': scatter_data,
            'label': 'Laptops'
        })

        color = get_color_for_route('/flipkart-laptops')
        source_url = "https://www.flipkart.com/search?q=laptop&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"

    except FileNotFoundError:
        return "Error: flipkart-laptops.csv not found in the 'data' folder.", 404
    except Exception as e:
        return f"An error occurred in show_flipkart_laptops: {e}", 500

    return render_template('showcase.html', project_title="Flipkart Laptops", description="Latest laptop listings from Flipkart.", headers=headers, data=data, color=color, color_rgb=get_color_rgb(color), source_url=source_url, charts_data=charts_data)

@app.route('/goodreads-quotes')
def show_goodreads_quotes():
    """Displays data and a chart for Goodreads Quotes."""
    try:
        csv_path = os.path.join(DATA_DIR, 'goodreads-quotes.csv')
        df = pd.read_csv(csv_path)
        headers = ['Quote', 'Author']
        df = df[headers]
        data = list(df.to_records(index=False))
        
        charts_data = []
        # Chart 1: Top 10 Most Quoted Authors
        author_counts = df['Author'].value_counts().nlargest(10)
        charts_data.append({
            'type': 'bar',
            'title': 'Top 10 Most Quoted Authors',
            'labels': author_counts.index.tolist(),
            'data': author_counts.values.tolist(),
            'label': 'Number of Quotes'
        })
        
        color = get_color_for_route('/goodreads-quotes')
        source_url = "https://www.goodreads.com/quotes"

    except FileNotFoundError:
        return "Error: goodreads-quotes.csv not found in the 'data' folder.", 404
    except Exception as e:
        return f"An error occurred in show_goodreads_quotes: {e}", 500

    return render_template('showcase.html', project_title="Goodreads Quotes", description="Popular and inspiring quotes from Goodreads.", headers=headers, data=data, color=color, color_rgb=get_color_rgb(color), source_url=source_url, charts_data=charts_data)

@app.route('/top-mutual-funds')
def show_mutual_funds():
    """Displays data and a chart for Top Mutual Funds."""
    try:
        csv_path = os.path.join(DATA_DIR, 'mutual_funds.csv')
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        
        # FIX: Select more columns for a complete table view
        display_cols = ['Name', 'Symbol', 'Last Price', 'Change', '52 Weeks Change%']
        df_display = df[display_cols].copy()
        
        # Data cleaning for the chart
        df_display['52 Weeks Change%'] = df_display['52 Weeks Change%'].astype(str).str.replace('%', '', regex=False)
        df_display['52 Weeks Change%'] = pd.to_numeric(df_display['52 Weeks Change%'], errors='coerce')
        df_display.dropna(subset=['52 Weeks Change%'], inplace=True)

        headers = ["Fund Name", "Symbol", "Last Price", "Change", "52 Week Change (%)"]
        df_display.columns = headers
        data = list(df_display.to_records(index=False))

        charts_data = []
        chart_df = df_display.nlargest(15, '52 Week Change (%)').copy()
        chart_df['Fund Name'] = chart_df['Fund Name'].apply(lambda x: x[:25] + '...' if len(x) > 25 else x)
        charts_data.append({
            'type': 'bar',
            'title': 'Top 15 by 52 Week Change (%)',
            'labels': chart_df['Fund Name'].tolist(),
            'data': chart_df['52 Week Change (%)'].tolist(),
            'label': '52 Week Change (%)'
        })

        color = get_color_for_route('/top-mutual-funds')
        source_url = "https://finance.yahoo.com/markets/mutualfunds/top/?start=0&count=25"

    except FileNotFoundError:
        return "Error: mutual_funds.csv not found in the 'data' folder.", 404
    except Exception as e:
        return f"An error occurred in show_mutual_funds: {e}", 500

    return render_template('showcase.html', project_title="Top Mutual Funds", description="Top performing mutual funds.", headers=headers, data=data, color=color, color_rgb=get_color_rgb(color), source_url=source_url, charts_data=charts_data)

@app.route('/crypto-gainers')
def show_crypto_gainers():
    """Displays data and charts for Top Crypto Gainers."""
    try:
        csv_path = os.path.join(DATA_DIR, 'crypto_gainers.csv')
        df = pd.read_csv(csv_path, on_bad_lines='skip')
        df.columns = [col.strip() for col in df.columns]

        def extract_crypto_data(row):
            price_str = str(row)
            price_match = re.search(r'(\d+\.\d+)', price_str)
            change_match = re.search(r'\(([\+\-.,\d]+)%\)', price_str)
            price = float(price_match.group(1)) if price_match else 0
            change = float(change_match.group(1).replace(',', '')) if change_match else 0
            return price, change
        
        # The price info is in the 5th column (index 4)
        df[['Price (USD)', '24h Change (%)']] = df.iloc[:, 4].apply(lambda x: pd.Series(extract_crypto_data(x)))
        
        # FIX: Select more columns for a complete table view
        display_cols = ['Name', 'Symbol', 'Price (USD)', '24h Change (%)', 'Market Cap', 'Volume']
        df_display = df[display_cols].copy()
        df_display = df_display.dropna()

        headers=["Name", "Symbol", "Price (USD)", "24h Change (%)", "Market Cap", "Volume"]
        data = list(df_display.to_records(index=False))

        charts_data = []
        # Chart 1: Top 15 by 24h Change
        change_chart_df = df_display.nlargest(15, '24h Change (%)')
        charts_data.append({
            'type': 'bar',
            'title': 'Top 15 by 24h Change (%)',
            'labels': change_chart_df['Name'].tolist(),
            'data': change_chart_df['24h Change (%)'].tolist(),
            'label': '24h Change (%)'
        })
        
        # Chart 2: Top 10 by Price
        price_chart_df = df_display.nlargest(10, 'Price (USD)')
        charts_data.append({
            'type': 'bar',
            'title': 'Top 10 by Price (USD)',
            'labels': price_chart_df['Name'].tolist(),
            'data': price_chart_df['Price (USD)'].tolist(),
            'label': 'Price (USD)'
        })
        
        color = get_color_for_route('/crypto-gainers')
        source_url = "https://finance.yahoo.com/markets/crypto/gainers/"

    except FileNotFoundError:
        return "Error: crypto_gainers.csv not found. Please ensure 'Top Gainer Crypto currency.csv' is renamed and placed in the 'data' folder.", 404
    except Exception as e:
        return f"An error occurred in show_crypto_gainers: {e}", 500

    return render_template('showcase.html', project_title="Crypto Gainers", description="Top gainer cryptocurrencies.", headers=headers, data=data, color=color, color_rgb=get_color_rgb(color), source_url=source_url, charts_data=charts_data)

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('data'):
        os.makedirs('data')
    app.run(debug=True)
