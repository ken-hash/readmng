from downloadimg import Downloader
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
downloader = Downloader(sql,'hide')
downloaded = {'chapterCounter':0}
while True:
    try:
        os.system('clear')
        print('Checking for new chapters...')
        print(f'Downloaded:\nManga:{len(downloaded.keys())-1}\nChaptersDownload:{downloaded["chapterCounter"]}')
        if 'error' in downloaded:
            print(f'Errors: {downloaded["error"]}')
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
                mangaSQL.append(elem['MangaTitle'])
            for manga in availableManga:
                #if manga that belongs to watch list is recently updated then sync
                if manga in mangaSQL:
                    mangaToSync.append(manga)
        else:
            for elem in sqlList:
                mangaToSync.append(elem['MangaTitle'])

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
            mangaDict[manga]['Chapters'] = manga1.getChaptersToDownload()
            print('Manga: \'',manga,'\' Latest Chapter is',latestchapter)

            #if the new chapter has already been downloaded or no new chapters then skip
            if mangaDict[manga]['Chapters'] is not None and len(mangaDict[manga]['Chapters'])>0:
                #increase num chapter downloaded 
                if manga not in downloaded:
                    downloaded[manga]={'chapters':len(mangaDict[manga]['Chapters'])}
                else:
                    downloaded[manga]['chapters']+=len(mangaDict[manga]['Chapters'])
                downloaded['chapterCounter']+=len(mangaDict[manga]['Chapters'])
                print(f'New chapter found for {manga}')
            
        for manga in mangaDict:
            if mangaDict[manga]['Chapters'] is not None:
                try:
                    for chapter in mangaDict[manga]['Chapters']:
                        downloader.downloadLinks(chapter['ImageList'])
                except Exception as e:
                    print(e)
                    continue
            #calls the script again

    except Exception as e:
        if 'error' not in downloaded:
            downloaded['error'] = e
        else:
            downloaded['error'] += f'\n{e}'
        print(e)
        time.sleep(500)
    #calls the script again in 10mins 
    time.sleep(600+randint(60,60*5))
