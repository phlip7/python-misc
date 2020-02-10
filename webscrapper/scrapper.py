import pandas as pd
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import unicodedata
import time 


"""
get the url for each items found in the search results 
"""
def get_items_links(base_url):
    items_links = []
    #paginate following this syntax : https://deals.jumia.ci/abidjan/appartements-a-vendre?page=1é
    for i in range(10):
        page = base_url+'?page='+str(i+1)
        request_result = requests.get(page)
        #The code we are looking for is 200. A 200 code means that it is okay to scrape the desired web page
        #print(request_result.status_code)
        soup = BeautifulSoup(request_result.content, 'lxml')
        div_res = soup.find('div', {'id':'search-results'})
        div_art = div_res.find_all('article')

        for row in div_art:
            link = row.find('a').get('href')
            items_links.append(link)
    return items_links

"""
get tag value
"""
def get_tag_value(res):
    value = res.text.strip() if res else 'n/a'
    '''
    I need to normalize unicode data in src variable to remove umlauts, accents etc. 
    For example “naïve café” would be changed to “naive cafe”. 
    I take this step to avoid any errors while printing out and storing ascii values:
    '''
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    return value


def get_item_details(items_links):
    item = {}
    items = []
    for i in range(len(items_links)):
        link = links[i]
        full_link = 'https://deals.jumia.ci'+link
        #print(full_link)
        response = requests.get(full_link)
        soup = BeautifulSoup(response.content,'lxml')

        #get dimensions
        dims = soup.find('div', {'class':'post-attributes'}).find_all('h3')
        item['rooms'] = get_tag_value(dims[0].find('span')) if len(dims)>0 else 'n/a'
        item['surface'] = get_tag_value(dims[1].find('span')) if len(dims)>1 else 'n/a'

        #get desciption
        desc = soup.find('div', {'class':'post-text-content'})
        #item['description'] = get_tag_value(desc.find('p')).encode('utf-8').decode('ascii', 'ignore') 

        #get price
        price = soup.find('span', {'class':'price'})
        item['price'] = price.find('span', {'itemprop':'price'})['content']
        item['currency'] = get_tag_value(price.find('span', {'itemprop':'priceCurrency'}))

        #get seller details
        seller_dtl = soup.find('div', {'class':'seller-details'})
        item['seller'] = get_tag_value(seller_dtl.find('span', {'itemprop':'name'}))
        item['location'] = get_tag_value(seller_dtl.find('span', {'itemprop':'addressLocality'}))
        item['published_at'] = seller_dtl.find('time')['datetime']

        #get category and url
        cat = soup.find('span', {'itemprop':'brand'})
        category = cat.find('meta')['content'] 
        item['category'] = unicodedata.normalize('NFKD', category).encode('ascii', 'ignore')
        item['url'] = full_link

        items.append(item.copy())
        time.sleep(1)
    
    df_realestate = pd.DataFrame(items)
    return df_realestate



url = 'https://deals.jumia.ci/abidjan/appartements-a-vendre'

links = get_items_links(url)
data = get_item_details(links)

print(data.head(20))
