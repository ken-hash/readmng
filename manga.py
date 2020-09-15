import urllib3
from bs4 import BeautifulSoup

class Manga:

    def __init__(self, title, chapter=None, link=None):
        self.title = title
        self.chapter = chapter
        self.link = link

        if chapter is None or link is None:
            data = urllib3.PoolManager().request('Get',self.generateurl()).data
            soup = BeautifulSoup(data,'html.parser')
            latestchapterlink = soup.html.body.find('div',{'id':'chapters_container'}).find('a').get('href')
            self.link = latestchapterlink+"/all-pages"
            self.chapter = latestchapterlink.split('/')[-1]

    def generateurl(self):
        titlenew = self.title.lower().replace(' ','-')[0:-1]
        url = "https://www.readmng.com/"+titlenew
        return url

    def getlinkchapter(self):
        return self.link

    def getlatestchapternum(self):
        return self.chapter


    def __str__(self):
        return 'Manga: '+self.title+' Latest Chaper: '+self.chapter
