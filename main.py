import time
import requests
import json
from datetime import datetime
from config.linetracker_config import db_file, query, feed_url
import sqlite3
import uuid
import logging
import argparse
import linetracker_setup

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
_logger.addHandler(ch)

# Database connection global
dbconn = None

# region Dictionary factory for sqlite queries
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
# endregion

# region Database connection methods
def opendb():
    global dbconn
    _logger.debug("Opening database connection")
    try:
       dbconn = sqlite3.connect(db_file)
       dbconn.row_factory = dict_factory
    except Exception as e:
        _logger.debug("Could not open a connection to the database: " + str(e))
    return dbconn.cursor()

def closedb():
    global dbconn
    _logger.debug("Closing database connection")
    dbconn.close()
# endregion

def update_day():
    cur = opendb()
    today = datetime.today().strftime('%Y-%m-%d')
    try:
        _logger.info("Getting feed data for: " + str(today))
        game_data = get_feed_data()
    except Exception as e:
        _logger.debug("Failed to get feed data: " + str(e))
    day_id = str(uuid.uuid4()).replace("-", "")

    # region Check if day already exists
    cur.execute(query['day']['check_day_exists'], (today,))
    day_data = cur.fetchall()
    if len(day_data) < 1:
        feed_data_modified = True
        _logger.info("Day does not exist, inserting new day: " + today)
        try:
            values = (day_id, game_data['day']['dateandtime'], game_data['day']['lastmodified'])
            cur.execute(query['day']['insert'], values)
            dbconn.commit()
        except Exception as e:
            _logger.debug("Failed to insert new day: " + str(e))
    elif int(game_data['day']['lastmodified']) != int(day_data[0]['lastmodified']):
        feed_data_modified = True
        new_lastmodified = int(game_data['day']['lastmodified'])
        old_lastmodified = int(day_data[0]['lastmodified'])
        _logger.info("Last modified date has changed. Was: " + str(old_lastmodified) + ", Now: " +
                     str(new_lastmodified) + " updating row in database for day: " + str(today))
        lastmodified = int(game_data['day']['lastmodified'])
        cur.execute(query['day']['update_lastmodified'], (lastmodified, today,))
        dbconn.commit()
    else:
        _logger.info("Game data has not changed since last update")
        feed_data_modified = False
    # endregion

    if feed_data_modified:
        # add modified entries into the database
        # update_games(game_data, today)
        pass
    update_games(game_data, today)
    # close the database connection
    closedb()


def insert_game(guid, day_id, league, game, cursor):
    global dbconn
    cursor.execute(query['games']['insert'], (
        str(guid),
        day_id,
        league['name'],
        game['primaryid'],
        game['date'],
        game['gamestatus'],
        game['period'],
        game['away']['info']['teamname'],
        game['away']['info']['sfid'],
        game['away']['info']['openline'],
        game['away']['info']['linemovementnowrap'],
        game['away']['info']['halftimecurrentline'],
        game['away']['info']['currentline'],
        game['away']['info']['currentmoneyline'],
        game['away']['info']['pitchername'],
        game['away']['info']['currentmlbrunline'],
        game['away']['info']['moneybettingtrends'],
        game['away']['info']['pointspreadbettingtrends'],
        game['away']['info']['totalbettingtrends'],
        game['home']['info']['teamname'],
        game['home']['info']['sfid'],
        game['home']['info']['openline'],
        game['home']['info']['linemovementnowrap'],
        game['home']['info']['halftimecurrentline'],
        game['home']['info']['currentline'],
        game['home']['info']['currentmoneyline'],
        game['home']['info']['pitchername'],
        game['home']['info']['currentmlbrunline'],
        game['home']['info']['moneybettingtrends'],
        game['home']['info']['pointspreadbettingtrends'],
        "test"
    ))
    dbconn.commit()


def update_games(data, today):
    _logger.info("Inserting new game data")
    cur = opendb()
    cur.execute(query['day']['get_day_id'], (today,))
    day_id = cur.fetchone()['day_id']
    _logger.info("Inserting games with day id: " + str(day_id))
    for league in data['day']['league']:
        if type(league['game']).__name__ == 'list':
            for game in league['game']:
                guid = uuid.uuid4()
                insert_game(guid, day_id, league, game, cur)
        else:
            guid = uuid.uuid4()
            game = league['game']
            insert_game(guid, day_id, league, game, cur)
    # close the database connection
    closedb()


def get_feed_data():
    today = datetime.today().strftime('%Y%m%d')
    response = requests.get(feed_url + today)
    return json.loads(response.text.lower())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose logging messages", dest="v")
    parser.add_argument("--setup", action="store_true", help="Prepare the application for first use.")
    args = parser.parse_args()
    if args.v:
        _logger.setLevel(logging.DEBUG)
        _logger.debug("Verbose logging enabled")

    if args.setup:
        # prepare the application for first use
        # set logging level to DEBUG since this is initial application setup task
        _logger.setLevel(logging.DEBUG)
        _logger.info("Performing initial setup of the application")
        # start the setup
        linetracker_setup.run_setup()
    else:
        # run application
        while True:
            update_day()
            time.sleep(300)


if __name__ == "__main__":
    # Call to main
    main()
