from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
from lxml.html import fromstring 
from itertools import cycle
import traceback
# Create your views here.
import requests
from bs4 import BeautifulSoup
import re
import json
def to_get_proxies():
    # website to get free proxies
    url = 'https://free-proxy-list.net/' 
 
    response = requests.get(url)
    
    parser = fromstring(response.text)
    # using a set to avoid duplicate IP entries.
    proxies = set() 
 
    for i in parser.xpath('//tbody/tr')[:10]:
 
        # to check if the corresponding IP is of type HTTPS
        if i.xpath('.//td[7][contains(text(),"yes")]'):
 
            # Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0],
                              i.xpath('.//td[2]/text()')[0]])
 
            proxies.add(proxy)
    return proxies

result = []
def get_detail(url):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    page = requests.get(url, headers=header)
    assert page.status_code == 200
    soup = BeautifulSoup(page.content, 'lxml')

    # title = soup.find('span', attrs={'id': 'productTitle'}).text.strip()  # to get the text, and strip is used to remove all the leading and trailing spaces from a string.
    try:
        discount_percent = soup.find('td', attrs={'class': 'a-span12 a-color-price a-size-base'}).find('span', attrs={
            'class': 'a-color-price'}).text.split('(')[1].replace(')', '')
    except AttributeError:
        discount_percent = ''

    if discount_percent:
        try:
            original_price = soup.find('span', attrs={'class': 'a-price a-text-price a-size-base'}).find('span', attrs={
                'class': 'a-offscreen'}).text.strip()
        except AttributeError:
            original_price = ''
        discount_save = soup.find('td', attrs={'class': 'a-span12 a-color-price a-size-base'}).find('span', attrs={
            'class': 'a-color-price'}).find('span', attrs={'class': 'a-offscreen'}).text.strip()
    else:
        original_price = ''
        discount_save = ''
        pass

    try:
        current_price = soup.find('span', attrs={'class': 'a-price a-text-price a-size-medium apexPriceToPay'}).find(
            'span', attrs={'class': 'a-offscreen'}).text.strip()
    except AttributeError:
        current_price = ''
    try:
        review_count = soup.find('span', attrs={'id': 'acrCustomerReviewText'}).text.strip()
    except AttributeError:
        review_count = ''
    try:
        feature_bullet = soup.find('div', attrs={'id': 'feature-bullets'}).find('ul', attrs={
            'class': 'a-unordered-list a-vertical a-spacing-mini'}).find_all('li')
        sv_feature = []
        for li in feature_bullet:
            text = li.find('span', attrs={'class': 'a-list-item'})
            features = str(text.string).strip()
            if 'None' in features:
                pass
            else:
                sv_feature.append(features)
    except AttributeError:
        sv_feature = ''
    data = soup.select(
        "#imageBlock_feature_div > script:nth-child(2)")  # using selector, right click > copy > copy selector
    try:
        script_text = data[0].text  # remove html tag
        # use regex to pull out the relevant json string
        json_str = re.search('{(.+)}', script_text)[0].replace("\'", '"').replace("null",
                                                                                  '"null"')  # replace single quote ' to double quote "
        json_obj = json.loads(json_str)
        images_url = []
        for i in json_obj['initial']:
            images_hires = i['hiRes']
            images_large = i['large']
            if images_hires is None:
                images_url.append(images_large)
            else:
                images_url.append(images_hires)
    except IndexError:
        images_url = ''

    try:
        available_stock = soup.find('div', attrs={'id': 'availability'}).find('span').text.strip()
    except AttributeError:
        available_stock = ''
    try:
        asin = soup.find(id='averageCustomerReviews').get('data-asin')
    except AttributeError:
        asin = url.split('/dp/')[1].replace('/', '')
    try:
        description = soup.find('div', attrs={'id': 'productDescription'}).text.replace('\n', '').strip()
    except AttributeError:
        description = ''
    try:
        rating = soup.find('span', attrs={'data-hook': 'rating-out-of-text'}).text.strip()
    except AttributeError:
        rating = ''
    manufacturer = ''
    try:
        feature_bullet = soup.find('div', attrs={'id': 'detailBullets_feature_div'}).find('ul', attrs={
            'class': 'a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list'}).find_all('li')
        sv_feature = []
        if len(feature_bullet) > 1:
            for li in feature_bullet:
                    text = li.find('span', attrs={'class': 'a-list-item'}).find('span:nth-child(1)')
                    if text is not None:
                        manufacturer = str(text.string).strip()
                        print(manufacturer)
                        if 'None' in features:
                            pass
    except AttributeError:
        manufacturer = ''



    goal = {
        'asin': asin,
        # 'title': title,
        'price': current_price,
        'rating': rating,
        'review': review_count,
        'stock': available_stock,
        'feature': sv_feature,
        'description': description,
        'discount_percent': discount_percent,
        'original_price': original_price,
        'discount_save': discount_save,
        'images_url': images_url,
        'manufacturer':manufacturer,
    }
    # print(goal)

    # result.append(goal)
    return goal

