from read_mng import ReadMng
from sqlsql import MySQLClass
import sys
from sort import Sort

mangaDict = {}

sql = MySQLClass()
newwrite = ''
sqlList = []
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 0:
        for arg in args:
            sqlList.append({'MangaTitle':arg})
    else:
        sqlList = sql.getAllMangaList()

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
    
Sort().main_sort()