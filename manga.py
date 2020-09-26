import urllib3
from bs4 import BeautifulSoup
import os
import re

#class Manga to gather information about argument Manga title contains information about chapterlinks, lastest chapter of the manga
class Manga:

    def __init__(self, title):
        self.title = title.lower().replace(' ','-')
        self.chapterlinks = []
        self.url = "https://www.readmng.com/"+self.title

#scrapes all chapters listed in website lastest chapter being first item and first chapter being the last item
        if not self.chapterlinks:
            data = urllib3.PoolManager().request('Get',self.url).data
            soup = BeautifulSoup(data,'lxml')
            self.numchapters = 1
            try:
                tempchapterlinks = soup.html.body.find('div',{'id':'chapters_container'}).findAll('a',{'href':re.compile(self.url,re.IGNORECASE)})
                for x in tempchapterlinks:
                    self.chapterlinks.append(x.get('href'))
            except:
                print('Invalid title/url. Please see listTitles.txt for titles to use')
                return

#returns latest chapter number
    def latestchapter(self):
        return self.chapterlinks[0].split('/')[-1]


    def latestchapterlink(self):
        newlink = self.chapterlinks[0]+'/all-pages'
        return newlink

    def getallchapters(self):
        return len(self.chapterlinks)

#returns chapter links depending on how many chapters needed to be downloaded e.g. if set to 5, it will download latest 5 chapters
    def getchapterlinks(self, num):
        newlinks = []
        #if set to all it will download all the available chapters
        if num.lower() == 'all':
            numchap = self.getallchapters()
            print('Attempting to download all chapters of',self.title)
        else:
            #downloads gaprelease or desired number of chapterdownloads. will always attempt to download/check last downloaded chapter for discrepancies
            gap = self.getgaps()
            if gap<int(num):
                numchap=int(num)
            else:
                numchap=gap
            if(int(num)>1):
                print('Found',str(numchap),'chapters of',self.title,'to download')
        #will always attempt to check if latest chapter is downloaded properly
        for x in self.chapterlinks[0:numchap]:
            newlinks.append(x+'/all-pages')
        return newlinks

    def getgaps(self):
        path = os.path.join(os.path.realpath('downloads'),self.title)
        #download only the latest chapter if directory doesnt exist
        if not os.path.isdir(path):
            print('New Manga found:',self.title)
            return 1
        else:
            #list all chapters downloaded in the folder
            listitems = os.listdir(path)
            lastdownloaded = 0
            #get last downloaded chapter number 
            for x in listitems:
                try:
                    x = int(x)
                except:
                    try:
                        x = float(x)
                    except:
                        continue
                if x>lastdownloaded:
                    lastdownloaded=x
            gaps=0
            #check how many chapter releases from last chapter downloaded
            for x in self.chapterlinks:
                try:
                    onlinechapter = int(x.split('/')[-1])
                except:
                    onlinechapter = float(x.split('/')[-1])
            #check last downloaded chapter if complete incase internet/power interuption
                if onlinechapter>=lastdownloaded:
                    gaps+=1
                else:
                    break
            return gaps
