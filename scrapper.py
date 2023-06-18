import requests
import os
import time
import json
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
from selenium import webdriver

# headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_links(url, get_url, get_tree):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    html = driver.page_source
    
    urls = []
    for link in tqdm(get_tree(html), "Extracting URLs"):
        link_url = get_url(link)

        if not link_url:
            continue
    
        link_url = urljoin(url, link_url)
        
        if is_valid(link_url):
            urls.append(link_url)
    
    driver.quit()

    return urls
    
def download(url, pathname):
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
    filename = os.path.join(pathname, url.split("/")[-1])
    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for data in progress.iterable:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))

def load_and_save_urls(url, path):
    urls = get_all_links(
        url,
        lambda link: link.attrs.get('href'),
        lambda html: bs(html, "html.parser").find_all(
            'a',
            class_=lambda x: x and 'item-link' in x
        ),
    )
    print('URLS', len(urls))
    
    with open(path, 'w') as f:
        json.dump(urls, f)

def load_and_save_img_urls(img_urls, path):
    urls = []
    
    def get_tree(html):
        soup = bs(html, "html.parser")
        figures = soup.find_all(
            'figure', class_=lambda x: x and 'pdp-image' in x
        )
        images = []
        for figure in figures:
            images.extend(figure.find_all('img'))
        
        return images
    
    for url in tqdm(img_urls, "Appending urls"):
        urls.append(
            get_all_links(
                url,
                lambda img: img.attrs.get('src'),
                get_tree
            )
        )

    print('URLS', len(urls))
    
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump([], f)

    with open(path, 'r') as f:
        data = json.load(f)

    data.extend(urls)

    with open(path, 'w') as f:
        json.dump(data, f)

def main():
    # get all images
    # imgs = get_all_images(url)
    # print("IMAGES", imgs)

    # for img in imgs:
    #     # for each image, download it
    #     download(img, path)
    
    with open('urls3.json', 'r') as f:
        data = json.load(f)
    load_and_save_img_urls(data,'images-grouped.json')

main()

# main("https://www2.hm.com/de_de/damen/neuheiten/alle-anzeigen.html?sort=stock&image-size=small&image=model&offset=1000&page-size=500", "urls")