import sc2reader
import requests
import os
import datetime
import json 
import re 
import argparse
import time

API_BASE = f"https://sc2pulse.nephest.com/sc2/api/character/search?term="
LOCAL_PWD = os.path.dirname(os.path.abspath(__file__))

# config
REPLAY_DIRECTORIES = {
"na": "/mnt/c/Users/Jrchu/Documents/StarCraft II/Accounts/65253659/1-S2-1-1656173/Replays/Multiplayer/",
"eu": "/mnt/c/Users/Jrchu/Documents/StarCraft II/Accounts/65253659/2-S2-1-9688821/Replays/Multiplayer/"
}

def sanitize_filename(name):
    # Replace bad filename characters with underscores
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def get_last_checked(replay_dir):

    json_file = os.path.join(LOCAL_PWD, "date.json")
    date_format = "%Y-%m-%d %H:%M:%S"

    with open(json_file, 'r') as file:
        data = json.load(file)

    if replay_dir in data:
        last_checked = datetime.datetime.strptime(data[replay_dir], date_format)
    else:
        last_checked = datetime.datetime.now() - datetime.timedelta(days=365)

    data[replay_dir] = datetime.datetime.now().strftime(date_format)

    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)

    return last_checked

def get_revealed_players():
    revealed_players_path = os.path.join(LOCAL_PWD, "revealed_players.json")

    if not os.path.exists(revealed_players_path):
        with open(revealed_players_path, "w") as file:
            json.dump({}, file, indent=4)
        return {}
    with open(revealed_players_path, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def set_revealed_players(json_dict):
    revealed_players_path = os.path.join(LOCAL_PWD, "revealed_players.json")

    with open(revealed_players_path, "w") as file:
        json.dump(json_dict, file, indent=4)

def get_names():
    names_path = os.path.join(LOCAL_PWD, "names.txt")
    if not os.path.exists(names_path):
        return None
    with open(names_path, 'r') as file:
        return [name.strip() for name in file.readlines()]

def rename_replays(server):
    

    my_names = get_names()
    
    if not my_names:
        print('Please add a name using the flag "-a {name}" or "--add-name {name}"')
        return
        
    replay_directory = REPLAY_DIRECTORIES[server.lower()]

    last_checked = get_last_checked(replay_directory).timestamp()

    revealed_players = get_revealed_players()

    count = 0

    # process files
    for filename in os.listdir(replay_directory):
        if not filename.endswith(".SC2Replay"):
            continue
        old_path = os.path.join(replay_directory, filename)

        # skip old replays
        if os.path.getmtime(old_path) < last_checked:
            continue
        try:

            # Load replay metadata
            replay = sc2reader.load_replay(old_path)


            # Identify self and opponent
            players = replay.players
            if len(players) != 2:
                continue
            me = next((p for p in players if p.name.lower() in my_names), None)
            opponent = next((p for p in players if p.name.lower() not in my_names), None)

            if not me or not opponent:
                print(f"Skipping (missing players): {filename}")
                continue

            if not opponent.is_human:
                print(f"Skipping AI game: {filename}")
                continue

            # Build new filename
            map_name = replay.map_name.replace(" ", "_")
            opp_race = opponent.play_race[0]
            opp_name = opponent.name
            timestamp = replay.start_time.strftime("%Y-%m-%d_%H-%M-%S")

            # See if the account is revealed
            
            region = opponent.detail_data['bnet']['region']
            subregion = opponent.detail_data['bnet']['subregion']
            uid = opponent.detail_data['bnet']['uid']
            search_term = f'https://starcraft2.blizzard.com/en-us/profile/{region}/{subregion}/{uid}'

            # if we have seen the player before
            if search_term in revealed_players.keys():
                if revealed_players[search_term] == -1: # if we dont know who it is
                    pass # keep the name in replay
                else:
                    opp_name = revealed_players[search_term] # if we know who it is
            # if we have not seen the player, search using sc2pulse
            else:
                url = API_BASE + search_term
                response = requests.get(url)
                player_id_data = json.loads(response.text)
                # if pulse has information
                if player_id_data and "proNickname" in player_id_data[0]['members']:
                    # set the name on the replay and in our datastructure
                    opp_name = player_id_data[0]['members']["proNickname"]
                    revealed_players[search_term] = opp_name 
                else:
                    # keep the name, but mark that pulse has no data
                    revealed_players[search_term] = -1
                # wait 0.25s to avoid rate limits on sc2pulse's api
                time.sleep(0.25)

            new_name = sanitize_filename(f"{opp_race}_{opp_name}_{map_name}_{timestamp}.SC2Replay")
            new_path = os.path.join(replay_directory, new_name)

            # Avoid accidental overwrite
            if os.path.exists(new_path):
                print(f"File already exists, skipping rename: {new_name}")
                continue
            count += 1
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} -> {new_name}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    if count != 0:
        print(f"Modified {count} replays to have a legible name")
    else:
        print("No necessary replay name changes")

    set_revealed_players(revealed_players)

def add_name(name):
    names = get_names()
    if name not in names:
        with open("names.txt", "a") as file:
            file.write(f"\n{name}")


def main():
    parser = argparse.ArgumentParser(
        prog="Replay name changer",
        description="Changes the names of replays to MAP_OPPONENT_RACE_DATETIME"
    )
    
    parser.add_argument("-a", "--add-name", type=str)

    parser.add_argument("-s", "--server", type=str)
    
    args = parser.parse_args()

    if args.add_name:
        add_name(args.add_name)
        return

    server = args.server
    if not server:
        return
    if server.lower() not in ["eu", "na", "both" ,"all"]:
        print("Expects server to be \"eu\", \"na\",  \"both\", or \"all\"")
        return
    if server.lower() in ["both", "all"]:
        print("Begining EU replay renaming")
        rename_replays("eu")
        print("Begining NA replay renaming")
        rename_replays("na")
    else:
        rename_replays(server);

if __name__ == "__main__":
    main()
