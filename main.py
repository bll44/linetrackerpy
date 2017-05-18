import time
import requests
import json
from datetime import datetime
from config import linetracker_config as lt_config
import sqlite3
import uuid
import logging
import argparse
import linetracker_setup
import threading
import cherrypy
from server import LTServer
from lib.logger import configure_logging


_logger = configure_logging(__name__, level='DEBUG')

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
    _logger.debug('Opening database connection')
    try:
       dbconn = sqlite3.connect(lt_config.db_file)
       dbconn.row_factory = dict_factory
    except Exception as e:
        _logger.debug('Could not open a connection to the database: ' + str(e))
    return dbconn.cursor()

def closedb():
    global dbconn
    _logger.debug('Closing database connection')
    dbconn.close()
# endregion

def run_server():
    cherrypy.config.update()
    cherrypy.quickstart(LTServer(), '/')

def update_data():
    while True:
        update_day()
        time.sleep(300)

def update_day():
    cur = opendb()
    today = datetime.today().strftime('%Y-%m-%d')
    try:
        _logger.info('Getting feed data for: ' + str(today))
        game_data = get_feed_data()
    except Exception as e:
        _logger.debug("Failed to get feed data: " + str(e))
    day_id = str(uuid.uuid4()).replace("-", "")

    # region Check if day already exists
    # _logger.debug(game_data)
    cur.execute(lt_config.query['day']['check_day_exists'], (today,))
    day_data = cur.fetchall()
    if len(day_data) < 1:
        feed_data_modified = True
        _logger.info('Day does not exist, inserting new day: ' + today)
        try:
            values = (day_id, game_data['day']['dateandtime'], game_data['day']['lastmodified'])
            cur.execute(lt_config.query['day']['insert'], values)
            dbconn.commit()
        except Exception as e:
            _logger.debug('Failed to insert new day: ' + str(e))
    elif int(game_data['day']['lastmodified']) != int(day_data[0]['lastmodified']):
        feed_data_modified = True
        new_lastmodified = int(game_data['day']['lastmodified'])
        old_lastmodified = int(day_data[0]['lastmodified'])
        _logger.info("Last modified date has changed. Was: " + str(old_lastmodified) + ", Now: " +
                     str(new_lastmodified) + " updating row in database for day: " + str(today))
        lastmodified = int(game_data['day']['lastmodified'])
        cur.execute(lt_config.query['day']['update_lastmodified'], (lastmodified, today,))
        dbconn.commit()
    else:
        _logger.info('Game data has not changed since last update')
        feed_data_modified = False
    # endregion

    if feed_data_modified:
        # add modified entries into the database
        # update_games(game_data, today)
        pass
    update_games(game_data, today)
    # close the database connection
    closedb()


def insert_game(guid, day_id, league, game, cursor, created_at):
    global dbconn
    cursor.execute(lt_config.query['games']['insert'], (
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
        game['home']['info']['totalbettingtrends'],
        created_at
    ))
    dbconn.commit()


def update_games(data, today):
    _logger.info('Inserting new game data')
    cur = opendb()
    cur.execute(lt_config.query['day']['get_day_id'], (today,))
    day_id = cur.fetchone()['day_id']
    _logger.info('Inserting games with day id: ' + str(day_id))
    created_at = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    for league in data['day']['league']:
        if type(league['game']).__name__ == 'list':
            for game in league['game']:
                guid = uuid.uuid4()
                insert_game(guid, day_id, league, game, cur, created_at)
        else:
            guid = uuid.uuid4()
            game = league['game']
            insert_game(guid, day_id, league, game, cur, created_at)
    # close the database connection
    closedb()


def get_feed_data():
    today = datetime.today().strftime('%Y%m%d')
    response = requests.get(lt_config.feed_url + today)
    return json.loads(response.text.lower())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose logging messages', dest='v')
    parser.add_argument('--setup', action='store_true', help='Prepare the application for first use.',
                        dest='setup')
    args = parser.parse_args()
    if args.v:
        _logger.setLevel(logging.DEBUG)
        _logger.debug('Verbose logging enabled')

    if args.setup:
        # prepare the application for first use
        # set logging level to DEBUG since this is initial application setup task
        _logger.setLevel(logging.DEBUG)
        _logger.info('Performing initial setup of the application')
        # start the setup
        linetracker_setup.run_setup()
    else:
        # run application
        data_thread = threading.Thread(target=update_data)
        data_thread.daemon = True
        data_thread.start()

        server = threading.Thread(target=run_server)
        server.daemon = True
        server.start()

        server.join()


if __name__ == '__main__':
    # Call to main
    main()
