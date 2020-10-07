import os 
import requests
from bs4 import BeautifulSoup
from manga import Manga
import re

#reads watchlist.txt to see what manga to download
path = os.path.relpath('watchlist.txt')

file = open(path,'r', encoding='utf-8')
data = file.read()
file.close()

mangalist = {
    'manga':[],
    'mangalink':[],
}

newwrite = ''
numupdates = 0

# if an entry in watchlist starts has # it wouldnt be included
for lines in data.split('\n'):
    if re.search('#',lines):
        newwrite+=lines+'\n'
        continue
    splits = lines.split('-')
    manga1 = Manga(splits[0].strip())
    mangalist['mangalink'].append(manga1.geturl())
    mangalist['manga'].append(splits[0].strip())

url = "https://www.readmng.com/"
html = requests.get(url).text
soup = BeautifulSoup(html,'lxml')
mangaupdates = soup.findAll('a',{'class':'manga_info'})

for x in mangaupdates:
    title = x.get('title')
    link = x.get('href')
    if link in mangalist['mangalink']:
        print(f'Found Manga Update of {title}')
        numupdates+=1

path = os.path.realpath('getlatestchapters.exe')
print(path)
if numupdates >1:
    os.system(path)

os.system('pause')