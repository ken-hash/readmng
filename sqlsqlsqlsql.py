import os 
from read_mng import ReadMng
from downloadimg import Downloader
import json
from sqlsql import MySQLClass
from sort import Sort

mangaDict = {}

sql = MySQLClass()
newwrite = ''
downloader = Downloader(sql,'hide')
if os.name == 'nt':
    sqlList = [
    #{'MangaTitle':'return-of-the-8th-class-magician'},
    #{'MangaTitle':'tensei-shitara-slime-datta-ken'},
    {'MangaTitle':'goblin-slayer'}
    ]
    '''
    #sqlList = sql.getAllMangaList('MangaTitle REGEXP \'^[u-w]\'')
    sqlList = sql.getAllMangaList('MangaTitle REGEXP \'^[a-r]\'')
    #sqlList = sql.getAllMangaList('MangaTitle REGEXP \'^[t-z]\' ORDER BY MangaTitle DESC')
    '''
else:
    #sqlList = sql.getAllMangaList()
    sqlList = [{'MangaTitle':'hanging-out-with-a-gamer-girl'}]


# if an entry in watchlist starts has # it wouldnt be included
for manga in sqlList:
    #creates Manga object using manga title
    try:
        manga1 = ReadMng(manga['MangaTitle'])
        #If theres the an invalid line e.g. title it will be discarded and wont be added back into watchlist
        latestchapter = manga1.chapterNumLinks[0]
        sql.updateValue(manga['MangaTitle'],latestchapter,'no')
        mangaDict[manga['MangaTitle']]={'links':[], 'latestchapter':latestchapter}
        mangaDict[manga['MangaTitle']]['chapterList'] = manga1.getChaptersToDownload()
        print('Manga: \'',manga['MangaTitle'].strip(),'\' Latest Chapter is',latestchapter)
    except Exception as e:
        print(e)

for manga in mangaDict:
    if mangaDict[manga]['chapterList'] is not None:
        try:
            for chapter in mangaDict[manga]['chapterList']:
                downloader.downloadLinks(chapter['ImageList'])
        except Exception as e:
            print(e)
            continue
summary = downloader.getSummary()
obj = json.dumps(summary)
print(json.dumps(obj, indent=3))
    
Sort().main_sort()