import re
from splinter import Browser
from bs4 import BeautifulSoup as Soup


# Initialize browser
exe_path = '/usr/local/bin/chromedriver'
browser = Browser('chrome', executable_path=exe_path, headless=False)

# Visit the site and get the html
site_url = 'https://books.toscrape.com/'
browser.visit(site_url)
book_soup = Soup(browser.html, 'html.parser')

# Data header
headings = 'upc;title;category;price;rating;num_reviews'
headings += ';in_stock;num_available;url\n'
# book_data = [headings]

# Output heading to file
outfile = 'books.csv'
with open(outfile, 'w') as f:
    f.write(headings)

# Book count
i = 0


# Continue scraping for all pages
while True:

    # Print current page
    page_num = browser.url.split('/')[-1].replace('.html', '')
    page_num = page_num.replace('-', ' ').upper()
    page_num = page_num if 'PAGE' in page_num else 'PAGE 1'
    print(' #', page_num, '#')

    # List of book titles on the page
    book_soup = Soup(browser.html, 'html.parser')
    books = book_soup.find_all('article', class_='product_pod')
    titles = [book.find('h3').get_text() for book in books]
    
    # For each book on the page
    for t in titles:

        # Replace quotes in titles
        t = t.replace('"', '')

        # Print book being scraped
        i += 1
        print(i, t)

        # Initialize data variables
        upc = title = category = price = rating = num_reviews = ''
        in_stock = num_available = url = ''

        # Go to the book's page and parse the html
        try:
            browser.links.find_by_partial_text(t).click()
            url = browser.url
            page_soup = Soup(browser.html, 'html.parser')
        except:
            print(' - Not found:', t)
            continue

        # Breadcrumb - category
        try:
            category = page_soup.select('ul.breadcrumb li')[2].find('a').text
        except:
            print(' - Category missing')

        # Main product section - title, price, rating
        try:
            p_main = page_soup.find('div', class_='product_main')
            title = p_main.find('h1').text
            price = p_main.find('p', class_='price_color').text[1:]
            rating = p_main.find('p', class_='star-rating').attrs['class'][1]
        except:
            print(' - Title/price/rating missing')

        # Stock availability - in_stock, num_available
        try:
            stock = page_soup.select_one('div.product_main p.availability')
            stock = stock.text.strip().split('(')
            in_stock = stock[0].strip()
            num_available = stock[1].split()[0]
        except:
            print(' - Stock/availability missing')

        # Product information - upc, num_reviews
        try:
            p_info = page_soup.find('table')
            upc = p_info.find('td').text
            num_reviews = p_info.find_all('td')[-1].text
        except:
            print(' - UPC/reviews missing')

        # Click back
        if re.search(r'/page\-\d+\.', browser.url):
            continue
        else:
            browser.back()

        # Combine data variables into a row
        book = f'{upc};{title};{category};{price};{rating};{num_reviews}'
        book += f';{in_stock};{num_available};{url}\n'
        # book_data.append(book)

        # Write row to file
        with open(outfile, 'a') as f:
            f.write(book)

    # Go to next page or quit browser if no more pages
    try:
        browser.links.find_by_partial_text('next').click()
    except:
        browser.quit()
        break


# # Write data to file
# f = open(outfile, 'a')
# for book in book_data:
#     f.write(book)
# f.close()