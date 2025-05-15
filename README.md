# 📘 Book Scraper and Analyzer

This project is a **Python-based tool** that scrapes book information from the website [BooksToScrape.com](http://books.toscrape.com/), stores the data in both JSON and SQLite formats, and allows users to perform **data analysis and visualization** to discover insights such as pricing trends, rating distribution, and best value books.

---

## 📦 Installation Instructions

1. **Clone the repository**  
```bash
git clone https://github.com/yourusername/book-scraper-analyzer.git
cd book-scraper-analyzer
```


2. **Install required dependencies**
```bash
pip install -r requirements.txt
```

---

## 🧪 Usage Examples

Run the script:
```bash
python book_scraper.py
```

You will see an interactive menu like this:

```
===== Book Scraper Menu =====
1. Scrape books
2. View book statistics
3. Find best value books
4. Look up book by ID
5. Show visualizations
6. EXIT
```

- Select **option 1** to scrape and save book data.
- Choose **option 2** to display total books, average price, and rating range.
- Use **option 3** to identify books with the highest ratings and lowest prices.
- Select **option 4** to retrieve book details using a specific ID.
- Use **option 5** to display plots (e.g., price vs rating histogram).

---

## ✨ Features Implemented

✅ Scrapes title, price, availability, and rating from multiple book pages  
✅ Cleans and saves scraped data in JSON format  
✅ Loads data into Pandas DataFrame for analysis  
✅ Stores data in an SQLite database  
✅ Retrieves book by ID using SQL queries  
✅ Visualizes data with matplotlib and seaborn  
✅ Identifies best value books (lowest price & highest rating)

---

## 🧠 Challenges Faced and Solutions

### 1. Handling Unicode Characters in Prices
- **Issue**: Scraped price strings had unexpected encoding like `Â£`.
- **Solution**: Used string cleaning functions to remove or replace non-ASCII characters.

### 2. Dynamic URL Correction
- **Issue**: Some product links didn’t include `catalogue/` in the URL path.
- **Solution**: Implemented a check to insert missing parts and ensure complete URLs.

### 3. Parsing Ratings Stored as Words
- **Issue**: Ratings were given as words (e.g., "Three", "Five").
- **Solution**: Created a mapping dictionary to convert rating strings to integers.

### 4. Preventing Duplicate Data in Database
- **Issue**: Re-running the scraper added duplicate rows.
- **Solution**: Checked if a title already existed in the database before inserting.

### 5. Missing or Incomplete Book Data
- **Issue**: Some fields like availability were not always present.
- **Solution**: Used `.get()` and fallback values to ensure robust scraping.

---

## 📁 Outputs

- `scraped_data/books_data.json`: Cleaned book data in JSON format  
- `scraped_data/books_database.db`: SQLite database of all books  
- Visualizations: Histograms and scatter plots displayed via matplotlib  

---

## 🔧 Dependencies

- `requests`  
- `beautifulsoup4`  
- `pandas`  
- `matplotlib`  
- `seaborn`

Install them with:

```bash
pip install -r requirements.txt
```

