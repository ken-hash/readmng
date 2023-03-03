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
            sqlList.append({'Title':arg})
    else:
        sqlList = sql.getAllMangaList()

for manga in sqlList:
    try:
        #if manga is valid then append all missing chapters to the download queue
        manga1 = ReadMng(manga['Title'])
        latestchapter = manga1.chapterNumLinks[0]
        sql.updateValue(manga['Title'],latestchapter,'no')
        print('Manga: \'',manga['Title'].strip(),'\' Latest Chapter is',latestchapter)
        mangaDict[manga['Title']]={'links':[], 'latestchapter':latestchapter}
        mangaDict[manga['Title']]['chapterList'] = manga1.getChaptersToDownload()
    except Exception as e:
        print(e)
    
Sort().main_sort()