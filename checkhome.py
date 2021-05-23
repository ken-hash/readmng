import os 
import requests
from bs4 import BeautifulSoup
from downloadimg import Downloader
import re
import time
import datetime

'''
This script will only monitor homepage for latest chapters for the titles in watchlist.txt
'''

#reads watchlist.txt to see what manga to download
path = os.path.relpath('watchlist2.txt')

file = open(path,'r', encoding='utf-8')
data = file.read()
file.close()

mangalist = {
    'manga':[],
    'mangalink':[],
    'latestchapter':[]
}

todownload = {
    'manga':[],
    'chapterlinks':[],
}

newwrite = ''

# if an entry in watchlist starts has # it wouldnt be included
for line in data.split('\n'):
    if re.search('#',line) or line=='\n' or line=='':
        newwrite+=line+'\n'
        continue
    splits = line.split(' -')
    title = splits[0].strip().lower().replace(' ','-')
    numChapters = splits[-1].strip()
    urlmanga = "https://www.readmng.com/"+ title
    mangalist['mangalink'].append(urlmanga)
    mangalist['manga'].append(title)
    mangalist['latestchapter'].append(splits[1].strip())

#program will keep running unless manually stopped

while True:
    #checks homepage if theres an update of any manga in the watchlist
    url = "https://www.readmng.com/"
    html = requests.get(url).text
    soup = BeautifulSoup(html,'lxml')
    mangaupdates = soup.findAll('dl')

    #creates new list for updated manga
    for x in mangaupdates:
        y = x.find('a',{'class':'manga_info'})
        if y is None:
            continue
        link = y.get('href')
        title = link.split('/')[-1]
        try:
            latestchapter = x.find('dd').text.split('-')[-1].strip()
        except:
            continue
        #checks all available titles in homepage with the titles gathered in watchlist.txt
        if link.lower() not in mangalist['mangalink'] or mangalist['latestchapter'][mangalist['manga'].index(title.lower())] == latestchapter:
            continue
        print(f'Found Manga Update of {title}')
        #adds the title to the download queue
        todownload['manga'].append(title)
        mangalist['latestchapter'][mangalist['manga'].index(title.lower())] = latestchapter
        chapterLink = f"{x.find('dd').find('a',{'href':True}).get('href')}/all-pages"
        todownload['chapterlinks'].append(chapterLink)

    if len(todownload['manga'])>0:
        #download only the updated manga titles
        Downloader().downloadLinks(todownload['chapterlinks'])
                
        counter = 0
        newwrite = ''
        for lines in mangalist['manga']:
            if counter<=len(mangalist['manga'])-1:
                newwrite+=lines+ " - " +str(mangalist['latestchapter'][counter]) + " - " + '1' + "\n"
                counter+=1

        file = open(path, 'w', encoding='utf-8')
        file.write(newwrite[:-1])
        file.close()
    #calls the script again in 10mins 
    time.sleep(600)
