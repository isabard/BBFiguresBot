import nba_py
from nba_py import player
import logging
import os
import pickle

#Current season
CURRENT_SEASON = '2017-18'

# Max age of stat file (seconds) before replace
MAX_AGE = 21600


# Get a list of player_ids for a season and save it
# Ids from each season are stored rather than a master list to minimize cases of duplicate name finds
# Season should be format 'XXXX-XX', e.g. '1995-96' or '2010-11'
# Return 0 for success, 1 for exception
def get_ids(season: str) -> int:
    # get list of all players
    try:
        raw = nba_py.player.PlayerList('00', season, 1)
        # trim raw data
        players = raw.json['resultSets'][0]['rowSet']

        # trim to list of player name and id pair
        player_id = dict(zip([r.pop(2) for r in players], [r.pop(0) for r in players]))

        # dump pickle of list to file
        with open(os.path.join(os.path.dirname(__file__), os.path.join("player_ids", season + ".txt")), "wb") as f:
            pickle.dump(player_id, f)
        return 0
    # Record exception if it occurs
    except nba_py.player.PlayerNotFoundException as err:
        logging.basicConfig(os.path.join(os.path.dirname(__file__), os.path.join("logs", "fetch.log")),
                            level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
        logger = logging.getLogger(__name__)
        logger.error(err)
        return 1


# Check if a file exists for a season of player_ids
# If it does not, call get_ids
# Return 0 for success, 1 for exception
def check_ids(season: str) -> int:
    # If it exists, return
    if os.path.exists(os.path.join(os.path.dirname(__file__), os.path.join("player_ids", season + ".txt"))):
        return 0
    # Otherwise, get list
    else:
        return get_ids(season)


# Get a player's id from his name and a season
# Return player id or -1 for doesn't exist
def get_player_id(name: str, season: str) -> int:
    # Make sure season list exists
    exist = check_ids(season)

    #If it doesn't, return -1
    if exist == -1:
        return -1

    # Open pickle
    with open(os.path.join(os.path.dirname(__file__), os.path.join("player_ids", season + ".txt")), "rb") as f:
        player_ids = pickle.load(f)

    # Return player_id
    if name in player_ids:
        return player_ids[name]
    # If it doesn't exist, return -1
    else:
        return -1


# Anatomy of the JSON retrieved from PlayerCareer
# - 'SeasonTotalsRegularSeason'
#   - ['PLAYER_ID', 'SEASON_ID', 'LEAGUE_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'PLAYER_AGE', 'GP', 'GS', 'MIN', 'FGM',
#       'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK',
#       'TOV', 'PF', 'PTS']
# - 'CareerTotalsRegularSeason'
#   - ['PLAYER_ID', 'LEAGUE_ID', 'Team_ID', 'GP', 'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM',
#      'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
# - 'SeasonTotalsPostSeason'
#   - ['PLAYER_ID', 'SEASON_ID', 'LEAGUE_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'PLAYER_AGE', 'GP', 'GS',
#      'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST',
#      'STL', 'BLK', 'TOV', 'PF', 'PTS']
# - 'CareerTotalsPostSeason'
#   - ['PLAYER_ID', 'LEAGUE_ID', 'Team_ID', 'GP', 'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM',
#      'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
# - 'SeasonTotalsAllStarSeason'
#   - ['PLAYER_ID', 'SEASON_ID', 'LEAGUE_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'PLAYER_AGE', 'GP', 'GS',
#      'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST',
#      'STL', 'BLK', 'TOV', 'PF', 'PTS']
# - 'CareerTotalsAllStarSeason'
#   - ['PLAYER_ID', 'LEAGUE_ID', 'Team_ID', 'GP', 'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM',
#      'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
# - 'SeasonTotalsCollegeSeason'
#   - ['PLAYER_ID', 'SEASON_ID', 'LEAGUE_ID', 'ORGANIZATION_ID', 'SCHOOL_NAME', 'PLAYER_AGE', 'GP', 'GS', 'MIN', 'FGM',
#      'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK',
#      'TOV', 'PF', 'PTS']
# - 'CareerTotalsCollegeSeason'
#   - ['PLAYER_ID', 'LEAGUE_ID', 'ORGANIZATION_ID', 'GP', 'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A',
#      'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
# - 'SeasonRankingsRegularSeason'
#   - ['PLAYER_ID', 'SEASON_ID', 'LEAGUE_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'PLAYER_AGE', 'GP', 'GS', 'RANK_PG_MIN',
#      'RANK_PG_FGM', 'RANK_PG_FGA', 'RANK_FG_PCT', 'RANK_PG_FG3M', 'RANK_PG_FG3A', 'RANK_FG3_PCT', 'RANK_PG_FTM',
#      'RANK_PG_FTA', 'RANK_FT_PCT', 'RANK_PG_OREB', 'RANK_PG_DREB', 'RANK_PG_REB', 'RANK_PG_AST', 'RANK_PG_STL',
#      'RANK_PG_BLK', 'RANK_PG_TOV', 'RANK_PG_PTS', 'RANK_PG_EFF']
# - 'SeasonRankingsPostSeason'
#   - ['PLAYER_ID', 'SEASON_ID', 'LEAGUE_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'PLAYER_AGE', 'GP', 'GS', 'RANK_PG_MIN',
#      'RANK_PG_FGM', 'RANK_PG_FGA', 'RANK_FG_PCT', 'RANK_PG_FG3M', 'RANK_PG_FG3A', 'RANK_FG3_PCT', 'RANK_PG_FTM',
#      'RANK_PG_FTA', 'RANK_FT_PCT', 'RANK_PG_OREB', 'RANK_PG_DREB', 'RANK_PG_REB', 'RANK_PG_AST', 'RANK_PG_STL',
#      'RANK_PG_BLK', 'RANK_PG_TOV', 'RANK_PG_PTS', 'RANK_PG_EFF']


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


# Save player pergame_stats to file
# Takes player id, a type (e.g. PerGame, Per36), and a filename then gets stats and saves it
# File will be saved in type_stats dir with name pid.txt
def save_stats(pid: int, stat_type: str, filename: str):
    # dump pickle of list to file
    stats = get_player_stats(pid, stat_type)
    with open(filename, "wb") as f:
        pickle.dump(stats, f)


# Checks if a stats file exists or is too old (for current season) for a given player name, season, and stat type
# If it does not exist or is too old, does a new fetch
# Otherwise, does nothing else
# Returns player id (-1 if not found)
def check_stats(name: str, season: str, stat_type: str) -> int:
    # Get player id
    pid = get_player_id(name, season)

    # Return -1 if not found
    if pid == -1:
        return pid

    # Filename
    filename = os.path.join(os.path.dirname(__file__), os.path.join(stat_type + "_stats", pid + ".txt"))

    # Check if file exists
    if os.path.exists(filename):
        # Check if current season
        if season == CURRENT_SEASON:
            # Check if file too old
            if os.path.getmtime(filename) >= MAX_AGE:
                # If so, get new stats
                save_stats(pid, stat_type, filename)
    # If it doesn't, get stats
    else:
        save_stats(pid, stat_type, filename)

    return pid

