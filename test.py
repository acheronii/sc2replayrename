# curl test
from pprint import pprint

URL_BASE = f"https://sc2pulse.nephest.com/sc2/api/character/search?term="
player_id = f"battlenet:://starcraft/profile/1/9600289098212311040"
player_id = f"battlenet:://starcraft/profile/1/9566632974271643648"
import requests
import json
import sc2reader

my_names = ["achiewakie"]

# get player id from replay
path = f"test.SC2Replay"
replay = sc2reader.load_replay(path)

players = replay.players
me = next((p for p in players if p.name.lower() in my_names), None)
opponent = next((p for p in players if p.name.lower() not in my_names), None)

# form search query
region = opponent.detail_data['bnet']['region']
subregion = opponent.detail_data['bnet']['subregion']
uid = opponent.detail_data['bnet']['uid']
search_term = f'https://starcraft2.blizzard.com/en-us/profile/{region}/{subregion}/{uid}'
url = URL_BASE + search_term

# see if we have searched, and if so we use that result and go to next replay


# if we havent searched it already, search it and store the result in our database 
response = requests.get(url)
data = json.loads(response.text)
with open("test.txt", "w") as file:
    pprint(data, stream=file, indent=4)

name = opponent.name
print(f'{name=}')
if data and "proNickname" in data[0]['members']:
    name = data[0]['members']["proNickname"]

# store player id, either in memory or we can store it as a file
print(f'{name=}')

import time
for i in range(10):
    print(i)
    time.sleep(0.25)