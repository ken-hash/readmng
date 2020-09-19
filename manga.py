import urllib3
from bs4 import BeautifulSoup
import re

#class to gather information of manga and get latestchapter of the manga

class Manga:

    def __init__(self, title):
        self.title = title
        self.chapterlinks = []
        self.url = None
        if self.url == None:
            self.generateurl()
        else:
            pass

        if len(self.chapterlinks)<1:
            data = urllib3.PoolManager().request('Get',self.url).data
            soup = BeautifulSoup(data,'html.parser')
            self.numchapters = 1
            tempchapterlinks = soup.html.body.find('div',{'id':'chapters_container'}).findAll('a',{'href':re.compile(self.url)})
            for x in tempchapterlinks:
                self.chapterlinks.append(x.get('href'))

    def generateurl(self):
        titlenew = self.title.lower().replace(' ','-')
        self.url = "https://www.readmng.com/"+titlenew

    def latestchapter(self):
        return self.chapterlinks[0].split('/')[-1]

    def latestchapterlink(self):
        newlink = self.chapterlinks[0]+'/all-pages'
        return newlink

    def getallchapters(self):
        return len(self.chapterlinks)

    def getchapterlinks(self, num):
        newlinks = []
        if num.lower() == 'all':
            num = self.getallchapters()
        else:
            num = int(num)
        for x in self.chapterlinks[0:num]:
            newlinks.append(x+'/all-pages')
        return newlinks


