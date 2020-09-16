import os 
import requests
import re
from tqdm import tqdm
from bs4 import BeautifulSoup

class DownloadImages:
    def __init__(self,title,chapter):
        self.title = title
        self.chapter = chapter

    def getpath(self):
        path ='downloads'+ '//' +self.geturl().split('/')[-3] + '//' +self.geturl().split('/')[-2] 
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def geturl(self):
        newtitle = self.title.lower().replace(' ','-')[0:-1]
        url = 'https://www.readmng.com/{}/{}/all-pages'.format(newtitle,self.chapter)
        return url

    def downloadimages(self, numchapters=None):
        if numchapters == None:
            numchapters = 1
        
        url = self.geturl()
        path = self.getpath()
        chapter = float(url.split('/')[-2])
        for x in range(numchapters):
            newtitle = self.title.lower().replace(' ','-')[0:-1]
            tempchapter = float(self.chapter) - x 
            if tempchapter.is_integer()==True:
                chapter=int(tempchapter)
            else:
                chapter=tempchapter
            path ='downloads'+ '//' +self.geturl().split('/')[-3] + '//' +str(chapter)
            if not os.path.isdir(path):
                os.makedirs(path)
            url = 'https://www.readmng.com/{}/{}/all-pages'.format(newtitle,str(chapter))
            response = requests.get(url)
            soup = BeautifulSoup(response.text,'html.parser')

            imageslinks = soup.html.body.findAll('img',{'src': re.compile('chapter_files')})
            for lines in imageslinks:
                if len(imageslinks)!=len(os.listdir(path)):
                    self.download(lines.get('src'), path)
                else:
                    pass

    def download(self, url, path=None):
        """
        Downloads a file given an URL and puts it in the folder `pathname`
        """
        if path==None:
            usepath=self.getpath()
        else:
            usepath=path
        # if path doesn't exist, make that path dir
        # download the body of response by chunk, not immediately
        response = requests.get(url, stream=True)
        # get the total file size
        file_size = int(response.headers.get("Content-Length", 0))
        # get the file name
        filename = os.path.join(usepath, url.split("/")[-1])
        if not os.path.exists(filename):
            # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
            progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
            with open(filename, "wb") as f:
                for data in progress:
                    # write data read to the file
                    f.write(data)
                    # update the progress bar manually
                    progress.update(len(data))
        else:
            print(filename+" exists")