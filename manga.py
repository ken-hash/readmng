import urllib3
from bs4 import BeautifulSoup
import os
import re
import random

class Manga:
    def __init__(self, title, numChapters):
        self.title = title.replace(' ','-')

        if numChapters == "" or numChapters is None:
            self.numChapters = 1
        else:
            self.numChapters = numChapters
        self.url = f"https://www.readmng.com/{self.title}"
        self.chapterNumLinks = []
        self.chapterlinks = []

        data = urllib3.PoolManager().request('Get',self.url).data
        self.soup = BeautifulSoup(data,'lxml')

        if self.soup.html.body.find('div',{'id':'chapters_container'}) is None:
            print('Invalid title/url. Please see listTitles.txt for titles to use')
            return
        self.getAllAvailableChapters()
           

    def getGaps(self):
        path = os.path.join(os.path.realpath('downloads'),self.title)
        #download only the latest chapter if directory doesnt exist
        if not os.path.isdir(path):
            print('New Manga found:',self.title)
            try:
                temp =  1 + int(self.numChapters)-1
            except:
                temp = 1
            return temp
        elif self.numChapters != "1":
            return int(self.numChapters)
        else:
            #list all chapters downloaded in the folder
            listitems = os.listdir(path)
            listitems.sort(key=lambda f: int(re.sub('\D', '', f)))
            indexLatest = self.chapterNumLinks.index(listitems[-1])
            return len(self.chapterNumLinks) -  len(self.chapterNumLinks)-indexLatest

    def getAllAvailableChapters(self):
        tempchapterlinks = self.soup.html.body.find('div',{'id':'chapters_container'}).findAll('a',{'href':re.compile(self.url,re.IGNORECASE)})
        for x in tempchapterlinks:
            chapterLinks = x.get('href')
            numChapterLinks = chapterLinks.split('/')[-1]
            self.chapterlinks.append(f"{chapterLinks}/all-pages")
            self.chapterNumLinks.append(numChapterLinks)

    def getSelectedLinks(self):
        selectedLinks = []
        if len(self.chapterlinks)<25:
            return self.chapterlinks
        else:
            for x in range(5):
                selectedLinks.append(self.chapterlinks[x])
            sampleList = random.sample(range(len(self.chapterlinks)-10), 15)
            for x in range(15):
                selectedLinks.append(self.chapterlinks[sampleList[x]+5])
            for x in range(5):
                selectedLinks.append(self.chapterlinks[x-5])
            return selectedLinks

    def getChaptersToDownload(self):
        if self.numChapters.strip().lower() == "all":
            return self.chapterlinks
        elif self.numChapters.strip().lower() == "minupdate":
            return self.getSelectedLinks()
        else:
            gaps = self.getGaps()
            return self.chapterlinks[-1:len(self.chapterlinks-gaps)]



