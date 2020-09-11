from bs4 import BeautifulSoup
import os 
import requests
import re

url = 'https://www.readmng.com/rebirth-of-the-urban-immortal-cultivator/467/all-pages'

response = requests.get(url)
soup = BeautifulSoup(response.text,'html.parser')

images = soup.html.body.findAll('img',{'src': True})

#only get links with chapter_files
for lines in images:
    #print(lines.get('src'))
    if re.search("chapter_files",lines.get('src')) != None:
        print(lines.get('src'))