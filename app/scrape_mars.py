from bs4 import BeautifulSoup as bs
import requests
import pymongo
from splinter import Browser
import pandas as pd
import datetime as dt
import time
import re
import pprint

def scrape_all():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_paragraph = mars_news(browser)
    featured_image_link = featured_image(browser)


    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image_link,
        "hemispheres": hemispheres(browser),
        "weather": twitter_weather(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()     
    }

    browser.quit()

    return data

def mars_news(browser):
    # NASA Mars news
    try:
        url='https://mars.nasa.gov/news/'
        browser.visit(url)

        browser.is_element_present_by_css("ul.item_list li.slide", wait_time=5)

        html = browser.html
        soup = bs(html, 'html.parser')

        first_title_div = soup.find('div', class_="content_title")
        news_title = first_title_div.text

        first_subtitle_div = soup.find('div', class_="article_teaser_body")
        news_p = first_subtitle_div.text

        return news_title, news_p
    except BaseException:
        return None, None

def featured_image(browser):
    try:
        # JPL Mars Space Images - Featured Image
        url='https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
        browser.visit(url)

        html = browser.html
        soup = bs(html, 'html.parser')

        featured_image = soup.find('article', class_= "carousel_item")
        featured_image_url= 'https://www.jpl.nasa.gov' + (featured_image["style"]).split("'")[1]

        return featured_image_url
    except BaseException:
        return None

def hemispheres(browser):
    try:
        # Mars Hemispheres
        urls=['https://astrogeology.usgs.gov/search/map/Mars/Viking/cerberus_enhanced', 'https://astrogeology.usgs.gov/search/map/Mars/Viking/schiaparelli_enhanced', 'https://astrogeology.usgs.gov/search/map/Mars/Viking/syrtis_major_enhanced', 'https://astrogeology.usgs.gov/search/map/Mars/Viking/valles_marineris_enhanced']

        hemisphere_image_urls = []

        for url in urls:
            browser.visit(url)

            html = browser.html
            soup = bs(html, 'html.parser')

            image = soup.find('img', class_= "wide-image")
            image_url= 'https://astrogeology.usgs.gov' + image["src"]

            title = soup.find('h2', class_= "title")
            title_text = title.text

            hemisphere_image_urls.append({'title': title_text, 'img_url': image_url})

        return hemisphere_image_urls
    except:
        return None

def twitter_weather(browser):
    try:
        # Mars Weather
        url='https://twitter.com/marswxreport?lang=en'
        browser.visit(url)
        time.sleep(5)

        html = browser.html
        soup = bs(html, 'html.parser')

        mars_weather_tweet = soup.find('div', attrs={"class": "tweets", "data-name": "Mars Weather"})
        
        mars_weather = mars_weather_tweet.find('p', 'tweet-text').get_text()
    except AttributeError:
        pattern = re.compile(r'sol')
        mars_weather = soup.find('span', text=pattern).text

    return mars_weather


def mars_facts():
    try:
        url = 'https://space-facts.com/mars/'
        tables = pd.read_html(url)

        df = tables[0]
        df.columns = ['Description', 'Value']
        df.set_index('Description', inplace=True)

        html_table = df.to_html()
        return html_table
        
    except BaseException:
        return None
    return

if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(scrape_all())
