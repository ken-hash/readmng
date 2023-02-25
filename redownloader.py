import os
import sys
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
        if arg is not None:
            self.mangaFolder = os.path.join(self.baseFolder,arg)
            self.mangaFolders(self.mangaFolder)
        else:
            self.mangaFolder = self.baseFolder
            self.checkAllFolders()
        if len(self.mangaReDL)>0:
            for manga in self.mangaReDL:
                manga1 = ReadMng(manga)
                manga1.getChaptersToDownload()


    def checkAllFolders(self):
        for manga in os.listdir(self.mangaFolder):
            self.mangaFolders(os.path.join(self.mangaFolder, manga))

    def mangaFolders(self,mangaFolder):
        for chapter in os.listdir(mangaFolder):
            print(f'Checking {os.path.join(mangaFolder, chapter)}')
            self.checkFolderForEmpty(os.path.join(mangaFolder, chapter))

    def checkFolderForEmpty(self, folder):
        needsToRedownload = False
        #bug -- usually the last image is empty
        #so plenty of redownload for chapters that have empty image needs to be redownloaded and 
        #gets to appear in mangareader
        for item in os.listdir(folder):
            itemPath = os.path.join(folder,item)
            if os.path.getsize(itemPath)==0:
                if needsToRedownload == False:
                    needsToRedownload = True
                print(itemPath+' needs to be removed.')
                os.remove(itemPath)
        if needsToRedownload == True:
            chapterPath = os.path.dirname(folder)
            chapter = os.path.basename(folder)
            title = os.path.basename(chapterPath)
            extraInfo = self.sql.getExtraInformation(title)
            newExtraInfo = extraInfo.replace(f',{chapter},',',')
            #useless as redownload would update lastupdated anyways
            if title not in self.mangaReDL:
                self.mangaReDL.append(title)
            self.sql.updateExtraInformation(title,newExtraInfo,'off')
                    

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        reDL = Redownloader()
    for arg in args:
        reDL = Redownloader(arg)
    
    print(reDL.mangaFolder)