import os
import json
import requests
from tqdm import tqdm
from urllib.parse import urlparse, parse_qs, unquote

def download(url, id, pathname):
    """
    Downloads a file given an URL and puts it in the folder `pathname`
    """
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)
    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))
    # get the file name
    filename = os.path.join(pathname, f'{id}.jpg')
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for data in progress.iterable:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))
        
def main():
    with open('data/images-grouped.json', 'r') as f:
        data = json.load(f)

    for uid in range(len(data)):
        urls = data[uid]
        for id in range(len(urls)):
            download(urls[id], id, f'images/group-{uid}')

main()