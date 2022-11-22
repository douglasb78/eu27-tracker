import bz2

import requests
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from bs4 import BeautifulSoup

USERAGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 ' \
            'Safari/537.36 '


@dataclass
class Character:
    name: str
    clan: str
    power: int


class MIR4ConectionError(Exception):
    pass


def download_powerscore_ranking(world_group, world):
    ranktype = '1'
    url = 'https://forum.mir4global.com/rank'
    url += f'?ranktype={ranktype}'
    url += f'&worldgroupid={world_group}'
    url += f'&worldid={world}'
    url += f'&liststyle=ol'

    try:
        r = requests.get(url, headers={'User-Agent': USERAGENT}, timeout=10)
        t = BeautifulSoup(r.text, 'html.parser')
        players = t.findAll('span', {'class': 'user_name'})
        guide_td = t.find_all('td', {'class': 'text_right'})
        characters = []
        for i in range(len(players)):
            char = Character(name=players[i].text,
                             clan=guide_td[i].find_previous('td').text.strip(),
                             power=int(guide_td[i].find_next('span').text.strip().replace(',', '')))
            characters.append(char)
        return characters
    except requests.exceptions.RequestException:
        raise MIR4ConectionError('Sem conexão, tente mais tarde.')


def get_powerscore_history(name):
    p = Path('.tmp/').glob('*')
    powerscores = []
    dates = []
    for file in p:
        filepath = f'.tmp/{file.name}'
        filedate = datetime.strptime(file.name.split('_')[0], "%Y%m%d")
        cached_results = bz2.open(filepath, 'rb').readlines()
        foundname_flag = False
        for line in range(0, len(cached_results), 3):
            charactername = cached_results[line].decode('raw_unicode_escape').strip()
            if name in charactername:
                powerscores.append(int(cached_results[line + 2].decode('raw_unicode_escape').strip()))
                foundname_flag = True
        if foundname_flag is False:
            powerscores.append(None)
        dates.append(str(filedate))
    powerscores, dates = (list(t) for t in zip(*sorted(zip(powerscores, dates))))
    return [powerscores, dates]


# This should be ran once a day:
def get_powerscore_ranking(world_group, world):
    now = datetime.now()
    Path('.tmp/').mkdir(parents=False, exist_ok=True)
    filepath = '.tmp/'
    filepath += f'{now.year}{now.month}{now.day}_{world_group}_{world}.bin'
    try:
        cached_results = bz2.open(filepath, 'rb').readlines()
        characters = []
        for line in range(0, len(cached_results), 3):
            char = Character(name=cached_results[line].decode('raw_unicode_escape').strip(),
                             clan=cached_results[line+1].decode('raw_unicode_escape').strip(),
                             power=int(cached_results[line+2].decode('raw_unicode_escape').strip()))
            characters.append(char)
        return characters
    except (FileNotFoundError, EOFError):
        try:
            cached_results = open(filepath, 'wb')
            characters = download_powerscore_ranking(world_group, world)
            for char in characters:
                b = bytes((char.name + '\n'), encoding='raw_unicode_escape')
                b += bytes((char.clan + '\n'), encoding='raw_unicode_escape')
                b += bytes((str(char.power) + '\n'), encoding='raw_unicode_escape')
                cached_results.write(bz2.compress(b))
            cached_results.close()
            return characters
        except MIR4ConectionError as err:
            raise err
