from bs4 import BeautifulSoup
import os 
import requests
import re
from pathlib import Path
import downloadimg
import img2pdf
import time

url = 'https://www.readmng.com/i-am-the-sorcerer-king/108/all-pages'

response = requests.get(url)
soup = BeautifulSoup(response.text,'html.parser')

images = soup.html.body.findAll('img',{'src': True})

#only get links with chapter_files
for lines in images:
    #print(lines.get('src'))
    if re.search("chapter_files",lines.get('src')) != None:
        downloadimg.download(lines.get('src'),'downloads\\')


#to do convert pdf automatically