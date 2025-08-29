import sc2reader
import os
import datetime
import json 
import re 
import argparse

def sanitize_filename(name):
    # Replace bad filename characters with underscores
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def get_last_checked(replay_dir):

    json_file = "date.json"
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

def get_names():
    path = "names.txt"

    data = []

    with open(path, 'r') as file:
        return [name.strip() for name in file.readlines()]

def rename_replays(server):
    # === Configuration ===
    replay_directories = {
    "na": "/mnt/c/Users/Jrchu/OneDrive/Documents/StarCraft II/Accounts/65253659/1-S2-1-1656173/Replays/Multiplayer/",
    "eu": "/mnt/c/Users/Jrchu/OneDrive/Documents/StarCraft II/Accounts/65253659/2-S2-1-9688821/Replays/Multiplayer/"
    }

    my_names = get_names()

    replay_directory = replay_directories[server.lower()]

    last_checked = get_last_checked(replay_directory)

    count = 0

    # === Process each replay file ===
    for filename in os.listdir(replay_directory):
        if not filename.endswith(".SC2Replay"):
            continue
        old_path = os.path.join(replay_directory, filename)

        # skip old replays
        if datetime.datetime.fromtimestamp(os.path.getmtime(old_path)) < last_checked:
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
            opp_name = opponent.name.replace(" ", "_")
            opp_race = opponent.play_race[0]
            timestamp = replay.start_time.strftime("%Y-%m-%d_%H-%M-%S")

            new_name = sanitize_filename(f"{map_name}_{opp_name}_{opp_race}_{timestamp}.SC2Replay")
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
    
    parser.add_argument("-a", "--add_name", type=str)

    parser.add_argument("-s", "--server", type=str)
    
    args = parser.parse_args()

    add_name(args.add_name)

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
