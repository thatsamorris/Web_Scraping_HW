from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
from splinter import Browser
def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome")
def scrape():
    browser = init_browser()
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    html = browser.html
    soup = bs(html,"html.parser")

    elements = soup.find_all('div', class_=['rollover_description_inner', 'content_title'])
    news_p= []
    news_title = []
    i = 0
    for element in elements:
        try:
            if i % 2 == 0:
                news_p.append(element.get_text())
            else:

                news_title.append(element.find('a').text)

        except AttributeError as e:
            print(e)
        i += 1
    print(news_title[0])
    print(news_p[0])
    latest_article_headline = news_title[0]
    latest_article = news_p[0]

    jpl_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(jpl_url)

    browser.click_link_by_partial_text('FULL IMAGE')

    browser.find_by_css('a.fancybox-expand').click()


    jpl_html = browser.html
    jpl_soup = bs(jpl_html, 'html.parser')

    img_relative = jpl_soup.find('img', class_='fancybox-image')['src']
    image_path = f'https://www.jpl.nasa.gov{img_relative}'
    print(image_path)

    twitter_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(twitter_url)
    weather_html = browser.html
    weather_soup = bs(weather_html, 'html.parser')

    tweets = weather_soup.find('ol', class_='stream-items')
    mars_weather = tweets.find('p', class_="tweet-text").text
    print(mars_weather)

    facts_url = 'http://space-facts.com/mars/'
    browser.visit(facts_url)
    facts_html = browser.html
    facts_soup = bs(facts_html, 'html.parser')
    facts = facts_soup.find('table', class_='tablepress-id-mars')
    fact_names = facts.find_all('td', class_="column-1")
    fact_value = facts.find_all('td', class_="column-2")

    info = [] 
    values = []
    for fact in fact_names:
        info.append(fact.text)
    for value in fact_value:
        values.append(value.text)

    mars_table = pd.DataFrame({'info': info, 'value': values})
    mars_table_html = mars_table.to_html(header=False, index=False, classes="table table-hover")

    hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemisphere_url)
    hemisphere_html = browser.html
    hemisphere_soup = bs(hemisphere_html, 'html.parser')
    links = hemisphere_soup.find_all('a', class_='product-item')

    hemi_names = []
    for link in links:
        if link.text:
             hemi_names.append(link.text)

    browser.visit(hemisphere_url)
    hemisphere_html = browser.html
    hemisphere_soup = bs(hemisphere_html, 'html.parser')
    image_links = browser.find_by_css('a.product-item')

    hemi_img = []
    for i in range(len(image_links)):
        if i % 2 != 0:
            browser.visit(hemisphere_url)
            hemisphere_html = browser.html
            hemisphere_soup = bs(hemisphere_html, 'html.parser')
            image_links = browser.find_by_css('a.product-item')
            image_links[i].click()
            browser.find_link_by_text('Sample').first.click()
            browser.windows.current = browser.windows[-1]
            hemi_img_html = browser.html
            browser.windows.current = browser.windows[0]
            browser.windows[-1].close()
            hemi_img_soup = bs(hemi_img_html, 'html.parser')
            hemi_img_path = hemi_img_soup.find('img')['src']
            hemi_img.append(hemi_img_path)
        else:
            continue

    hemisphere_dicts = []
    for i in range(4):
        hemisphere_dict = {}
        hemisphere_dict['title'] = hemi_names[i]
        hemisphere_dict['url'] = hemi_img[i]
        hemisphere_dicts.append(hemisphere_dict)
    print(hemisphere_dicts)
    
    mars_data = { 'latest_headline':latest_article_headline,
                  'latest_news': latest_article, 
                  'featured_image_url':image_path, 
                  'Mars_weather': mars_weather, 
                  'Mars_facts': mars_table_html, 
                  'Hemispheres': hemisphere_dicts}
    return(mars_data)
    