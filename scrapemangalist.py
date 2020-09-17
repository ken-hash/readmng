from bs4 import BeautifulSoup
import requests

#to be run once. scrapes all manga titles available on readmanga and its corresponding links
#will be used for mapping for more scraping

alphabet = ''
for x in range(27):
    if x==0:
        alphabet = '#'
    else:
        alphabet=chr(x+64)
    url = 'https://www.readmng.com/manga-list/'+alphabet
    response = requests.get(url).text
    soup = BeautifulSoup(response,'html.parser')
    write = alphabet+"\n"
    data = soup.html.body.findAll('span',{'class':'manga-item'})
    for x in data:
        try:
            write+=x.find('a',{'href':True}).string.strip()+' - '+x.find('a').get('href')+'\n'
        except:
            continue
    file = open('listmanga.txt','a',encoding='utf-8')
    file.write(write)
    file.close()
