from bs4 import BeautifulSoup
import urllib3

#init scrape
#saving scrape to readmg.txt for practice parsing

data = urllib3.PoolManager().request('GET','https://www.readmng.com/').data
soup = BeautifulSoup(data,'html.parser')

prettysoup = soup.prettify()
file = open('readmng.txt','w', encoding='utf-8')
file.write(prettysoup)
file.close()


file = open('readmng.txt','r', encoding='utf-8')
data = file.read()
file.close()

soup = BeautifulSoup(data,'html.parser')
for lines in soup.html.body.findAll('dd'):
    try:
        print(lines.contents[1].string)
        print(lines.contents[1].get('href'))
    except:
        pass

