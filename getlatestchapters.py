import os 
from manga import Manga
import downloadimg 
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
    try:
        mangalist['manga'].append(splits[0])
        manga1 = Manga(splits[0])
        latestchapter = manga1.latestchapter()
        if splits[1].strip()!='':
            if latestchapter == splits[1].strip():
                mangalist['latestchapter'].append(splits[1].strip())
        else:
            mangalist['latestchapter'].append(latestchapter)
        if splits[2].strip()!='':
            mangalist['numlinks'].append(splits[2].strip())
            mangalist['links'].append(manga1.getchapterlinks(int(splits[2].strip())))
        else:
            mangalist['numlinks'].append(1)
            mangalist['links'].append(manga1.getchapterlinks(1))
    except:
        pass

print(mangalist)
counter = 0
for lines in mangalist['manga']:
    if counter<=len(mangalist['manga'])-1:
        newwrite+=lines+ "- " +str(mangalist['latestchapter'][counter]) + " - " + str(mangalist['numlinks'][counter]) + "\n"
        counter+=1

file = open(path, 'w', encoding='utf-8')
file.write(newwrite[:-1])
file.close()

for x in range(len(mangalist['manga'])):
    download1 = downloadimg.DownloadImages(mangalist['manga'][x],mangalist['latestchapter'][x])
    download1.downloadLinks(mangalist['links'][x])