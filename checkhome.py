import os 
import requests
from bs4 import BeautifulSoup
from manga import Manga
from downloadimg import Downloader
import re
import time
import datetime

'''
This script will only monitor homepage for latest chapters for the titles in watchlist.txt
'''

#reads watchlist.txt to see what manga to download
path = os.path.relpath('watchlist.txt')

file = open(path,'r', encoding='utf-8')
data = file.read()
file.close()

mangalist = {
    'manga':[],
    'mangalink':[],
}

todownload = {
    'manga':[],
    'chapterlinks':[],
}

# if an entry in watchlist starts has # it wouldnt be included
for lines in data.split('\n'):
    if re.search('#',lines):
        newwrite+=lines+'\n'
        continue
    splits = lines.split('-')
    title = splits[0].strip()
    urlmanga = "https://www.readmng.com/"+ title.lower().replace(' ','-')
    mangalist['mangalink'].append(urlmanga)
    mangalist['manga'].append(title)

#program will keep running unless manually stopped

while True:
    newwrite = ''
    numupdates = 0

    #checks homepage if theres an update of any manga in the watchlist
    url = "https://www.readmng.com/"
    html = requests.get(url).text
    soup = BeautifulSoup(html,'lxml')
    mangaupdates = soup.findAll('a',{'class':'manga_info'})

    #creates new list for updated manga
    for x in mangaupdates:
        title = x.get('title')
        link = x.get('href')
        #checks all available titles in homepage with the titles gathered in watchlist.txt
        if link.lower() in mangalist['mangalink']:
            print(f'Found Manga Update of {title}')
            striptitle = link.split('.com/')[1].replace('-',' ')
            #adds the title to the download queue
            todownload['manga'].append(striptitle)
            numupdates+=1

    #download only the updated manga titles
    if numupdates >=1:
        for manga in todownload['manga']:
            manga1 = Manga(manga)
            todownload['chapterlinks'].append(manga1.getchapterlinks('1'))
        for x in range(len(todownload['manga'])):
            Downloader().downloadLinks(todownload['chapterlinks'][x])
            
    #calls the script again in 10mins 
    time.sleep(600)
