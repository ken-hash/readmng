import os 
import re
from tqdm import tqdm
import concurrent.futures
import requests
from bs4 import BeautifulSoup


class Downloader:
    #useless code
    def __init__(self):
        pass

    #download function needing list containing links to be downloaded
    def downloadLinks(self, links):
        if not links:
            return 
        else:
            #downloading in reverse order so latest chapter will be downloaded last
            for link in links[::-1]:
                title = link.split('/')[3].split('-chapter-')
                path ='downloads'+ '//' +title[0] + '//Chapter_' +title[-1]
                # if path doesn't exist, make that path dir
                if not os.path.isdir(path):
                    os.makedirs(path)
                response = requests.get(link).text
                soup = BeautifulSoup(response,'lxml')
                #parsing imagelinks from the link provided
                imageslinks = soup.html.body.findAll('img',{'class': re.compile('size-full')})
                print(f"Checking for Chapter {link.split('/')[-2]:>5s} of {link.split('/')[-3]+'.':<20}Found {len(os.listdir(path))} of {len(imageslinks)} ")
                counter = 0
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    for lines in imageslinks:
                        if len(imageslinks)-2>=len(os.listdir(path)):
                            executor.submit(self.download(lines.get('src'),counter, path))
                            counter+=1
                        else:
                            continue
                        

    def download(self, url,counter, path=None):
        """
        Downloads a file given an URL and puts it in the folder `pathname`
        """
        # download the body of response by chunk, not immediately
        response = requests.get(url, stream=True)
        # get the total file size
        file_size = int(response.headers.get("Content-Length", 0))
        # get the file name
        title = path.split('//')[-2]
        chapternum = path.split('//')[-1]
        type1 = url.split('/')[-1].split('.')[-1]
        if type1 == 'gif':
            return
        fileid = f"Image_{counter}.{type1}"
        filename = os.path.join(path, fileid)
        if not os.path.exists(filename):
            # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
            progress = tqdm(response.iter_content(1024), f"Downloading: {title} Chapter#{chapternum} Image#{fileid}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
            with open(filename, "wb") as f:
                for data in progress:
                    # write data read to the file
                    f.write(data)
                    # update the progress bar manually
                    progress.update(len(data))
        else:
            print(filename+" exists")
