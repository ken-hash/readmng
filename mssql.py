from datetime import datetime
import pyodbc
import os
from dotenv import load_dotenv
from os import getenv

class MSSQLClass:
    def __init__(self):
        load_dotenv()
        self.password = getenv("ubuntuPass")
        self.user = getenv("ubuntuUser")
        # Trusted Connection to Named Instance

    def connect(self):
        if os.name == 'nt':
            self.connection = pyodbc.connect(DRIVER='{ODBC Driver 17 for SQL Server}',SERVER='192.168.50.11',IntegratedSecurity='no',DATABASE='UbuntuServer',Trusted_Connection='no',user=self.user,password=f'{{{self.password}}}')
        else:
            self.connection = pyodbc.connect(DRIVER='{ODBC Driver 17 for SQL Server}',SERVER='192.168.50.11',IntegratedSecurity='no',DATABASE='UbuntuServer',Trusted_Connection='no',user=self.user,password=f'{{{self.password}}}')
        self.mycursor = self.connection.cursor()

    def disconnect(self):
        self.mycursor.close()
        self.connection.close()
    
    def getAllMangaLogs(self, title):
        self.connect()
        sql = f'''
            SELECT s.MangaLogId, s.DateTime, s.MangaId, t.MangaChaptersId, t.MangaChapter, t.Path, u.Name 
            FROM dbo.MangaLogs s 
            INNER JOIN dbo.MangaChapters t ON t.MangaChaptersId = s.MangaChaptersId 
            INNER JOIN dbo.Mangas u ON s.MangaId = u.MangaId
            WHERE s.Status = \'Added\' AND u.Name =\'{title}\' ORDER BY DATETIME ASC
            '''
        self.mycursor.execute(sql,)
        mangaList = self.mycursor.fetchall()
        results = [dict(zip([column[0] for column in self.mycursor.description], row)) for row in mangaList]
        self.disconnect()
        return results

    def UpdateMangaLogDateTime(self, mangaLogId, datetime):
        self.connect()
        sql = f'''
            UPDATE dbo.MangaLogs SET DateTime = \'{datetime}\' WHERE MangaLogId = \'{mangaLogId}\'
        '''
        self.mycursor.execute(sql,)
        self.connection.commit()
        self.disconnect()

    def getAllMangas(self):
        self.connect()
        sql = f"SELECT * FROM dbo.Mangas"
        self.mycursor.execute(sql,)
        mangaChapterList = self.mycursor.fetchall()
        results = [dict(zip([column[0] for column in self.mycursor.description], row)) for row in mangaChapterList]
        self.disconnect()
        return results
