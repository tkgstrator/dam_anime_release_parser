import requests
import json
import argparse
import os
import logging
import sys
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

def __config_logger(level: str):
    """Config logger

    Args:
        level (str): Log level
    """

    level = logging.getLevelName(level)
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    )

def merge_json(release_date: str, force_fetch: bool, search_info: bool):
    results = []
    for category_id in [50100, 50300]:
        # ファイルを読み込んでマージする
        target_path = f'dist/{category_id}.json'
        with open(target_path, 'r') as f:
            results.extend(json.load(f))
    # 重複を削除する
    filtered_results = list(filter(lambda result: result['distStart'] >= release_date, results))
    filtered_results = list({v['requestNo']:v for v in filtered_results}.values())
    # 詳細検索オプションが有効の時
    if search_info:
        logging.info(f'Searching detailed information...')
        target_path = f'dist/00000.json'
        if not os.path.exists(target_path) or force_fetch:
            results = []
            length = len(str(len(filtered_results)))
            for index, result in enumerate(filtered_results):
                request_no = result['requestNo']
                title = result['title']
                logging.info(f'Progress: {str(index + 1).rjust(length)}/{str(len(filtered_results)).rjust(length)} RequestNo: {request_no} Title: {title}')
                results.append(get_detailed_by_request_no(request_no))
            logging.info(f'Complete!: {len(results)}')
            with open(target_path, 'w') as f:
                f.write(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            with open(target_path, 'r') as f:
                logging.error(f'Results: {len(json.load(f))}')
                logging.error(f'File exists: {target_path}')
    # 詳細検索オプションが無効の時
    # 単純にマージして終了
    else:
        logging.info(f'Complete!: {len(results)} --> {len(filtered_results)}') 
        target_path = f'dist/{release_date}.json'
        with open(target_path, 'w') as f:
            f.write(json.dumps(filtered_results, indent=2, ensure_ascii=False))
    sys.exit(0)

def get_json(category_id: list[int], force_fetch: bool):
    for category_id in category_id: 
        target_path = f'dist/{category_id}.json'
        if not os.path.exists(target_path) or force_fetch:
            results = []
            title_list = get_list_by_category(category_id)
            length = len(str(len(title_list)))
            for index, title_id in enumerate(title_list):
                program_title = title_id['programTitle']
                logging.info(f'Progress: {str(index + 1).rjust(length)}/{str(len(title_list)).rjust(length)} ProgramTitle: {program_title}')
                logging.info(f'Complate: {len(results)}')
                results.extend(get_list_by_program_title(program_title, category_id))
            logging.info(f'Complate: {len(results)}')
            with open(target_path, 'w') as f:
                f.write(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            with open(target_path, 'r') as f:
                logging.error(f'Results: {len(json.load(f))}')
                logging.error(f'File exists: {target_path}')
        sys.exit(0)

def format(result: dict) -> dict:
    return {
        'artistCode': int(result.artistId),
        'artistKana': result.artistKana,
        'artist': result.artistName,
        'distEnd': result.distEnd if result.distEnd != '99999999' else None,
        'distStart': f'{result.distStart[:4]}-{result.distStart[4:6]}-{result.distStart[6:]}',
        'firstLine': result.firstBars,
        'animeFlag': result.funcAnimePicture != '0',
        'honninFlag': result.funcPersonPicture != '0',
        'recordingType': int(result.funcRecording),
        'scoreFlag': result.funcScore != '0',
        'indicationMonth': result.indicationMonth if result.indicationMonth != '' else None,
        'myKey': int(result.myKey),
        'orgKey': int(result.orgKey),
        'programTitle': result.programTitle,
        'requestNo': f'{result.reqNo[:4]}-{result.reqNo[4:]}',
        'title': result.songName,
        'titleYomi_Kana': result.songKana,
        'titleFirstKana': result.titleFirstKana
    }

def format_detailed(result: dict) -> dict:
    music_info = result.list[0].kModelMusicInfoList[0]
    model_list = music_info.eachModelMusicInfoList
    return {
        'artistCode': result.data.artistCode,
        'artist': result.data.artist,
        'firstLine': result.data.firstLine,
        'programTitle': music_info.highlightTieUp,
        'requestNo': result.data.requestNo,
        'title': result.data.title,
        'titleYomi_Kana': result.data.titleYomi_Kana,
        'kidsFlag': music_info.kidsFlag != '0',
        'damTomoPublicVocalFlag': music_info.damTomoPublicVocalFlag != '0',
        'damTomoPublicMovieFlag': music_info.damTomoPublicMovieFlag != '0',
        'damTomoPUblicRecordingFlag': music_info.damTomoPUblicRecordingFlag != '0',
        'karaokeDamFlag': music_info.karaokeDamFlag != '0',
        'playbackTime': music_info.playbackTime,
        'eachModelMusicInfoList': list(map(lambda model: {
            'karaokeModelNum': int(model.karaokeModelNum),
            'karaokeModelName': model.karaokeModelName,
            'releaseDate': model.releaseDate,
            'shift': int(model.shift) if model.shift is not None else None,
            'mainMovieId': int(model.mainMovieId),
            'mainMovieName': model.mainMovieName if model.mainMovieName != '対応していない' else None,
            'subMovieId': int(model.subMovieId),
            'subMovieName': model.subMovieName if model.subMovieName != '対応していない' else None,
            'honninFlag': model.honninFlag != '0',
            'animeFlag': model.animeFlag != '0',
            'liveFlag': model.liveFlag != '0',
            'mamaotoFlag': model.mamaotoFlag != '0',
            'namaotoFlag': model.namaotoFlag != '0',
            'duetFlag': model.duetFlag != '0',
            'guideVocalFlag': model.guideVocalFlag != '0',
            'prookeFlag': model.prookeFlag != '0',
            'scoreFlag': model.scoreFlag != '0',
            'duetDxFlag': model.duetDxFlag != '0',
            'damTomoMovieFlag': model.damTomoMovieFlag != '0',
            'damTomoRecordingFlag': model.damTomoRecordingFlag != '0',
            'myListFlag': model.myListFlag != '0',
        }, list(filter(lambda model: model.karaokeModelNum in ['17', '53', '56'], model_list))))
    }

def get_detailed_by_request_no(requestNo: str) -> dict:
    url = 'https://denmokuapp.clubdam.com/dkwebsys/search-api/GetMusicDetailInfoApi'
    parameters = {
        "requestNo": requestNo,
        "authKey": "2/Qb9R@8s*",
        "compId": "1",
        "modelTypeCode": "3"
    }
    headers = {
        'content-type': 'application/json',
        'dmk-access-key': 'ZRLkesTqAHDM6G2VLxps'
    }
    return format_detailed(requests.post(url, data=json.dumps(parameters), headers=headers).json(object_hook=AttributeDict))


def get_list_by_program_title(programTitle: dict, category_id: int) -> list[dict]:
    url = 'https://denmokuapp.clubdam.com/dkdenmoku/DkDamSearchServlet'
    parameters = {
        "deviceId": "ZlUs4awByTK35bDar1cPoHR0W7V3Aywv55/QbQoLSmg=",
        "appVer": 36,
        "categoryCd": f"0{category_id}",
        "page": 1,
        "programTitle": programTitle,
        "songSearchFlag": 2,
    }
    headers = {
        'content-type': 'application/json',
        'dmk-access-key': 'ZRLkesTqAHDM6G2VLxps'
    }
    results = requests.post(url, data=json.dumps(parameters), headers=headers).json(object_hook=AttributeDict).searchResult
    return list(map(lambda result: format(result), results))

def get_list_by_category(category_id: str) -> list[dict]:
    url = 'https://denmokuapp.clubdam.com/dkdenmoku/DkDamSearchServlet'
    parameters = {
        "deviceId": "ZlUs4awByTK35bDar1cPoHR0W7V3Aywv55/QbQoLSmg=",
        "appVer": 36,
        "categoryCd": f'0{category_id}',
        "page": 1,
        "songSearchFlag": 2,
        "songMatchType": 3
    }
    headers = {
        'content-type': 'application/json',
        'dmk-access-key': 'ZRLkesTqAHDM6G2VLxps'
    }
    results = requests.post(url, data=json.dumps(parameters), headers=headers).json(object_hook=AttributeDict).searchResult
    logging.info(f'Category Id: {category_id}')
    logging.info(f'Results: {len(results)}')
    return list(map(lambda result: format(result), results))

def main(_argv: list[str] | None = None):
    """Main

    Args:
        _argv (list[str] | None, optional): Commandline arguments. Defaults to None.
    """
    parser = argparse.ArgumentParser(description='Get DAM Karaoke music list which has anime picture(animeFlag is True) or belongs to anime category.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-c',
        '--category',
        help='download json',
        metavar="CATEGORY_ID",
        type=int,
        dest='category_id',
        nargs='+',
        choices=[50100, 50200, 50300],
    )
    group.add_argument(
        '-m',
        '--merge',
        help='merge json',
        metavar="RELEASE_DATE",
        type=str,
        dest='release_date',
    )
    parser.add_argument(
        "-f",
        "--force",
        help="force fetch",
        action="store_true",
        dest="force",
    )
    parser.add_argument(
        "-s",
        "--search",
        help="search detailed information",
        action="store_true",
        dest="search",
    )
    parser.add_argument(
        "-log",
        "--loglevel",
        default="INFO",
        help="logging level",
        choices=["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )

    args = parser.parse_args()
    force_fetch = args.force
    search_info = args.search
    release_date = args.release_date
    category_id = args.category_id
    __config_logger(args.loglevel)

    logging.info(f'------ Mode: {"Merge and filter" if release_date is not None else "Download"}')
    logging.info(f'------ Force: {force_fetch}') 
    logging.info(f'------ Search: {search_info}') 
    if release_date is not None:
        logging.info(f'------ Release Date: {release_date}')
    else:
        logging.info(f'------ Category Id: {category_id}') 
    os.makedirs('dist', exist_ok=True)

    if release_date is not None:
        merge_json(release_date, force_fetch, search_info)
    if category_id is not None:
        get_json(category_id, force_fetch)


if __name__ == '__main__':
    main()