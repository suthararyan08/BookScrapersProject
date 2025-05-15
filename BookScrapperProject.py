import requests
import os
import json
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


# Create data directory if it doesn't exist
data_dir = "scraped_data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

class BookScraper:
    def __init__(self):
        self.base_url = "http://books.toscrape.com/"
        self.books = []

    def fetch_webpage(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return response.text 
            else:
                print(f"Error: status code {response.status_code}") 
                return None

        except Exception as e:
            print(f"An error occurred: {str(e)}")  
            return None

    def scrape_books_from_page(self, page_num=1):
        url = f"{self.base_url}catalogue/page-{page_num}.html"
        html_content = self.fetch_webpage(url)

        if not html_content:
            return False

        soup = BeautifulSoup(html_content, 'html.parser')
        book_containers = soup.select('article.product_pod')

        if not book_containers:
            return False

        for book in book_containers:
            # Extract book details
            title = book.h3.a['title']
            price = book.select_one('p.price_color').text
            availability = book.select_one('p.availability').text.strip()
            rating = book.select_one('p.star-rating')['class'][1]

            # Get book URL for additional details
            book_url = book.h3.a['href']
            if 'catalogue/' not in book_url:
                book_url = 'catalogue/' + book_url
            book_full_url = self.base_url + book_url

            self.books.append({
                'title': title,
                'price': price,
                'availability': availability,
                'rating': rating,
                'url': book_full_url
            })

        return True

    def scrape_multiple_pages(self, num_pages=1):  # Reduced to 1 page for quicker demo
        for page in range(1, num_pages + 1):
            print(f"Scraping page {page}...")
            success = self.scrape_books_from_page(page)
            if not success:
                print(f"Failed to scrape page {page} or no more pages available.")
                break

        print(f"Scraped a total of {len(self.books)} books.")
        return self.books

    def save_to_json(self, filename="books_data.json"):
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.books, f, indent=4)
        print(f"Book data saved to {filepath}")