def view_url(request):

    proxies = to_get_proxies()
    proxyPool = cycle(proxies) 
    
    HEADERS = ({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                            'Accept-Language': 'en-US, en;q=0.5'})
 

    # productcsv = open('product.csv', 'w+')
    # writer = csv.writer(productcsv)
    # writer.writerow(('Description','manufacturer'))
    csvFile = open('test.csv', 'w+')
    writer = csv.writer(csvFile)
    writer.writerow(('product','anchor', 'price','ASIN','Product Description','Manufacturer','rating','review'))
    for i in range(2,21):
        url=f'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{i}'
        webpage = requests.get(url, headers=HEADERS)
        while webpage.status_code!=200:
            webpage = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(webpage.content, "lxml")
        content = soup.prettify()
        mydivs = soup.find_all("div",{"data-component-type":"s-search-result"})
        record = []
        rating_div=''
        if len(mydivs):
            for div in mydivs:
                asin = div.get('data-asin')
                
                product_div = div.find("div",{"class":"a-section a-spacing-none puis-padding-right-small s-title-instructions-style"})
                h2_div = product_div.findChild('h2',{"class":"a-size-mini a-spacing-none a-color-base s-line-clamp-2"},recursive=True)
                product_url_anchor = h2_div.findChild('a',{"class":"a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"},recursive=True).get('href')
                product_url_anchor_text = h2_div.findChild('a',{"class":"a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"},recursive=True).text
                url=f'https://www.amazon.in/dp/{asin}'
                result = get_detail(url)
                rating_div = div.findChild('div',{"class":'a-section a-spacing-none a-spacing-top-micro'},recursive=True)
                
                rating = rating_div.find('span',{"class":"a-size-base"},recursive=True).text
                price = div.find('div',{"class":'sg-row'}).find('span',{"class":"a-offscreen"}).text
                writer.writerow((product_url_anchor_text,product_url_anchor,price,asin,result['description'],result['manufacturer'],result['rating'],result['review']))
                record.append({'product':product_url_anchor_text,'anchor':product_url_anchor,"rating":result['rating'],'price':result['price']})
   
    # product_description=''
    # text =''
    # description = []
    # manufacturer =[]
    # with open("test1.csv", mode='r') as csv_file:
    #         csv_reader = csv.DictReader(csv_file)
    #         for row in csv_reader:
    #             product_url = row['ASIN']
                
                
                # for i in range(1, 11):
                    
                #     try:
                #         proxy = next(proxyPool)
                        
                #         webpage = requests.get(url,headers=HEADERS,proxies={"http": proxy, "https": proxy})
                #         soup = BeautifulSoup(webpage.content, "lxml")
                #         product_description = soup.find("ul",{"class":"a-unordered-list a-vertical a-spacing-mini"},recursive=True)
                #         if product_description:
                #             for li in product_description:
                #                 text += li.text
                #         product_details_div = soup.find("div",{"id":"detailBullets_feature_div"})
                #         product_details_li = product_details_div.find_all('li')
                #         product_manufacturer = product_details_li[2].find('span',{"class":"a-list-item"}).find('span')[1].text
                #         description.append(product_description)
                #         manufacturer.append(product_manufacturer)
                #     except BaseException as e:
                #         print(e)    
            # while product_description is None:
            #     webpage = requests.get(url, headers=HEADERS)
            # product_description = soup.find("ul",{"class":"a-unordered-list a-vertical a-spacing-mini"},recursive=True)
            # soup = BeautifulSoup(webpage.content, "lxml")
            # content = soup.prettify()
            # product_description_li = product_description.descendants
            # text = ''
            # dictionary = {'Description':description,'manufacturer':manufacturer}
            # df = pd.DataFrame(dictionary)
            # df.to_csv('product.csv')
    return render(request,'respons.html',{'content':record})


                



