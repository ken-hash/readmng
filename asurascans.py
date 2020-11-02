"""
will download everything in asurascans.com
"""
import os
from asuraManga import Manga
from bs4 import BeautifulSoup
import requests
from asuradownloadimg import Downloader

homeUrl = "https://asurascans.com/"
mangalistUrl = "https://asurascans.com/manga/"

mangalist = {
    'manga':[],
    'latestchapter':[],
    'links':[],
    'baselink':[],
}


url=mangalistUrl
while(url!=None):
    data = requests.get(url).text
    soup = BeautifulSoup(data,'lxml')
    title = soup.html.body.findAll('div',{'class':'bsx'})
    for x in title:
        mangalist['manga'].append(x.find('div',{'class':"tt"}).text.strip())
        mangalist['baselink'].append(x.find('a').get('href'))
    pagenum = soup.html.body.find('div',{'class':'hpage'})
    if pagenum.get_text().strip() != 'Previous':
        url = mangalistUrl + pagenum.find('a').get('href')
    else:
        url = None

for x in mangalist['manga']:
    manga1 = Manga(x)
    try:
        latestchapter = manga1.latestchapter()
        print('Manga: \'',x,'\' Latest Chapter is',latestchapter)
        mangalist['latestchapter'].append(latestchapter)
        mangalist['links'].append(manga1.getchapterlinks('All'))
    except:
        continue

for x in range(len(mangalist['manga'])):
    Downloader().downloadLinks(mangalist['links'][x])