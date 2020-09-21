import urllib3
from bs4 import BeautifulSoup
import os
import re

#class to gather information of manga and get latestchapter of the manga

class Manga:

    def __init__(self, title):
        self.title = title.lower().replace(' ','-')
        self.chapterlinks = []
        self.url = "https://www.readmng.com/"+self.title

#scrapes all chapters listed in website lastest chapter being first item and last chapter being the first chapter
        if len(self.chapterlinks)<1:
            data = urllib3.PoolManager().request('Get',self.url).data
            soup = BeautifulSoup(data,'html.parser')
            self.numchapters = 1
            tempchapterlinks = soup.html.body.find('div',{'id':'chapters_container'}).findAll('a',{'href':re.compile(self.url)})
            for x in tempchapterlinks:
                self.chapterlinks.append(x.get('href'))

#returns latest chapter number
    def latestchapter(self):
        return self.chapterlinks[0].split('/')[-1]


    def latestchapterlink(self):
        newlink = self.chapterlinks[0]+'/all-pages'
        return newlink

    def getallchapters(self):
        return len(self.chapterlinks)

#returns chapter links depending on how many chapters needed
    def getchapterlinks(self, num):
        newlinks = []
        if num.lower() == 'all':
            num = self.getallchapters()
        else:
            num = int(num)
        for x in self.chapterlinks[0:num]:
            newlinks.append(x+'/all-pages')
        return newlinks


#experimental to-do as need to consider decimal chapter gaps
    def getgaps(self):
        path = os.path.join(os.path.realpath('downloads'),self.title)
        listitems = os.listdir(path)
        listitems.sort()
        #will break if theres nonstring folder names
        min=int(listitems[0])
        max=int(listitems[0])
        for x in listitems:
            y = int(x)
            if y <= min:
                min=y
            if y >= max:
                max=y
        print(min, max)
        #one solution maybe check max(chapter) folder then compare list from links(getting how many chapter from that max to the latest) and download gap chapters
        #exception when its None/empty
        if (max-min)+1 == len(listitems):
            print('No gaps')
        else:
            print('There is gaps')
        return listitems


