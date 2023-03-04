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
from sqlsql import MySQLClass
import sys

class AsuraManga:
    def __init__(self, title):
        chrome_options = uc.ChromeOptions()
        #headless seems cant go past cloudflare bot detection
        #chrome_options.add_argument('--headless')
        #chrome_options.add_argument("--log-level=3")
        #chrome_options.headless = True
        chrome_options.add_argument("start-maximized")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=chrome_options, service=ChromeService( 
	ChromeDriverManager().install()))
        if self.validateItems(title) is None:
            raise Exception(f'Error {title} is Invalid ')
        self.chapterNumLinks = {}
        self.sql = MySQLClass()
        self.getAllAvailableChapters()
        if os.name == 'nt':
            self.downloadPath =  os.path.join("\\\\192.168.50.11","Public-Manga","downloads")
        else:
            self.downloadPath = os.path.join('/','mnt','MangaPi','downloads')
        
        
    def wait_for_secure_connection(self, driver, timeout=10):
        try:
            WebDriverWait(driver, timeout).until(
                EC.url_contains("https://")
            )
        except Exception as e:
            print("Secure connection not established within specified timeout.")

    #validate parameters return None if title is invalid
    def validateItems(self, title):
        if title == None:
            return None
        #bug when /title is a valid manga
        self.title = title.replace('/','')
        prefix = r'1672760368'
        self.url = f"https://www.asurascans.com/manga/{prefix}-{self.title}"
        if self.initWebScrape() is None:
            self.url = f"https://www.asurascans.com/manga/{self.title}"
            if self.initWebScrape() is None:
                return None
        return True

    #check if title is found in asura
    def initWebScrape(self):
        self.driver.get(self.url)
        self.wait_for_secure_connection(self.driver)
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
    def getImageLinks(self, htmlLink,option='Ok'):
        self.driver.get(htmlLink)
        self.wait_for_secure_connection(self.driver)
        wait = WebDriverWait(self.driver, 10)
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
            images = readerarea.find_all('img',{'class':re.compile(r'wp-image-')})
        imagesMatch = []
        for image in images: 
            imagesMatch.append(image.get('src'))
        if imagesMatch is None or len(imagesMatch) == 0:
            return None
        return imagesMatch

    #get all nondownloaded chapters based on title
    #if manga title isnt in database then insert
    def getChaptersToDownload(self):
        if self.sql.doesExist(self.title,'AsuraScans'):
            chaptersChecked = self.sql.getExtraInformation(self.title,'AsuraScans') 
        else:
            orderedDict = OrderedDict(self.chapterNumLinks.items())
            orderedList = list(orderedDict)
            self.sql.insertValue(self.title,"",orderedList[0],'AsuraScans')
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

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 0:
        for arg in args:
            asura = AsuraManga(arg)
            asura.getChaptersToDownload()
            asura.driver.quit()
    else:
        sql = MySQLClass()
        mangas = sql.getAllMangaList(table='AsuraScans')
        for manga in mangas:
            asura = AsuraManga(manga['Title'])
            asura.getChaptersToDownload()
            asura.driver.quit()
