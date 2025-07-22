# 🏘️ Idealista Agency Scraper

A Python-based web scraper for extracting real estate agency data from [Idealista.it](https://www.idealista.it), designed to simulate human behavior, avoid detection, and efficiently gather long-term rental listings by region and province.

---

## 📌 Features

- ✅ Extracts agency name, contact number, region, province, and listing info
- ✅ Supports 20,000+ agency pages with pagination
- ✅ Anti-bot detection techniques (via undetected-chromedriver)
- ✅ Manual CAPTCHA bypass (once) with cookie reuse
- ✅ Human-like mouse movement & scrolling
- ✅ Resume support for already visited links
- ✅ Exports data to both Excel and CSV

---

## 🧠 Tech Stack

- [Python 3](https://www.python.org/)
- [Selenium](https://pypi.org/project/selenium/)
- [undetected-chromedriver](https://pypi.org/project/undetected-chromedriver/)
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)
- [pandas](https://pypi.org/project/pandas/)
- [fake-useragent](https://pypi.org/project/fake-useragent/)

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/idealista-agency-scraper.git
cd idealista-agency-scraper
