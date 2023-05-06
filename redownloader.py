import os
import sys
from asura_manga import AsuraManga
from read_mng import ReadMng
from sqlsql import MySQLClass

class Redownloader:
    def __init__(self,arg=None) -> None:
        if os.name == 'nt':
            self.downloadPath =  os.path.join("\\\\192.168.50.11","Public-Manga","downloads")
        else:
            self.downloadPath = os.path.join('/','mnt','MangaPi','downloads')
        self.baseFolder = self.downloadPath
        self.sql = MySQLClass()
        self.mangaReDL = []
        self.asuraReDL = []
        if arg is not None:
            self.mangaFolder = os.path.join(self.baseFolder,arg)
            self.mangaFolders(self.mangaFolder)
        else:
            self.mangaFolder = self.baseFolder
            self.checkAllFolders()
        print('Redownloading Chapters')
        if len(self.mangaReDL)>0:
            for manga in self.mangaReDL:
                manga1 = ReadMng(manga)
                manga1.getChaptersToDownload()
        if len(self.asuraReDL)>0:
            for manga in self.asuraReDL:
                manga1 = AsuraManga(manga)
                manga1.getChaptersToDownload()


    def checkAllFolders(self):
        for manga in os.listdir(self.mangaFolder):
            if self.sql.doesExist(manga):
                self.mangaFolders(os.path.join(self.mangaFolder, manga))
            else:
                self.mangaFolders(os.path.join(self.mangaFolder, manga), table='AsuraScans')

    def mangaFolders(self,mangaFolder, table='ReadMng'):
        for chapter in os.listdir(mangaFolder):
            #print(f'Checking {os.path.join(mangaFolder, chapter)}')
            self.checkFolderForEmpty(os.path.join(mangaFolder, chapter), table)

    def checkFolderForEmpty(self, folder, table):
        needsToRedownload = False
        #bug -- usually the last image is empty
        #so plenty of redownload for chapters that have empty image needs to be redownloaded and 
        #gets to appear in mangareader
        for item in os.listdir(folder):
            itemPath = os.path.join(folder,item)
            if (os.path.getsize(itemPath)>5*1024 and os.path.getsize(itemPath)<7*1024) or os.path.getsize(itemPath)==0*1024:
                if needsToRedownload == False:
                    needsToRedownload = True
                print(itemPath+' needs to be removed.')
                os.remove(itemPath)
        if needsToRedownload == True:
            chapterPath = os.path.dirname(folder)
            chapter = os.path.basename(folder)
            title = os.path.basename(chapterPath)
            extraInfo = self.sql.getExtraInformation(title,table=table)
            newExtraInfo = extraInfo.replace(f',{chapter},',',')
            #useless as redownload would update lastupdated anyways
            if title not in self.mangaReDL and table=='ReadMng':
                self.mangaReDL.append(title)
            if title not in self.asuraReDL and table=='AsuraScans':
                self.asuraReDL.append(title)
            self.sql.updateExtraInformation(title,newExtraInfo,'off', table=table)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        reDL = Redownloader()
    for arg in args:
        reDL = Redownloader(arg)
    
    print(reDL.mangaFolder)