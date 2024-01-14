## dam anime release parser

第一興商のAPIからリリースされているすべてのアニメ楽曲を取得します.

- ~~XG5000ではアニメ映像がついていない楽曲~~
- ~~XG5000で配信されていないアニメ映像付き楽曲~~
- アニメ映像付きの楽曲
- アニメカテゴリに分類される楽曲

をサーバーから取得して出力します.

どの筐体で有効な楽曲かどうかを調べるには一曲ずつAPI(GetMusicDetailInfoApi)を叩く必要があり、2024年01月14日現在でこれらの楽曲は30000曲以上もあるため非常に時間がかかる処理になります.

> 1秒で1曲調べたとして9時間ほどかかる計算になります.

### get_anime_list.py

使い方はヘルプに載っている通り.

```zsh
usage: get_anime_list.py [-h] (-c CATEGORY_ID [CATEGORY_ID ...] | -m RELEASE_DATE) [-f] [-s]
                         [-log {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}]

Get DAM Karaoke music list which has anime picture(animeFlag is True) or belongs to anime category.

options:
  -h, --help            show this help message and exit
  -c CATEGORY_ID [CATEGORY_ID ...], --category CATEGORY_ID [CATEGORY_ID ...]
                        download json
  -m RELEASE_DATE, --merge RELEASE_DATE
                        merge json
  -f, --force           force fetch
  -s, --search          search detailed information
  -log {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}, --loglevel {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        logging level
```

ただ、困る人がいるかも知れないので一応書いておきます.

```zsh
# 指定時間よりあとに配信された楽曲のみキャッシュから抽出
python get_anime_list.py -m 2022-12-01

# 指定時間よりあとに配信された楽曲のみキャッシュから抽出して詳細取得
python get_anime_list.py -m 2022-12-01 -s

# 指定されたカテゴリの楽曲の一覧取得
python get_anime_list.py -c 50100 
```

> 指定できるカテゴリは現在50100(アニメ), 50300(アニメ映像)のみ
>
> 他のもすぐに対応できますが必要とされていないので未対応です