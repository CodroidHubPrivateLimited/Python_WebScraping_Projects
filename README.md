# Web Scraping Projects

This repository contains multiple web scraping projects that extract data from various websites including **Amazon**, **Flipkart**, **Gilson**, **Goodreads**, **Mutual Funds**, **PubMed**, and **CryptoCurrency** platforms. These projects demonstrate how to collect, process, and store data using Python and popular web scraping libraries.

---

## Table of Contents

- [Projects Included](#projects-included)  
- [Libraries Used](#libraries-used)  
- [Installation](#installation)  
- [Usage](#usage)  

---

## Projects Included

1. **Amazon & Flipkart Product Scraper**  
   Scrapes product details such as name, price, ratings, and reviews.  

2. **Gilson Data Scraper**  
   Collects product specifications and laboratory equipment details.  

3. **Goodreads Books Scraper**  
   Extracts book titles, authors, ratings, and reviews.  

4. **Mutual Funds Scraper**  
   Fetches fund names, NAV, performance metrics, and ratings.  

5. **PubMed Articles Scraper**  
   Collects article titles, abstracts, authors, and publication dates.  

6. **CryptoCurrency Scraper**  
   Extracts prices, market cap, volume, and trends for various cryptocurrencies.  

---

## Libraries Used

This repository uses the following Python libraries:

- **pandas** – for data manipulation and storage in tabular format (CSV, Excel, etc.)  
- **BeautifulSoup (`bs4`)** – for parsing HTML and XML content  
- **requests** – for sending HTTP requests and receiving responses from websites  

---

## Installation

1. Clone the repository:
git clone https://github.com/yourusername/your-repo-name.git

3. Create a virtual environment (recommended):
   1. cd your-repo-name
   2. python -m venv venv
   3. source venv/bin/activate  # Linux/Mac
   4. venv\Scripts\activate     # Windows

4. Install the required libraries:
pip install pandas beautifulsoup4 requests

5. Usage
  1. Navigate to the folder of the project you want to run.
  2. Open the Python script (e.g., amazon_scraper.py) and run it:
       python amazon_scraper.py

