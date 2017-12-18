import nba_py
from nba_py import player
import logging
import os
import pickle
import re

# Current season
CURRENT_SEASON = '2017-18'

# Max age of stat file (seconds) before replace
MAX_AGE = 21600

# Rows to remove from printed dicts
UNNEEDED_ROWS = ["PLAYER_ID", "LEAGUE_ID", "TEAM_ID", "Team_ID", "ORGANIZATION_ID"]

# Rows to rename for printing
NEW_ROW_NAMES = {"SEASON_ID": "SEASON", "TEAM_ABBREVIATION": "TEAM", "PLAYER_AGE": "AGE"}


# Get a list of player_ids and save it
# Return 0 for success, 1 for exception
def get_ids() -> int:
    # get list of all players
    try:
        raw = nba_py.player.PlayerList('00', CURRENT_SEASON, 0)
        # trim raw data
        players = raw.json['resultSets'][0]['rowSet']

        # trim to list of player name and id pair
        player_id = dict(zip([r.pop(2) for r in players], [r.pop(0) for r in players]))

        # dump pickle of list to file
        with open(os.path.join(os.path.dirname(__file__), "player_ids.txt"), "wb") as f:
            pickle.dump(player_id, f)
        return 0
    # Record exception if it occurs
    except nba_py.player.PlayerNotFoundException as err:
        logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), os.path.join("logs", "fetch.log")),
                            level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
        logger = logging.getLogger(__name__)
        logger.error(err)
        return 1


# Check if player_ids exists
# If it does not, call get_ids
# Return 0 for success, 1 for exception
def check_ids() -> int:
    # If it exists, return
    if os.path.exists(os.path.join(os.path.dirname(__file__), "player_ids.txt")):
        return 0
    # Otherwise, get list
    else:
        return get_ids()


# Get a player's id from his name and a season
# Return player id or -1 for doesn't exist
def get_player_id(name: str, season: str) -> int:
    # Make sure season list exists
    exist = check_ids()

    # If it doesn't, return -1
    if exist == -1:
        return -1

    # Open pickle
    with open(os.path.join(os.path.dirname(__file__), "player_ids.txt"), "rb") as f:
        player_ids = pickle.load(f)

    # Return player_id
    if name in player_ids:
        return player_ids[name]
    # If it doesn't exist, return -1
    else:
        return -1


# Return a dict of dicts for a player's pergame_stats for career from his id and a stat type (e.g. PerGame, Per36)
# Each dict will have a key from above with a space and then season (if applicable)
#   (e.g. 'SeasonTotalsRegularSeason 2016-17') with keys listed under it
def get_player_stats(pid: int, stat_type: str) -> dict:
    # Get json
    player_json = player.PlayerCareer(pid, stat_type, '00')
    pl = player_json.json['resultSets']

    # Form into usable dicts
    player_stats = {}
    for i in pl:
        # If the rowSet has more than 1, add each
        if len(i['rowSet']) > 1:
            for j in i['rowSet']:
                player_stats[i['name'] + " " + j[1]] = dict(zip(i['headers'], j))
        # If it has just one, add the one rowSet
        elif len(i['rowSet']) > 0:
            player_stats[i['name']] = dict(zip(i['headers'], i['rowSet'][0]))
        # Otherwise, leave it empty
        else:
            player_stats[i['name']] = {}

    return player_stats


# Save player stats to file
# Takes player id and a type (e.g. PerGame, Per36) and saves it
# File will be saved in type_stats dir with name pid.txt
def save_stats(pid: int, stat_type: str):
    # Filename
    filename = os.path.join(os.path.dirname(__file__), os.path.join(stat_type.lower() + "_stats", str(pid) + ".txt"))

    # dump pickle of list to file
    stats = get_player_stats(pid, stat_type)
    with open(filename, "wb+") as f:
        pickle.dump(stats, f)


# Open player stats from file
# Takes player id and a type (e.g. PerGame, Per36) and returns the dict
# Will do work of checking that stats exists
def open_stats(name: str, season: str, stat_type: str) -> dict:
    # Get player id
    pid = get_player_id(name, season)

    # Filename
    filename = os.path.join(os.path.dirname(__file__), os.path.join(stat_type.lower() + "_stats", str(pid) + ".txt"))

    # Check if the file doesn't exist
    if not pid == check_stats(pid, season, stat_type):
        # If not, save them
        save_stats(pid, stat_type)

    # Open it and return
    with open(filename, "rb") as f:
        return pickle.load(f)


