import requests
import re
import json
from bs4 import BeautifulSoup

def main():
    url = 'https://www.clubdam.com/genre/anison/all_songlist.html'
    res = requests.get(url).text
    xml = BeautifulSoup(res, 'html.parser')
    songs = xml.find_all('a', class_='p-song--song')
    songs = list(map(lambda song: get_song_info(song), songs))
    songs.sort(key=lambda song: song['requestNo'])
    with open('songs.json', 'w') as f:
        f.write(json.dumps(songs, indent=2, ensure_ascii=False))

def get_song_info(xml) -> dict:
    requestNo = re.search(r'requestNo=([\d]{4}-[\d]{2})', xml['href']).group(1)
    tieup = xml.find('div', class_='p-song__tieup')
    tieup = tieup if tieup is None else re.search(r'『(.*)?』', tieup.text).group(1)
    title = xml.find('h4', class_='p-song__title').text
    artist = xml.find('div', class_='p-song__artist').text
    return {
        'tieup': tieup,
        'requestNo': requestNo,
        'title': title,
        'artist': artist
    }

if __name__ == '__main__':
    main()