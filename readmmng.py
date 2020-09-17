from bs4 import BeautifulSoup
import urllib3

#not used init scraping

data = urllib3.PoolManager().request('GET','https://www.readmng.com/').data
soup = BeautifulSoup(data,'html.parser')

prettysoup = soup.prettify()

#read watch list

soup = BeautifulSoup(prettysoup,'html.parser')
for lines in soup.html.body.findAll('dd'):
    try:
        print(lines.contents[1].string)
        print(lines.contents[1].get('href'))
    except:
        pass

