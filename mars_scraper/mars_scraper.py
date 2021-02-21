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


def scrape_news(browser, url=news_url, n_articles=3,
                article_html='ul.item_list li.slide'):

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
    article_html : str, optional
        HTML element containing articles, by default 'ul.item_list li.slide'

    Returns
    -------
    ndarray[`n_articles`, 3]
        Article names, summaries, and links
    """

    # Visit the site and allow 1 second for it to load
    browser.visit(url)
    browser.is_element_present_by_css(article_html, 1)

    # Parse the HTML
    soup = Soup(browser.html, 'html.parser')

    # Get the first `n_articles` articles
    try:
        # Articles
        articles = soup.select(article_html)
        scraped = []

        # Get the title, summary, and link for each article
        for i in range(n_articles):
            title = articles[i].select_one('div.content_title').get_text().strip()
            summary = articles[i].select_one('div.article_teaser_body').get_text().strip()
            link = articles[i].select_one('div.content_title a').attrs['href'] # partial url
            link = url.replace('/news/', '') + link # full url
            scraped.append([title, summary, link])
    except AttributeError:
        return None

    # Convert to arr
    scraped_arr = np.array(scraped)
    return scraped_arr


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

    # Visit the Mars hemisphere search results page
    browser.visit(url)
    
    
    # Hemisphere names and image links
    names, imgs = [], []

    # Scrape all 4 hemispheres
    try:
        for i in range(4): # 4 hemispheres

            # Visit hemisphere page
            browser.is_element_present_by_css(
                'div.description a.product-item', 1) # 1s delay
            hemisphere = browser.links.find_by_partial_text(
                'Hemisphere Enhanced')[i] # page link
            hemisphere.click() # click hemisphere page
            soup = Soup(browser.html, 'html.parser') # parse HTML

            # Scrape hemisphere name and image link
            img = soup.select_one('div.downloads a').attrs['href']
            name = soup.select_one('section.metadata h2.title').text
            name = name.split(' Hemisphere')[0]
            names.append(name)
            imgs.append(img)
            browser.back() # click back to search results
    except AttributeError:
        return None, None

    return names, imgs


def scrape_img(browser, url=img_url):

    """
    Scrape the featured image in the Mars category of the NASA website.

    Parameters
    ----------
    browser : Splinter WebDriver
        Automated browser for scraping
    url : str, optional
        Website to scrape, by default 
        'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    Returns
    -------
    str
        URL of the featured Mars image
    """

    # Visit the Mars images page
    browser.visit(url)

    # Click the full image button on the featured image
    browser.is_element_present_by_css('a#full_image', 1)
    browser.links.find_by_partial_text('FULL IMAGE').click()

    # Click the more info buttom in the slide show
    browser.is_element_present_by_css('div.buttons a.button', 1)
    browser.links.find_by_partial_text('more info').click()

    # Parse the HTML
    soup = Soup(browser.html, 'html.parser')

    # Get the URL of the main image on the page
    try:
        main_img = soup.select_one('figure.lede a img').get('src')
        main_img = 'https://www.jpl.nasa.gov' + main_img
    except AttributeError:
        return None

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

    # Scrape Mars facts
    mars_url = url + 'mars/'
    try:
        df = pd.read_html(mars_url)[0]
        df.columns = ['Description', 'Mars']
    except BaseException:
        return None

    # Scrape Earth facts
    earth_url = url + 'earth/'
    try:
        earth_df = pd.read_html(earth_url)[0]
        earth_df.columns = ['Description', 'Earth']
    except BaseException:
        return None

    # Merge data
    df = pd.merge(df, earth_df, on='Description').set_index('Description')
    df.index.name = None

    # Convert the df to HTML
    html = df.to_html()
    return html


def scrape_all(headless=True, n_articles=3):

    """
    Scrape the following from the NASA website:
        [1] Title and summary of the most recent Mars article
        [2] Featured Mars image
        [3] Main facts table about Mars

    Parameters
    ----------
    headless : bool, optional
        Whether to perform the scraping without displaying the browser, by 
        default True
    n_articles : int, optional
        Number of articles to scrape, by default 3. This is a pass-through 
        argument for the scrape_news function.

    Returns
    -------
    dict{5}
        Scraped data and the date and time it was scraped
    """

    # Initialize browser
    exe_path = '/usr/local/bin/chromedriver'
    browser = Browser('chrome', executable_path=exe_path, headless=headless)

    # Bootstrap table classes to apply to facts table
    table_classes = 'table table-striped table-bordered'

    # Call all scraping functions
    time = dt.datetime.now()
    titles, summaries, links = scrape_news(browser, n_articles=n_articles).T
    names, images = scrape_hemis(browser)
    img = scrape_img(browser)
    facts = scrape_facts().replace('dataframe', table_classes)

    # Store the scraped data into a dictionary
    data = {
        'news_titles': list(titles),
        'news_summaries': list(summaries),
        'news_links': list(links),
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
    # print(scrape_all(False))
    print(hemi_url)