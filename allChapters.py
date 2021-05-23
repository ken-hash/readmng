import os 
from refreshfolders import RefreshIt
from manga import Manga
from downloadimg import Downloader
import re


'''
This script will attempt to get all latest chapters of the titles in
watchlist.txt
'''
#reads watchlist.txt to see what manga to download
path = os.path.relpath('watchlist.txt')

file = open(path,'r', encoding='utf-8')
data = file.read()
file.close()

mangalist = {
    'manga':[],
    'latestchapter':[],
    'links':[],
}

newwrite = ''

# if an entry in watchlist starts has # it wouldnt be included
for lines in data.split('\n'):
    if re.search('#',lines):
        newwrite+=lines+'\n'
        continue
    splits = lines.split(' -')
    #creates Manga object using manga title
    try:
        numChapters = splits[-1]
        manga1 = Manga(splits[0].strip(), numChapters)

        #If theres the an invalid line e.g. title it will be discarded and wont be added back into watchlist
        latestchapter = manga1.chapterNumLinks[0]
        mangalist['manga'].append(splits[0].strip())
        print('Manga: \'',splits[0].strip(),'\' Latest Chapter is',latestchapter)
        mangalist['latestchapter'].append(latestchapter)
        #If only manga title is supplied it will only download the latest chapter
        if len(splits)<3:
                mangalist['links'].append(manga1.chapterlinks[0])
        else:
            #request multiple chapters if argument is supplied
            if splits[-1].strip()!='':
                mangalist['links'].append(manga1.getChaptersToDownload())
            else:
                mangalist['links'].append(manga1.chapterlinks[0])
    except:
        print(f"Error reading {lines}")



for x in range(len(mangalist['manga'])):
    try:
        Downloader().downloadLinks(mangalist['links'][x])
    except:
        continue

#Reseting MangaTitle - Latest Chapter - Number of Chapters to download back to 1 into the watchlist.txt upon completion of downloads
counter = 0
for lines in mangalist['manga']:
    if counter<=len(mangalist['manga'])-1:
        newwrite+=lines+ " - " +str(mangalist['latestchapter'][counter]) + " - " + 'MinUpdate' + "\n"
        counter+=1

file = open(path, 'w', encoding='utf-8')
file.write(newwrite[:-1])
file.close()

RefreshIt().refresh()
os.system('pause')