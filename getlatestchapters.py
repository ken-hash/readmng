import os 
from manga import Manga
from downloadimg import Downloader
import re

path = os.path.relpath('watchlist.txt')

file = open(path,'r', encoding='utf-8')
data = file.read()
file.close()

mangalist = {
    'manga':[],
    'latestchapter':[],
    'numlinks':[],
    'links':[],
}

newwrite = ''

for lines in data.split('\n'):
    if re.search('#',lines):
        newwrite+=lines+'\n'
        continue
    splits = lines.split('-')
    print(splits)
    mangalist['manga'].append(splits[0])
    manga1 = Manga(splits[0].strip())
    latestchapter = manga1.latestchapter()
    mangalist['latestchapter'].append(latestchapter)
    try:
        if splits[2].strip()!='':
            mangalist['numlinks'].append(splits[2].strip())
            mangalist['links'].append(manga1.getchapterlinks(splits[2].strip()))
        else:
            mangalist['numlinks'].append(1)
            mangalist['links'].append(manga1.getchapterlinks(1))
    except:
        if len(splits)<3:
            mangalist['numlinks'].append(1)
            mangalist['links'].append(manga1.getchapterlinks(1))
        else:
            pass


print(mangalist)
counter = 0
for lines in mangalist['manga']:
    if counter<=len(mangalist['manga'])-1:
        newwrite+=lines+ "- " +str(mangalist['latestchapter'][counter]) + " - " + '1' + "\n"
        counter+=1

file = open(path, 'w', encoding='utf-8')
file.write(newwrite[:-1])
file.close()

for x in range(len(mangalist['manga'])):
    Downloader().downloadLinks(mangalist['links'][x])