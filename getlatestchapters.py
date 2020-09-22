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

# if an entry in watchlist starts has # it would be included
for lines in data.split('\n'):
    if re.search('#',lines):
        newwrite+=lines+'\n'
        continue
    splits = lines.split('-')
    #creates Manga object from manga title and adding it to mangalist
    manga1 = Manga(splits[0].strip())
    try:
        latestchapter = manga1.latestchapter()
        mangalist['manga'].append(splits[0].strip())
        print('Manga: \'',splits[0].strip(),'\' Latest Chapter is',latestchapter)
        mangalist['latestchapter'].append(latestchapter)
        #checks if format is followed Would automatically download latest chapter if only Manga Title is suppolied
        if len(splits)<3:
                mangalist['links'].append(manga1.getchapterlinks('1'))
        else:
            #if third value is supplied e.g. download 5 chapters or download 'All'
            if splits[2].strip()!='':
                mangalist['links'].append(manga1.getchapterlinks(splits[2].strip()))
            else:
                mangalist['links'].append(manga1.getchapterlinks('1'))
    except:
        continue

print(mangalist)

for x in range(len(mangalist['manga'])):
    Downloader().downloadLinks(mangalist['links'][x])

#Writing MangaTitle - Lastest Chapter - Number of Chapters to download back to 1 into the watchlist.txt
counter = 0
for lines in mangalist['manga']:
    if counter<=len(mangalist['manga'])-1:
        newwrite+=lines+ " - " +str(mangalist['latestchapter'][counter]) + " - " + '1' + "\n"
        counter+=1

file = open(path, 'w', encoding='utf-8')
file.write(newwrite[:-1])
file.close()

