from bs4 import BeautifulSoup
import requests

listname = ''
for x in range(27):
    if x==0:
        listname = '#'
    else:
        listname=chr(x+96)
    url = 'https://www.readmng.com/manga-list/'+listname
    response = requests.get(url).text
    soup = BeautifulSoup(response,'html.parser')
    prettysoup = soup.prettify()
    write = listname+"\n"
    data = soup.html.body.findAll('span',{'class':'manga-item'})
    for x in data:
        try:
            write+=x.find('a',{'href':True}).string.strip()+' - '+x.find('a').get('href')+'\n'
        except:
            continue
    file = open('listmanga.txt','a',encoding='utf-8')
    file.write(write)
    file.close()
