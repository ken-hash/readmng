from bs4 import BeautifulSoup
import requests
from sqlsql import MySQLClass
import re
from download_model import DownloadObject
import os

class ReadMng:
    def __init__(self, title):
        if self.validateItems(title) == None:
            raise Exception(f'Error {title} is Invalid ')
        self.chapterNumLinks = []
        self.chapterlinks = []
        if os.name == 'nt':
            self.downloadPath =  os.path.join("\\\\192.168.50.11","Public-Manga","downloads")
        else:
            self.downloadPath = os.path.join('/','mnt','MangaPi','downloads')
        self.sql = MySQLClass()
        self.getAllAvailableChapters()

    #validate parameters return None if title is invalid
    def validateItems(self, title):
        if title == None:
            return None
        self.title = title
        self.url = f"https://www.readmng.com/{self.title}"
        if self.initWebScrape() is None:
            return None
        return True

    #check if title is found in readmanga
    def initWebScrape(self):
        data = requests.get(self.url).text
        self.soup = BeautifulSoup(data,'lxml')
        if self.soup.html.body.find('div',{'class':'cardFlex checkBoxFlex'}) is None:
            print('Invalid title/url. Please see listTitles.txt for titles to use')
            return None
        return True

    #grabs all chapters available for the manga in readmng 
    def getAllAvailableChapters(self):
        chapterBoxes = self.soup.html.body.findAll('div',{'class':'cardFlex checkBoxFlex'})
        for chapterBox in chapterBoxes:
            tempchapterlinks = chapterBox.findAll('a',{'href':True})
            for link in tempchapterlinks:
                chapterLinks = link.get('href')
                numChapterLinks = chapterLinks.split('/')[-1]
                self.chapterlinks.append(f"https://www.readmng.com{chapterLinks}")
                self.chapterNumLinks.append(numChapterLinks)

    #checks sql chapters csv and return missing chapters from available readmanga chapters
    def sqlLinks(self,extraInfo):
        selectedLinks = []
        if (extraInfo != '' and extraInfo is not None):
            #transform csv to list
            extraInfoList = extraInfo.replace(',,',',').split(',')
        else:
            extraInfoList = []
        s = set(extraInfoList)
        #missing chapters
        notchecked = [x for x in self.chapterNumLinks if x not in s]
        if len(notchecked)==0:
            return 
        else:
            #arrange the chapters not downloaded backwards so older chapter gets downloaded first
            notchecked.reverse()
            excludedChapters = self.sql.getChaptersExcluded(self.title)
            batch = []
            for x in range(len(notchecked)):
                if len(batch) >= 100:
                    self.sql.insertDownloadQueue(batch)
                    batch = []
                if x in excludedChapters:
                    continue
                chapterDict = {}
                chapterDict['link']= f"https://www.readmng.com/{self.title}/{notchecked[x]}/all-pages"
                imagesMatch = self.getImageLinks(chapterDict['link'])
                chapterDict['ImageList'] = []
                path = os.path.join(self.downloadPath,self.title,notchecked[x])
                if imagesMatch is None:
                    continue
                for match in imagesMatch:
                    #append download objects for each image for every chapter
                    link = match[0].replace('\\/','/')
                    if len(re.findall(r'.jp.?g$|.pn.?g$|.webp$',link, re.IGNORECASE))>0:
                        dlObject = self.downloadFactory(path, link)
                    chapterDict['ImageList'].append(dlObject)
                    batch.append(dlObject)
                selectedLinks.append(chapterDict)
            self.sql.insertDownloadQueue(batch)
        return selectedLinks

    #get all images founded in the manga page
    def getImageLinks(self, htmlLink):
        response = requests.get(htmlLink)
        imagesMatch =  re.findall(r'(https:.*?www\.funmanga\.com.*?\.(jp.?g|pn.?g|webp))', response.text, re.MULTILINE)
        if imagesMatch is None or len(imagesMatch) == 0:
            return None
        return imagesMatch

    #get all nondownloaded chapters based on title
    #if manga title isnt in database then insert
    def getChaptersToDownload(self):
        if self.sql.doesExist(self.title):
            chaptersChecked = self.sql.getExtraInformation(self.title) 
        else:
            self.sql.insertValue(self.title,"",self.chapterNumLinks[0])
            chaptersChecked = self.sql.getExtraInformation(self.title) 
        return self.sqlLinks(chaptersChecked)

    #creates download object from path and image url
    def downloadFactory(self, path, url):
            dlObject = DownloadObject()
            if os.name == 'nt':
                dlObject.title = path.split('\\')[-2]
                dlObject.chapterNum = path.split('\\')[-1]
                dlObject.fileId = url.split('/')[-1]
            else:
                dlObject.title = path.split('/')[-2]
                dlObject.chapterNum = path.split('/')[-1]
                dlObject.fileId = url.split('/')[-1]
            #save webp into jpg files
            if len(re.findall(r'webp',dlObject.fileId))>0:
                temp = re.sub('\.(webp|jpeg)','.jpg',dlObject.fileId)
                dlObject.fileId = temp
            dlObject.url = url
            return dlObject

class ReadMangaSite:
    def __init__(self):
        pass

    #returns all latest manga found in homepage
    def getHomePageAvailableManga(self):
        url = "https://www.readmng.com"
        html = requests.get(url).text
        soup = BeautifulSoup(html,'lxml')
        mangaupdates = soup.findAll("div", {"class": "miniListCard"})
        allAvailableMangas = {}
        for manga in mangaupdates:
            linkElem = manga.find("a",{"title":True})
            title = linkElem.get('href').replace('/','')
            allAvailableMangas[title]={'chapters':[]}
            try:
                chapterBox = manga.find("div", {"class": "chapterBox"})
                allAvailableChapters = chapterBox.findAll('a')
                for chapter in allAvailableChapters:
                    chapterCheck = chapter.get('href').split('/')[-1].strip()
                    allAvailableMangas[title]['chapters'].append(chapterCheck)
            except Exception as e:
                print(e)
                continue
        return allAvailableMangas


