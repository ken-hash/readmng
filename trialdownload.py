from bs4 import BeautifulSoup
import os 
import requests
import re
from pathlib import Path
from downloadimg import DownloadImages
import time

url = 'https://www.readmng.com/one-piece/990/all-pages'
path ='downloads'+ '//' +url.split('/')[-3] + '//' +url.split('/')[-2] 

response = requests.get(url)
soup = BeautifulSoup(response.text,'html.parser')

imageslinks = soup.html.body.findAll('img',{'src': re.compile('chapter_files')})
for lines in imageslinks:
    if len(imageslinks)!=len(os.listdir(path)):
        download1 = DownloadImages(lines.get('src'),path)
        download1.download()
    else:
        pass

#to do convert pdf automatically