import json

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

def release_5k8k(song: dict) -> bool:
    if song is None:
        return False
    xg5k = list(filter(lambda model: model.karaokeModelNum == 17, song.eachModelMusicInfoList))
    xg8k = list(filter(lambda model: model.karaokeModelNum == 56, song.eachModelMusicInfoList))

    if len(xg5k) != 0 and len(xg8k) != 0:
        return True
    return False

def release_8k(song: dict) -> bool:
    if song is None:
        return False
    xg5k = list(filter(lambda model: model.karaokeModelNum == 17, song.eachModelMusicInfoList))
    xg8k = list(filter(lambda model: model.karaokeModelNum == 56, song.eachModelMusicInfoList))

    if len(xg5k) == 0 and len(xg8k) != 0:
        return True
    return False

def has_movie_only_8k(song: dict) -> bool:
    xg5k = list(filter(lambda model: model.karaokeModelNum == 17, song.eachModelMusicInfoList))
    xg8k = list(filter(lambda model: model.karaokeModelNum == 56, song.eachModelMusicInfoList))
    xg5k = xg5k[0]
    xg8k = xg8k[0]
    return xg8k.animeFlag and not xg5k.animeFlag

def release_5k_after(song: dict, date: str) -> bool:
    xg5k = list(filter(lambda model: model.karaokeModelNum == 17, song.eachModelMusicInfoList))
    xg5k = xg5k[0]
    return xg5k.releaseDate >= date

def main():
    # 第一興商のウェブサイトで映像付きの楽曲一覧を取得する
    # @TODO: パーサーが適当なので数曲デコード失敗している
    # 2024-01-13時点で1911曲 
    anime_songs = json.loads(open('dist/songs.json', 'r').read(), object_hook=AttributeDict)
    anime_songs = list(filter(lambda song: song is not None, anime_songs))

    # 1911曲に対して楽曲取得APIを叩いて詳細情報を取得したもの
    # 2024-01-13時点で1911曲 
    detail_songs = json.loads(open('dist/song_details.json', 'r').read(), object_hook=AttributeDict)
    detail_songs = list(filter(lambda song: song is not None, detail_songs))

    print(f"楽曲取得Web: {len(anime_songs)}")
    print(f"楽曲取得API: {len(detail_songs)}")

    # XG8000にだけ配信されている曲
    songs_8k = set(list(map(lambda song: song.requestNo, list(filter(lambda song: release_8k(song), detail_songs)))))
    # XG8000だけ映像がついている曲
    songs_5k8k = list(filter(lambda song: release_5k8k(song), detail_songs))
    songs_has_movie_8k = set(list(map(lambda song: song.requestNo, list(filter(lambda song: has_movie_only_8k(song), songs_5k8k)))))

    # 指定日以降の曲
    limit_date = '2022-12-20'
    category_songs = json.loads(open('dist/050100.json', 'r').read(), object_hook=AttributeDict)
    songs_after_date = set(list(map(lambda song: song.requestNo, list(filter(lambda song: song.distStart >= limit_date, category_songs)))))
    
    print(f'XG8000配信: {len(songs_8k)}')
    print(f'XG8000映像: {len(songs_has_movie_8k)}')
    print(f'XG5000日付: {len(songs_after_date)}')
    required_songs = songs_8k | songs_has_movie_8k | songs_after_date
    print(f'要取得曲数: {len(required_songs)}')

    category_songs = json.loads(open('dist/050100.json', 'r').read())
    print(f'カテゴリ曲数: {len(category_songs)}')
    with open('dist/xg5k.json', 'w') as f:
        f.write(json.dumps(list(filter(lambda song: song['requestNo'] in required_songs, category_songs)), indent=2, ensure_ascii=False))

# 映像がついている楽曲のうちXG5000で配信されていないまたはXG5000で映像が配信されていないものを取得する
if __name__ == '__main__':
    main()