# Checks if a stats file exists or is too old (for current season) for a given player id, season, and stat type
# If it does not exist or is too old, does a new fetch
# Otherwise, does nothing else
# Returns player id (-1 if not found)
def check_stats(pid: int, season: str, stat_type: str) -> int:
    # Return -1 if not found
    if pid == -1:
        return pid

    # Filename
    filename = os.path.join(os.path.dirname(__file__), os.path.join(stat_type.lower() + "_stats", str(pid) + ".txt"))

    # Check if file exists
    if os.path.exists(filename):
        # Check if current season
        if season == CURRENT_SEASON:
            # Check if file too old
            if os.path.getmtime(filename) >= MAX_AGE:
                # If so, get new stats
                save_stats(pid, stat_type)
    # If it doesn't, get stats
    else:
        save_stats(pid, stat_type)

    return pid


# Return a table formatted string for a PlayerCareer dict
def dict_to_string(stats: dict, dict_name: str) -> str:
    st = stats[dict_name]
    stat_string = ""

    # Remove useless columns from dict
    for header in UNNEEDED_ROWS:
        st.pop(header, None)

    # Add header row
    for header in st.keys():
        stat_string += header + "|"

    # Remove last |
    stat_string = stat_string[:-1]

    # New line
    stat_string += "\n"

    # Add cell formatting
    for i in range(0, len(st)):
        stat_string += ":-:" + "|"

    # Remove last |
    stat_string = stat_string[:-1]

    # New line
    stat_string += "\n"

    # Add values
    for header in st.keys():
        stat_string += str(st[header]) + "|"

    # Remove last |
    stat_string = stat_string[:-1]

    # Rename some rows
    for header in NEW_ROW_NAMES.keys():
        stat_string = stat_string.replace(header, NEW_ROW_NAMES[header])

    return stat_string


# Take in a string request for a stat table and return a string of that table
# Request format: Get PLAYER_NAME's SEASON SEASON_TYPE STAT_TYPE TOTAL_OR_RANKINGS
# PLAYER NAME: e.g. Paul Pierce
# SEASON: e.g. 2008-09 or career
# SEASON TYPE: regular season/postseason/college season/allstar season
# STAT TYPE: totals/per game/ per 36
# TOTAL OR RANKINGS: totals/rankings
# Total request e.g.: Get Paul Pierce's 2008-09 regular season per game totals
#               e.g.: Get Kevin Garnett's career postseason per 36 totals
def get_stat_table(request: str) -> str:
    # Lowercase version for searching
    req_low = request.lower()

    # Extract player name
    try:
        player_name = re.search("Get (.*)'s ", request).group(1)
    except AttributeError:
        raise Exception("No name found!")

    # Extract season
    try:
        season = re.search("'s (\d{4}-\d{2}) ", request).group(1)
    except AttributeError:
        season = ""

    # dict_name
    dict_name = ""

    # Determine if career or season
    if "career" in req_low:
        dict_name += "Career"
    else:
        dict_name += "Season"

    # Determine if rankings or totals
    if "rankings" in req_low:
        dict_name += "Rankings"
    else:
        dict_name += "Totals"

    # Determine if regular/post/college/allstar
    if "regular" in req_low:
        dict_name += "RegularSeason"
    elif "postseason" in req_low:
        dict_name += "PostSeason"
    elif "college" in req_low:
        dict_name += "CollegeSeason"
    elif "allstar" in req_low:
        dict_name += "AllStarSeason"
    else:
        raise Exception("No season type found!")

    # Add season if applicable
    if len(season) > 0:
        dict_name += " " + season
    else:
        season = CURRENT_SEASON

    # Get stat type
    if "per game" in req_low:
        stat_type = "PerGame"
    elif "per 36" in req_low:
        stat_type = "Per36"
    else:
        stat_type = "Totals"

    # Get player dict
    player_dict = open_stats(player_name, season, stat_type)

    # Return string of table
    return dict_to_string(player_dict, dict_name)
