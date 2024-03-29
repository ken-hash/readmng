from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService 
from selenium.webdriver.chrome.options import Options 
import undetected_chromedriver as uc 
import re
from collections import OrderedDict
from download_model import DownloadObject
import os
import datetime
from sqlsql import MySQLClass
import sys

class AsuraManga:
    def __init__(self, title, mangaLink=None):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=chrome_options, service=ChromeService( 
	ChromeDriverManager().install()))
        self.mangaLink = mangaLink
        if mangaLink is None:
            self.getMangaLinks()
        if self.validateItems(title) is None:
            raise Exception(f'Error {title} is Invalid ')
        self.chapterNumLinks = {}
        self.sql = MySQLClass()
        self.getAllAvailableChapters()
        if os.name == 'nt':
            self.downloadPath =  os.path.join("\\\\192.168.50.11","Public-Manga","downloads")
        else:
            self.downloadPath = os.path.join('/','mnt','MangaPi','downloads')
        
    def getMangaLinks(self):
        if self.mangaLink is not None:
            return self.mangaLink
        allMangaList = "https://www.asurascans.com/manga/list-mode/"
        try:
            self.driver.get(allMangaList)
            self.wait_for_secure_connection(self.driver)
        except:
            pass
        self.mangaLink = {}
        data = self.driver.page_source
        self.soup = BeautifulSoup(data,'lxml')
        mangaList = self.soup.html.body.find('div',{'class':'soralist'})
        mangas = mangaList.findAll('a',{'class':'series'})
        for manga in mangas:
            mangaLink = manga.get('href')
            match = re.search(r'https:\/\/www\.asurascans\.com\/manga\/\d+-([\w-]+)\/', mangaLink)
            if match:
                title = match.group(1)
            else:
                noPrefix  = re.search(r'https:\/\/www\.asurascans\.com\/manga\/([\w-]+)\/', mangaLink)
                if noPrefix:
                    title = noPrefix.group(1)
                else:
                    continue
            if title not in self.mangaLink:
                self.mangaLink[title] = mangaLink
        return self.mangaLink


    def wait_for_secure_connection(self, driver, timeout=1):
        try:
            wait = WebDriverWait(driver, timeout)
            wait.until(
                EC.url_contains("https://")
            )
        except Exception as e:
            raise Exception(f"Secure connection not established within specified timeout. {e}")

    #validate parameters return None if title is invalid
    def validateItems(self, title):
        if title == None:
            return None
        #bug when /title is a valid manga
        self.title = title.replace('/','')
        self.url = self.mangaLink[title]
        if self.initWebScrape() is None:
            return None
        return True

    #check if title is found in asura
    def initWebScrape(self):
        try:
            self.driver.get(self.url)
            self.wait_for_secure_connection(self.driver)
        except:
            pass
        data = self.driver.page_source
        self.soup = BeautifulSoup(data,'lxml')
        if self.soup.html.body.find('div',{'class':'releases'}) is None:
            return None
        return True

    #grabs all chapters in asura 
    def getAllAvailableChapters(self):
        chapterBoxes = self.soup.html.body.findAll('div',{'class':'chbox'})
        for chapterBox in chapterBoxes:
            chapterLinks = chapterBox.find('a',{'href':True}).get('href')
            match = re.search(r'(?<=ch-)\d?[^\/]+|(?<=ch(?:apter){1}-)\d?[^\/]+', chapterLinks)
            if match:
                numChapterLinks = match.group(0)
            else:
                text = chapterBox.find('span',{'class':'chapternum'}).text
                matchText = re.search(r'Chapter\s*(\d+)',text)
                if matchText:
                    numChapterLinks = matchText.group(1)
            self.chapterNumLinks[numChapterLinks] = chapterLinks

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
        notchecked = [x for x in self.chapterNumLinks.keys if x not in s]
        if len(notchecked)==0:
            return 
        else:
            for x in range(len(notchecked)):
                selectedLinks.append(self.chapterNumLinks[notchecked[x]])
        return selectedLinks

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
            for chap in notchecked:
                if len(batch) >= 100:
                    self.sql.insertDownloadQueue(batch)
                    batch = []
                if chap in excludedChapters:
                    continue
                chapterDict = {}
                #scrape all images from the chapter link
                imagesMatch = self.getImageLinks(self.chapterNumLinks[chap])
                chapterDict['ImageList'] = []
                path = os.path.join(self.downloadPath,self.title,chap)
                if imagesMatch is None:
                    continue
                for match in imagesMatch:
                    #append download objects for each image for every chapter
                    if len(re.findall(r'.jp.?g$|.pn.?g$|.webp$',match, re.IGNORECASE))>0:
                        dlObject = self.downloadFactory(path, match)
                    chapterDict['ImageList'].append(dlObject)
                    batch.append(dlObject)
                selectedLinks.append(chapterDict)
            self.sql.insertDownloadQueue(batch)
        return selectedLinks

    #get all images founded in the manga page
    def getImageLinks(self, htmlLink):
        try:
            self.driver.get(htmlLink)
            self.wait_for_secure_connection(self.driver)
        except:
            pass
        wait = WebDriverWait(self.driver, 5)
        #.wp-image-173795
        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'img[decoding="async"][loading="lazy"]')))
        except Exception as e:
            print(e)
            pass
        response = self.driver.page_source
        soup = BeautifulSoup(response,'lxml')
        readerarea = soup.find('div',{'id':'readerarea'})
        if readerarea is None:
            return None
        else:
            images = readerarea.find_all('img',{'decoding':'async'})
        imagesMatch = []
        if images is None:
            images = readerarea.find_all('img',{'class':re.compile(r'wp-image')})
        for image in images: 
            imagesMatch.append(image.get('src'))
        if imagesMatch is None or len(imagesMatch) == 0:
            return None
        return imagesMatch

    #get all nondownloaded chapters based on title
    #if manga title isnt in database then insert
    def getChaptersToDownload(self):
        orderedDict = OrderedDict(self.chapterNumLinks.items())
        orderedList = list(orderedDict)
        if len(orderedList)==0:
            return None
        if self.sql.doesExist(self.title,'AsuraScans'):
            chaptersChecked = self.sql.getExtraInformation(self.title,'AsuraScans') 
            self.sql.updateValue(self.title,orderedList[0],'no','AsuraScans')
        else:
            self.sql.insertValue(self.title,orderedList[0],table='AsuraScans')
            chaptersChecked = self.sql.getExtraInformation(self.title,'AsuraScans') 
        return self.sqlLinks(chaptersChecked)

    #creates download object from path and image url
    def downloadFactory(self, path, url):
        dlObject = DownloadObject()
        dlObject.title =  os.path.basename(os.path.dirname(path))
        dlObject.chapterNum = os.path.basename(path)
        dlObject.fileId = url.split('/')[-1]
        #save webp into jpg files
        if len(re.findall(r'webp',dlObject.fileId))>0:
            temp = re.sub('\.(webp|jpeg)','.jpg',dlObject.fileId)
            dlObject.fileId = temp
        dlObject.url = url
        return dlObject

