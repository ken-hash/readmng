import os 
import requests
from tqdm import tqdm

url = 'Gay.jpg'
response = requests.get('https://ichef.bbci.co.uk/news/800/cpsprodpb/E318/production/_103463185_gettyimages-480146543.jpg', stream=True)

pathname = 'birbs/example'

# if path doesn't exist, make that path dir
if not os.path.isdir(pathname):
    os.makedirs(pathname)
# get the total file size
file_size = int(response.headers.get("Content-Length", 0))
# get the file name
filename = os.path.join(pathname, url.split("/")[-1])
# progress bar, changing the unit to bytes instead of iteration (default by tqdm)
progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
with open(filename, "wb") as f:
    for data in progress:
        # write data read to the file
        f.write(data)
        # update the progress bar manually
        progress.update(len(data))
