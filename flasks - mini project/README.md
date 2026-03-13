# AI Based Intelligent Web Data Scraping System

A modern Flask-based web application for scraping, storing, and viewing data from various websites. The project includes multiple web scrapers for different data sources with a clean, interactive user interface.

![Flask](https://img.shields.io/badge/Flask-3.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.x-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Scrapers](#scrapers)
- [Data Storage](#data-storage)
- [API Endpoints](#api-endpoints)
- [Screenshots](#screenshots)
- [Future Enhancements](#future-enhancements)
- [License](#license)

## ✨ Features

### Core Features
- **User Authentication**: Sign up, login, and email verification with OTP
- **Multiple Data Sources**: Support for static, dynamic, and API-based scrapers
- **Data Viewing**: Interactive table view for scraped data
- **CSV Export**: Download scraped data in CSV format
- **Power BI Integration**: View and embed Power BI reports

### Scrapers Included
- **Static Scrapers**: Web scraping from static HTML pages
- **Dynamic Scrapers**: JavaScript-rendered content using Selenium
- **API Scrapers**: Direct API data fetching

### UI Features
- Modern 3D animated landing page
- Responsive design for all devices
- Dark/Light theme support
- Interactive data tables with sorting and filtering

## 🛠 Tech Stack

### Backend
- **Flask**: Web framework
- **Python 3.x**: Programming language
- **SQLite/MySQL**: Database
- **Pandas**: Data manipulation

### Web Scraping
- **BeautifulSoup4**: HTML parsing
- **Selenium**: Browser automation
- **Requests**: HTTP requests

### Frontend
- **HTML5**: Markup
- **CSS3**: Styling (with animations)
- **JavaScript**: Interactivity

## 📁 Project Structure

```
flasks-mini-project/
├── app.py                 # Main Flask application
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── TODO.md              # Project task list
├── .gitignore           # Git ignore rules
├── app.db               # SQLite database
├── SMTP_SETUP.md        # SMTP configuration guide
│
├── scrapers/            # Web scrapers
│   ├── api/             # API-based scrapers
│   │   └── Dominos.py   # Dominos pizza scraper
│   ├── dynamic_data/    # Dynamic scrapers (Selenium)
│   │   └── codroidHub.py
│   └── static_data/     # Static scrapers (BeautifulSoup)
│
├── data/                # Data storage
│   ├── api_data/        # API scraped data (CSV)
│   ├── csv_data/        # CSV data files
│   ├── dynamic_data/    # Dynamic scraped data
│   ├── img/             # Images
│   ├── power_bi/        # Power BI reports
│   └── static_data/    # Static scraped data
│
├── static/              # Static files
│   ├── files.css
│   ├── landing.css
│   ├── select.css
│   ├── style.css
│   ├── view.css
│   └── ... (other CSS files)
│
└── templates/           # HTML templates
    ├── landing.html     # Landing page
    ├── index.html       # Home page
    ├── login.html       # Login page
    ├── signup.html      # Signup page
    ├── select.html      # Data source selection
    ├── files.html       # Files listing
    ├── view.html        # Data viewer
    └── ... (other templates)
```

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher
- Chrome browser (for Selenium scrapers)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd "flasks - mini project"
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
SESSION_DAYS=7

# Database Configuration
DB_ENGINE=sqlite  # or 'mysql'
SQLITE_DB_PATH=app.db

# MySQL Configuration (if using MySQL)
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=your-database

# SMTP Configuration (for email verification)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Data Scraper
SMTP_USE_TLS=True

# Authentication (optional)
AUTH_REQUIRED=False
```

## 🚀 Running the Application

### Development Mode

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Production Mode

```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🕷 Scrapers

### Available Scrapers

| Scraper | Type | Description |
|---------|------|-------------|
| Dominos | API | Scrapes pizza menu from Dominos India |
| CodroidHub | Dynamic | Scrapes tech articles from CodroidHub |
| BookToScrape | Static | Book data from Books to Scrape |
| Flipkart | Dynamic | Product listings from Flipkart |
| IMDb | Dynamic | Movie ratings and details |
| And more... | Various | Multiple other data sources |

### Running Scrapers

Scrapers can be run through the web interface or programmatically:

```python
# Import and run a scraper
import importlib
module = importlib.import_module("scrapers.dynamic_data.codroidHub")
module.run()
```

## 💾 Data Storage

### Database Schema

**Users Table**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password TEXT NOT NULL,
    is_verified INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Email Verifications Table**
```sql
CREATE TABLE email_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    code TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Data Folders
- `data/static_data/`: Static scraped CSV files
- `data/api_data/`: API-sourced CSV files
- `data/dynamic_data/`: Dynamic scraped data
- `data/csv_data/`: User-uploaded CSV files
- `data/power_bi/`: Power BI report files

## 🌐 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/signup` | User registration |
| GET/POST | `/login` | User login |
| GET/POST | `/verify-email` | Email verification |
| GET | `/logout` | User logout |

### Data Pages
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page |
| GET | `/home` | Home/Dashboard |
| GET | `/select` | Data source selection |
| GET | `/static-data` | Static data scrapers |
| GET | `/dynamic-data` | Dynamic data scrapers |
| GET | `/api-data` | API data sources |

### Data Operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/view/<type>/<filename>` | View scraped data |
| GET | `/download/<type>/<filename>` | Download CSV file |
| GET | `/csv-data` | List CSV files |
| GET | `/view-csv/<filename>` | View CSV data |
| GET | `/power-bi` | List Power BI files |
| GET | `/view-pbix/<filename>` | View Power BI report |

## 📸 Screenshots

The application features:
- Modern animated landing page with 3D elements
- Clean login/signup pages with email verification
- Interactive data selection page
- Data tables with export functionality
- Power BI report viewer

## 🔮 Future Enhancements

- [ ] Add more web scrapers for popular websites
- [ ] Implement scheduled scraping with cron jobs
- [ ] Add user dashboard with scraping history
- [ ] Implement data visualization charts
- [ ] Add API for programmatic access
- [ ] Dockerize the application
- [ ] Add unit tests for scrapers

## 📝 License

This project is licensed under the MIT License.

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)

---

<p align="center">Made with ❤️ using Flask</p>

