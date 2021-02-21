import datetime as dt
import numpy as np
import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup as Soup


# URLs
news_url = 'https://mars.nasa.gov/news/'
hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
img_url = 'https://www.jpl.nasa.gov/images?search=&category=Mars'
facts_url = 'https://space-facts.com/'


def scrape_news(browser, url=news_url, n_articles=3):

    """
    Scrape the title, summary, and link of the most recent articles at NASA's 
    Mars news page.

    Parameters
    ----------
    browser : Splinter WebDriver
        Automated browser for scraping
    url : str, optional
        Website to scrape, by default 'https://mars.nasa.gov/news/'
    n_articles : int, optional
        Number of articles to scrape, by default 3

    Returns
    -------
    list[str]
        Titles of the most recent articles
    list[str]
        Summaries of the most recent articles
    list[str]
        Links of the most recent articles
    """

    # Scraped articles
    titles, summaries, links = [], [], []

    try:
        # Visit the site
        browser.visit(url)
        browser.is_element_present_by_css('ul.item_list li.slide', 1) # allow 1s for loading

        # Extract articles
        soup = Soup(browser.html, 'html.parser') # parse html
        articles = soup.select('ul.item_list li.slide')

        # Get the title, summary, and link for each article
        for i in range(n_articles):
            title = articles[i].select_one('div.content_title').text.strip()
            summary = articles[i].select_one('div.article_teaser_body').text.strip()
            link = articles[i].select_one('div.content_title a').attrs['href'] # partial url
            link = url.replace('/news/', '') + link # full url
            
            # Add all 3 to scraped lists
            titles.append(title)
            summaries.append(summary)
            links.append(link)

    except BaseException as E:
        print('Error in scraping news:', E)

    # Convert to arr
    return titles, summaries, links


def scrape_hemis(browser, url=hemi_url):
    
    """
    Scrape the Mars hemisphere names and image links from the search results of 
    the USGS website.

    browser : Splinter WebDriver
        Automated browser for scraping
    url : str, optional
        Website to scrape, by default 
        'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    Returns
    -------
    names : lst[str:4]
        Names of the 4 Mars hemispheres
    imgs : lst[str:4]
        Links to images of the 4 Mars hemispheres
    """

    # Scraped names and image links
    names, imgs = [], []

    try:
        # Visit the Mars hemisphere search results page
        browser.visit(url)    
    
        # Get the name and image url for all 4 hemispheres
        for i in range(4): # 4 hemispheres
            # Visit hemisphere page
            browser.is_element_present_by_css('div.description a.product-item', 1) # 1s delay
            hemisphere = browser.links.find_by_partial_text('Hemisphere Enhanced')[i] # page link
            hemisphere.click() # click hemisphere page
            browser.is_element_present_by_css('div.downloads a', 1)
            soup = Soup(browser.html, 'html.parser') # parse HTML

            # Add hemisphere name and image link to scraped lists
            img = soup.select_one('div.downloads a').attrs['href']
            name = soup.select_one('section.metadata h2.title').text.strip()
            name = name.split(' Hemisphere')[0] # filter for hemisphere name
            names.append(name)
            imgs.append(img)
            browser.back() # back to search results

    except BaseException as E:
        print('Error in scraping Mars hemispheres:', E)

    return names, imgs


def scrape_first_img(browser, url=img_url):
    
    """
    Scrape the most recent image in the Mars category of the NASA website.

    Parameters
    ----------
    browser : Splinter WebDriver
        Automated browser for scraping
    url : str, optional
        Website to scrape, by default 
        'https://www.jpl.nasa.gov/images?search=&category=Mars'

    Returns
    -------
    str
        URL of the featured Mars image
    """

    # Scraped image URL
    first_img = ''

    try:
        # Visit the Mars images page
        browser.visit(img_url)

        # Click the most recent image in the search results
        browser.is_element_present_by_css('section a.group', wait_time=1)
        browser.links.find_by_partial_href('images/').click()

        # Get the image URL
        img_soup = Soup(browser.html, 'html.parser')
        first_img = img_soup.find('img', class_='BaseImage').attrs['src']

    except BaseException as E:
        print('Error in scraping image:', E)

    return first_img


