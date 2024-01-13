import requests
import re
import json
import time
from bs4 import BeautifulSoup
from functools import reduce
from itertools import chain

class AttributeDict(object):
    def __init__(self, obj):
        self.obj = obj

    def __getstate__(self):
        return self.obj.items()

    def __setstate__(self, items):
        if not hasattr(self, 'obj'):
            self.obj = {}
        for key, val in items:
            self.obj[key] = val

    def __getattr__(self, name):
        if name in self.obj:
            return self.obj.get(name)
        else:
            return None

    def fields(self):
        return self.obj

    def keys(self):
        return self.obj.keys()

def main():
    # with open('050300.json', 'w') as f:
    #     f.write(json.dumps(get_category('050300'), indent=2, ensure_ascii=False))
    with open('050100.json', 'r') as f:
        with open('dist/050100.json', 'w') as w:
            results = json.load(f)
            results = list(chain.from_iterable(results))
            w.write(json.dumps(results, indent=2, ensure_ascii=False))
        # results = list(map(lambda category: get_program_title(category), get_category('050100')))
        # f.write(json.dumps(results, indent=2, ensure_ascii=False))

def format(result: dict) -> dict:
    return {
        'artistCode': int(result.artistId),
        'artistKana': result.artistKana,
        'artist': result.artistName,
        'distEnd': result.distEnd if result.distEnd != '99999999' else None,
        'distStart': f'{result.distStart[:4]}-{result.distStart[4:6]}-{result.distStart[6:]}',
        'firstLine': result.firstBars,
        'animeFlag': result.funcAnimePicture == '1',
        'honninFlag': result.funcPersonPicture == '1',
        'recordingType': int(result.funcRecording),
        'scoreFlag': result.funcScore == '1',
        'indicationMonth': result.indicationMonth if result.indicationMonth != '' else None,
        'myKey': int(result.myKey),
        'orgKey': int(result.orgKey),
        'tieUp': result.programTitle,
        'requestNo': f'{result.reqNo[:4]}-{result.reqNo[4:]}',
        'title': result.songName,
        'titleYomi_Kana': result.songKana,
        'titleFirstKana': result.titleFirstKana
    }

def get_program_title(category: dict) -> list[dict]:
    requestNo: str = category['requestNo']
    title: str = category['tieUp']
    print(f'\r {requestNo} {title}', end='')
    url = 'https://denmokuapp.clubdam.com/dkdenmoku/DkDamSearchServlet'
    parameters = {
        "deviceId": "ZlUs4awByTK35bDar1cPoHR0W7V3Aywv55/QbQoLSmg=",
        "appVer": 36,
        "categoryCd": "050100",
        "page": 1,
        "programTitle": title,
        "songSearchFlag": 2,
    }
    headers = {
        'content-type': 'application/json',
        'dmk-access-key': 'ZRLkesTqAHDM6G2VLxps'
    }
    res = requests.post(url, data=json.dumps(parameters), headers=headers).json(object_hook=AttributeDict)
    results = res.searchResult
    return list(map(lambda result: format(result), results))

def get_category(id: str) -> list[dict]:
    url = 'https://denmokuapp.clubdam.com/dkdenmoku/DkDamSearchServlet'
    parameters = {
        "deviceId": "ZlUs4awByTK35bDar1cPoHR0W7V3Aywv55/QbQoLSmg=",
        "appVer": 36,
        "categoryCd": id,
        "page": 1,
        "songSearchFlag": 2,
        "songMatchType": 3
    }
    headers = {
        'content-type': 'application/json',
        'dmk-access-key': 'ZRLkesTqAHDM6G2VLxps'
    }
    res = requests.post(url, data=json.dumps(parameters), headers=headers).json(object_hook=AttributeDict)
    results = res.searchResult
    return list(map(lambda result: format(result), results))

if __name__ == '__main__':
    main()