import os 
from manga import Manga


"""
trial to read doc watchlist copy.
decipher what manga list is to watch and check if theres latest chapters data available
if not override it as non.
Title - None
"""
path = os.path.relpath('watchlist.txt')

file = open(path,'r', encoding='utf-8')
data = file.read()
file.close()

mangalist = {
    'manga':[],
    'latestchapter':[]
}

for lines in data.split('\n'):
    splits = lines.split('-')
    try:
        mangalist['manga'].append(splits[0])
        manga1 = Manga(splits[0])
        if splits[1].strip()!='':
            mangalist['latestchapter'].append(lines.split('-')[1].strip())
        else:
            mangalist['latestchapter'].append(manga1.getlatestchapternum())
    except:
        pass

newwrite = ''
counter = 0
for lines in mangalist['manga']:
    if counter<=len(mangalist['manga'])-1:
        newwrite+=lines+ "- " +str(mangalist['latestchapter'][counter]) +"\n"
        counter+=1

file = open(path, 'w', encoding='utf-8')
file.write(newwrite[:-1])
file.close()