def scrape_img(browser, url=img_url):

    """
    Scrape the featured image in the Mars category of the NASA website. If 
    there is no featured image, scrape the most recent image.

    Parameters
    ----------
    browser : Splinter WebDriver
        Automated browser for scraping
    url : str, optional
        Website to scrape, by default 
        'https://www.jpl.nasa.gov/images?search=&category=Mars'

    Returns
    -------
    str
        URL of the featured Mars image
    """

    # Scraped image URL
    main_img = ''

    try:
        # Visit the Mars images page
        browser.visit(url)

        # Click the full image button on the featured image
        browser.is_element_present_by_css('a#full_image', 1)
        browser.links.find_by_partial_text('FULL IMAGE').click()

        # Click the more info buttom in the slide show
        browser.is_element_present_by_css('div.buttons a.button', 1)
        browser.links.find_by_partial_text('more info').click()

        # Parse the HTML
        browser.is_element_present_by_css('figure.lede a img', 1)
        soup = Soup(browser.html, 'html.parser')

        # Get the URL of the main image on the page
        main_img = soup.select_one('figure.lede a img').get('src')
        main_img = 'https://www.jpl.nasa.gov' + main_img

    except BaseException as E:
        print('Error in scraping featured image:', E)
        main_img = scrape_first_img(browser) # scrape first image instead

    return main_img


def scrape_facts(url=facts_url):

    """
    Scrape the main facts table about Mars and Earth from the space-facts 
    website.

    Parameters
    ----------
    url : str, optional
        Base url of facts website, by default 'https://space-facts.com/'

    Returns
    -------
    str
        HTML for the facts table
    """

    # URL for facts tables
    mars_url = url + 'mars/'
    earth_url = url + 'earth/'
    html = '' # html for the combined facts table

    # Scrape Mars and Earth facts
    try:
        # Get Mars facts
        mars_df = pd.read_html(mars_url)[0]
        mars_df.columns = ['Description', 'Mars']

        # Get earth facts
        earth_df = pd.read_html(earth_url)[0]
        earth_df.columns = ['Description', 'Earth']

        # Merge data
        df = pd.merge(mars_df, earth_df, on='Description').set_index('Description')
        df.index.name = None

        # Convert the df to HTML
        html = df.to_html()

    except BaseException as E:
        print('Error in scraping Mars and Earth facts:', E)

    return html


def scrape_all(headless=True, n_articles=3):

    """
    Scrape the following:
        [1] Title, summary, and url of the most recent Mars articles
        [2] Name and image url for each of the 4 Mars hemisphers
        [3] URL for featured, or most recent, Mars image
        [4] Main facts table about Mars and Earth

    Parameters
    ----------
    headless : bool, optional
        Whether to perform the scraping without displaying the browser, by 
        default True
    n_articles : int, optional
        Number of articles to scrape, by default 3. This is a pass-through 
        argument for the `scrape_news` function.

    Returns
    -------
    dict{8}
        Scraped data and the date and time it was scraped
    """

    # Start browser
    exe_path = '/usr/local/bin/chromedriver'
    browser = Browser('chrome', executable_path=exe_path, headless=headless)

    # Bootstrap table classes to apply to facts table
    table_classes = 'table table-striped table-bordered'

    # Call all scraping functions
    time = dt.datetime.now()
    titles, summaries, links = scrape_news(browser, n_articles=n_articles)
    names, images = scrape_hemis(browser)
    img = scrape_img(browser)
    facts = scrape_facts().replace('dataframe', table_classes)

    # Store the scraped data into a dictionary
    data = {
        'news_titles': titles,
        'news_summaries': summaries,
        'news_links': links,
        'hemisphere_names': names,
        'hemisphere_images': images,
        'featured_image': img,
        'facts': facts,
        'last_modified': time
    }

    # Quit browser and return the data
    browser.quit()
    return data


if __name__ == '__main__':
    print(scrape_all(headless=False))