class AsuraScansSite:
    def __init__(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=chrome_options, service=ChromeService( 
	ChromeDriverManager().install()))
        self.url = "https://www.asurascans.com/"
        self.sessionTime = datetime.datetime.now()
        self.sql = MySQLClass()

    #returns all latest manga found in homepage
    def getHomePageAvailableManga(self):
        self.driver.get(self.url)
        wait = WebDriverWait(self.driver, 5)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//body')))
        except Exception as e:
            print(e)
            pass
        response = self.driver.page_source
        soup = BeautifulSoup(response,'lxml')
        mangaupdates = soup.findAll("div", {"class": "utao styletwo"})
        allAvailableMangas = {}
        #lastUpdated = datetime.datetime.strptime(self.sql.getLastUpdated()['LastUpdated'], "%Y-%m-%d %H:%M:%S")
        dictManga = self.sql.getLastUpdated(table='AsuraScans')
        for manga in mangaupdates:
            linkElem = manga.find("a",{"title":True})
            link = linkElem.get('href')
            match = re.search(r'https:\/\/www\.asurascans\.com\/manga\/\d+-([\w-]+)\/', link)
            if match:
                title = match.group(1)
            else:
                noPrefix  = re.search(r'https:\/\/www\.asurascans\.com\/manga\/([\w-]+)\/', link)
                title = noPrefix.group(1)
            try:
                allAvailableChapters = manga.findAll('li')
                for chapter in allAvailableChapters:
                    chapterText = chapter.find('a').text
                    timedeltaText = chapter.find('span').text
                    timedeltaNum = re.match(r'\d+', timedeltaText).group(0)
                    timedeltaMatch = re.search(r"(\d+)\s+(min|mins|week|weeks|hour|hours|day|days)", timedeltaText)
                    if timedeltaMatch is None:
                        dateTimeAgo = self.sessionTime - datetime.timedelta(seconds=1)
                    else:
                        timeDelta = timedeltaMatch.group(2)
                        if timeDelta == 'min' or timeDelta == 'mins':
                            dateTimeAgo = self.sessionTime - datetime.timedelta(minutes=int(timedeltaNum))
                        elif timeDelta == 'hour' or timeDelta == 'hours':
                            dateTimeAgo = self.sessionTime - datetime.timedelta(hours=int(timedeltaNum))
                        elif timeDelta == 'day' or timeDelta == 'days':
                            dateTimeAgo = self.sessionTime - datetime.timedelta(days=int(timedeltaNum))
                    chapterMatch = re.search(r'Chapter\s*(\d+)',chapterText)
                    if chapterMatch:
                        chapterCheck = chapterMatch.group(1)
                    if title in dictManga:
                        if chapterCheck == dictManga[title][0]:
                            break
                        elif dictManga[title][1] >= dateTimeAgo:
                            break
                    if title not in allAvailableMangas:
                        allAvailableMangas[title]={'chapters':[]}
                    allAvailableMangas[title]['chapters'].append(chapterCheck)
            except Exception as e:
                print(e)
                continue
        self.driver.close()
        return allAvailableMangas


if __name__ == "__main__":
    args = sys.argv[1:]
    mangaList = None
    if len(args) > 0:
        for arg in args:
            asura = AsuraManga(arg, mangaList)
            if mangaList is None:
                mangaList = asura.getMangaLinks()
            asura.getChaptersToDownload()
            asura.driver.quit()
    else:
        asura = AsuraScansSite()
        newMangas = asura.getHomePageAvailableManga()
        for manga in newMangas:
            asura = AsuraManga(manga, mangaList)
            if mangaList is None:
                mangaList = asura.getMangaLinks()
            asura.getChaptersToDownload()
            asura.driver.quit()
        '''
        sql = MySQLClass()
        mangas = sql.getAllMangaList(options='ExtraInformation =\',\'',table='AsuraScans')
        for manga in mangas:
            asura = AsuraManga(manga['Title'], mangaList)
            if mangaList is None:
                mangaList = asura.getMangaLinks()
            asura.getChaptersToDownload()
            asura.driver.quit()
        '''

