import requests
import re
import json
import time
from bs4 import BeautifulSoup

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
    with open('songs.json', 'r') as f:
        songs = json.loads(f.read(), object_hook=AttributeDict)
        songs = list(map(lambda song: get_song_detail(song[1], song[0]), enumerate(songs)))
        with open('song_details.json', 'w') as f:
            f.write(json.dumps(songs, indent=2, ensure_ascii=False))

def get_song_detail(song: dict, index: int) -> dict:
    print(f'\r {song.requestNo} {index}', end='')
    url = 'https://denmokuapp.clubdam.com/dkwebsys/search-api/GetMusicDetailInfoApi'
    parameters = {
        'requestNo': song.requestNo,
        'authKey': '2/Qb9R@8s*',
        'compId': '1',
        'modelTypeCode': '3'
    }
    headers = {
        'content-type': 'application/json',
        'dmk-access-key': 'ZRLkesTqAHDM6G2VLxps'
    }
    res = requests.post(url, data=json.dumps(parameters), headers=headers).json(object_hook=AttributeDict)
    data = res.data
    try:
        musicInfo = res.list[0].kModelMusicInfoList[0]
        parameters = {
            'artistCode': data.artistCode,
            'artist': data.artist,
            'requestNo': data.requestNo,
            'title': data.title,
            'titleYomi_Kana': data.titleYomi_Kana,
            'firstLine': data.firstLine,
            'tieUp': song.tieUp,
            'highlightTieUp': musicInfo.highlightTieUp,
            'kidsFlag': musicInfo.kidsFlag == '1',
            'damTomoPublicVocalFlag': musicInfo.damTomoPublicVocalFlag == '1',
            'damTomoPublicMovieFlag': musicInfo.damTomoPublicMovieFlag == '1',
            'damTomoPUblicRecordingFlag': musicInfo.damTomoPUblicRecordingFlag == '1',
            'karaokeDamFlag': musicInfo.karaokeDamFlag == '1',
            'playbackTime': musicInfo.playbackTime,
            'eachModelMusicInfoList': list(map(lambda musicInfo: {
                'karaokeModelNum': int(musicInfo.karaokeModelNum),
                'karaokeModelName': musicInfo.karaokeModelName,
                'releaseDate': musicInfo.releaseDate,
                'shift': int(musicInfo.shift),
                'mainMovieId': int(musicInfo.mainMovieId),
                'mainMovieName': musicInfo.mainMovieName if musicInfo.mainMovieName != '対応していない' else None,
                'subMovieId': int(musicInfo.subMovieId),
                'subMovieName': musicInfo.subMovieName if musicInfo.subMovieName != '対応していない' else None,
                'honninFlag': musicInfo.honninFlag == '1',
                'animeFlag': musicInfo.animeFlag == '1',
                'liveFlag': musicInfo.liveFlag == '1',
                'mamaFlag': musicInfo.mamaFlag == '1',
                'namaotoFlag': musicInfo.namaotoFlag == '1',
                'duetFlag': musicInfo.duetFlag == '1',
                'guideVocalFlag': musicInfo.guideVocalFlag == '1',
                'prookeFlag': musicInfo.prookeFlag == '1',
                'scoreFlag': musicInfo.scoreFlag == '1',
                'duetDxFlag': musicInfo.duetDxFlag == '1',
                'damTomoMovieFlag': musicInfo.damTomoMovieFlag == '1',
                'damTomoRecordingFlag': musicInfo.damTomoRecordingFlag == '1',
                'myListFlag': musicInfo.myListFlag == '1',
            }, musicInfo.eachModelMusicInfoList))
        }
        return parameters
    except TypeError:
        print(f'Error!! {song.requestNo}')
        return

if __name__ == '__main__':
    main()