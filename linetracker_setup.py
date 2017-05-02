import os
from config.linetracker_config \
    import \
    db_file, \
    db_path, \
    db_name, \
    create_day_table_sql, \
    create_game_table_sql, \
    verify_table_sql, \
    database_tables
import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

# global database connection
dbconn = None

def run_setup():
    # region Directory setup
    _logger.info("Setting up required directories...")
    try:
        os.mkdir(db_path)
    except FileExistsError as e:
        _logger.info("Directory `%s` already exists" % (db_path,))
    except Exception as e:
        _logger.debug(e)
    # endregion

    # region Database setup
    _logger.info("Beginning database setup...")
    global dbconn
    try:
        dbconn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        _logger.debug("Error when connecting to the sqlite3 database '%s' due to exception: %s" % (db_name, e))
    # create the database tables
    create_tables()
    # endregion

def create_table(table_name, sql):
    global dbconn
    cur = dbconn.cursor()
    try:
        _logger.info("Creating `%s` table..." % (table_name,))
        cur.execute(sql)
        _logger.info("Created `%s` table" % (table_name,))
    except sqlite3.DatabaseError as db_error:
        _logger.debug(db_error)
    except sqlite3.Error as e:
        _logger.debug("Another error has occurred: '%s' " % (e,))

# Database table creation statements
def create_tables():
    global dbconn
    cur = dbconn.cursor()
    try:
        _logger.info("Creating `day` table...")
        cur.execute(create_day_table_sql)
        _logger.info("Created `day` table")
    except sqlite3.DatabaseError as db_error:
        _logger.debug(db_error)
    except sqlite3.Error as e:
        _logger.debug("Another error has occurred: '%s' " % (e,))

    # verify setup
    verify()

def verify():
    global dbconn
    _logger.info("Verifying setup...")
    if not os.path.exists(db_file):
        _logger.debug("Could not find database file '%s'" % (db_file,))
    else:
        _logger.info("Found database file `%s`" % (db_file,))

    # region Verify database configuration
    _logger.info("Verifying database tables exist...")
    cur = dbconn.cursor()
    try:
        for t in database_tables:
            cur.execute(verify_table_sql, (t,))
            count = len(cur.fetchall())
            if count == 1:
                _logger.info("Table `%s` exists" % (t,))
            else:
                _logger.debug("Could not find table `%s`" % (t,))
    except Exception as e:
        _logger.debug(e)
    finally:
        dbconn.close()
    # endregion

    _logger.info("Setup verified successfully!")