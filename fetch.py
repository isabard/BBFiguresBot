import nba_py
from nba_py import player
import logging
import os
import pickle


# Get a list of player_ids for a season and save it
# Season should be format 'XXXX-XX', e.g. '1995-96' or '2010-11'
def get_ids(season) -> int:
    # get list of all players
    try:
        raw = nba_py.player.PlayerList('00', season, 1)
        # trim raw data
        players = raw.json['resultSets'][0]['rowSet']
        # trim to list of player name and id pair
        player_id = list(zip([r.pop(2) for r in players], [r.pop(0) for r in players]))
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

