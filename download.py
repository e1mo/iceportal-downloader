from bs4 import BeautifulSoup
from pathlib import Path,PurePath
import re
import json
import csv
import requests
import time

def downloadAudiobook(page):
    baseUrl = 'https://iceportal.de'
    apiBasePath = '/api1/rs/page'
    dataBasePath = 'data'

    apiBaseUrl = baseUrl + apiBasePath
    apiPageUrl = apiBaseUrl + page
    dataPath = '{}{}'.format(dataBasePath, page)

    r = requests.get('{}{}/'.format(apiBaseUrl, page))

    if r.status_code != 200:
        print('Non 200 http code on {} given. {} was returned. Exiting.'.format(apiBaseUrl + page, r.status_code))
        exit(1)

    p = Path(dataPath)
    p.mkdir(parents=True, exist_ok=True)

    with open(dataPath + '/working', 'w') as f:
        f.write(str(time.time()))

    with open(dataPath + '/page.json', 'w') as f:
        f.write(r.text)
        print(f)

    r = r.json()
    files = r['files']

    for srcFile in files:
        path = srcFile['path']
        p = Path(dataPath + path)
        p.parent.mkdir(parents=True, exist_ok=True)
        localpath = p.resolve()
        pathApiUrl = baseUrl + '/api1/rs/audiobooks/path' + path
        print(pathApiUrl)
        lr = requests.get(pathApiUrl)
        path = lr.json()['path']
        print(lr.json())
        with requests.get(baseUrl + path, stream=True) as s:
            s.raise_for_status()
            with open(localpath, 'wb') as f:
                for chunk in s.iter_content(chunk_size=8192): 
                    f.write(chunk)
    Path(dataPath + '/done').unlink(missing_ok=True)

    with open(dataPath + '/done', 'w') as f:
        f.write(str(time.time()))

def isAudiobookPresent(page):
    baseUrl = 'https://iceportal.de'
    apiBasePath = '/api1/rs/page'
    dataBasePath = 'data'

    apiBaseUrl = baseUrl + apiBasePath
    apiPageUrl = apiBaseUrl + page
    dataPath = '{}{}'.format(dataBasePath, page)
    donePath = dataPath + '/done'
    donePath = Path(donePath)
    workingPath = dataPath + '/working'
    workingPath = Path(donePath)
    return donePath.is_file() or workingPath.is_file()

if __name__ == "__main__":
    r = requests.get('https://iceportal.de/api1/rs/page/hoerbuecher')
    hoerbuecher = r.json()['teaserGroups'][0]['items']
    for item in hoerbuecher:
        nav = item['navigation']
        print(nav['linktext'])
        if not isAudiobookPresent(nav['href']):
            print('downloading')
            downloadAudiobook(nav['href'])
        else:
            print('Already present - skipping')
