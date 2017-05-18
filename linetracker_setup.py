import os
import sqlite3

from config.linetracker_config \
    import \
    db_file, \
    db_path, \
    db_name, \
    verify_table_sql, \
    dbtable_create_statements
from helpers.utils.logger import configure_logging

# _logger = logging.getLogger(__name__)
# _logger.setLevel(logging.DEBUG)
# ch = logging.StreamHandler()
# ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# _logger.addHandler(ch)

_logger = configure_logging(__name__, level='DEBUG')

# global database connection
dbconn = None

def run_setup():
    # region Directory setup
    _logger.info('Setting up required directories...')
    try:
        os.mkdir(db_path)
    except FileExistsError as e:
        _logger.info('Directory `%s` already exists' % (db_path,))
    except Exception as e:
        _logger.debug(e)
    # endregion

    # region Database setup
    _logger.info('Beginning database setup...')
    global dbconn
    try:
        dbconn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        _logger.debug('Error when connecting to the sqlite3 database \'%s\' due to exception: %s' % (db_name, e))
    # create the database tables
    create_tables()
    # endregion

# Database table creation statements
def create_tables():
    global dbconn
    cur = dbconn.cursor()
    for key in dbtable_create_statements:
        try:
            cur.execute(dbtable_create_statements[key])
            _logger.info('`%s` table created successfully' % key)
        except sqlite3.DatabaseError as db_error:
            _logger.debug(db_error)
        except sqlite3.Error as e:
            _logger.debug('Another error has occurred: \'%s\' ' % e)

    # verify setup
    verify_setup()

def verify_setup():
    _logger.info('*************** Beginning setup verification phase ***************')
    global dbconn
    if not os.path.exists(db_file):
        _logger.debug('Could not find database file \'%s\'' % (db_file,))
    else:
        _logger.info('Found database file `%s`' % (db_file,))

    # region Verify database configuration
    _logger.info('Verifying database tables exist...')
    cur = dbconn.cursor()
    try:
        for t in dbtable_create_statements:
            cur.execute(verify_table_sql, (t,))
            count = len(cur.fetchall())
            if count == 1:
                _logger.info('Table `%s` exists' % (t,))
            else:
                _logger.debug('Could not find table `%s`' % (t,))
    except Exception as e:
        _logger.debug(e)
    finally:
        _logger.info('Closing database connection')
        dbconn.close()
    # endregion
    _logger.info('Setup verified successfully!')
    print('\nSetup complete.')