import os 
import errno
import requests
import re
import concurrent.futures
from tqdm import tqdm
from bs4 import BeautifulSoup
import shutil
from addChapters import MangaRequests
from donotdownload import donotdownload

class Downloader:
    def __init__(self, sql, options='show'):
        self.sql = sql
        if os.name == 'nt':
            self.downloadPath =  os.path.join("\\\\192.168.50.11","Public-Manga","downloads")
        else:
            self.downloadPath = os.path.join('/','mnt','MangaPi','downloads')
        self.options = options
        self.log = {}
        self.Summary = {'downloadedManga':0,
        'downloadedChapters':0,
        'failedDownloads':0,
        'skippedDownloads':0
        }
        self.req = MangaRequests()

    def validateLinks(self, links):
        if links is None:
            return False
        self.doNotDownload = donotdownload()
        return True

    #download function needing list containing links to be downloaded
    def downloadLinks(self, imageList):
        if self.validateLinks(imageList) is True:
            title = None
            chapternum = None
            chapterPath = None
            images = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for dlObject in imageList:
                    try:
                        title = dlObject.title
                        chapternum = dlObject.chapterNum
                        if chapterPath is None:
                            chapterPath = os.path.join(self.downloadPath,title,chapternum)
                        if self.checkChapterIsValid(title, chapternum) is False:
                            continue
                        if self.checkPathIsValid(chapterPath) is False:
                            raise(f"Error adding {chapterPath}")
                        filesInFolder = len(os.listdir(chapterPath))
                        imagesAvailable = len(imageList)
                        numChapToDownload = imagesAvailable - filesInFolder
                        if numChapToDownload == 0:
                            self.addToLog(title,'Skipped',chapternum)
                            break
                        images.append(os.path.basename(dlObject.fullPath))
                        if not os.path.exists(dlObject.fullPath):
                            executor.submit(self.download, dlObject)
                    except Exception as e:
                        print(e)
            if self.checkDownloadedItems(chapterPath, title, chapternum) is True:
                payload = ','.join(images)
                self.req.createPayload(title,chapternum,payload)
                req = self.req.sendRequest()
                if req.status_code not in [200,201]:
                    print(f'Error adding: {title} : {chapternum}')
                    print(f'{req.status_code}:{req.text}')
                elif req.status_code == 200:
                    print(f'Modified: {req.text}')

    def checkDownloadedItems(self, path, title, chapterNum):
        if self.checkItems(path):
            if self.options == "show":
                if os.name == 'nt':
                    os.system('cls')
                else:
                    os.system('clear')
            print(f"Downloaded: {chapterNum:>5s} of {title+'.':<20}")
            self.sql.appendExtraInformation(title, chapterNum)
            self.addToLog(title,'Chapters',chapterNum)
            return True
        else:
            self.addToLog(title,'Failed', chapterNum)
            print(f"Chapter {chapterNum:>5s} of {title+'.':<20} - Failed Download")
            self.doNotDownload.addToList(title, chapterNum)
            return False

    def addToLog(self, key, valueName, value):
        if key not in self.log:
            self.log[key]={}
        if valueName not in self.log[key]:
            self.log[key] = {valueName: [value]}
        else:
            self.log[key][valueName].append(value)

    def getSummary(self):
        for manga in self.log:
            self.Summary['downloadedManga'] += 1
            self.Summary['downloadedChapters'] += self.getDictionaryCounts(manga,'Chapters')
            self.Summary['failedDownloads'] += self.getDictionaryCounts(manga,'Failed')
            self.Summary['skippedDownloads'] += self.getDictionaryCounts(manga,'Skipped')
        return self.Summary

    def getDictionaryCounts(self,title,key):
        if key not in self.log[title]:
            return 0
        return len(self.log[title][key])

    def checkPathIsValid(self, path):
        if not os.path.isdir(path):
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                print(e)
                return False
        return True

    def checkChapterIsValid(self, title, chapterNum):
        noList = self.doNotDownload.getList(title)
        if chapterNum in noList:
            return False
        else:
            if len(re.findall(r',|:', chapterNum))>0:
                self.doNotDownload.addToList(title, chapterNum)
                return False
        return True

    def getImageLinks(self, htmlLink):
        response = requests.get(htmlLink)
        imagesMatch =  re.findall(r'(https:.*?www\.funmanga\.com.*?\.(jp.?g|pn.?g|webp))', response.text, re.MULTILINE)
        if imagesMatch is None or len(imagesMatch) == 0:
            return None
        return imagesMatch

    def checkItems(self, path):
        """
        Checks if the items in the folder `pathname` are all downloaded
        """
        hasAllFiles = False
        if not os.path.isdir(path):
            return False
        else:
            for item in os.listdir(path):
                if os.path.getsize(os.path.join(path,item))!=0:
                    hasAllFiles = True
        return hasAllFiles

    def download(self, dlObject):
        try:
            # download the body of response by chunk, not immediately
            response = requests.get(dlObject.url, stream=True)
            if self.options != 'show':
                with open(dlObject.fullPath, "wb") as f:
                    shutil.copyfileobj(response.raw, f)
            else:
                file_size = int(response.headers.get("Content-Length", 0))
                # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
                progress = tqdm(response.iter_content(1024), f"{dlObject.title} Chapter#{dlObject.chapterNum} Image#{dlObject.fileId}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
                with open(dlObject.fullPath, "wb") as f:
                    for data in progress:
                        f.write(data)
                        progress.update(len(data))
        except Exception as e:
            print(e)

    def downloadFactory(self, path, url):
        dlObject = DownloadObject()
        if os.name == 'nt':
            dlObject.title = path.split('\\')[-2]
            dlObject.chapterNum = path.split('\\')[-1]
            dlObject.fileId = url.split('/')[-1]
            dlObject.fullPath = os.path.join(path, url.split("/")[-1])
        else:
            dlObject.title = path.split('/')[-2]
            dlObject.chapterNum = path.split('/')[-1]
            dlObject.fileId = url.split('/')[-1]
            dlObject.fullPath = os.path.join(path, url.split("/")[-1])
        #save webp into jpg files
        if len(re.findall(r'webp',dlObject.fullPath))>0:
            temp = re.sub('\.(webp|jpeg)','.jpg',dlObject.fullPath)
            dlObject.fullPath = temp
        dlObject.url = url
        return dlObject

class DownloadObject:
    def __init__(self):
        self.title = None
        self.chapterNum = None
        self.fileId = None
        self.fullPath = None
        self.url = None