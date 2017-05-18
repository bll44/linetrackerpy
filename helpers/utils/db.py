import sqlite3
from config.linetracker_config import db_file
from helpers.utils.logger import configure_logging

_logger = configure_logging(__name__, level='DEBUG')

dbconn = None

# region Dictionary factory for sqlite queries
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
# endregion

# region Database connection methods
def get_cursor():
    global dbconn
    _logger.debug('Opening database connection')
    try:
       dbconn = sqlite3.connect(db_file)
       dbconn.row_factory = dict_factory
    except Exception as e:
        _logger.debug('Could not open a connection to the database: %s' % e)
    return dbconn.cursor()

def closedb():
    global dbconn
    _logger.debug('Closing database connection')
    dbconn.close()
# endregion