class BookDataAnalyzer:
    def __init__(self, books_data=None, json_file=None):
        self.df = pd.DataFrame()

        if books_data:
            print("Initializing analyzer with provided book data...")
            self.df = pd.DataFrame(books_data)
            self._preprocess_data()
        elif json_file:
            print(f"Loading data from JSON file: {json_file}")
            try:
                filepath = os.path.join(data_dir, json_file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    books_data = json.load(f)
                self.df = pd.DataFrame(books_data)
                self._preprocess_data()
                print(f"Successfully loaded {len(self.df)} books from JSON")
            except Exception as e:
                print(f"Error loading JSON file: {str(e)}")

    def _preprocess_data(self):
        print("Preprocessing data...")
        # Clean price
        self.df['price_numeric'] = self.df['price'].str.replace('Â£', '', regex=False).str.replace('£', '', regex=False).astype(float)

        # Map ratings
        rating_map = {
            "One": 1, 
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        self.df['rating_numeric'] = self.df['rating'].map(rating_map)
        print("Data preprocessing complete")

    def get_summary_stats(self):
        print("Calculating summary statistics...")
        if self.df.empty:
            print("Warning: DataFrame is empty")
            return {"total_books": 0}

        stats = {
            'total_books': len(self.df),
            'avg_price': self.df['price_numeric'].mean(),
            'min_price': self.df['price_numeric'].min(),
            'max_price': self.df['price_numeric'].max(),
            'avg_rating': self.df['rating_numeric'].mean()
        }

        print("Statistics calculated successfully")
        return stats

    def get_best_value_book(self, min_rating=4, n=5):
        print(f"Finding best value books with rating >= {min_rating}...")
        if self.df.empty:
            print("Warning: DataFrame is empty")
            return pd.DataFrame()

        value_books = self.df[self.df['rating_numeric'] >= min_rating]
        result = value_books.sort_values('price_numeric').head(n)
        print(f"Found {len(result)} matching books")
        return result


    def plot_price_distribution(self):
        if self.df.empty:
            print("No data to plot.")
            return

        plt.figure(figsize=(10, 6))
        sns.histplot(self.df['price_numeric'], kde=True, bins=20, color='skyblue')
        plt.title('Distribution of Book Prices')
        plt.xlabel('Price (£)')
        plt.ylabel('Number of Books')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_avg_price_by_rating(self):
        if self.df.empty:
            print("No data to plot.")
            return

        avg_price = self.df.groupby('rating_numeric')['price_numeric'].mean().reset_index()

        plt.figure(figsize=(8, 5))
        sns.barplot(data=avg_price, x='rating_numeric', y='price_numeric', palette='mako',hue='rating_numeric')
        plt.title('Average Price by Rating')
        plt.xlabel('Rating')
        plt.ylabel('Average Price (£)')
        plt.tight_layout()
        plt.show()

    def plot_rating_distribution(self):
        if self.df.empty:
            print("No data to plot.")
            return

        plt.figure(figsize=(8, 5))
        sns.countplot(data=self.df, x='rating_numeric', hue='rating_numeric', palette='pastel', legend=False)

        plt.title('Number of Books by Rating')
        plt.xlabel('Rating')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.show()
        
    def is_empty(self):
        return self.df.empty


class BookDatabase:
    def __init__(self):
        print("Initializing database...")
        # Try to remove the existing database to avoid locks
        db_path = os.path.join(data_dir, "books_database.db")
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
                print("Removed existing database")
        except Exception as e:
            print(f"Note: Could not remove existing database: {e}")

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
        print("Database initialized successfully")

    def _create_tables(self):
        print("Creating tables...")
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price REAL NOT NULL,
                rating INTEGER NOT NULL,
                availability TEXT,
                url TEXT            
            )
        ''')
        self.conn.commit()
        print("Tables created successfully")

    def insert_books(self, books_df):
        print("Inserting books into database...")
        if books_df.empty:
            print("Warning: No books to insert (DataFrame is empty)")
            return

        # Get existing titles
        try:
            self.cursor.execute('SELECT title from books')
            existing_titles = [row[0] for row in self.cursor.fetchall()]
        except:
            existing_titles = []

        insert_count = 0
        for _, row in books_df.iterrows():
            if row['title'] not in existing_titles:
                try:
                    self.cursor.execute('''
                    INSERT INTO books (title, price, rating, availability, url)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (
                        row['title'],
                        row['price_numeric'],
                        row['rating_numeric'],
                        row['availability'],
                        row['url']
                    ))
                    insert_count += 1
                except Exception as e:
                    print(f"Error inserting book {row['title']}: {e}")

        self.conn.commit()
        print(f"Added {insert_count} new books to database")

    def get_book_by_id(self, book_id):
        print(f"Looking up book with ID {book_id}...")
        try:
            self.cursor.execute('''
            SELECT id, title, price, rating, availability, url
            FROM books 
            WHERE id = ?
            ''', (book_id,))

            book = self.cursor.fetchone()
            if book:
                print(f"Found book: {book[1]}")
            else:
                print(f"No book found with ID {book_id}")
            return book
        except Exception as e:
            print(f"Error looking up book: {e}")
            return None

    def close(self):
        print("Closing database connection...")
        if self.conn:
            self.conn.close()
            print("Database connection closed")


def run_scraping():
    scraper = BookScraper()
    books = scraper.scrape_multiple_pages(1)  
    scraper.save_to_json()
    return books




def display_menu():
    print("\n===== Book Scraper Menu =====")
    print("1. Scrape books")
    print("2. View book statistics")
    print("3. Find best value books")
    print("4. Look up book by ID")
    print("5. Show visualizations")
    print("6. EXIT")
    choice = input("Enter your choice (1-6): ")
    print(f"You selected: {choice}")
    return choice


