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

#returns chapter links depending on how many chapters needed to be downloaded e.g. if set to 5, it will download latest 5 chapters
    def getchapterlinks(self, num):
        newlinks = []
        #if set to all it will download all the available chapters
        if num.lower() == 'all':
            num = self.getallchapters()
        else:
            #if just downloading only the latest chapter(1) it will automatically check for gap release from the last downloaded chapter else it would download desired number of chapters plus the gap releases
            if(int(num)==1):
                num=self.getgaps()
            else:
                num = int(num) + self.getgaps()
                print('Found',str(num),'chapters of',self.title,'to download')
        for x in self.chapterlinks[0:num]:
            newlinks.append(x+'/all-pages')
        return newlinks

    def getgaps(self):
        path = os.path.join(os.path.realpath('downloads'),self.title)
        #download only the latest chapter if directory doesnt exist
        if not os.path.isdir(path):
            print('New Manga found:',self.title,'Found 1 Chapter to download')
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
                if onlinechapter>lastdownloaded:
                    gaps+=1
                else:
                    break
            return gaps
