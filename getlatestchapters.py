import os 
from manga import Manga
from downloadimg import Downloader
import re

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
    splits = lines.split('-')
    #creates Manga object using manga title
    manga1 = Manga(splits[0].strip())
    #If theres the an invalid line e.g. title it will be discarded and wont be added back into watchlist
    try:
        latestchapter = manga1.latestchapter()
        mangalist['manga'].append(splits[0].strip())
        print('Manga: \'',splits[0].strip(),'\' Latest Chapter is',latestchapter)
        mangalist['latestchapter'].append(latestchapter)
        #If only manga title is supplied it will only download the latest chapter
        if len(splits)<3:
                mangalist['links'].append(manga1.getchapterlinks('1'))
        else:
            #request multiple chapters if argument is supplied
            if splits[2].strip()!='':
                mangalist['links'].append(manga1.getchapterlinks(splits[2].strip()))
            else:
                mangalist['links'].append(manga1.getchapterlinks('1'))
    except:
        continue

for x in range(len(mangalist['manga'])):
    Downloader().downloadLinks(mangalist['links'][x])

#Reseting MangaTitle - Latest Chapter - Number of Chapters to download back to 1 into the watchlist.txt upon completion of downloads
counter = 0
for lines in mangalist['manga']:
    if counter<=len(mangalist['manga'])-1:
        newwrite+=lines+ " - " +str(mangalist['latestchapter'][counter]) + " - " + '1' + "\n"
        counter+=1

file = open(path, 'w', encoding='utf-8')
file.write(newwrite[:-1])
file.close()

os.system('pause')