def main():
    print("\n===== Welcome to the Book Scraper Application =====")

    # Create a  database
    db = BookDatabase()
    analyzer = None

    while True:
        try:
            choice = display_menu()

            if choice == '1':
                print("\n--- Scraping Books ---")
                books = run_scraping()

                # Create a new analyzer with the scraped data
                print("Creating analyzer with scraped data...")
                analyzer = BookDataAnalyzer(books_data=books)

                # Insert books into database
                print("Saving books to database...")
                db.insert_books(analyzer.df)
                print("Scraping complete!")

            elif choice == '2':
                print("\n--- Book Statistics ---")
                # Load analyzer if not already loaded
                if analyzer is None or analyzer.is_empty():
                    print("No data loaded. Attempting to load from JSON file...")
                    analyzer = BookDataAnalyzer(json_file="books_data.json")
                    if analyzer.is_empty():
                        print("Could not load data. Please scrape books first (Option 1).")
                        continue

                # Get and display statistics
                stats = analyzer.get_summary_stats()
                print("\nBook Statistics:")
                for key, val in stats.items():
                    if isinstance(val, float):
                        print(f"{key}: {val:.2f}")
                    else:
                        print(f"{key}: {val}")

            elif choice == '3':
                print("\n--- Best Value Books ---")
                # Load analyzer if not already loaded
                if analyzer is None or analyzer.is_empty():
                    print("No data loaded. Attempting to load from JSON file...")
                    analyzer = BookDataAnalyzer(json_file="books_data.json")
                    if analyzer.is_empty():
                        print("Could not load data. Please scrape books first (Option 1).")
                        continue

                # Get rating from user
                try:
                    rating = int(input("Enter minimum rating (1-5): "))
                    if rating < 1 or rating > 5:
                        print("Rating must be between 1 and 5")
                        continue
                except ValueError:
                    print("Please enter a valid number")
                    continue


                best_books = analyzer.get_best_value_book(min_rating=rating)

                if best_books.empty:
                    print(f"No books found with rating {rating} or higher")
                else:
                    print(f"\nBest Value Books (Rating {rating}+):")
                    for i, (_, book) in enumerate(best_books.iterrows(), 1):
                        print(f"{i}. {book['title']} - £{book['price_numeric']:.2f}")

            elif choice == '4':
                print("\n--- Look Up Book by ID ---")

                if analyzer is None or analyzer.is_empty():
                    print("No data loaded. Attempting to load from JSON file...")
                    analyzer = BookDataAnalyzer(json_file="books_data.json")
                    if analyzer.is_empty():
                        print("Could not load data. Please scrape books first (Option 1).")
                        continue


                # Lookup and display book
                book_id = input("Enter the book ID: ")
                book = db.get_book_by_id(book_id)

                if book:
                    print("\nBook Details:")
                    print(f"ID: {book[0]}")
                    print(f"Title: {book[1]}")
                    print(f"Price: £{book[2]:.2f}")
                    print(f"Rating: {book[3]} stars")
                    print(f"Availability: {book[4]}")
                    print(f"URL: {book[5]}")
                else:
                    print(f"No book found with ID {book_id}")

            elif choice == '5':
                print("\n--- Data Visualizations ---")
                if analyzer is None or analyzer.is_empty():
                    print("No data loaded. Attempting to load from JSON file...")
                    analyzer = BookDataAnalyzer(json_file="books_data.json")
                    if analyzer.is_empty():
                        print("Could not load data. Please scrape books first (Option 1).")
                        continue
    
                print("\nChoose a visualization:")
                print("1. Rating Distribution")
                print("2. Average Price by Rating")
                print("3. Price Distribution")
    
                viz_choice = input("Enter your choice (1-3): ")
                
                if viz_choice == '1':
                    analyzer.plot_rating_distribution()
                elif viz_choice == '2':
                    analyzer.plot_avg_price_by_rating()
                elif viz_choice == '3':
                    analyzer.plot_price_distribution()
                else:
                    print("Invalid choice.")
    
            
            elif choice == '6':
                print("Thank you for using the Book Scraper Application. Goodbye!")
                db.close()
                break

            else:
                print("Invalid choice! Please enter a number between 1 and 5.")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            import traceback
            traceback.print_exc()
            print("Please try again.")


if __name__ == "__main__":
    main()