import requests
import json
from datetime import datetime
from config.linetracker_config import db_file, query, feed_url
import sqlite3
import uuid
import logging
import argparse
from linetracker_setup import run_setup

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)
# Set as DEBUG for testing

# Database connection global
db_conn = None

# region Dictionary factory for sqlite queries
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
# endregion

# region Database connection methods
def opendb():
    global db_conn
    _logger.debug("Opening database connection")
    try:
       db_conn = sqlite3.connect(db_file)
       db_conn.row_factory = dict_factory
    except Exception as e:
        _logger.debug("Could not open a connection to the database: " + str(e))
    return db_conn.cursor()

def closedb():
    global db_conn
    db_conn.close()
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
        feed_data_modified = False
        _logger.info("Day does not exist, inserting new day: " + today)
        try:
            values = (day_id, game_data['day']['dateandtime'], game_data['day']['lastmodified'])
            cur.execute(query['day']['insert'], values)
            db_conn.commit()
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
        db_conn.commit()
    else:
        _logger.info("Game data has not changed since last update")
        feed_data_modified = False
    # endregion

    # close the database connection
    closedb()


def get_feed_data():
    today = datetime.today().strftime('%Y%m%d')
    response = requests.get(feed_url + today)
    json_data = json.loads(response.text.lower())
    return json_data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose logging messages", dest="v")
    parser.add_argument("--setup", action="store_true", help="Perform initial setup for the application. "
                                        "This will create sqlite3 file and the proper database tables.")
    args = parser.parse_args()
    if args.v:
        _logger.setLevel(logging.DEBUG)
        print("Verbose logging enabled")
        _logger.debug("Verbose logging enabled")

    if args.setup:
        # prepare the application for first use
        _logger.setLevel(logging.DEBUG)
        _logger.info("Performing initial setup of the application")
        print("Beginning initial setup...")
        run_setup()
    else:
        # run application
        update_day()


if __name__ == "__main__":
    main()