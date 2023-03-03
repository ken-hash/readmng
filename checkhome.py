from read_mng import ReadMng, ReadMangaSite
import time
from sqlsql import MySQLClass
from random import randint
import os

'''
script to run on background that refreshes readmng
and download latest chapters 
'''

sql = MySQLClass()
mangaLatest = {}
while True:
    try:
        os.system('clear')
        print('Checking for new chapters...')
        mangaDict = {}
        #if a new manga get added then attempt to sync up first
        sqlList = sql.getAllMangaList('ExtraInformation = \',\'')
        mangaToSync = []
        if len(sqlList)==0:
            #else check all recent manga available in home page 
            sqlList = sql.getAllMangaList()
            availableManga = ReadMangaSite().getHomePageAvailableManga()
            mangaSQL = []
            #map all manga in sql to list
            for elem in sqlList:
                mangaSQL.append(elem['Title'])
            for manga in availableManga:
                #if manga that belongs to watch list is recently updated then sync
                if manga in mangaSQL:
                    mangaToSync.append(manga)
        else:
            for elem in sqlList:
                mangaToSync.append(elem['Title'])

        #sync
        for manga in mangaToSync:
            manga1 = ReadMng(manga)
            latestchapter = manga1.chapterNumLinks[0]
            #skip if already downloaded
            if manga in mangaLatest and 'latestChapter' in mangaLatest[manga] and mangaLatest[manga]['latestChapter']==latestchapter:
                continue
            else:
                if manga not in mangaLatest:
                    mangaLatest[manga]={}
                mangaLatest[manga]['latestChapter']=latestchapter
            #update latest chapter to new value
            sql.updateValue(manga,latestchapter,'no')
            mangaDict[manga]={'Chapters':[], 'latestchapter':latestchapter}
            print('Manga: \'',manga,'\' Latest Chapter is',latestchapter)
            mangaDict[manga]['Chapters'] = manga1.getChaptersToDownload()
    except Exception as e:
        print(e)
        time.sleep(500)
    #calls the script again in 10mins 
    time.sleep(600+randint(60,60*5))
