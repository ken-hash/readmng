import os 
import requests
import re
import concurrent.futures
from tqdm import tqdm
import shutil
import sort 
from addChapters import MangaRequests

class Downloader:
    def __init__(self, sql, options='show'):
        self.sql = sql
        if os.name == 'nt':
            self.downloadPath =  os.path.join("\\\\192.168.50.11","Public-Manga","downloads")
            self.path_regex = re.compile(r'^(?:(?:[a-zA-Z]:|\\\\[\w\-.]+\\[\w.$\-+!()\[\]]+)(\\|\\(?:[^\\/:*?"<>|\r\n]+))+)$')
        else:
            self.path_regex = re.compile(r'^(/[\w\-\.]+)+/?$')
            self.downloadPath = os.path.join('/','mnt','MangaPi','downloads')
        self.options = options
        self.req = MangaRequests()
        self.sort = sort.Sort()


    def validateLinks(self, links):
        if links is None:
            return False
        return True

    #downloads list of download objects
    def downloadLinks(self, downloadList):
        if self.validateLinks(downloadList) is True:
            title = None
            chapternum = None
            chapterPath = None
            dictMangaDownloaded = {}
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for dlObject in downloadList:
                    try:
                        title = dlObject.title
                        chapternum = dlObject.chapterNum
                        filename = dlObject.fileId
                        if title not in dictMangaDownloaded:
                            dictMangaDownloaded[title]= {"Chapters": {}}
                        if chapternum not in dictMangaDownloaded[title]["Chapters"]:
                            dictMangaDownloaded[title]["Chapters"][chapternum] = []
                        if filename not in dictMangaDownloaded[title]["Chapters"][chapternum]:
                            dictMangaDownloaded[title]["Chapters"][chapternum].append(filename)
                        if re.search(r"https?:\/\/(?:www\.)?(?:asurascans\.com|asura\.gg)", dlObject.url):
                            table = "AsuraScans"
                        else:
                            table = "ReadMng"
                        dictMangaDownloaded[title]["Table"] = table
                        chapterPath = os.path.join(self.downloadPath,title,chapternum)
                        #skip if chapter is in exclusion list
                        if self.checkChapterIsValid(title, chapternum) is False:
                            continue
                        #skip if folder is not valid 
                        if self.checkPathIsValid(chapterPath) is False:
                            self.sql.addChapterExcluded(title,chapternum)
                            continue
                        #if number of files in folder matches the number of images in chapters then skip
                        path = os.path.join(self.downloadPath,title,chapternum,dlObject.fileId)
                        #else check if file needs to be downloaded is in folder then download
                        if not os.path.exists(path):
                            executor.submit(self.download, dlObject)
                    except Exception as e:
                        print(e)
            #check and update manga's chapter image values
            for manga in dictMangaDownloaded:
                for chapter in dictMangaDownloaded[manga]["Chapters"]:
                    chapterPath = os.path.join(self.downloadPath,manga,chapter)
                    table = dictMangaDownloaded[manga]["Table"]
                    if self.checkDownloadedItems(chapterPath, manga, chapter, table) is True:
                        imgList = dictMangaDownloaded[manga]["Chapters"][chapter]
                        payload = ','.join(imgList)
                        self.req.createPayload(manga,chapter,payload)
                        req = self.req.sendRequest()
                        #if show error if the chapter and downloaded objects are already in db
                        if req.status_code not in [200,201]:
                            print(f'Error adding: {title} : {chapternum}')
                            print(f'{req.status_code}:{req.text}')
                        elif req.status_code == 200:
                            print(f'Modified: {req.text}')

    #update manga db when the download has atleast one image downloaded
    def checkDownloadedItems(self, path, title, chapterNum, table):
        if self.checkItems(path):
            if self.options == "show":
                if os.name == 'nt':
                    os.system('cls')
                else:
                    os.system('clear')
            print(f"Downloaded: {chapterNum:>5s} of {title+'.':<20}")
            self.sql.appendExtraInformation(title, chapterNum, table)
            return True
        else:
            print(f"Chapter {chapterNum:>5s} of {title+'.':<20} - Failed Download")
            self.sql.addChapterExcluded(title,chapterNum)
            return False

    def checkPathIsValid(self, path):
        if self.path_regex.match(path) is None:
            return False
        if not os.path.isdir(path):
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                print(e)
                return False
        return True

    def checkChapterIsValid(self, title, chapterNum):
        noList = self.sql.getChaptersExcluded(title)
        if chapterNum in noList or len(re.findall(r',|:', chapterNum))>0:
            self.sql.addChapterExcluded(title, chapterNum)
            return False
        return True

    #check if downloaded folder has alteast one downloaded image
    def checkItems(self, path):
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
            path = os.path.join(self.downloadPath,dlObject.title,dlObject.chapterNum,dlObject.fileId)
            if self.options != 'show':
                with open(path, "wb") as f:
                    shutil.copyfileobj(response.raw, f)
            else:
                file_size = int(response.headers.get("Content-Length", 0))
                # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
                progress = tqdm(response.iter_content(1024), f"{dlObject.title} Chapter#{dlObject.chapterNum} Image#{dlObject.fileId}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
                with open(path, "wb") as f:
                    for data in progress:
                        f.write(data)
                        progress.update(len(data))
        except Exception as e:
            raise (e)

