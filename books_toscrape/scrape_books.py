import re
from splinter import Browser
from bs4 import BeautifulSoup as Soup


# Initialize a browser
exe_path = '/usr/local/bin/chromedriver'
browser = Browser('chrome', executable_path=exe_path, headless=False)

# Visit the site and get the html
site_url = 'https://books.toscrape.com/'
browser.visit(site_url)
book_soup = Soup(browser.html, 'html.parser')

# Book data
headings = 'upc,title,category,price,rating,num_reviews'
headings += ',in_stock,num_available,url\n'
book_data = [headings]

# Output file
outfile = 'book_data.csv'
with open(outfile, 'a') as f:
    f.write(headings)

# Book count
i = 0


# Continue scraping for all pages
while True:

    # Get a list of book titles on the page
    book_soup = Soup(browser.html, 'html.parser')
    books = book_soup.find_all('article', class_='product_pod')
    titles = [book.find('h3').find('a').text for book in books]
    
    # For each book on the page
    for t in titles:

        i += 1
        print(i, t)

        # Initialize data variables
        upc = title = category = price = rating = num_reviews = ''
        in_stock = num_available = url = '' 

        # Go to the book's page and get the html
        try:
            browser.click_link_by_partial_text(t)
            url = browser.url
            page_soup = Soup(browser.html, 'html.parser')
        except:
            print('^^^^ Not found ^^^^')
            continue

        # Breadcrumb
        try:
            crumb = page_soup.find('ul', class_='breadcrumb').find_all('li')
            category = crumb[2].find('a').text
        except:
            pass

        # Main product section
        try:
            p_main = page_soup.find('div', class_='product_main')
            title = p_main.find('h1').text.replace(',', '\,')
            price = p_main.find('p', class_='price_color').text[1:]
            rating = p_main.find('p', class_='star-rating').attrs['class'][1]
        except:
            pass

        # Stock availability
        try:
            stock = p_main.find('p', class_='availability').text.strip()
            stock = stock.split('(')
            in_stock = stock[0].strip()
            num_available = stock[1].split()[0]
        except:
            pass

        # Product information
        try:
            p_info = page_soup.find('table')
            upc = p_info.find('td').text
            num_reviews = p_info.find_all('td')[-1].text
        except:
            pass

        # Add book to data
        book = f'{upc},{title},{category},{price},{rating},{num_reviews}'
        book += f',{in_stock},{num_available},{url}\n'
        book_data.append(book)

        # Write row to file
        with open(outfile, 'a') as f:
            f.write(book)

        # Click back
        if not re.search(r'/page\-\d+\.', url):
            browser.back()

    # Go to next page
    try:
        browser.click_link_by_partial_text('next')
    except:
        break


# # Write data to file
# for book in book_data:
#     f.write(book)
# f.close()