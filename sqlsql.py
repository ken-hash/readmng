from datetime import datetime
from mysql.connector import pooling
from dotenv import load_dotenv
from os import getenv
from download_model import DownloadObject

class MySQLClass:
    def __init__(self):
        load_dotenv()
        self.password = getenv("piPass")
        self.user = getenv("piUser")
        self.mydb = pooling.MySQLConnectionPool(user=self.user , password=self.password , port=3307,
                    host='192.168.50.10',
                    database='kennSQL',pool_reset_session=True, pool_size=15,pool_name="piPool")

    '''
    Manga Points
    '''
    def connect(self):
        self.conn = self.mydb.get_connection()
        self.mycursor = self.conn.cursor(buffered=True, dictionary=True)

    def disconnect(self):
        self.mycursor.close()
        self.conn.close()
    
    def getAllMangaList(self, options='True'):
        self.connect()
        sql = f"SELECT * FROM mangaDatabase WHERE {options} ORDER BY MangaTitle"
        self.mycursor.execute(sql,)
        mangaList = self.mycursor.fetchall()
        self.disconnect()
        return mangaList

    def doesExist(self,manga):
        self.connect()
        date = datetime.now().strftime('%Y-%M-%d')
        sql = f"SELECT COUNT(1) FROM mangaDatabase WHERE mangaTitle = '{manga}'"
        self.mycursor.execute(sql,)
        if (self.mycursor.fetchone() is not None):
            self.disconnect()
            return True
        else:
            self.disconnect()
            return False

    def  insertValue(self, title, lastChapter, lastRead):
        self.connect()
        sql = f"INSERT INTO mangaDatabase(MangaTitle, LatestChapter, LastUpdated, LastRead) VALUES ('{title}','{lastChapter}','{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}','{lastRead}')"
        self.mycursor.execute(sql,)
        self.conn.commit()
        self.disconnect()

    '''
    Exclusion Points
    '''
    def getChaptersExcluded(self, title):
        self.connect()
        sql = "SELECT * FROM ExcludeManga WHERE MangaTitle = %s"
        self.mycursor.execute(sql,(title,))
        chapterExclusionList = self.mycursor.fetchall()
        chapterExcluded = [obj['Chapter'] for obj in chapterExclusionList]
        self.disconnect()
        return chapterExcluded

    def addChapterExcluded(self,title,chapter):
        self.connect()
        rowCountsql = "SELECT COUNT(1) FROM ExcludeManga WHERE MangaTitle = %s AND Chapter = %s"
        self.mycursor.execute(rowCountsql,(title,chapter,))
        res = self.mycursor.fetchone()
        if res is None:
            sql = "INSERT ExcludeManga(MangaTitle,Chapter) VALUES (%s,%s)"
            self.mycursor.execute(sql,(title,chapter,))
            self.conn.comit()
        self.disconnect()

    '''
    Chapter Points
    '''
    def updateValue(self, title, lastChapter,option='yes'):
        if self.doesExist(title) is False:
            self.insertValue(title, lastChapter, 0)
        self.connect()
        if option=='no':
            sql = f"UPDATE mangaDatabase SET LatestChapter ='{lastChapter}' WHERE MangaTitle = '{title}'"
        else:
            sql = f"UPDATE mangaDatabase SET LatestChapter ='{lastChapter}', LastUpdated='{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}', ExtraInformation = CONCAT(ExtraInformation, '{lastChapter},') WHERE MangaTitle = '{title}'"
        self.mycursor.execute(sql,)
        self.conn.commit()
        self.disconnect()

    def getExtraInformation(self, title):
        if self.doesExist(title) is False:
            self.insertValue(title, 0, 0)
        self.connect()
        sql = f"SELECT ExtraInformation FROM mangaDatabase WHERE MangaTitle = '{title}'"
        self.mycursor.execute(sql,)
        extraInfo = self.mycursor.fetchone()
        self.disconnect()
        return extraInfo["ExtraInformation"]

    def updateExtraInformation(self, title, extraInformation, update='on'):
        self.connect()
        if (update=='off'):
            sql = f"UPDATE mangaDatabase SET ExtraInformation ='{extraInformation.replace(',,',',')}' WHERE MangaTitle = '{title}'"
        else:
            sql = f"UPDATE mangaDatabase SET ExtraInformation ='{extraInformation.replace(',,',',')}', LastUpdated='{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}' WHERE MangaTitle = '{title}'"
        self.mycursor.execute(sql,)
        self.conn.commit()
        self.disconnect()

    def appendExtraInformation(self, title, extraInformation):
        self.connect()
        sql = f"UPDATE mangaDatabase SET ExtraInformation = REPLACE(ExtraInformation,',,',',') WHERE MangaTitle = '{title}'"
        self.mycursor.execute(sql,)
        self.conn.commit()
        sql = f"UPDATE mangaDatabase SET LastUpdated='{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}', ExtraInformation = CONCAT(ExtraInformation, '{extraInformation},') WHERE MangaTitle = '{title}'"
        self.mycursor.execute(sql,)
        self.conn.commit()
        self.disconnect()

    '''
    Queue Points
    '''
    def insertDownloadQueue(self, downloadObjectList):
        if downloadObjectList is None or len(downloadObjectList)==0:
            return
        sql_obj_list = self.serialize_obj(downloadObjectList)
        self.connect()
        sql = f"INSERT INTO DownloadQueue(Title, ChapterNum, FileId, Url) VALUES (%s, %s ,%s, %s)"
        self.mycursor.executemany(sql,sql_obj_list)
        self.conn.commit()
        self.disconnect()

    def getDownloadQueue(self, limit=100):
        self.connect()
        rowCountsql = "SELECT COUNT(1) FROM DownloadQueue"
        self.mycursor.execute(rowCountsql,)
        res = self.mycursor.fetchone()
        if res is None:
            return None
        rowCount = res['COUNT(1)']
        if rowCount > limit:
            sql = f"SELECT * FROM DownloadQueue ORDER BY ChapterNum ASC LIMIT {limit} "
        else:
            sql = "SELECT * FROM DownloadQueue ORDER BY ChapterNum ASC "
        self.mycursor.execute(sql,limit)
        queue = self.mycursor.fetchall()
        self.disconnect()
        return queue

    def deleteDownloadQueue(self, downloadObjectList):
        sql = "DELETE FROM DownloadQueue WHERE ID = %s LIMIT %s"
        batchSize = 10
        if batchSize > len(downloadObjectList):
            batchSize = len(downloadObjectList) 
        idList = [obj['ID'] for obj in downloadObjectList]
        self.connect()
        for i in range(0,len(idList), batchSize):
            batch = idList[i:i+batchSize]
            self.mycursor.executemany(sql, [(id, batchSize) for id in batch])
        self.conn.commit()
        self.disconnect()

    '''
    Helper functions
    '''
    def serialize_obj(self, obj_list):
        sql_obj_list = []
        for obj in obj_list:
            sql_obj = (obj.title, obj.chapterNum, obj.fileId, obj.url)
            sql_obj_list.append(sql_obj)
        return sql_obj_list

    def deserialize_sql_dict(self, sql_dict):
        obj_list = []
        for row in sql_dict:
            obj = DownloadObject()
            obj.title = row['Title']
            obj.fileId = row['FileId']
            obj.chapterNum = row['ChapterNum']
            obj.url = row['Url']
            obj_list.append(obj)
        return obj_list