from bs4 import BeautifulSoup
import requests
import sqlite3

def reset_database():
    cur.executescript('''
    DROP TABLE IF EXISTS books;

    CREATE TABLE books(
        title TEXT,
        price FLOAT,
        genre TEXT,
        availability TEXT,
        rating TEXT,
        upc TEXT
    );
    ''')

# Establish database connection
conn = sqlite3.connect('Books.db')
cur = conn.cursor()

# Reset database
reset_database()

# Page to scrape
html_text = requests.get('http://books.toscrape.com/').text


while True:
    # Access website
    soup = BeautifulSoup(html_text, 'lxml')

    # Get next page url
    try:
        next_tag = soup.find('li', class_='next')
        if 'catalogue' in next_tag.a.get('href'):
            next_link = next_tag.a.get('href')
        else:
            next_link = 'catalogue/' + next_tag.a.get('href')
        # next_link = next_tag.a.get('href')
        next_url = 'http://books.toscrape.com/' + next_link
        print(next_url)
    except:
        pass

    # Get current page and total pages
    page_string = soup.find('li', class_='current').text.strip()
    current_page = int(page_string.split()[1])
    total_pages = int(page_string.split()[3])

    # Get all book links
    book_links = soup.find_all('li', class_='col-xs-6 col-sm-4 col-md-3 col-lg-3')

    # for each book, follow book link and scrape book info
    for book_link in book_links:
        if 'catalogue' in book_link.h3.a.get('href'):
            book_url = 'http://books.toscrape.com/' + book_link.h3.a.get('href')
        else:
            book_url = 'http://books.toscrape.com/catalogue/' + book_link.h3.a.get('href')
        print(book_url)
        html_text = requests.get(book_url).text
        soup = BeautifulSoup(html_text, 'lxml')

        book = soup.find('div', class_='col-sm-6 product_main')
        title = book.h1.text
        price = book.find('p', class_='price_color').text[2:]
        availability = book.find('p', class_='instock availability').text.strip()
        
        breadcrumb = soup.find('ul', class_='breadcrumb')
        breadcrumb_lists = breadcrumb.find_all('li')
        for item in breadcrumb_lists:
            if item.text.strip() != 'Home' and item.text.strip() != 'Books':
                genre = item.text.strip()
                break

        upc = soup.table.tr.text.strip()[3:]

        for el in book.find_all('p'):
            if 'Five' in el['class']:
                rating = 5
                break
            elif 'Four' in el['class']:
                rating = 4
                break
            elif 'Three' in el['class']:
                rating = 3
                break
            elif 'Two' in el['class']:
                rating = 2
                break
            elif 'One' in el['class']:
                rating = 1
                break
            else:
                rating = 'Unknown'

        # Add data to database
        cur.execute('''INSERT OR IGNORE INTO books (title, price, availability, rating, upc, genre)
            VALUES (?, ?, ?, ?, ?, ?)''', (title, price, availability, rating, upc, genre))


    conn.commit()

    if current_page == total_pages:
        break
    
    # Set next page
    html_text = requests.get(next_url).text