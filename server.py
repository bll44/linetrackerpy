import cherrypy
import logging
from lib.logger import configure_logging
import sqlite3

# _logger = logging.getLogger(__name__)
# _logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
# _logger.addHandler(ch)

_logger = configure_logging(__name__, level='DEBUG')

class LTServer(object):

    @cherrypy.expose
    def index(self):
        _logger.info('testing the configure_logging method')
        return 'Linetrackerpy'

    @cherrypy.expose
    def view_data(self):
        return 'LTServer data'