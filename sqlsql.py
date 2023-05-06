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
    
    def getAllMangaList(self, options='True', table='ReadMng'):
        self.connect()
        sql = f"SELECT * FROM {table} WHERE {options} ORDER BY Title"
        self.mycursor.execute(sql,)
        mangaList = self.mycursor.fetchall()
        self.disconnect()
        return mangaList

    def doesExist(self,manga,table='ReadMng'):
        self.connect()
        sql = f"SELECT COUNT(1) FROM {table} WHERE Title = %s"
        self.mycursor.execute(sql,(manga,))
        res = self.mycursor.fetchone()
        if res is not None and res['COUNT(1)']>0:
            self.disconnect()
            return True
        else:
            self.disconnect()
            return False

    def  insertValue(self, title, lastChapter, Folder=None, table='ReadMng'):
        self.connect()
        if Folder is None:
            sql = f"INSERT INTO {table}(Title, LatestChapter, LastUpdated) VALUES ('{title}','{lastChapter}','{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}')"
        else:
            sql = f"INSERT INTO {table}(Title, Folder, LatestChapter, LastUpdated) VALUES ('{title}','{Folder}','{lastChapter}','{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}')"
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
        if res is None or res['COUNT(1)'] == 0:
            sql = "INSERT ExcludeManga(MangaTitle,Chapter) VALUES (%s,%s)"
            self.mycursor.execute(sql,(title,chapter,))
            self.conn.commit()
        self.disconnect()

    '''
    Chapter Points
    '''
    def updateValue(self, title, lastChapter,option='yes', table='ReadMng'):
        if self.doesExist(title, table) is False:
            self.insertValue(title, lastChapter, table=table)
        self.connect()
        if option=='no':
            sql = f"UPDATE {table} SET LatestChapter ='{lastChapter}' WHERE Title = '{title}'"
        else:
            sql = f"UPDATE {table} SET LatestChapter ='{lastChapter}', LastUpdated='{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}', ExtraInformation = CONCAT(ExtraInformation, '{lastChapter},') WHERE Title = '{title}'"
        self.mycursor.execute(sql,)
        self.conn.commit()
        self.disconnect()

    def getExtraInformation(self, title, table='ReadMng'):
        if self.doesExist(title,table) is False:
            self.insertValue(title, 0, table=table)
        self.connect()
        sql = f"SELECT ExtraInformation FROM {table} WHERE Title = %s"
        self.mycursor.execute(sql,(title,))
        extraInfo = self.mycursor.fetchone()
        self.disconnect()
        return extraInfo["ExtraInformation"]

    def updateExtraInformation(self, title, extraInformation, update='on', table='ReadMng'):
        self.connect()
        if (update=='off'):
            sql = f"UPDATE {table} SET ExtraInformation ='{extraInformation.replace(',,',',')}' WHERE Title = '{title}'"
        else:
            sql = f"UPDATE {table} SET ExtraInformation ='{extraInformation.replace(',,',',')}', LastUpdated='{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}' WHERE Title = '{title}'"
        self.mycursor.execute(sql,)
        self.conn.commit()
        self.disconnect()

    def appendExtraInformation(self, title, extraInformation,table='ReadMng'):
        self.connect()
        sql = f"UPDATE {table} SET ExtraInformation = REPLACE(ExtraInformation,',,',',') WHERE Title = %s"
        self.mycursor.execute(sql,(title,))
        self.conn.commit()
        sql = f"UPDATE {table} SET LastUpdated='{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}', ExtraInformation = CONCAT(ExtraInformation, '{extraInformation},') WHERE Title = '{title}'"
        self.mycursor.execute(sql,)
        self.conn.commit()
        self.disconnect()

    def getLastUpdated(self, condition='True', table='ReadMng'):
        self.connect()
        sql = f"SELECT Title, LatestChapter, LastUpdated FROM {table} WHERE {condition} ORDER BY Title"
        self.mycursor.execute(sql,)
        res = self.mycursor.fetchall()
        dictManga = {}
        for row in res:
            dictManga[row['Title']] = (row['LatestChapter'], row['LastUpdated'])
        return dictManga
    
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

    def getDownloadQueue(self, limit=10):
        self.connect()
        rowCountsql = "SELECT COUNT(1) FROM DownloadQueue"
        self.mycursor.execute(rowCountsql,)
        res = self.mycursor.fetchone()
        if res is None:
            return None
        sqlTemp = f'SELECT ID, Title, ChapterNum, COUNT(1) as count FROM DownloadQueue GROUP BY Title, ChapterNum ORDER BY ID ASC LIMIT %s'
        self.mycursor.execute(sqlTemp,(limit,))
        queue = []
        tempTable = self.mycursor.fetchall()
        sql = 'SELECT * FROM DownloadQueue WHERE Title = %s AND ChapterNum = %s'
        for group in tempTable:
            self.mycursor.execute(sql,(group['Title'], group['ChapterNum'],))
            queue += self.mycursor.fetchall()
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