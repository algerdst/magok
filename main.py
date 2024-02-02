import requests
from bs4 import BeautifulSoup
import math
import re
import time
import json




user = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.686 YaBrowser/23.9.5.686 Yowser/2.5 Safari/537.36'

headers = {
    'user-agent': user
}

def parse(file):
    with open(file,'r',encoding='utf-8') as file:
        urls_array=[url.strip('\n') for url in file]
        length=len(urls_array)
        count=1
    with open('result.json','w', encoding='utf-8') as file:
        for url in urls_array:
            response=requests.get(url, headers=headers)
            if response.status_code!=200:
                continue
            soup=BeautifulSoup(response.text, 'lxml')
            title=soup.find('h1', class_='mt-3').text.strip()
            articles=soup.findAll('div', class_='info_art')
            artile1=articles[0].text.strip()
            artile2=articles[1].text.strip()
            div_picture=soup.find('div', class_='gallery')
            pictures_block=div_picture.findAll('img')
            pictures=[]
            for element in pictures_block:
                picture='https://magok.ru'+element['src']
                if picture not in pictures:
                    pictures.append(picture)
            pictures=pictures[:math.ceil(len(pictures)/2)]
            pictures='\n'.join(pictures)
            description=soup.find('div', class_='product__description').text.replace('Описание','').strip()
            availability=soup.find('div','product__availability').text.strip()
            breadcumb=soup.find('ul','bx-breadcrumb').text.replace('\n','')
            specifications = {}
            specifications_blocks=soup.findAll('div', class_='product__meta-item')
            for block in specifications_blocks:
                key=block.findNext('span', class_='specification-key').text.strip()
                value=block.findNext('span', class_='specification-val').text.replace('\n','').strip()
                specifications[key]=value
            #формирование цены
            price=soup.find('table', class_='discount-rules').findAll('tr')
            _RE_COMBINE_WHITESPACE = re.compile(r"\s+")
            total_price=''
            for row in price:
                # print(row.text.strip().replace('\n',' ').replace(' '*10,' '))
                my_str = _RE_COMBINE_WHITESPACE.sub(" ", row.text.strip()).strip()
                if my_str[-1]=='%':
                    my_str=my_str.split('р')
                    my_str[0]=my_str[0]+'Старая цена'
                    my_str[1]=my_str[1]+'Новая цена'
                    my_str[2]='Скидка'+my_str[2]
                    my_str=" ".join(my_str)
                total_price+=my_str+'\n'
            data={
                'title':title,
                'artile1':artile1,
                'artile2':artile2,
                'availability':availability,
                'total_price':total_price,
                'description':description,
                'pictures':pictures,
                'breadcumb':breadcumb,
                'url':url,
                'specifications':specifications
            }
            json.dump(data, file, indent=4, ensure_ascii=False)
            print(f'Данные из ссылки номер {count} добавлены, осталось обойти {length- count} ссылок')
            count += 1
            time.sleep(1)
parse('links.txt')
