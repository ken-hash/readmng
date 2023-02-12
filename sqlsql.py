import mysql.connector
import json
from datetime import datetime
from mysql.connector import pooling
from dotenv import load_dotenv
from os import getenv

class MySQLClass:
    def __init__(self):
        load_dotenv()
        self.password = getenv("piPass")
        self.user = getenv("piUser")
        self.mydb = pooling.MySQLConnectionPool(user=self.user , password=self.password , port=3307,
                                    host='192.168.50.10',
                                    database='kennSQL',pool_reset_session=True, pool_size=5,pool_name="UbuntuPool")


    def connect(self):
        self.conn = self.mydb.get_connection()
        self.mycursor = self.conn.cursor(buffered=True, dictionary=True)

    def disconnect(self):
        self.mycursor.close()
        self.conn.close()
    
    def getAllMangaList(self, options=None):
        if options is None:
            self.connect()
            sql = "SELECT * FROM mangaDatabase WHERE TRUE ORDER BY MangaTitle"
            self.mycursor.execute(sql,)
            mangaList = self.mycursor.fetchall()
            self.disconnect()
            return mangaList
        else:
            self.connect()
            sql = f"SELECT * FROM mangaDatabase WHERE {options}"
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

    def  insertValue(self, title, lastChapter, lastRead):
        self.connect()
        sql = f"INSERT INTO mangaDatabase(MangaTitle, LatestChapter, LastUpdated, LastRead) VALUES ('{title}','{lastChapter}','{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}','{lastRead}' )"
        self.mycursor.execute(sql,)
        self.conn.commit()
        self.disconnect()

